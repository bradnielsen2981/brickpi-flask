import brickpi3 # import the BrickPi3 drivers
import time
import math
import sys
import logging
import threading 
from di_sensors.inertial_measurement_unit import InertialMeasurementUnit
from di_sensors.temp_hum_press import TempHumPress

#Created a Class to wrap the robot functionality, one of the features is the idea of keeping track of the CurrentCommand, this is important when more than one process is running...
class Robot():

    #use the init method to define your configuration
    def __init__(self, log=None):
        self.BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3
        if log == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = log
        bp = self.BP
        self.rightmotor = bp.PORT_A
        self.leftmotor = bp.PORT_B
        self.largemotors = bp.PORT_A + bp.PORT_B
        self.mediummotor = bp.PORT_C
        #self.thp = TempHumPress() #port is the I2c Grove
        self.imu = InertialMeasurementUnit()
        self.thermal = bp.PORT_1
        bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.I2C, [0, 20]) 
        self.colour = bp.PORT_2 #Colour Sensor
        bp.set_sensor_type(self.colour, bp.SENSOR_TYPE.EV3_COLOR_COLOR)
        #self.gyro = bp.PORT_3 # Lego Gyro Sensor
        #bp.set_sensor_type(self.gyro, bp.SENSOR_TYPE.EV3_GYRO_ABS_DPS)
        self.ultra = bp.PORT_4 #UltraSonic Senor
        bp.set_sensor_type(self.ultra, bp.SENSOR_TYPE.EV3_ULTRASONIC_CM)
        self.thermal_thread = None #for later thread
        time.sleep(4) #you need to delay or else sensors are not configured!!!'''
        self.CurrentCommand = "loaded"
        self.thermal_thread = threading.Thread(target=self.update_thermal_sensor_thread, args=(1,))
        self.thermal_thread.daemon = True
        self.thermal_thread.start()
        self.logger.info("Configuration Loaded...")
        return

    #get the current voltage - need to work out how to determine battery life
    def get_battery(self):
        return self.BP.get_voltage_battery()

    #get the gyro sensor -- returns 0 if not working but total degrees otherwise
    #can switch between IMU sensor and EV3 sensor.
    def get_gyro_sensor(self, IMUgyro=True):
        bp = self.BP
        degrees = 0
        try:
            if IMUgyro:
                #the IMU gyroscope actually reads angular velocity
                #(x,y,z) = self.imu.read_gyroscope()
                #the IMU euler value actually reads orientation
                (degrees,roll,pitch) = self.imu.read_euler()
            else: #using EV3 gyro
                degrees = bp.get_sensor(self.gyro)[0]
            time.sleep(0.01)
        except brickpi3.SensorError as error:
            self.logger.error("GYRO: " + str(error))
            self.CurrentCommand = "stop"
        return degrees

    #get the ultrasonic sensor
    def get_ultra_sensor(self):
        distance = 0
        bp = self.BP
        try:
            distance = bp.get_sensor(self.ultra)
            time.sleep(0.3)
        except brickpi3.SensorError as error:
            self.logger.error("ULTRASONIC: " + str(error))
            self.CurrentCommand = "stop"
        return distance

    #read temp and humidity from the I2C port, you need an I2C temp sensor
    def get_temp_humidity_press_sensor(self):
        try:
            temp = self.thp.get_temperature_celsius()
            hum = self.thp.get_humidity()
            press = self.thp.get_pressure()
            time.sleep(0.01)
        except brickpi3.SensorError as error:
            self.logger.error("TEMP HUMIDY PRESSURE: " + str(error))
            return (0,0,0)
        return(temp,hum,press) #return a tuple containing temp,hum,press'''

    #returns the compass value from the IMU - note if the IMU is placed near a motor it can be affected
    def get_compass(self):
        heading = 0
        try:
            (x, y, z)  = self.imu.read_magnetometer()
            time.sleep(0.01)
            heading = math.atan2(y, x) * (180 / math.pi)
        except brickpi3.SensorError as error:
            self.logger.error("IMU: " + str(error))
        return heading

    #returns the colour current sensed - "none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"
    def get_colour_sensor(self):
        bp = self.BP
        value = 0
        colours = ["none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"]
        try: 
            value = bp.get_sensor(self.colour) 
            time.sleep(0.01)
        except brickpi3.SensorError as error:
            self.logger.error("COLOUR: " + str(error))    
        return colours[value]

    #updates the thermal sensor by making continual I2C transactions through a thread
    def update_thermal_sensor_thread(self, name):
        bp = self.BP
        self.logger.info("Starting Thread - thermal sensor i2c transactions")
        TIR_I2C_ADDR        = 0x0E      # TIR I2C device address 
        TIR_AMBIENT         = 0x00      # Ambient Temp
        TIR_OBJECT          = 0x01      # Object Temp
        TIR_SET_EMISSIVITY  = 0x02      
        TIR_GET_EMISSIVITY  = 0x03
        TIR_CHK_EMISSIVITY  = 0x04
        TIR_RESET           = 0x05
        while self.CurrentCommand != "exit":
            try:
                bp.transact_i2c(self.thermal, TIR_I2C_ADDR, [TIR_OBJECT], 2)
                time.sleep(0.01)
            except brickpi3.SensorError as error:
                self.logger.error("THERMAL: " + str(error))
        self.logger.info("Ending Thread - thermal sensor i2c transactions")
        return

    #return the infrared temperature - this seems to work but im sceptical
    def get_thermal_sensor(self, usethread=True):
        bp = self.BP
        temp = 0
        if not usethread:
            self.update_thermal_sensor() #not necessary if thread is running
        try:
            value = bp.get_sensor(self.thermal) # read the sensor values
            time.sleep(0.01)
            temp = (float)((value[1] << 8) + value[0]) # join the MSB and LSB part
            temp = temp * 0.02 - 0.01                  # Converting to Celcius
            temp = temp - 273.15                       
        except brickpi3.SensorError as error:
            self.logger.error("THERMAL: " + str(error))
        return float("%3.f" % temp)

    #updates the thermal sensor by making a single I2C transaction
    def update_thermal_sensor(self):
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
        except brickpi3.SensorError as error:
            self.logger.error("THERMAL: " + str(error))
        return

    #disable thermal sensor
    def disable_thermal_sensor(self):
        bp = self.BP
        bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.NONE) 
        return
    
    #------MOTOR COMMANDS--------#
    def move_power(self, power):
        bp = self.BP
        self.CurrentCommand = "move"
        if self.CurrentCommand != "stop":
            self.BP.set_motor_power(self.largemotors, power)
        else:
            self.BP.set_motor_power(self.largemotors, 0)
        return

    #moves for the specified time (seconds) and power - use negative power to reverse
    def move_time_power(self, power, t):
        bp = self.BP
        self.CurrentCommand = "movepower"
        target = time.time() + t
        while time.time() < target and self.CurrentCommand != "stop":
            bp.set_motor_power(self.largemotors, power)
        self.CurrentCommand = "stop"
        self.BP.set_motor_power(self.largemotors, 0)
        return
    
    #moves with power until obstruction and return time travelled
    def move_power_untildistanceto(self, power, distanceto):
        self.CurrentCommand = "moveuntil"
        bp = self.BP
        distancedetected = 300 # to set an inital distance detected before loop
        elapsedtime = 0;  start = time.time()
        #ultra sonic sensors can sometimes return 0
        bp.set_motor_power(self.largemotors, power)
        while (distancedetected > distanceto or distancedetected == 0.0) and (self.CurrentCommand != "stop"):
            distancedetected = self.get_ultra_sensor()
            self.logger.info("MOVING - Distance detected: " + str(distancedetected))
        self.CurrentCommand = "stop"
        elapsedtime = time.time() - start
        bp.set_motor_power(self.largemotors, 0)
        return elapsedtime
        
    #Rotates the robot with power and degrees. negative degrees = left. 
    def rotate_power_degrees(self, power, degrees):
        self.CurrentCommand = "rotate"
        bp = self.BP
        currentdegrees = self.get_gyro_sensor()
        targetdegrees = currentdegrees + degrees
        #Complex code - need to reverse if statements based on left or right turn
        symbol = '>' if degrees < 0 else '<'  #shorthand if statement
        power = -(power) if degrees < 0 else power
        expression = 'currentdegrees' + symbol + 'targetdegrees'
        while eval(expression) and self.CurrentCommand != "stop":
            bp.set_motor_power(self.rightmotor, -power)
            bp.set_motor_power(self.leftmotor, power)
            print("ROTATING - Gyro degrees remaining: " + str(targetdegrees - currentdegrees))
            currentdegrees = self.get_gyro_sensor()
        self.CurrentCommand = "stop"
        bp.set_motor_power(self.largemotors, 0) #stop
        return

    #rotates the robot until faces targetheading, (negative power rotates left)
    def rotate_power_heading(self, power, targetheading):
        bp = self.BP
        self.CurrentCommand = "rotate to heading"
        heading = self.get_compass()
        if heading == targetheading:
            return
        symbol = '>' if targetheading > heading else '<'  #shorthand if statement
        power = -(power) if targetheading > heading else power
        expression = 'targetheading' + symbol + 'heading'
        while eval(expression) and self.CurrentCommand != "stop":
            bp.set_motor_power(self.rightmotor, -power)
            bp.set_motor_power(self.leftmotor, power)
            self.logger.info("Current Heading: " + str(heading))
            heading = self.get_compass()
        self.CurrentCommand = "stop"
        bp.set_motor_power(self.largemotors, 0) #stop
        return

    #moves the target class to the target degrees
    def move_claw_targetdegrees(self, targetdegrees):
        self.CurrentCommand = "grab"
        bp = self.BP
        targetdegrees = targetdegrees * 6 #rotation of motor needs to be calibrated to angles via a constant 
        bp.offset_motor_encoder(self.mediummotor, bp.get_motor_encoder(self.mediummotor)) #reset encoder C to take into account current degree of turn - which is by default 0
        bp.set_motor_limits(self.mediummotor, 100, 600) #set a power limit (in percent) and a speed limit (in Degrees Per Second)
        current = bp.get_motor_encoder(self.mediummotor) #current could be 
        while current != targetdegrees and self.CurrentCommand != "stop":
            bp.set_motor_position(self.mediummotor, targetdegrees)
            current = bp.get_motor_encoder(self.mediummotor) #ACCURACY PROBLEM
        self.CurrentCommand = "stop"
        bp.set_motor_power(self.mediummotor, 0)
        return

    #log out whatever
    def log(self, message):
        self.logger.info(message)
        return

    #stop all motors and set command to stop
    def stop_all(self):
        bp = self.BP
        bp.set_motor_power(self.largemotors+self.mediummotor, 0)
        self.CurrentCommand = "stop"
        return

    #---EXIT--------------#
    # call this function to turn off the motors and exit safely.
    def safe_exit(self):
        bp = self.BP
        self.stop_all() #stop all motors
        self.logger.info("Exiting")
        bp.reset_all() # Unconfigure the sensors, disable the motors
        exit()
        return
    
#--------------------------------------------------------------------
#Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    robot = Robot()
    #robot.safe_exit()
    #robot.move_power_untildistanceto(30,10)
    #robot.rotate_power_heading(20, 90)
    robot.rotate_power_degrees(30,90)
    target = time.time() + 2
    while time.time() < target:
        print("Battery: " + str(robot.get_battery()))
        print("Compass: " + str(robot.get_compass()))
        print("Gyro: " + str(robot.get_gyro_sensor()))
        print("Colour: " + str(robot.get_colour_sensor()))
        print("Ultra: " + str(robot.get_ultra_sensor()))
        print("Thermal: " + str(robot.get_thermal_sensor()))
    robot.CurrentCommand = "stop" 
    robot.safe_exit()
    #robot.disable_thermal_sensor() -- could also enable and disable thermal sensor when needed

