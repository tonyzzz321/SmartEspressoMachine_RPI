import time
from threading import Thread, Lock
from sem_constants import *
from sem_gpio_util import GPIO_Util

class Machine():
   
   def __init__(self, gpio_dict=GPIO_DICT):
   # def __init__(self, scheduler, machine_gpio, water_gpio, cup_gpio):
      # self.scheduler = scheduler
      self.gpio_util = GPIO_Util(gpio_dict)
      self.cup_present = None
      self.water_level = None
      self.water_enough = None
      self.machine_state = None
      self.cup_present_lock = Lock()
      self.water_level_lock = Lock()
      self.water_enough_lock = Lock()
      self.machine_state_lock = Lock()
      self.thread_exit = False
      self.child_thread = Thread(target=self.__keep_update_coffee_ready_status)
      self.get_machine_state()
      # READY_TO_MAKE, NOT_READY_TO_MAKE, COFFEE_IS_READY, MAKING_IN_PROGRESS

   def get_machine_state(self):
      if self.machine_state == 'READY_TO_MAKE':
         if not self.__is_cup_present() or not self.__is_water_enough():
            self.__set_machine_state('NOT_READY_TO_MAKE')
      elif self.machine_state == 'NOT_READY_TO_MAKE':
         if self.__is_cup_present() and self.__is_water_enough():
            self.__set_machine_state('READY_TO_MAKE')
      elif self.machine_state == 'COFFEE_IS_READY':
         pass
      elif self.machine_state == 'MAKING_IN_PROGRESS':
         pass
      else: # default
         if self.__is_cup_present() and self.__is_water_enough():
            self.__set_machine_state('READY_TO_MAKE')
         else:
            self.__set_machine_state('NOT_READY_TO_MAKE')
      return self.machine_state

   def get_sensors_status(self, update = False):
      if update == True:
         self.__is_cup_present(update_machine_state = True)
         self.__is_water_enough()
      return {
         'cup_present': self.cup_present,
         'water_enough': self.water_enough,
         'water_level': self.water_level
         }

   def get_not_ready_reason(self):
      if self.machine_state == 'NOT_READY_TO_MAKE':
         if self.cup_present and not self.water_enough:
            return 'not enough water'
         elif not self.cup_present and self.water_enough:
            return 'no cup detected'
         elif not self.cup_present and not self.water_enough:
            return 'not enough water and no cup detected'
      elif self.machine_state == 'COFFEE_IS_READY':
         return 'please consume the previously made cofee first'
      elif self.machine_state == 'MAKING_IN_PROGRESS':
         return 'coffee is in the progress of making, please wait for that to finish first'
      return 'something is wrong, please get machine state again'

   def start_make_coffee(self):
      if self.get_machine_state() != 'READY_TO_MAKE':
         return 'ERROR: ' + self.get_not_ready_reason()
      self.gpio_util.make_coffee('ESPRESSO') # need to add different coffee option later
      self.__set_machine_state('MAKING_IN_PROGRESS')
      self.child_thread.start()
      return 'SUCCESS'

   def __set_machine_state(self, new_state):
      if new_state not in ['READY_TO_MAKE', 'NOT_READY_TO_MAKE', 'COFFEE_IS_READY', 'MAKING_IN_PROGRESS']:
         raise ValueError()
      with self.machine_state_lock:
         self.machine_state = new_state
      return 'SUCCESS'

   def __is_cup_present(self, update_machine_state = False):
      new_value = True  # placeholder for now
      # new_value = self.gpio_util.get_cup_presence()
      with self.cup_present_lock:
         self.cup_present = new_value
      if update_machine_state and (not self.cup_present) and (self.machine_state == 'COFFEE_IS_READY'):
         self.__set_machine_state('NOT_READY_TO_MAKE')
      return self.cup_present

   def __is_water_enough(self, threshold = WATER_THRESHOLD):
      new_value = (self.__get_water_level() >= threshold)
      with self.water_enough_lock:
         self.water_enough = new_value
      return self.water_enough

   def __get_water_level(self):
      new_value = 12 # placeholder for now
      # new_value = self.gpio_util.get_water_level()
      with self.water_level_lock:
         self.water_level = new_value
      return self.water_level

   def __is_coffee_ready(self):
      pass

   def __keep_update_coffee_ready_status(self):
      while self.machine_state == 'MAKING_IN_PROGRESS':
         if self.thread_exit:
            return
         if self.__is_coffee_ready():
            break
         time.sleep(1)
      self.__set_machine_state('COFFEE_IS_READY')
      self.__keep_update_coffee_pickup_status()

   def __keep_update_coffee_pickup_status(self):
      while self.machine_state == 'COFFEE_IS_READY':
         if self.thread_exit:
            return
         if not self.__is_cup_present():
            break
         time.sleep(1)
      self.__set_machine_state('NOT_READY_TO_MAKE')
      # self.scheduler.start_timer_for_next_job()

