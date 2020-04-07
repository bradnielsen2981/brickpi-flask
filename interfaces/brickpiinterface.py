import brickpi3 # import the BrickPi3 drivers
import time
import math
import sys
import logging
import threading
from di_sensors.easy_mutex import ifMutexAcquire, ifMutexRelease 
from di_sensors.inertial_measurement_unit import InertialMeasurementUnit
from di_sensors.temp_hum_press import TempHumPress
#DO I NEED TO USE MUTEX???

#this needs to go inside the class at somepoint, im trying to avoid confusing students
NOREADING = 999 #just using 999 to represent no reading
MAGNETIC_DECLINATION = 11 #i believe this is correct for Brisbane
USEMUTEX = True #avoid threading issues using the IMU sensorm might need to use this for thermal sensor
ENABLED = 1
DISABLED = 5 #if the sensor returns NOREADING more than 5 times in a row, its permanently disabled

#Created a Class to wrap the robot functionality, one of the features is the idea of keeping track of the CurrentCommand, this is important when more than one process is running...
class BrickPiInterface():

    #Initialise log and timelimit
    def __init__(self, timelimit=20):
        self.logger = None
        self.CurrentCommand = "loading"
        self.Configured = False #is the robot yet configured?
        self.BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3
        self.timelimit = timelimit #failsafe timelimit - motors turn off after
        self.imu_status = 0 
        self.set_ports()
        self.CurrentCommand = "loaded" #when the device is ready for a new instruction it will be set to stop
        return

    #--- Initialise Ports --------#
    def set_ports(self):
        bp = self.BP
        self.rightmotor = bp.PORT_A
        self.leftmotor = bp.PORT_B
        self.largemotors = bp.PORT_A + bp.PORT_B
        self.mediummotor = bp.PORT_C
        self.thermal = bp.PORT_1 #Thermal infrared Sensor
        self.colour = bp.PORT_2 #Colour Sensor
        self.ultra = bp.PORT_4 #ultraSonic Sensor
        self.claw_closed = False #Current state of the claw
        self.thermal_thread = None #DO NOT REMOVE THIS - USED LATER
        self.configure_sensors()
        return

    #-- Configure Sensors - take 4 seconds ---------#
    def configure_sensors(self):
        bp = self.BP
        self.config = {} #create a dictionary that represents if the sensor is configured
        #set up colour sensor
        try:
            bp.set_sensor_type(self.colour, bp.SENSOR_TYPE.EV3_COLOR_COLOR)
            time.sleep(1)
            self.config['colour'] = ENABLED #enabled
        except Exception as error:
            self.log("Colour Sensor not found")
            self.config['colour'] = DISABLED #disabled
        #set up ultrasonic
        try:
            bp.set_sensor_type(self.ultra, bp.SENSOR_TYPE.EV3_ULTRASONIC_CM)
            time.sleep(1.5)
            self.config['ultra'] = ENABLED
        except Exception as error:
            self.log("Ultrasonic Sensor not found")
            self.config['ultra'] = DISABLED
        #set up thermal
        try:
            bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.I2C, [0, 20])
            time.sleep(1)
            self.config['thermal'] = ENABLED
            self.__start_thermal_infrared_thread()
        except Exception as error:
            self.log("Thermal Sensor not found")
            self.config['thermal'] = DISABLED 
        #set up imu      
        try:
            self.imu = InertialMeasurementUnit()
            time.sleep(1)
            self.config['imu'] = ENABLED
        except Exception as error:
            self.log("IMU sensor not found")
            self.config['imu'] = DISABLED   
        
        bp.set_motor_limits(self.mediummotor, 100, 600) #set power / speed limit 
        self.Configured = True #there is a 4 second delay - before robot is configured
        return

    #-- Start Infrared I2c Thread ---------#
    def __start_thermal_infrared_thread(self):
        self.thermal_thread = threading.Thread(target=self.__update_thermal_sensor_thread, args=(1,))
        self.thermal_thread.daemon = True
        self.thermal_thread.start()
        return

    #changes the logger
    def set_log(self, logger):
        self.logger=logger
        return

    #-----------SENSOR COMMAND----------------#
    #get the current voltage - need to work out how to determine battery life
    def get_battery(self):
        return self.BP.get_voltage_battery()

    #self.log out a complete output from the IMU sensor
    def calibrate_imu(self, timelimit=20):
        if self.config['imu'] >= DISABLED:
            return
        self.stop_all() #stop everything while calibrating...
        self.CurrentCommand = "calibrate_imu"
        self.log("Move around the robot to calibrate the Compass Sensor...")
        self.imu_status = 0
        elapsed = 0; start = time.time()
        timelimit = start + timelimit #maximum of 20 seconds to calibrate compass sensor
        while self.imu_status != 3 and time.time() < timelimit:
            newtime = time.time()
            newelapsed = int(newtime - start)
            if newelapsed > elapsed:
                elapsed = newelapsed
                self.log("Calibrating IMU. Status: " + str(self.imu_status) + " Time: " + str(elapsed))
            ifMutexAcquire(USEMUTEX)
            try:
                self.imu_status = self.imu.BNO055.get_calibration_status()[3]
                self.config['imu'] = ENABLED
                time.sleep(0.01)
            except Exception as error:
                self.log("IMU Calibration Error: " + str(error))
                self.config['imu'] += 1
            finally:
                ifMutexRelease(USEMUTEX)
        if self.imu_status == 3:
            self.log("IMU Compass Sensor has been calibrated")
            return True
        else:
            self.log("Calibration unsuccessful")
            return 
        return

    #hopefull this is an emergency reconfigure of the IMU Sensor
    def reconfig_IMU(self):
        ifMutexAcquire(USEMUTEX)
        try:
            self.imu.BNO055.i2c_bus.reconfig_bus()
            time.sleep(0.1) #restabalise the sensor
            self.config['imu'] = ENABLED
        except Exception as error:
            self.log("IMU RECONFIG HAS FAILED" + str(error))
            self.config['imu'] = DISABLED
        finally:
            ifMutexRelease(USEMUTEX)
        return

    #returns the compass value from the IMU sensor - note if the IMU is placed near a motor it can be affected -SEEMS TO RETURN A VALUE BETWEEN -180 and 180. 
    def get_compass_IMU(self):
        heading = NOREADING
        if self.config['imu'] >= DISABLED:
            return heading
        ifMutexAcquire(USEMUTEX)
        try:
            (x, y, z)  = self.imu.read_magnetometer()
            time.sleep(0.01)
            self.config['imu'] = ENABLED
            heading = int(math.atan2(y, x)*(180/math.pi)) + MAGNETIC_DECLINATION 
            #make it 0 - 360 degrees
            if heading < 0:
                heading += 360
            elif heading > 360:
                heading -= 360
        except Exception as error:
            self.log("IMU: " + str(error))
            self.config['imu'] += 1
        finally:
            ifMutexRelease(USEMUTEX)
        return heading

    #returns the absolute orientation value using euler rotations, I think this is calilbrated from the compass sensor and therefore requires calibration
    def get_orientation_IMU(self):
        readings = (NOREADING,NOREADING,NOREADING)
        if self.config['imu'] >= DISABLED:
            return readings
        ifMutexAcquire(USEMUTEX)
        try:
            readings = self.imu.read_euler()
            time.sleep(0.01)
            self.config['imu'] = ENABLED
        except Exception as error:
            self.log("IMU Orientation: " + str(error))
            self.config['imu'] += 1
        finally:
            ifMutexRelease(USEMUTEX)
        return readings  
    
    #returns the acceleration from the IMU sensor - could be useful for detecting collisions or an involuntary stop
    def get_linear_acceleration_IMU(self):
        readings = (NOREADING,NOREADING,NOREADING)
        if self.config['imu'] >= DISABLED:
            return readings
        ifMutexAcquire(USEMUTEX)
        try:
            #readings = self.imu.read_accelerometer()
            readings = self.imu.read_linear_acceleration()
            #readings = tuple([int(i*100) for i in readings])
            time.sleep(0.01)
            self.config['imu'] = ENABLED
        except Exception as error:
            self.log("IMU Acceleration: " + str(error))
            self.config['imu'] += 1
        finally:
            ifMutexRelease(USEMUTEX)   
        return readings

    #get the gyro sensor angle/seconds acceleration from IMU sensor
    def get_gyro_sensor_IMU(self):
        gyro_readings = (NOREADING,NOREADING,NOREADING)
        if self.config['imu'] >= DISABLED:
            return gyro_readings
        ifMutexAcquire(USEMUTEX)
        try:
            gyro_readings = self.imu.read_gyroscope() #degrees/s
            time.sleep(0.01)
            self.config['imu'] = ENABLED
        except Exception as error:
            self.log("IMU GYRO: " + str(error))
            self.config['imu'] += 1
        finally:
            ifMutexRelease(USEMUTEX)
        return gyro_readings

    #gets the temperature using the IMU sensor
    def get_temperature_IMU(self):
        temp = NOREADING
        if self.config['imu'] >= DISABLED:
            return temp
        ifMutexAcquire(USEMUTEX)
        try:
            temp = self.imu.read_temperature()
            time.sleep(0.01)
            self.config['imu'] = ENABLED
        except Exception as error:
            self.log("IMU Temp: " + str(error))
            self.config['imu'] += 1
        finally:
            ifMutexRelease(USEMUTEX)
        return temp

    #get the ultrasonic sensor
    def get_ultra_sensor(self):
        distance = NOREADING
        if self.config['ultra'] >= DISABLED:
            return distance
        bp = self.BP
        ifMutexAcquire(USEMUTEX)
        try:
            distance = bp.get_sensor(self.ultra)
            time.sleep(0.3)
            self.config['ultra'] = ENABLED
        except brickpi3.SensorError as error:
            self.log("ULTRASONIC: " + str(error))
            self.config['ultra'] += 1
        finally:
            ifMutexRelease(USEMUTEX) 
        return distance

    #returns the colour current sensed - "none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"
    def get_colour_sensor(self):
        if self.config['colour'] >= DISABLED:
            return "NOREADING"
        bp = self.BP
        value = 0
        colours = ["NOREADING", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"]
        ifMutexAcquire(USEMUTEX)
        try: 
            value = bp.get_sensor(self.colour) 
            time.sleep(0.01)
            self.config['colour'] = ENABLED
        except brickpi3.SensorError as error:
            self.log("COLOUR: " + str(error))
            self.config['colour'] += 1
        finally:
            ifMutexRelease(USEMUTEX)                
        return colours[value]

    #updates the thermal sensor by making continual I2C transactions through a thread
    def __update_thermal_sensor_thread(self, name):
        while self.CurrentCommand != "exit":
            self.update_thermal_sensor()
        return

    #updates the thermal sensor by making a single I2C transaction
    def update_thermal_sensor(self):
        if self.config['thermal'] >= DISABLED:
            self.CurrentCommand = 'exit' #end thread
            return
        bp = self.BP
        TIR_I2C_ADDR        = 0x0E      # TIR I2C device address 
        TIR_AMBIENT         = 0x00      # Ambient Temp
        TIR_OBJECT          = 0x01      # Object Temp
        TIR_SET_EMISSIVITY  = 0x02      
        TIR_GET_EMISSIVITY  = 0x03
        TIR_CHK_EMISSIVITY  = 0x04
        TIR_RESET           = 0x05
        try:
            bp.transact_i2c(self.thermal, TIR_I2C_ADDR, [TIR_OBJECT], 2)
            time.sleep(0.01)
        except Exception as error:
            self.log("THERMAL UPDATE: " + str(error))
        finally:
            pass
        return

    #return the infrared temperature - if usethread=True - it uses the thread set up in init
    def get_thermal_sensor(self, usethread=True):
        temp = NOREADING
        if self.config['thermal'] >= DISABLED:
            return temp
        bp = self.BP
        if not usethread:
            self.update_thermal_sensor() #not necessary if thread is running
        ifMutexAcquire(USEMUTEX)
        try:
            value = bp.get_sensor(self.thermal) # read the sensor values
            time.sleep(0.01)
            self.config['thermal'] = ENABLED
            temp = (float)((value[1] << 8) + value[0]) # join the MSB and LSB part
            temp = temp * 0.02 - 0.01                  # Converting to Celcius
            temp = temp - 273.15                       
        except Exception as error:
            self.log("THERMAL READ: " + str(error))
            self.config['thermal'] += 1
        finally:
            ifMutexRelease(USEMUTEX)    
        return float("%3.f" % temp)

    #disable thermal sensor - might be needed to reenable motors (they disable for some reason when thermal sensor is active)
    def disable_thermal_sensor(self):
        bp = self.BP
        bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.NONE) 
        return

    #--------------MOTOR COMMANDS-----------------#
    #simply turns motors on
    def move_power(self, power):
        bp = self.BP
        self.CurrentCommand = "move_power"
        self.BP.set_motor_power(self.largemotors, power)
        return

    #moves for the specified time (seconds) and power - use negative power to reverse
    def move_power_time(self, power, t):
        bp = self.BP
        self.CurrentCommand = "move_power_time"
        timelimit = time.time() + t
        while time.time() < timelimit and self.CurrentCommand != "stop":
            bp.set_motor_power(self.largemotors, power)
        self.CurrentCommand = "stop"
        self.BP.set_motor_power(self.largemotors, 0)
        return
    
    #moves with power until obstruction and return time travelled
    def move_power_untildistanceto(self, power, distanceto):
        if self.config['ultra'] >= DISABLED:
            return 0
        self.CurrentCommand = "move_power_untildistanceto"
        bp = self.BP
        distancedetected = 300 # to set an initial distance detected before loop
        elapsedtime = 0;  start = time.time()
        #Turn motors on
        bp.set_motor_power(self.largemotors, power)
        timelimit = time.time() + self.timelimit  #all timelimits are a backup plan
        while (self.CurrentCommand != "stop" and time.time() < timelimit):

            ##if sensor fails, or distanceto has been reached quit, or distancedetected = 0
            distancedetected = self.get_ultra_sensor()
            self.logger.info("MOVING - Distance detected: " + str(distancedetected))
            if ((self.config['ultra'] > DISABLED) or (distancedetected < distanceto and distancedetected != 0.0)): 
                #if an object has been detected, identify the type of object
                break 

            ##insert other tests e.g if red colour

        self.CurrentCommand = "stop"
        elapsedtime = time.time() - start
        bp.set_motor_power(self.largemotors, 0)
        return elapsedtime

    #Rotate power and time, -power to reverse
    def rotate_power_time(self, power, t):
        self.CurrentCommand = "rotate_power_time"
        bp = self.BP
        target = time.time() + t
        while time.time() < target and self.CurrentCommand != 'stop':
            bp.set_motor_power(self.rightmotor, -power)
            bp.set_motor_power(self.leftmotor, power)
        bp.set_motor_power(self.largemotors, 0) #stop
        self.CurrentCommand = 'stop'
        return
        
    #Rotates the robot with power and degrees using the IMU sensor. Negative degrees = left.
    #the larger the number of degrees and the low the power, the more accurate
    #you can set a margin of error if its a little off
    def rotate_power_degrees_IMU(self, power, degrees, marginoferror=3):
        if self.config['imu'] >= DISABLED:
            return
        self.CurrentCommand = "rotate_power_degrees_IMU"
        bp = self.BP
        symbol = '<'; limit = 0
        if degrees == 0:
            return
        elif degrees < 0:
            symbol = '>='; limit = degrees+marginoferror
        else:
            symbol = '<='; limit = degrees-marginoferror; power = -power
        totaldegreesrotated = 0; lastrun = 0
        timelimit = time.time() + self.timelimit #useful if time is exceeded
        self.log("target degrees: " + str(degrees))
        self.log(str(totaldegreesrotated) + str(symbol) + str(limit))
        while eval("totaldegreesrotated" + str(symbol) + "limit") and (self.CurrentCommand != "stop") and (time.time() < timelimit) and self.config['imu'] < DISABLED:
            lastrun = time.time()
            bp.set_motor_power(self.rightmotor, power)
            bp.set_motor_power(self.leftmotor, -power)
            self.log("Total degrees rotated: " + str(totaldegreesrotated))
            gyrospeed = self.get_gyro_sensor_IMU()[2] #roate around z-axis
            totaldegreesrotated += (time.time() - lastrun)*gyrospeed
        self.CurrentCommand = "stop"
        bp.set_motor_power(self.largemotors, 0) #stop
        return

    #rotates the robot until faces targetheading - only works for a heading between 0 - 360
    def rotate_power_heading_IMU(self, power, targetheading, marginoferror=3):
        if self.config['imu'] >= DISABLED:
            return
        bp = self.BP
        self.CurrentCommand = "rotate_power_heading"
        if targetheading < 0:
            targetheading += 360
        elif targetheading > 360:
            targetheading -= 360
        heading = self.get_compass_IMU()
        if heading == targetheading:
            return
        symbol = '<'; limit = 0
        if heading < targetheading:
            symbol = '<='; limit = targetheading-marginoferror; power = -power
        else:
            symbol = '>='; limit = targetheading+marginoferror; 
        expression = 'heading' + symbol + 'limit'
        self.log('heading'+symbol+str(limit))
        timelimit = time.time() + self.timelimit
        #start rotating until heading is reached
        while (eval(expression) and (self.CurrentCommand != "stop") and time.time() < timelimit) and self.config['imu'] < DISABLED:
            bp.set_motor_power(self.rightmotor, -power)
            bp.set_motor_power(self.leftmotor, power)
            heading = self.get_compass_IMU()
            self.log("Current heading: " + str(heading))
        self.CurrentCommand = "stop"
        bp.set_motor_power(self.largemotors, 0) #stop
        return

    #moves the target class to the target degrees
    def __move_claw_targetdegrees(self, degrees):
        self.CurrentCommand = "move_claw_targetdegrees"
        degrees = -degrees #reversing 
        bp = self.BP
        if degrees == 0:
            return
        bp.offset_motor_encoder(self.mediummotor, bp.get_motor_encoder(self.mediummotor)) #reset encoder
        limit = 0; symbol ='<'
        currentdegrees = 0 
        if degrees > 0:
            symbol = '<'; limit = degrees - 5
        else:
            symbol = '>'; limit = degrees + 5
        expression = 'currentdegrees' + symbol + 'limit'
        currentdegrees = bp.get_motor_encoder(self.mediummotor)

        timelimit = time.time() + self.timelimit/2
        while (eval(expression) and (self.CurrentCommand != "stop") and (time.time() < timelimit)):
            currentdegrees = bp.get_motor_encoder(self.mediummotor) #where is the current angle
            bp.set_motor_position(self.mediummotor, degrees)
            currentdegrees = bp.get_motor_encoder(self.mediummotor) #ACCURACY PROBLEM
        self.CurrentCommand = "stop"
        bp.set_motor_power(self.mediummotor, 0)
        return

    #open the claw
    def open_claw(self, degrees=-1100):
        self.CurrentCommand = 'open claw'
        if self.claw_closed == True:
            self.__move_claw_targetdegrees(degrees)
            self.claw_closed = False
            self.CurrentCommand = 'stop'
        return

    #close the claw
    def close_claw(self, degrees=1100):
        self.CurrentCommand = 'close claw'
        if self.claw_closed == False:
            self.__move_claw_targetdegrees(degrees)
            self.claw_closed = True   
            self.CurrentCommand = 'stop'
        return

    #log out whatever !!!!!THIS IS NOT WORKING UNLESS FLASK LOG USED, DONT KNOW WHY!!!!!
    def log(self, message):
        self.logger.error(message)
        return

    #stop all motors and set command to stop
    def stop_all(self):
        bp = self.BP
        bp.set_motor_power(self.largemotors+self.mediummotor, 0)
        self.CurrentCommand = "stop"
        return      

    #returns the current command
    def get_current_command(self):
        return self.CurrentCommand

    #returns a dictionary of all current sensors
    def get_all_sensors(self):
        sensordict = {} #create a dictionary for the sensors
        sensordict['battery'] = self.get_battery()
        sensordict['colour'] = self.get_colour_sensor()
        sensordict['ultrasonic'] = self.get_ultra_sensor()
        sensordict['thermal'] = self.get_thermal_sensor()
        sensordict['acceleration'] = self.get_linear_acceleration_IMU()
        sensordict['compass'] = self.get_compass_IMU()
        sensordict['gyro'] = self.get_gyro_sensor_IMU()
        sensordict['temperature'] = self.get_temperature_IMU()
        sensordict['orientation'] = self.get_orientation_IMU()
        return sensordict

    #---EXIT--------------#
    # call this function to turn off the motors and exit safely.
    def safe_exit(self):
        bp = self.BP
        self.CurrentCommand = 'exit' #should exit thread
        self.stop_all() #stop all motors
        self.log("Exiting")
        bp.reset_all() # Unconfigure the sensors, disable the motors
        time.sleep(2) #gives time to reset??
        return
    
#--------------------------------------------------------------------
# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    robot = BrickPiInterface(timelimit=20)
    logger = logging.getLogger()
    robot.set_log(logger)
    robot.calibrate_imu(timelimit=10) #calibration might requirement movement
    robot.log(robot.get_all_sensors())
    robot.move_power_untildistanceto(30,10)
    robot.safe_exit()

