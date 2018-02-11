from jsonrpcserver import methods
# pip install jsonrpcserver

@methods.add
def ping(**kwargs):
   return 'pong'
