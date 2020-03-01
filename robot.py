# This class inherits from the BrickPi interface, it should include any code for sub-routines
# You can also over-ride any functions that you do not like

import brickpiinterface
import databaseinterface
import logging

class Robot(BrickPiInterface):

    def __init__(self, timelimit=30, database):
        super().__init__(timelimit)
        self.database = database #a handle to the database
        self.CurrentRoutine = 'none' #could be useful to keep track of the current routine
        return

    #Override this function if you wish to change the ports
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

    #gets the current routine
    def get_current_routine(self):
        return self.CurrentRoutine

    #create a function that will find a path to the victim and save path events to the database
    def find_path_victim(self):
        self.CurrentRoutine = "find_path_victim"
        return

    #rescue the victim using the claw.
    def rescue_victim(self):
        self.CurrentRoutine = "rescue_victim"
        return

    #use the saved path data to determine a way back to the start
    def return_victim_to_start(self):
        self.CurrentRoutine = "return_victim_to_start"
        return

    #------------POSSIBLE FUNCTIONS TO USE OR OVERRIDE--------------------#
    #def calibrate_imu(self, timelimit=20)

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