# This class inherits from the BrickPi interface, it should include any code for sub-routines
# You can also over-ride any functions that you do not like. The BrickPiInterface is code created by your teacher to make using the robot easier. It is composed of snippets of code from the DexterIndustries github 
from interfaces.brickpiinterface import BrickPiInterface
from interfaces.databaseinterface import DatabaseHelper 
import logging
import time

ENABLED = 1
DISABLED = 5 #if the sensor returns NOREADING more than 5 times in a row, its permanently 

class Robot(BrickPiInterface):
    
    def __init__(self, timelimit=30, database=None):
        super().__init__(timelimit)
        self.database = database #database handle, use ViewQueryHelper, ModifyQueryHelper to run queries
        self.CurrentRoutine = 'ready' #could be useful to keep track of the current routine
        return

    #Override this function if you wish to change the Ports
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
        #self.gyro = bp.PORT_3  #lego Gyro Sensor - replaced with IMU sensor
        self.configure_sensors() #CONFIGURES SENSORS!!! from BrickPi Interface
        bp.set_motor_limits(self.mediummotor, 100, 600) #set medium motor power / speed limit 
        return

    #gets the current routine
    def get_current_routine(self):
        return self.CurrentRoutine

    #create a function that will find a path to the victim and save path events to the database
    def find_path_victim(self):
        if self.CurrentRoutine != "ready":
            return
        self.CurrentRoutine = "find_path_victim"
        #insert your code here
        self.CurrentRoutine = "ready"
        return

    #rescue the victim using the claw.
    def rescue_victim(self):
        if self.CurrentRoutine != "ready":
            return
        self.CurrentRoutine = "rescue_victim"
        #insert your code here
        self.CurrentRoutine = "ready"        
        return

    #use the saved path data to determine a way back to the start
    def return_victim_to_start(self):
        if self.CurrentRoutine != "ready":
            return
        self.CurrentRoutine = "return_victim_to_start"
        #insert your code here
        self.CurrentRoutine = "ready"
        return

    #CREATE A BETTER METHOD OF MOVING FORWARD UNTIL SOMETHING IS ENCOUNTERED
    def move_power_until_event(self, power, distanceto):
        self.CurrentCommand = "move_power_untildistanceto"
        bp = self.BP
        elapsedtime = 0;  start = time.time()
        eventtype = None; eventdata = None

        #Turn motors on
        bp.set_motor_power(self.largemotors, power)
        timelimit = time.time() + self.timelimit  #timelimit is simply a limit to how long to execute incase there is an error 

        while (self.CurrentCommand != "stop" and time.time() < timelimit):

            ##if sensor fails, or distanceto has been reached quit, or distancedetected = 0
            distancedetected = self.get_ultra_sensor()
            self.log("MOVING - Distance detected: " + str(distancedetected))
            if (self.config['ultra'] > DISABLED) or ((distancedetected < distanceto) and (distancedetected != 0.0)):
                #if an object has been detected, identify the type of object
                eventtype = "objectdetected"
                #if object is hot its a fire, cold its the victim, else its the wall
                break
            
            ##INSERT OTHER TESTS e.g IF RED COLOUR
            colourdetected = self.get_colour_sensor()
            self.log("MOVING - Colour detected: " + str(colourdetected))
            if (colourdetected == 'Red'):
                eventtype = "junctiondetected"
                break

            #if colourdetect == "red":

        self.CurrentCommand = "stop"
        elapsedtime = time.time() - start
        bp.set_motor_power(self.largemotors, 0)
        return (eventtype,eventdata,elapsedtime)

    #------------POSSIBLE FUNCTIONS TO USE OR OVERRIDE--------------------#
    #def calibrate_imu(self, timelimit=20)

    #def reconfig_IMU(self)

    #def get_compass_IMU(self)

    #def get_orientation_IMU(self)

    #def get_linear_acceleration_IMU(self)

    #def get_gyro_sensor_IMU(self)

    #def get_temperature_IMU(self)

    #def get_gyro_sensor_EV3(self)

    #def get_ultra_sensor(self)

    #def get_colour_sensor(self)

    #def get_thermal_sensor(self, usethread=True)

    #def get_battery(self)

    #def move_power(self, power)

    #def move_power_time(self, power, t)

    #def move_power_untildistanceto(self, power, distanceto)

    #def rotate_power_time(self, power, t)

    #def rotate_power_degrees_IMU(self, power, degrees, marginoferror=3)

    #def rotate_power_heading_IMU(self, power, targetheading, marginoferror=3)

    #def open_claw(self, degrees=-1100)

    #def close_claw(self, degrees=1100)

    #def log(self, message)

    #def stop_all(self)

    #def get_current_command(self)

    #def get_all_sensors(self)

    #def safe_exit(self)

#--------------------------------------------------------------------
#Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    robot = Robot(timelimit=20)
    logger = logging.getLogger()
    robot.set_log(logger)
    robot.log(robot.get_all_sensors())
    robot.calibrate_imu(timelimit=10) #calibration might requirement movement
    print(robot.move_power_until_event(30,10))
    robot.safe_exit()
    print("bradnielsen2981")
