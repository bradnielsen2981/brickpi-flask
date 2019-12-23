from di_sensors.temp_hum_press import TempHumPress
import time
import logging

log = logging.getLogger('app')
thp = TempHumPress()

#read temp and humidity
def read_temp_humidity_sensor_I2C(port):
    temp = thp.get_temperature_celsius()
    hum = thp.get_humidity()
    press = thp.get_pressure()
    time.sleep(0.02)
    return [temp,hum,press]

#--------------------------------------------------------------------
#Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    pass