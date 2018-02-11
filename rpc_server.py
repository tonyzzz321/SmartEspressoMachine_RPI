import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from jsonrpcserver import methods
# pip install jsonrpcserver

from rpc_server_methods import *
from rpc_server_constants import *

class TestHttpServer(BaseHTTPRequestHandler):
   def forbidden(self):
      request = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode())
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

   def do_POST(self):
      host = self.headers['Host']
      print(self.path)
      if (SERVER_DOMAIN not in host) or (self.path != RPC_PATH):
         self.forbidden()
         return
      # Process request
      request = self.rfile.read(int(self.headers['Content-Length'])).decode()
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


def start():
   HTTPServer(('', 9999), TestHttpServer).serve_forever()
