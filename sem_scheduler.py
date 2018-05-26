import json, logging
from threading import Lock, Timer
from datetime import datetime
from croniter import croniter

from sem_constants import AVAILABLE_COFFEE_TYPE_LIST

class Scheduler():

   def __init__(self, db_path):
      self.logger = logging.getLogger(__name__)
      self.database_path = db_path
      self.database = None
      self.next_id = None
      self.load_database()
      self.timer = None
      self.timer_running = False
      self.timer_running_lock = Lock()
      self.times_up = False
      self.times_up_lock = Lock()
      self.next_coffee_type = None
      self.start_timer_for_next_job()

   def msg(self, text, level='info'):
      if hasattr(self.logger, level):
         getattr(self.logger, level)(text)

   def load_database(self):
      self.msg('Attempting to load schedule database from %s' % self.database_path, 'info')
      try:
         with open(self.database_path, 'r', encoding='utf-8') as db:
            self.database = json.loads(db.read())
            self.next_id = self.get_next_id()
         self.msg('Schedule database loaded', 'info')
      except:
         self.msg('Schedule database does not exist, creating new database', 'info')
         self.database = {'pi':[]}   # dict with key = user, value = list of dict below
         # {'id': int(id), 'cron': str(cron_expression), 'enabled': True/False, 'coffee_type': str(type)}
         # cron_expression: '* * * * *' (minute, hour, day of month, month, day of week)
         self.next_id = 1
         self.msg('Schedule database created', 'info')

   def start_timer_for_next_job(self):
      self.msg('Attempting to start timer for next job', 'info')
      if self.timer_running == True:
         self.msg('Timer already running, canceling existing timer', 'info')
         self.timer.cancel()
         self.__set_timer_running_state(False)
         self.msg('Existing timer canceled, Timer state is set to NOT RUNNING', 'info')
      countdown, coffee_type = self.seconds_until_next_job()
      if countdown > 0:
         self.msg('Next job is to make %s in %s seconds' % (coffee_type, str(countdown)), 'info')
         self.next_coffee_type = coffee_type
         self.timer = Timer(countdown, self.__timer_expire_action)
         self.__set_timer_running_state(True)
         self.msg('Timer state is set to RUNNING', 'info')
         self.timer.start()
         self.msg('Timer started for making %s in %s seconds' % (coffee_type, str(countdown)), 'info')
      elif countdown == -1:
         self.msg('None of the schedules are enabled, timer not started', 'info')
      else:
         self.msg('Unknown error, timer not started', 'info')

   def __timer_expire_action(self):
      self.msg('Timer is expiring, attempting to reset Timer state and set TimerIsUp state', 'info')
      self.__set_timer_running_state(False)
      self.__set_times_up_state(True)
      self.msg('Timer state is set to NOT RUNNING, TimeIsUP state is set to TRUE', 'info')

   def __set_timer_running_state(self, new_state):
      with self.timer_running_lock:
         self.timer_running = new_state

   def __set_times_up_state(self, new_state):
      with self.times_up_lock:
         self.times_up = new_state

   def outside_reset_times_up_state(self):
      self.msg('Attempting to reset TimeIsUp state from outside sem_scheduler', 'info')
      self.__set_times_up_state(False)
      self.msg('TimeIsUp state is set to FALSE', 'info')

   def get_next_id(self):
      self.msg('Attempting to get next available ID for schedule database', 'info')
      if self.next_id != None:
         self.next_id += 1
         return self.next_id - 1
      id_list = []
      for entry_list in self.database.values():
         try:
            ids = map((lambda x: x['id']), entry_list)
            id_list.append(max(ids))
         except KeyError:
            pass
      next_available_id = max(id_list) + 1
      self.msg('Next available ID for schedule database is %s' % int(next_available_id), 'info')
      return next_available_id

   def write_database(self):
      self.msg('Attempting to write schedule database to %s' % self.database_path, 'info')
      with open(self.database_path, 'w', encoding='utf-8') as db:
         db.write(json.dumps(self.database, indent=3, sort_keys=True, ensure_ascii=False))
      self.msg('Schedule database written to file sucessfully', 'info')

   def add_entry(self, cron_text, coffee_type, enabled = True, id = 0, user = 'pi'):
   # id = zero -> add new entry, id = nonzero -> replace entry
   # will add user to database if user is new, return error if user is ''
   # use this method to change any setting of an entry (except id)
      if id == 0:
         self.msg('Attempting to add entry to schedule database: cron_text: %s, coffee_type: %s, enabled: %s' % (cron_text, coffee_type, str(enabled)), 'info')
      else:
         self.msg('Attempting to replace entry ID %s in schedule database: cron_text: %s, coffee_type: %s, enabled: %s' % (str(id), cron_text, coffee_type, str(enabled)), 'info')
      if user == '':
         self.msg('Adding/replacing schedule entry failed: user string is empty', 'info')
         return 'ERROR: username empty'
      if croniter.is_valid(cron_text) == False:
         self.msg('Adding/replacing schedule entry failed: %s is not a valid cron string' % cron_text, 'info')
         return 'ERROR: invalid cron text'
      if type(enabled) is not bool:
         self.msg('Adding/replacing schedule entry failed: %s is not a recognized boolean value for \'enabled\'' % str(enabled), 'info')
         return 'ERROR: enabled is not boolean'
      if user not in self.database.keys():
         self.msg('%s is a new user, adding new user to schedule database' % user, 'info')
         self.database[user] = []

      if cron_text in map((lambda x: x['cron']), self.database[user]):
         self.msg('Adding/replacing schedule entry failed: identical cron schedule %s already exist in schedule database' % cron_text, 'info')
         return 'ERROR: identical cron schedule already exist'
      if coffee_type not in AVAILABLE_COFFEE_TYPE_LIST:
         self.msg('Adding/replacing schedule entry failed: %s is not a valid coffee type' % coffee_type, 'info')
         return 'ERROR: invalid coffee type'

      if id == 0:
         self.database[user].append({
         'id': self.get_next_id(),
         'cron': cron_text,
         'enabled': enabled,
         'coffee_type': coffee_type
         })
         self.msg('New entry added to schedule database: cron_text: %s, coffee_type: %s, enabled: %s' % (cron_text, coffee_type, str(enabled)), 'info')
         self.write_database()
         self.msg('Updating timer for new schedule entry', 'info')
         self.start_timer_for_next_job()
         return 'SUCCESS'
      for entry in self.database[user]:
         if entry['id'] == id:
            entry['cron'] = cron_text
            entry['enabled'] = enabled
            entry['coffee_type'] = coffee_type
            self.msg('Entry ID %s replaced in schedule database: cron_text: %s, coffee_type: %s, enabled: %s' % (str(id), cron_text, coffee_type, str(enabled)), 'info')
            self.write_database()
            self.msg('Updating timer for replaced schedule entry', 'info')
            self.start_timer_for_next_job()
            return 'SUCCESS'
      self.msg('Replacing schedule entry failed: schedule ID %s not found for user %s' % (str(id), user), 'info')
      return 'ERROR: id not found for this user'

   def delete_entry(self, id, user = 'pi'):
   # id = zero -> delete all entries for specified user, id = nonzero -> delete specified entry for specified user
   # return 'SUCCESS' if success, 'ERROR' otherwise, i.e. id or user not found
      if id == 0:
         self.msg('Attempting to clear schedule entries for user %s' % user, 'info')
      else:
         self.msg('Attempting to delete schedule entry ID %s for user %s' % (str(id), user), 'info')
      if user not in self.database.keys():
         self.msg('Deleting schedule entry failed: user %s not found' % user, 'info')
         return 'ERROR: user not found'
      if id == 0:
         self.database[user] = []
         self.msg('Schedule entries for user %s cleared' % user, 'info')
         self.write_database()
         self.msg('Updating timer for modified schedule entry', 'info')
         self.start_timer_for_next_job()
         return 'SUCCESS'
      for entry in self.database[user]:
         if entry['id'] == id:
            self.database[user].remove(entry)
            self.msg('Schedule entry ID %s for user %s deleted' % (str(id), user), 'info')
            self.write_database()
            self.msg('Updating timer for modified schedule entry', 'info')
            self.start_timer_for_next_job()
            return 'SUCCESS'
      self.msg('Deleting schedule entry failed: schedule ID %s not found for user %s' % (str(id), user), 'info')
      return 'ERROR: id not found for this user'

   def get_entry(self, id = 0, user = 'pi'):
   # id = zero -> get all entries for specified user, id = nonzero -> get specific entry
   # return 'ERROR' if id = nonzero and not found for specified user
      if id == 0:
         self.msg('Attempting to get schedule entries for user %s' % user, 'info')
      else:
         self.msg('Attempting to get schedule entry ID %s for user %s' % (str(id), user), 'info')
      if user not in self.database.keys():
         self.msg('Getting schedule entry failed: user %s not found' % user, 'info')
         return 'ERROR: user not found'
      if id == 0:
         # if len(self.database[user]) == 0:
         #    return 'ERROR: this user has no job schedule'
         # else:
         self.msg('Getting schedule entries for user %s successfully' % user, 'info')
         return self.database[user]
      for entry in self.database[user]:
         if entry['id'] == id:
            self.msg('Getting schedule entry ID %s for user %s successfully' % (str(id), user), 'info')
            return entry
      self.msg('Getting schedule entry failed: ID %s not found for user %s' % (str(id), user), 'info')
      return 'ERROR: id not found for this user'

   def seconds_until_next_job(self, id = 0, user = 'pi'):
   # id = zero -> process all jobs for specified user, id = nonzero -> process specific job
   # user = '' -> process all users, user = non-empty string -> process specific user
   # return None if id disabled or not found, or if user not found
      self.msg('Attempting to get next scheduled job', 'info')
      all_entries = []
      if user == '':
         for entry_list in self.database.values():
            all_entries += entry_list
      elif user not in self.database.keys():
         self.msg('Getting next scheduled job failed: user %s not exist' % user, 'info')
         return (-3, 'user not found')   # user not found
      else:
         all_entries = self.database[user]

      if id != 0:
         temp_entry_list = None
         for entry in all_entries:
            if entry['id'] == id:
               temp_entry_list = [entry]
               break
         if temp_entry_list == None:
            self.msg('Getting next scheduled job failed: ID %s not found for user %s' % (str(id), user), 'info')
            return (-2, 'id not found')   # id not found
         else:
            all_entries = temp_entry_list

      enabled_entries = filter((lambda x: x['enabled'] == True), all_entries)
      base_time = datetime.now()
      second_in_entries = list(map((lambda x: (int(croniter(x['cron'], base_time).get_next(datetime).timestamp() - base_time.timestamp()), x['coffee_type'])), enabled_entries))

      if len(second_in_entries) == 0:
         self.msg('Getting next scheduled job failed: no enabled entries', 'info')
         return (-1, 'entry not enabled')   # entry not enabled
      return min(second_in_entries, key=(lambda x: x[0]))

