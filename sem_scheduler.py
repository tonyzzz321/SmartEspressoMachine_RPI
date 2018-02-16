import json, time
from threading import Lock, Timer
from croniter import croniter

class Scheduler():

   def __init__(self, db_path):
      self.database_path = db_path
      self.database = None
      self.next_id = None
      self.load_database()
      self.timer = None
      self.timer_running = False
      self.timer_running_lock = Lock()
      self.times_up = False
      self.times_up_lock = Lock()
      self.start_timer_for_next_job()

   def load_database(self):
      try:
         with open(self.database_path, 'r', encoding='utf-8') as db:
            self.database = json.loads(db.read())
            self.next_id = self.get_next_id()
      except:
         self.database = {'pi':[]}   # dict with key = user, value = list of dict below
         # {'id': int(id), 'cron': str(cron_expression), enabled': True/False}
         # cron_expression: '* * * * *' (minute, hour, day of month, month, day of week)
         self.next_id = 1

   def start_timer_for_next_job(self):
      if self.timer_running == True:
         self.timer.cancel()
         self.__set_timer_running_state(False)
      countdown = self.seconds_until_next_job()
      if countdown != None and type(countdown) == int:
         self.timer = Timer(countdown, self.__timer_expire_action)
         self.__set_timer_running_state(True)
         self.timer.start()

   def __timer_expire_action(self):
      self.__set_timer_running_state(False)
      self.__set_times_up_state(True)

   def __set_timer_running_state(self, new_state):
      with self.timer_running_lock:
         self.timer_running = new_state

   def __set_times_up_state(self, new_state):
      with self.times_up_lock:
         self.times_up = new_state

   def outside_reset_times_up_state(self):
      self.__set_times_up_state(False)

   def get_next_id(self):
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
      return max(id_list) + 1

   def write_database(self):
      with open(self.database_path, 'w', encoding='utf-8') as db:
         db.write(json.dumps(self.database, indent=3, sort_keys=True, ensure_ascii=False))

   def add_entry(self, cron_text, enabled = True, id = 0, user = 'pi'):
   # id = zero -> add new entry, id = nonzero -> replace entry
   # will add user to database if user is new, return error if user is ''
   # use this method to change any setting of an entry (except id)
      if user == '':
         return 'ERROR: username empty'
      if croniter.is_valid(cron_text) == False:
         return 'ERROR: invalid cron text'
      if type(enabled) is not bool:
         return 'ERROR: enabled is not boolean'
      if user not in self.database.keys():
         self.database[user] = []
      if id == 0:
         self.database[user].append({
         'id': self.get_next_id(),
         'cron': cron_text,
         'enabled': enabled
         })
         self.start_timer_for_next_job()
         self.write_database()
         return 'SUCCESS'
      for entry in self.database[user]:
         if entry['id'] == id:
            entry['cron'] = cron_text
            entry['enabled'] = enabled
            self.start_timer_for_next_job()
            self.write_database()
            return 'SUCCESS'
      return 'ERROR: id not found for this user'

   def delete_entry(self, id, user = 'pi'):
   # id = zero -> delete all entries for specified user, id = nonzero -> delete specified entry for specified user
   # return 'SUCCESS' if success, 'ERROR' otherwise, i.e. id or user not found
      if user not in self.database.keys():
         return 'ERROR: user not found'
      if id == 0:
         self.database[user] = []
         self.start_timer_for_next_job()
         self.write_database()
         return 'SUCCESS'
      for entry in self.database[user]:
         if entry['id'] == id:
            self.database[user].remove(entry)
            self.start_timer_for_next_job()
            self.write_database()
            return 'SUCCESS'
      return 'ERROR: id not found for this user'

   def get_entry(self, id = 0, user = 'pi'):
   # id = zero -> get all entries for specified user, id = nonzero -> get specific entry
   # return 'ERROR' if id = nonzero and not found for specified user
      if user not in self.database.keys():
         return 'ERROR: user not found'
      if id == 0:
         if len(self.database[user]) == 0:
            return 'ERROR: this user has no job schedule'
         else:
            return self.database[user]
      for entry in self.database[user]:
         if entry['id'] == id:
            return entry
      return 'ERROR: id not found for this user'

   def seconds_until_next_job(self, id = 0, user = 'pi'):
   # id = zero -> process all jobs for specified user, id = nonzero -> process specific job
   # user = '' -> process all users, user = non-empty string -> process specific user
   # return None if id disabled or not found, or if user not found
      all_entries = []
      if user == '':
         for entry_list in self.database.values():
            all_entries += entry_list
      elif user not in self.database.keys():
         return 'ERROR: user not found'
      else:
         all_entries = self.database[user]

      enabled_entries = filter((lambda x: x['enabled'] == True), all_entries)
      base_time = time.time()
      second_in_entries = list(map((lambda x: int(croniter(x['cron'], base_time).get_next() - base_time)), enabled_entries))

      if len(second_in_entries) == 0:
         return None
      return min(second_in_entries)
