import time, logging
from threading import Thread, Lock
from sem_constants import *
from sem_gpio_util import GPIO_Util

class Machine():
   
   def __init__(self, notifier, gpio_dict=GPIO_DICT):
      self.logger = logging.getLogger(__name__)
      self.notifier = notifier
      self.gpio_util = GPIO_Util(gpio_dict)
      self.cup_present = None # boolean
      self.water_level = None # integer from 0 to 100, representing percentage
      self.water_enough = None   # boolean
      self.machine_state = None
      self.cup_present_lock = Lock()
      self.water_level_lock = Lock()
      self.water_enough_lock = Lock()
      self.machine_state_lock = Lock()
      self.thread_exit = False
      self.child_thread = None
      self.get_machine_state()
      # READY_TO_MAKE, NOT_READY_TO_MAKE, COFFEE_IS_READY, MAKING_IN_PROGRESS
      self.dummy_timer = None

   def msg(self, text, level='info'):
      if hasattr(self.logger, level):
         getattr(self.logger, level)(text)

   def get_machine_state(self):
      self.msg('Attempting to update machine state, current machine state: %s' % str(self.machine_state), 'info')
      if self.machine_state == 'READY_TO_MAKE':
         local_cup = self.__is_cup_present()
         local_water = self.__is_water_enough()
         if not local_cup or not local_water:
            self.msg('Cup not present of water not enough, changing machine state to \'NOT_READY_TO_MAKE\'', 'info')
            self.__set_machine_state('NOT_READY_TO_MAKE')
      elif self.machine_state == 'NOT_READY_TO_MAKE':
         local_cup = self.__is_cup_present()
         local_water = self.__is_water_enough()
         if local_cup and local_water:
            self.msg('Cup is present and water is enough, changing machine state to \'READY_TO_MAKE\'', 'info')
            self.__set_machine_state('READY_TO_MAKE')
      elif self.machine_state == 'COFFEE_IS_READY':
         pass
      elif self.machine_state == 'MAKING_IN_PROGRESS':
         pass
      else: # default
         if self.__is_cup_present() and self.__is_water_enough():
            self.msg('Cup is present and water is enough, changing machine state to \'READY_TO_MAKE\'', 'info')
            self.__set_machine_state('READY_TO_MAKE')
         else:
            self.msg('Cup not present of water not enough, changing machine state to \'NOT_READY_TO_MAKE\'', 'info')
            self.__set_machine_state('NOT_READY_TO_MAKE')
      self.msg('Updated machine state: %s' % self.machine_state, 'info')
      return self.machine_state

   def get_sensors_status(self, update = False):
      self.msg('Attempting to %s sensor status' % ('update' if update else 'retrieve'), 'info')
      if update == True:
         self.__is_cup_present(update_machine_state = True)
         self.__is_water_enough()
      result = {
         'cup_present': self.cup_present,
         'water_enough': self.water_enough,
         'water_level': self.water_level
         }
      self.msg('Sensor status retrieved: %s' % str(result), 'info')
      return result

   def get_not_ready_reason(self):
      self.msg('Attempting to retrieve machine not ready reason', 'info')
      if self.machine_state == 'NOT_READY_TO_MAKE':
         if self.cup_present and not self.water_enough:
            result = 'not enough water'
         elif not self.cup_present and self.water_enough:
            result = 'no cup detected'
         elif not self.cup_present and not self.water_enough:
            result = 'not enough water and no cup detected'
      elif self.machine_state == 'COFFEE_IS_READY':
         result = 'please consume the previously made covfefe first'
      elif self.machine_state == 'MAKING_IN_PROGRESS':
         result = 'coffee is in the progress of making, please wait for that to finish first'
      else:
         result = 'something is wrong, please get machine state again'
      self.msg('Not ready reason: %s' % result, 'info')
      return result

   def start_make_coffee(self, coffee_type):
      self.msg('Attempting to initiate making coffee %s' % str(coffee_type), 'info')
      if coffee_type not in AVAILABLE_COFFEE_TYPE_LIST:
         self.msg('Making coffee failed: unknown coffee type %s' % str(coffee_type), 'info')
         return 'ERROR: unknown coffee type ' + coffee_type
      if self.get_machine_state() != 'READY_TO_MAKE':
         reason = self.get_not_ready_reason()
         self.msg('Making coffee failed: %s' % reason, 'info')
         return 'ERROR: ' + reason
      result = self.gpio_util.make_coffee(coffee_type)
      if result != 'SUCCESS':
         self.msg('Making coffee failed: %s' % result, 'info')
         return result
      self.__set_machine_state('MAKING_IN_PROGRESS')
      self.msg('Starting child thread to monitor coffee progress', 'info')
      self.child_thread = Thread(target=self.__keep_update_coffee_ready_status)
      self.child_thread.start()
      self.msg('Child thread started, coffee is on the way', 'info')
      return 'SUCCESS'

   def __set_machine_state(self, new_state):
      self.msg('Attempting to set new machine state: %s' % str(new_state), 'info')
      if new_state not in ['READY_TO_MAKE', 'NOT_READY_TO_MAKE', 'COFFEE_IS_READY', 'MAKING_IN_PROGRESS']:
         self.msg('%s is not a valid machine state, raising exception' % str(new_state), 'info')
         raise ValueError()
      with self.machine_state_lock:
         self.machine_state = new_state
      self.msg('New machine state successfully set', 'info')
      return 'SUCCESS'

   def __is_cup_present(self, update_machine_state = False):
      self.msg('Attempting to update cup presence %s' % (' and update machine state accordingly' if update_machine_state else ''), 'info')
      # new_value = True  # placeholder for now
      new_value = self.gpio_util.get_cup_presence()
      with self.cup_present_lock:
         self.cup_present = new_value
      self.msg('Cup presence updated: %s' % str(self.cup_present), 'info')
      if update_machine_state and (not self.cup_present) and (self.machine_state == 'COFFEE_IS_READY'):
         self.__set_machine_state('NOT_READY_TO_MAKE')
         self.msg('Machine state updated: %s' % self.machine_state, 'info')
      return self.cup_present

   def __is_water_enough(self, threshold = WATER_THRESHOLD):
      self.msg('Attempting to update water sufficiency', 'info')
      new_value = (self.__get_water_level() >= threshold)
      with self.water_enough_lock:
         self.water_enough = new_value
      self.msg('Water sufficiency compared to threshold %s%% updated: %s' % (str(threshold), str(self.water_enough)), 'info')
      return self.water_enough

   def __get_water_level(self):
      self.msg('Attempting to update water level', 'info')
      # new_value = 12 # placeholder for now
      new_value = self.gpio_util.get_water_level()
      with self.water_level_lock:
         self.water_level = new_value
      self.msg('Water level updated: %s%%' % str(self.water_level), 'info')
      return self.water_level

   def __is_coffee_ready(self):
      if self.dummy_timer < 60:
         self.dummy_timer += 1
         return False
      return True

   def __keep_update_coffee_ready_status(self):
      self.msg('Started monitoring coffee making progress continuously', 'info')
      self.dummy_timer = 0
      while self.machine_state == 'MAKING_IN_PROGRESS':
         if self.thread_exit:
            self.msg('Received terminate signal, child thread exiting', 'info')
            return
         if self.__is_coffee_ready():
            break
         time.sleep(1)
      self.msg('Detected coffee making progress completion', 'info')
      self.__set_machine_state('COFFEE_IS_READY')
      self.msg('Sending coffee ready push notification', 'info')
      self.notifier.send('Coffee Now Ready', 'The coffee you scheduled is now ready to enjoy!')
      self.msg('Push notification sending completed')
      self.__keep_update_coffee_pickup_status()
      self.msg('Child thread returning')

   def __keep_update_coffee_pickup_status(self):
      self.msg('Started monitoring coffee pickup continuously', 'info')
      while self.machine_state == 'COFFEE_IS_READY':
         if self.thread_exit:
            self.msg('Received terminate signal, child thread exiting', 'info')
            return
         if not self.__is_cup_present():
            break
         time.sleep(1)
      self.msg('Detected coffee has been picked up', 'info')
      self.__set_machine_state('NOT_READY_TO_MAKE')
