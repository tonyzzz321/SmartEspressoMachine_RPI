#!/usr/bin/env python3

import sys, logging, traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from jsonrpcserver import methods


@methods.add
def ping():
   return 'pong'


class TestHttpServer(BaseHTTPRequestHandler):
   def do_POST(self):
      host = self.headers['Host']
      print(self.path)
      if ('sem.pezhang.xyz' not in host) or (self.path != '/jsonrpc'):
         self.send_response(403)
         self.send_header('Content-type', 'application/json')
         self.end_headers()
         return
      # Process request
      request = self.rfile.read(int(self.headers['Content-Length'])).decode()
      response = methods.dispatch(request)
      # Return response
      self.send_response(response.http_status)
      self.send_header('Content-type', 'application/json')
      self.end_headers()
      self.wfile.write(str(response).encode())

   def do_GET(self):
      self.send_error(403)

def main(argv):
   HTTPServer(('', 9999), TestHttpServer).serve_forever()

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
   uname = 'chip' # 'chip' or 'pi'
   log_file_path = '/home/%s/SEM_RPI/SEM.log' % uname
   log_level = logging.INFO
   log_date_format = '%m-%d-%Y %I:%M:%S %p'
   log_msg_format = '%(asctime)s | %(name)s | %(levelname)s: %(message)s'

   logging.basicConfig(handlers=[logging.FileHandler(log_file_path, encoding='utf-8')], level=log_level, datefmt=log_date_format, format=log_msg_format)
   logger = logging.getLogger('SEM')
   
   try:
      main(sys.argv[1:])
   except SystemExit:
      pass
   except:
      tb = traceback.format_exc()
      msg(tb, level='error')
      sys.exit(100)
