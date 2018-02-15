class RPCExecutor():
   def __init__(self, scheduler, machine, notifier):
      self.scheduler = scheduler
      self.machine = machine
      self.notifier = notifier

   def ping(self):
      return 'pong'

   def ping_param(self, param1, param2):
      return str(param1) + ' pong ' + str(param2)

   def add_schedule(self, id, cron_text):
      pass

   def delete_schedule(self, id):
      pass

   def get_schedule_by_id(self, id):
      pass

   def get_schedule_list(self):
      pass

   def get_seconds_to_next_schedule(self, id):
      pass

   def test_notification(self):
      return self.notifier.send('this is a test message')

   def make_coffee_now(self):
      pass

   def get_cup_status(self):
      pass

   def get_water_level(self):
      pass

   def get_machine_state(self):
      pass
