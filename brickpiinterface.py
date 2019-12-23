import brickpi3 # import the BrickPi3 drivers
import time
import sys
import logging

log = logging.getLogger('app') #if a log has been created this will get it

#Created a Class to wrap the robot functionality, one of the features is idea of keeping track of the current command, this is important when more than one process is running...
class Robot():

    #use the init method to define your configuration
    def __init__(self):
        self.CurrentCommand = "none"
        self.BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class
        bp = self.BP
        self.rightmotor = bp.PORT_A
        self.leftmotor = bp.PORT_B
        self.largemotors = bp.PORT_A + bp.PORT_B
        self.mediummotor = bp.PORT_C
        bp.set_motor_power(bp.PORT_A + bp.PORT_B + bp.PORT_C, 0) #stop all motors
        
        self.colour = bp.PORT_2 #Colour Sensor
        bp.set_sensor_type(self.colour, bp.SENSOR_TYPE.EV3_COLOR_COLOR)
        
        self.ultra = bp.PORT_4 #UltraSonic Senor
        bp.set_sensor_type(self.ultra, bp.SENSOR_TYPE.EV3_ULTRASONIC_CM)
        
        self.gyro = bp.PORT_3 #Gyro Sensor
        bp.set_sensor_type(self.gyro, bp.SENSOR_TYPE.EV3_GYRO_ABS_DPS)
        return
        
    #moves for the specified time and power - use negative power to reverse, power is a percentage
    def move_time_power(self, t, power):
        bp = self.BP #sick of writing self.BP all the time
        self.CurrentCommand = 'move_time_power' #this will be changed by the stop thread
        elapsedtime = 0
        start = time.time()
        while elapsedtime < t and self.CurrentCommand == 'move_time_power':
            elapsedtime = time.time() - start
            bp.set_motor_power(self.largemotors, power)
            time.sleep(0.1) #you may need to reduce Pi processing load
        bp.set_motor_power(self.largemotors, 0)
        self.CurrentCommand = 'none'
        return
    
    #moves with power until obstruction and return time travelled
    def move_power_untildistanceto(self, power, distanceto):
        bp = self.BP
        self.CurrentCommand = 'move_power_untildistanceto'
        distancedetected = 300 # to set an inital distance detected before loop
        elapsedtime = 0, start = time.time()
        #ultra sonic sensors can sometimes return 0
        while (distancedetected > distanceto or distancedetected == 0.0) and self.CurrentCommand == 'move_power_untildistanceto':
            bp.set_motor_power(self.largemotors, power)
            distancedetected = bp.get_sensor(self.ultra)
            time.sleep(0.1) #you need to allow the sound time to bounce back
        elapsedtime = time.time() - start
        self.CurrentCommand = 'none'
        bp.set_motor_power(self.largemotors, 0)
        return elapsedtime

    #returns the colour current sensed - "none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"
    def get_colour_sensed(self):
        bp = self.BP
        colours = ["none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"] 
        value = bp.get_sensor(self.colour) 
        return colours[value]

    #Rotates the robot with power and degrees. negative degrees = left. Negative power reverses rotation
    def rotate_power_degrees(self, power, degrees):
        bp = self.BP
        self.CurrentCommand = 'rotate_power_degrees'
        currentdegrees = bp.get_sensor(self.gyro)[0]
        targetdegrees = currentdegrees + degrees

        #Complex code - need to reverse if statements based on left or right turn
        symbol = '>' if degrees < 0 else symbol = '<'  #shorthand if statement
        power = -(power) if degrees < 0
        expression = 'currentdegrees' + symbol + 'targetdegrees'

        while self.CurrentCommand == 'rotate_power_degrees' and eval(expression):
            bp.set_motor_power(self.rightmotor, -power)
            bp.set_motor_power(self.leftmotor, power)
            currentdegrees = bp.get_sensor(self.gyro)[0]
            time.sleep(0.05)
            print(currentdegrees)
        bp.set_motor_power(self.largemotors, 0) #stop
        self.CurrentCommand = 'none'
        return

    #moves the target class to the target degrees
    def move_claw_targetdegrees(self, targetdegrees):
        bp = self.BP
        targetdegrees = targetdegrees * 6 #rotation of motor needs to be calibrated to angles via a constant 
        self.CurrentCommand = 'move_claw_targetdegrees'
        bp.offset_motor_encoder(self.mediummotor, bp.get_motor_encoder(self.mediummotor)) #reset encoder C to take into account current degree of turn - which is by default 0
        bp.set_motor_limits(self.mediummotor, 100, 600) #set a power limit (in percent) and a speed limit (in Degrees Per Second)
        current = bp.get_motor_encoder(self.mediummotor) #current could be 
        while self.CurrentCommand == 'move_claw_targetdegrees' and current != targetdegrees:
            bp.set_motor_position(self.mediummotor, targetdegrees)
            current = bp.get_motor_encoder(self.mediummotor) #ACCURACY IS A BIG ISSUE TO BE SOLVED
        self.CurrentCommand = 'none'
        bp.set_motor_power(self.mediummotor, 0)
        return

    #stop all motors and set command to stop
    def stop_all(self):
        bp = self.BP
        bp.set_motor_power(self.largemotors+self.mediummotor, 0)
        self.CurrentCommand = 'none'
        return
    
    #I think this actually resets all the sensor configurations which is dangerous..once ports are set up
    def reset_all(self):
        self.CurrentCommand = 'none'
        bp = self.BP
        bp.reset_all()
        return

    #get the current voltage - need to work out how to determine battery life
    def get_battery(self):
        return robot.BP.get_voltage_9v()
    
#--------------------------------------------------------------------
#Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    robot = Robot()
    time.sleep(1) #You need to allow time for the Ports to be setup!!!!
    #robot.rotate_power_degrees(20, -90)
    robot.reset_all()
    robot.stop_all()
    print(robot.get_battery)
    