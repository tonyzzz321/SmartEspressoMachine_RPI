# general program constants
UNAME = 'chip' # 'chip' or 'pi'
PROGRAM_NAME = 'SEM'
PROGRAM_PATH = '/home/%s/SEM_RPI' % UNAME
LOG_FILE_PATH = PROGRAM_PATH + '/%s.log' % PROGRAM_NAME

# scheduler constants
SCHEDULER_DATABASE_PATH = PROGRAM_PATH + '/%s_schedule.json' % PROGRAM_NAME

# json rpc server constants
SERVER_DOMAIN = 'sem.pezhang.xyz'
SERVER_BIND_IP = ''  # '' for all interface, '127.0.0.1' for localhost
SERVER_PORT = 9999
RPC_PATH = '/jsonrpc'

SSL_CERT = ''
SSL_KEY = ''

# machine constants
WATER_THRESHOLD = 12


# def sign(rpc_call, param_dict, ts, app_key):
#    params = param_dict
#    params['rpc_call'] = rpc_call
#    params['ts'] = ts

#    data = ""
#    keys = list(params.keys())
#    keys.sort()
#    for key in keys:
#       data += "" if (data == "") else "&"
#       value = params[key]
#       if type(value) == int:
#          value = str(value)
#       data += key + "=" + str(urllib.parse.quote(value))
#    h = hashlib.sha256()
#    h.update((data + app_key).encode())
#    return h.hexdigest()
#    

