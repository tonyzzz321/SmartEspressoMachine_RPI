import json, hashlib, time, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from jsonrpcserver import methods
from jsonrpcserver.exceptions import MethodNotFound, InvalidParams

from sem_constants import *
from app_key import *
import sem_rpc_responder as RPCResponser

def MakeCustomLoggableJSONRPCRequestHandler(logger):

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
            request['id']
            if request['method'] != 'sem_do':
               raise KeyError
            params = request['params']
         except KeyError:
            return False
         try:
            params['rpc_call']
            timestamp = params['ts']
            signature = params['sign']
         except KeyError:
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



global_server_pipe = None

def start(logger, pipe):
   global global_server_pipe
   global_server_pipe = pipe
   handler = MakeCustomLoggableJSONRPCRequestHandler(logger)
   HTTPServer((SERVER_BIND_IP, SERVER_PORT), handler).serve_forever()


@methods.add
def sem_do(**kwargs):
   param = dict(**kwargs)
   # if param['rpc_call'] not in rpc_methods_dict.keys():
   if hasattr(RPCResponser, param['rpc_call']) == False:
      raise MethodNotFound('method %s is not supported' % param['rpc_call'])
   # for required_param in rpc_methods_dict[param['rpc_call']]:
   for required_param in getattr(RPCResponser, param['rpc_call']).__code__.co_varnames:
      if required_param not in param.keys():
         raise InvalidParams('param %s is missing for method %s' % (required_param, param['rpc_call']))
   global_server_pipe.send(param)
   result = global_server_pipe.recv()
   return str(result)