#!/usr/bin/env python3

import sys, logging, traceback, time, inspect
from multiprocessing import Process, Pipe

from sem_scheduler import Scheduler
from sem_notifier import Notifier
from sem_machine import Machine
import sem_rpc_server as Server
from sem_rpc_executor import RPCExecutor
from sem_constants import *

class Controller():

   def __init__(self):
      self.scheduler = Scheduler(db_path = SCHEDULER_DATABASE_PATH)
      msg('Scheduling module loaded', 'info')
      self.notifier = Notifier(token_path = FCM_CLIENT_TOKEN_PATH)
      msg('Notification module loaded' , 'info')
      self.machine = Machine(self.notifier)
      msg('Espresso machine module loaded' , 'info')
      self.executor = RPCExecutor(self.scheduler, self.machine, self.notifier)
      msg('RPC command execution module loaded' , 'info')
      parent_conn, child_conn = Pipe()
      self.server_pipe = parent_conn
      self.server_process = Process(target = Server.start, args = (child_conn, ))
      self.server_process.start()
      msg('HTTP server process started' , 'info')

   def main(self):
      msg('Server is now ready' , 'info')
      while True:
         if self.server_pipe.poll(1) == True:
            msg('Received a request from RPC, calling rpc_executor to handle the request' , 'info')
            self.server_pipe.send(self.process_rpc_request(self.server_pipe.recv()))
            msg('RPC request handling completed' , 'info')
         if self.scheduler.times_up == True:
            msg('Schedule timer expired, calling machine to make coffee' , 'info')
            result = self.machine.start_make_coffee(self.scheduler.next_coffee_type)
            if result == 'SUCCESS':
               msg('Scheduled coffee making process started', 'info')
            else:
               msg('Scheduled coffee making failed: %s. Sending push notification' % result, 'info')
               self.notifier.send('Scheduled Coffee Making Failed', result)
               msg('Push notification sending completed', 'info')
            msg('Resetting schedule timer', 'info')
            self.scheduler.outside_reset_times_up_state()
            self.scheduler.start_timer_for_next_job()
            msg('Time has been resetted', 'info')
         else:
            time.sleep(1)

   def process_rpc_request(self, request_dict):
      rpc_call_name = request_dict['rpc_call']
      if hasattr(self.executor, rpc_call_name):
         rpc_call_method = getattr(self.executor, rpc_call_name)
         param_dict = dict()
         for required_param in inspect.getfullargspec(rpc_call_method).args:
            if required_param == 'self':
               continue
            param_dict[required_param] = request_dict[required_param]
         return rpc_call_method(**param_dict)
      return None


def msg(text, level='info'):
   print(text)
   if hasattr(logger, level):
      getattr(logger, level)(text)
   else: # print only, no log
      return

def exit_script(exit_code = 0):
   msg('Receive terminate signal, script exiting with exit code %d\n' % exit_code)
   try:
      controller.machine.gpio_util.clean_up()
      controller.server_process.terminate()
      controller.scheduler.timer.cancel()
      controller.machine.thread_exit = True
   except (NameError, AttributeError):
      pass
   sys.exit(exit_code)

if __name__ == "__main__":
   log_file_path = LOG_FILE_PATH
   log_level = logging.INFO
   log_date_format = '%m-%d-%Y %I:%M:%S %p'
   log_msg_format = '%(asctime)s | %(name)s | %(levelname)s: %(message)s'

   logging.basicConfig(handlers=[logging.FileHandler(log_file_path, encoding='utf-8')], level=log_level, datefmt=log_date_format, format=log_msg_format)
   logger = logging.getLogger(PROGRAM_NAME)
   
   try:
      controller = Controller()
      controller.main()
   except Exception:
      tb = traceback.format_exc()
      msg(tb, level='error')
      exit_script(100)
   except (SystemExit, KeyboardInterrupt):
      exit_script()
