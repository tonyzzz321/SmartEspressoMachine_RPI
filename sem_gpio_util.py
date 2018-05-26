import RPi.GPIO as GPIO
import time, logging

from rpisensors.proximity import VL6180X
from sem_constants import AVAILABLE_COFFEE_TYPE_LIST, CUP_DISTANCE_THRESHOLD, WATER_LEVEL_TABLE

class GPIO_Util():

   def __init__(self, gpio_dict): # {func_name: {pin: int, mode: str}}

      self.logger = logging.getLogger(__name__)
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

   def msg(self, text, level='info'):
      if hasattr(self.logger, level):
         getattr(self.logger, level)(text)

   def __push_the_button(self, gpio_pin):
      self.msg('Attempting to push the button on GPIO %s' % str(gpio_pin), 'info')
      GPIO.output(gpio_pin, GPIO.HIGH)
      time.sleep(1)
      GPIO.output(gpio_pin, GPIO.LOW)
      self.msg('Successfully pushed the button on GPIO %s' % str(gpio_pin), 'info')

   def __get_pin(self, func_name):
      self.msg('Attempting to get the GPIO pin number for %s' % func_name, 'info')
      result = self.gpio_dict[func_name]['pin']
      self.msg('GPIO pin number for %s is %s' % (func_name, str(result)), 'info')
      return result

   def __proximity_sensor_read_raw(self, name):
      self.msg('Attempting to read raw %s sensor data' % name, 'info')
      if name == 'CUP':
         self.msg('Turning on the CUP sensor', 'info')
         GPIO.output(self.__get_pin('WTR_SNS_CS'), GPIO.LOW)
         GPIO.output(self.__get_pin('CUP_SNS_CS'), GPIO.HIGH)
         self.msg('CUP sensor is now ON', 'info')
      elif name == 'WATER':
         self.msg('Turning on the WATER sensor', 'info')
         GPIO.output(self.__get_pin('CUP_SNS_CS'), GPIO.LOW)
         GPIO.output(self.__get_pin('WTR_SNS_CS'), GPIO.HIGH)
         self.msg('WATER sensor is now ON', 'info')
      self.msg('Reading raw value from %s sensor' % name, 'info')
      value = 0
      for x in range(3):
         raw = VL6180X(1).read_distance()
         if raw == None:
            raw = 255
         self.msg('Raw reading of pass %s: %s' % (str(x+1), str(raw)), 'info')
         value += raw
      value /= 3
      self.msg('Average reading of 3 passes: %s' % str(value), 'info')
      self.msg('Turning off all sensors', 'info')
      GPIO.output(self.__get_pin('CUP_SNS_CS'), GPIO.LOW)
      GPIO.output(self.__get_pin('WTR_SNS_CS'), GPIO.LOW)
      self.msg('All sensors is now OFF', 'info')
      return value

   def make_coffee(self, option):
      self.msg('Attempting to start making coffee: %s' % option, 'info')
      if option in AVAILABLE_COFFEE_TYPE_LIST:
         self.__push_the_button(self.__get_pin(option))
         self.msg('Coffee making process initiated successfully', 'info')
         return 'SUCCESS'
      else:
         self.msg('Start making coffee failed: unknown coffee option %s' % option, 'info')
         return 'ERROR: unknown coffee option %s' % option

   def get_cup_presence(self):
      self.msg('Attempting to determine cup presence', 'info')
      result = (self.__proximity_sensor_read_raw('CUP') < CUP_DISTANCE_THRESHOLD)
      self.msg('Determined CUP presence: %s' % str(result), 'info')
      return result

   def get_water_level(self):
      self.msg('Attempting to determine water level', 'info')
      raw_reading = self.__proximity_sensor_read_raw('WATER')
      self.msg('WATER sensor raw value received: %s' % str(raw_reading), 'info')
      # translate reading to water level
      for convert in WATER_LEVEL_TABLE:
         if raw_reading <= convert['max_distance']:
            water_level = convert['level']
            break
      self.msg('Translated water level: %s%%' % str(water_level), 'info')
      return water_level
      
   def clean_up(self):
      
      GPIO.cleanup()
