#!/usr/bin/env python3

import sys, logging, traceback
import rpc_server
from sem_scheduler import Scheduler
from sem_constants import *

def main(argv):
   scheduler = Scheduler(db_path = SHEDULER_DATABASE_PATH)
   rpc_server.start(logger=logger)

def msg(text, level='info'):
   print(text)
   if level == 'debug':
      logger.debug(text)
   elif level == 'info':
      logger.info(text)
   elif level == 'warning':
      logger.warning(text)
   elif level == 'error':
      logger.error(text)
   elif level == 'critical':
      logger.critical(text)
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
      main(sys.argv[1:])
   except SystemExit:
      pass
   except:
      tb = traceback.format_exc()
      msg(tb, level='error')
      sys.exit(100)
