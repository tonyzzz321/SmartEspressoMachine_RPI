class RPCExecutor():
   def __init__(self, scheduler, machine, notifier):
      self.scheduler = scheduler
      self.machine = machine
      self.notifier = notifier

   def __verify_param_type(self, type_dict, param_dict):
      for key in param_dict.keys():
         if type(param_dict[key]) != type_dict[key]:
            return 'ERROR: parameter %s should be type %s' % (key, type_dict[key].__name__)
      return 'SUCCESS'


   def ping(self):
      return 'pong'

   def ping_param(self, param1, param2):
      param_dict = locals()
      del param_dict['self']
      type_dict = {'param1': str, 'param2': str}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         return result

      return param1 + ' pong ' + param2

   def add_schedule(self, id, cron_text, enabled):
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int, 'cron_text': str, 'enabled': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         return result

      enabled_bool = (enabled == 1)
      return self.scheduler.add_entry(cron_text=cron_text, id=id, enabled=enabled_bool)

   def delete_schedule(self, id):
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         return result

      return self.scheduler.delete_entry(id=id)

   def get_schedule_by_id(self, id):
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         return result

      if id <= 0:
         return 'ERROR: id must be positive'
      result = self.scheduler.get_entry(id=id)
      result['enabled'] = 1 if result['enabled'] else 0
      return result

   def get_schedule_list(self):
      result = self.scheduler.get_entry()
      for entry in result:
         entry['enabled'] = 1 if entry['enabled'] else 0
      return result

   def get_seconds_to_next_schedule(self, id):
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         return result

      return self.scheduler.seconds_until_next_job(id=id)

   def test_notification(self):
      return self.notifier.send('Test', 'this is a test message')

   def make_coffee_now(self, coffee_type):
      return self.machine.start_make_coffee(coffee_type)

   def get_sensors_status(self, update):
      param_dict = locals()
      del param_dict['self']
      type_dict = {'update': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         return result
         
      update_bool = (update == 1)
      result = self.machine.get_sensors_status(update=update_bool)
      result['cup_present'] = 1 if result['cup_present'] else 0
      result['water_enough'] = 1 if result['water_enough'] else 0

      return result

   def get_not_ready_reason(self):
      return self.machine.get_not_ready_reason()

   def get_machine_state(self):
      return self.machine.get_machine_state()

   def upload_firebase_token(self, token):
      return self.notifier.new_token()

   def delete_firebase_token(self, token):
      if token == 'DELETE_ALL':
         return self.notifier.clear_token()
      else:
         return self.notifier.delete_token(token)
