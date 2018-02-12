from jsonrpcserver import methods

@methods.add
def ping(**kwargs):
   return 'pong'
