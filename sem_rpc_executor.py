import logging

class RPCExecutor():
   def __init__(self, scheduler, machine, notifier):
      self.logger = logging.getLogger(__name__)
      self.scheduler = scheduler
      self.machine = machine
      self.notifier = notifier

   def msg(self, text, level='info'):
      if hasattr(self.logger, level):
         getattr(self.logger, level)(text)

   def __verify_param_type(self, type_dict, param_dict):
      for key in param_dict.keys():
         if type(param_dict[key]) != type_dict[key]:
            return 'ERROR: parameter %s should be type %s' % (key, type_dict[key].__name__)
      return 'SUCCESS'


   def ping(self):
      self.msg('Executing \'ping\' method', 'debug')
      result = 'pong'
      self.msg('Returning result from \'ping\' method: %s' % result, 'debug')
      return result

   def ping_param(self, param1, param2):
      self.msg('Executing \'ping_param\' method with parameters: param1=%s, param2=%s' % (str(param1), str(param2)), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'param1': str, 'param2': str}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'ping_param\' method: %s' % result, 'debug')
         return result
      result = param1 + ' pong ' + param2
      self.msg('Returning result from \'ping_param\' method: %s' % result, 'debug')
      return result

   def add_schedule(self, id, cron_text, enabled, coffee_type='ESPRESSO'):
      self.msg('Executing \'add_schedule\' method with parameters: id=%s, cron_text=%s, enabled=%s, coffee_type=%s' % (str(id), str(cron_text), str(enabled), str(coffee_type)), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int, 'cron_text': str, 'enabled': int, 'coffee_type': str}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'add_schedule\' method: %s' % result, 'debug')
         return result

      enabled_bool = (enabled == 1)
      result = self.scheduler.add_entry(cron_text=cron_text, id=id, coffee_type=coffee_type, enabled=enabled_bool)
      self.msg('Returning result from \'add_schedule\' method: %s' % result, 'debug')
      return result

   def delete_schedule(self, id):
      self.msg('Executing \'delete_schedule\' method with parameters: id=%s' % str(id), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'delete_schedule\' method: %s' % result, 'debug')
         return result

      result = self.scheduler.delete_entry(id=id)
      self.msg('Returning result from \'delete_schedule\' method: %s' % result, 'debug')
      return result

   def get_schedule_by_id(self, id):
      self.msg('Executing \'get_schedule_by_id\' method with parameters: id=%s' % str(id), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'get_schedule_by_id\' method: %s' % result, 'debug')
         return result

      if id <= 0:
         self.msg('Error executing \'get_schedule_by_id\' method: ERROR: id must be positive', 'debug')
         return 'ERROR: id must be positive'
      result = self.scheduler.get_entry(id=id)
      result['enabled'] = 1 if result['enabled'] else 0
      self.msg('Returning result from \'get_schedule_by_id\' method: %s' % str(result), 'debug')
      return result

   def get_schedule_list(self):
      self.msg('Executing \'get_schedule_list\' method', 'debug')
      result = self.scheduler.get_entry()
      for entry in result:
         entry['enabled'] = 1 if entry['enabled'] else 0
      self.msg('Returning result from \'get_schedule_list\' method: %s' % str(result), 'debug')
      return result

   def get_seconds_to_next_schedule(self, id):
      self.msg('Executing \'get_seconds_to_next_schedule\' method with parameters: id=%s' % str(id), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'id': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'get_seconds_to_next_schedule\' method: %s' % result, 'debug')
         return result

      result = (self.scheduler.seconds_until_next_job(id=id))[0]
      self.msg('Returning result from \'get_seconds_to_next_schedule\' method: %s' % str(result), 'debug')
      return result

   def test_notification(self):
      self.msg('Executing \'test_notification\' method', 'debug')
      result = self.notifier.send('Test', 'this is a test message')
      self.msg('Returning result from \'get_seconds_to_next_schedule\' method: %s' % result, 'debug')
      return result

   def make_coffee_now(self, coffee_type):
      self.msg('Executing \'make_coffee_now\' method with parameters: coffee_type=%s' % str(coffee_type), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'coffee_type': str}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'make_coffee_now\' method: %s' % result, 'debug')
         return result

      result = self.machine.start_make_coffee(coffee_type)
      self.msg('Returning result from \'make_coffee_now\' method: %s' % result, 'debug')
      return result

   def get_sensors_status(self, update):
      self.msg('Executing \'get_sensors_status\' method with parameters: update=%s' % str(update), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'update': int}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'get_sensors_status\' method: %s' % result, 'debug')
         return result
         
      update_bool = (update == 1)
      result = self.machine.get_sensors_status(update=update_bool)
      result['cup_present'] = 1 if result['cup_present'] else 0
      result['water_enough'] = 1 if result['water_enough'] else 0
      self.msg('Returning result from \'get_sensors_status\' method: %s' % str(result), 'debug')
      return result

   def get_not_ready_reason(self):
      self.msg('Executing \'get_not_ready_reason\' method', 'debug')
      result = self.machine.get_not_ready_reason()
      self.msg('Returning result from \'get_not_ready_reason\' method: %s' % result, 'debug')
      return result

   def get_machine_state(self):
      self.msg('Executing \'get_machine_state\' method', 'debug')
      result = self.machine.get_machine_state()
      self.msg('Returning result from \'get_machine_state\' method: %s' % result, 'debug')
      return result

   def upload_firebase_token(self, token):
      self.msg('Executing \'upload_firebase_token\' method with parameters: token=%s' % str(token), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'token': str}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'upload_firebase_token\' method: %s' % result, 'debug')
         return result

      result = self.notifier.new_token(token)
      self.msg('Returning result from \'upload_firebase_token\' method: %s' % result, 'debug')
      return result

   def delete_firebase_token(self, token):
      self.msg('Executing \'delete_firebase_token\' method with parameters: token=%s' % str(token), 'debug')
      param_dict = locals()
      del param_dict['self']
      type_dict = {'token': str}
      result = self.__verify_param_type(type_dict, param_dict)
      if result != 'SUCCESS':
         self.msg('Error executing \'delete_firebase_token\' method: %s' % result, 'debug')
         return result

      if token == 'DELETE_ALL':
         result = self.notifier.clear_token()
      else:
         result = self.notifier.delete_token(token)
      self.msg('Returning result from \'delete_firebase_token\' method: %s' % result, 'debug')
      return result
      