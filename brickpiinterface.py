import brickpi3 # import the BrickPi3 drivers
import time
import sys
import logging
import threading #the Thermal Sensor needs a thread, this could be started by Flask

#from di_sensors.temp_hum_press import TempHumPress
logger = None
#logger = logging.getLogger('app') #will attempt to get Flask log

#Created a Class to wrap the robot functionality, one of the features is idea of keeping track of the CurrentCommand, this is important when more than one process is running...
class Robot():

    #use the init method to define your configuration
    def __init__(self):
        self.BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class
        bp = self.BP
        self.rightmotor = bp.PORT_A
        self.leftmotor = bp.PORT_B
        self.largemotors = bp.PORT_A + bp.PORT_B
        self.mediummotor = bp.PORT_C
        #self.thp = TempHumPress() #port is the I2c Grove
        self.thermal = bp.PORT_1
        bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.I2C, [0, 20]) 
        self.colour = bp.PORT_2 #Colour Sensor
        bp.set_sensor_type(self.colour, bp.SENSOR_TYPE.EV3_COLOR_COLOR)
        self.gyro = bp.PORT_3 #Gyro Sensor
        bp.set_sensor_type(self.gyro, bp.SENSOR_TYPE.EV3_GYRO_ABS_DPS)
        self.ultra = bp.PORT_4 #UltraSonic Senor
        bp.set_sensor_type(self.ultra, bp.SENSOR_TYPE.EV3_ULTRASONIC_CM)
        time.sleep(3) #you need to delay or else sensors are not configured!!!'''
        self.CurrentCommand = "loaded"

        '''self.thermal_thread = threading.Thread(target=self.update_thermal_sensor_thread, args=(1,))
        self.thermal_thread.daemon = True
        self.thermal_thread.start()'''

        return

    #get the current voltage - need to work out how to determine battery life
    def get_battery(self):
        return self.BP.get_voltage_battery()

    #get the gyro sensor -- returns 0 if not working but total degrees otherwise
    def get_gyro_sensor(self):
        bp = self.BP
        degrees = 0
        try:
            degrees = bp.get_sensor(self.gyro)[0]
            time.sleep(0.01)
        except brickpi3.SensorError as error:
            print("GYRO: " + str(error))
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
            print("ULTRASONIC: " + str(error))
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
            print(error)
            #print("TEMPHUMPRESSURE: " + str(error))
            return (0,0,0)
        return(temp,hum,press) #return a tuple containing temp,hum,press'''

    #returns the colour current sensed - "none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"
    def get_colour_sensor(self):
        bp = self.BP
        value = 0
        colours = ["none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"]
        try: 
            value = bp.get_sensor(self.colour) 
            time.sleep(0.01)
        except brickpi3.SensorError as error:
            print("COLOUR: " + str(error))    
        return colours[value]

    #updates the thermal sensor by making continual I2C transactions through a thread
    def update_thermal_sensor_thread(self, name):
        bp = self.BP
        print("Starting Thread - thermal sensor i2c transactions")
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
                time.sleep(1)
            except brickpi3.SensorError as error:
                print("THERMAL: " + str(error))
        print("Ending Thread - thermal sensor i2c transactions")
        return

    #return the infrared temperature
    def get_thermal_sensor(self, usethread=False):
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
            print("THERMAL: " + str(error))
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
            print("THERMAL: " + str(error))
        return

    #disable thermal sensor
    def disable_thermal_sensor(self):
        bp = self.BP
        bp.set_sensor_type(self.thermal, bp.SENSOR_TYPE.NONE) 
        return
    
    #------MOTOR COMMANDS--------#
    def move_power(self, power):
        bp = self.BP
        if self.CurrentCommand != "stop":
            self.BP.set_motor_power(self.largemotors, power)
        else:
            self.BP.set_motor_power(self.largemotors, 0)
        return


    #moves for the specified time (seconds) and power - use negative power to reverse
    def move_time_power(self, t, power):
        bp = self.BP
        if self.CurrentCommand != "stop":
           self.CurrentCommand = "move"
        target = time.time() + t
        while time.time() < target and self.CurrentCommand != "stop":
            bp.set_motor_power(self.largemotors, power)
        self.BP.set_motor_power(self.largemotors, 0)
        return
    
    #moves with power until obstruction and return time travelled
    def move_power_untildistanceto(self, power, distanceto):
        if self.CurrentCommand != "stop":
           self.CurrentCommand = "moveuntil"
        bp = self.BP
        distancedetected = 300 # to set an inital distance detected before loop
        elapsedtime = 0;  start = time.time()
        #ultra sonic sensors can sometimes return 0
        bp.set_motor_power(self.largemotors, power)
        while (distancedetected > distanceto or distancedetected == 0.0) and (self.CurrentCommand != "stop"):
            distancedetected = self.get_ultra_sensor()
        elapsedtime = time.time() - start
        bp.set_motor_power(self.largemotors, 0)
        return elapsedtime
        
    #Rotates the robot with power and degrees. negative degrees = left. 
    def rotate_power_degrees(self, power, degrees):
        if self.CurrentCommand != "stop":
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
            print("Gyro degrees remaining: " + str(targetdegrees - currentdegrees))
            currentdegrees = self.get_gyro_sensor()
        bp.set_motor_power(self.largemotors, 0) #stop
        return

    #moves the target class to the target degrees
    def move_claw_targetdegrees(self, targetdegrees):
        if self.CurrentCommand != "stop":
           self.CurrentCommand = "grab"
        bp = self.BP
        targetdegrees = targetdegrees * 6 #rotation of motor needs to be calibrated to angles via a constant 
        bp.offset_motor_encoder(self.mediummotor, bp.get_motor_encoder(self.mediummotor)) #reset encoder C to take into account current degree of turn - which is by default 0
        bp.set_motor_limits(self.mediummotor, 100, 600) #set a power limit (in percent) and a speed limit (in Degrees Per Second)
        current = bp.get_motor_encoder(self.mediummotor) #current could be 
        while current != targetdegrees and self.CurrentCommand != "stop":
            bp.set_motor_position(self.mediummotor, targetdegrees)
            current = bp.get_motor_encoder(self.mediummotor) #ACCURACY PROBLEM
        bp.set_motor_power(self.mediummotor, 0)
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
        print("Exiting")
        bp.reset_all() # Unconfigure the sensors, disable the motors
        exit()
        return
   
#--------------------------------------------------------------------
#Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    robot = Robot()
    #robot.disable_thermal_sensor() 
    robot.rotate_power_degrees(30,-90)
    target = time.time() + 20
    while time.time() < target:
        print("Battery: ",robot.get_battery())
        print("Gyro: ",robot.get_gyro_sensor())
        print("Colour: ",robot.get_colour_sensor())
        print("Ultra: ",robot.get_ultra_sensor())
        #print("Thermal: ",robot.get_thermal_sensor()) 
    robot.CurrentCommand = "stop"   
    robot.safe_exit()