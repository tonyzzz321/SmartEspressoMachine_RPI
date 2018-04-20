import RPi.GPIO as GPIO
import time

from rpisensors.proximity import VL6180X
from sem_constants import CUP_DISTANCE_THRESHOLD, MAX_WATER_DISTANCE

class GPIO_Util():

   def __init__(self, gpio_dict): # {func_name: {pin: int, mode: str}}

      self.gpio_dict = gpio_dict
      GPIO.setmode(GPIO.BOARD)
      for func_name in self.gpio_dict.keys():
         entry = gpio_dict[func_name]
         if entry['mode'] == 'in':
            GPIO.setup(entry['pin'], GPIO.IN)
         elif entry['mode'] == 'out':
            GPIO.setup(entry['pin'], GPIO.OUT, initial=GPIO.LOW)
         elif entry['mode'] == 'i2c':
            pass
            # GPIO.setup(entry[pin])
      GPIO.output(self.__get_pin('CUP_SNS_CS'), GPIO.LOW)
      GPIO.output(self.__get_pin('WTR_SNS_CS'), GPIO.LOW)

   def __push_the_button(self, gpio_pin):

      GPIO.output(gpio_pin, GPIO.HIGH)
      time.sleep(1)
      GPIO.output(gpio_pin, GPIO.LOW)

   def __get_pin(self, func_name):

      return self.gpio_dict[func_name]['pin']

   def __proximity_sensor_read_raw(self, name):

      if name == 'CUP':
         GPIO.output(self.__get_pin('WTR_SNS_CS'), GPIO.LOW)
         GPIO.output(self.__get_pin('CUP_SNS_CS'), GPIO.HIGH)
      elif name == 'WATER':
         GPIO.output(self.__get_pin('CUP_SNS_CS'), GPIO.LOW)
         GPIO.output(self.__get_pin('WTR_SNS_CS'), GPIO.HIGH)

      value = 0
      for x in range(3):
         value += VL6180X(1).read_distance()
      value /= 3
      
      GPIO.output(self.__get_pin('CUP_SNS_CS'), GPIO.LOW)
      GPIO.output(self.__get_pin('WTR_SNS_CS'), GPIO.LOW)

      return value

   def make_coffee(self, option):

      if option in ['ESPRESSO', 'CAPPUCCINO', 'LATTE']:
         self.__push_the_button(self.__get_pin(option))
         return 'SUCCESS'
      else:
         return 'ERROR: unknown option %s' % option

   def get_cup_presence(self):

      return (self.__proximity_sensor_read_raw('CUP') < CUP_DISTANCE_THRESHOLD)

   def get_water_level(self):

      raw_reading = self.__proximity_sensor_read_raw('WATER')

      # translate reading to water level
      water_level = MAX_WATER_DISTANCE - raw_reading

      return water_level
      
   def clean_up(self):
      
      GPIO.cleanup()