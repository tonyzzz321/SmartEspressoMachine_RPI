#!/usr/bin/env python3

import sys, logging, traceback, time
from multiprocessing import Process, Pipe


from sem_scheduler import Scheduler
from sem_notifier import Notifier
from sem_machine import Machine
import sem_rpc_server as Server
import sem_rpc_responder as RPCResponser
from sem_constants import *

class Controller():

   machine = None
   notifier = None
   scheduler = None
   server_pipe = None
   server_process = None

   def __init__(self):
      self.scheduler = Scheduler(db_path = SCHEDULER_DATABASE_PATH)
      self.machine = Machine()
      self.notifier = Notifier()
      parent_conn, child_conn = Pipe()
      self.server_pipe = parent_conn
      self.server_process = Process(target = Server.start, args = (logger, child_conn, ))
      self.server_process.start()

   def main(self):
      while True:
         if self.server_pipe.poll(1) == True:
            self.server_pipe.send(self.process_rpc_request(self.server_pipe.recv()))
         else:
            time.sleep(1)

   def process_rpc_request(self, request_dict):
      rpc_call_name = request_dict['rpc_call']
      if hasattr(RPCResponser, rpc_call_name):
         rpc_call_method = getattr(RPCResponser, rpc_call_name)
         param_dict = dict()
         for required_param in rpc_call_method.__code__.co_varnames:
            param_dict[required_param] = request_dict[required_param]
         return rpc_call_method(**param_dict)



def msg(text, level='info'):
   print(text)
   if hasattr(logger, level):
      getattr(logger, level)(text)
   else: # print only, no log
      return

if __name__ == "__main__":
   log_file_path = LOG_FILE_PATH
   log_level = logging.INFO
   log_date_format = '%m-%d-%Y %I:%M:%S %p'
   log_msg_format = '%(asctime)s | %(name)s | %(levelname)s: %(message)s'

   logging.basicConfig(handlers=[logging.FileHandler(log_file_path, encoding='utf-8')], level=log_level, datefmt=log_date_format, format=log_msg_format)
   logger = logging.getLogger(PROGRAM_NAME)
   
   try:
      Controller().main()
   except SystemExit:
      pass
   except:
      tb = traceback.format_exc()
      msg(tb, level='error')
      sys.exit(100)
