# general program constants
UNAME = 'pi' # 'chip' or 'pi'
PROGRAM_NAME = 'SEM'
PROGRAM_PATH = '/home/%s/SEM_RPI' % UNAME
LOG_FILE_PATH = PROGRAM_PATH + '/%s.log' % PROGRAM_NAME

# scheduler constants
SCHEDULER_DATABASE_PATH = PROGRAM_PATH + '/%s_schedule.json' % PROGRAM_NAME

# json rpc server constants
# SERVER_DOMAIN = 'sem.pezhang.xyz' # not checking for now
SERVER_BIND_IP = ''  # '' for all interface, '127.0.0.1' for localhost
SERVER_PORT = 9999
RPC_PATH = '/jsonrpc'

# SSL is not enabled for now
# SSL_CERT = '/home/%s/letsencrypt/cert.pem' % UNAME
# SSL_KEY = '/home/%s/letsencrypt/key.pem' % UNAME

# machine constants
WATER_THRESHOLD = 10
CUP_DISTANCE_THRESHOLD = 5
MAX_WATER_DISTANCE = 100
# GPIO_MODE = GPIO.BOARD
GPIO_DICT = {
   'ESPRESSO':    {'pin': 16, 'mode': 'out'},
   'CAPPUCCINO':  {'pin': 18, 'mode': 'out'},
   'LATTE':       {'pin': 22, 'mode': 'out'},
   'CUP_SNS_CS':  {'pin': 13, 'mode': 'out'},
   'WTR_SNS_CS':  {'pin': 15, 'mode': 'out'}
}

# notifier constants
FCM_CLIENT_TOKEN_PATH = PROGRAM_PATH + '/%s_fcm_client_tokens.json' % PROGRAM_NAME
FCM_SERVICE_ACCOUNT_PRIV_KEY = 'service-account.json'
FCM_API_LINK = 'https://fcm.googleapis.com/v1/projects/fir-messaging-319b2/messages:send'

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

