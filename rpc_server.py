import json, hashlib, time, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from jsonrpcserver import methods
# pip install jsonrpcserver

from rpc_server_methods import *
from rpc_server_constants import *
from app_key import *

def MakeHttpJsonRpcServer(logger):

   class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
      
      logger = None

      def __init__(self, *args, **kwargs):
         self.logger = logger
         super(CustomHTTPRequestHandler, self).__init__(*args, **kwargs)

      def log_message(self, format, *args):
         self.logger.info("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))

      def do_POST(self):
         request = self.rfile.read(int(self.headers['Content-Length'])).decode()
         # check if domain+path is requesting the jsonrpc
         host = self.headers['Host']
         if (SERVER_DOMAIN not in host) or (self.path != RPC_PATH):
            self.forbidden(request)
            return
         # check if param sign is valid
         if self.is_request_valid(request) == False:
            self.forbidden(request)
            return
         # Process request
         response = methods.dispatch(request)
         # Return response
         self.send_response(response.http_status)
         self.send_header('Content-type', 'application/json')
         self.end_headers()
         self.wfile.write(json.dumps(response).encode())

      def do_OPTIONS(self):
         self.send_response(200)
         self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
         self.end_headers()

      def forbidden(self, req):
         request = json.loads(req)
         try:
            request_id = int(request['id'])
         except ValueError:
            request_id = request['id']
         except KeyError:
            request_id = None
         self.send_response(403)
         self.send_header('Content-type', 'application/json')
         self.end_headers()
         response = {
            "jsonrpc": "2.0",
            "error": {"code": 403, "message": "Forbidden"},
            "id": request_id
         }
         self.wfile.write(json.dumps(response).encode())

      def is_request_valid(self, req):
         # jsonrpc request: {'id': int(id), 'jsonrpc': '2.0', 'method': str(method), 'params': {params}}
         # params: {'method': str(method_call), 'ts': str(epoch_time), 'sign': str(sign), param1': 'argum1', 'param2': 'argum2'}
         # sign: all parameters in params (except sign itself) sorted by keys and chained together in HTTP query string format in URL encoding,
         #       concatenate with APP_KEY, and take SHA-256 hash of the concatenated string

         request = json.loads(req)
         try:
            method = request['method']
            params = request['params']
         except KeyError:
            return False
         try:
            timestamp = params['ts']
            signature = params['sign']
            method_call = params['method_call']
         except KeyError:
            return False

         if method != method_call:
            return False

         if self.is_time_valid(ts = timestamp, max_diff = 30) is False:
            return False

         del params['sign']

         data = ""
         keys = list(params.keys())
         keys.sort()
         for key in keys:
            data += "" if (data == "") else "&"
            value = params[key]
            if type(value) == int:
               value = str(value)
            data += key + "=" + str(urllib.parse.quote(value))
         h = hashlib.sha256()
         h.update((data + APP_KEY).encode())
         return (h.hexdigest() == signature)

      def is_time_valid(self, ts, max_diff = 30):
         now = time.time()
         return (abs(int(ts) - int(now)) <= max_diff)

   return CustomHTTPRequestHandler


def start(logger):
   HttpJsonRpcServer = MakeHttpJsonRpcServer(logger)
   HTTPServer(('', 9999), HttpJsonRpcServer).serve_forever()
