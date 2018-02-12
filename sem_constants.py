# general program constants
UNAME = 'chip' # 'chip' or 'pi'
PROGRAM_NAME = 'SEM'
PROGRAM_PATH = '/home/%s/SEM_RPI' % UNAME
LOG_FILE_PATH = PROGRAM_PATH + '/%s.log' % PROGRAM_NAME

# scheduler constants
SCHEDULER_DATABASE_PATH = PROGRAM_PATH + '/%s_schedule.json' % PROGRAM_NAME

# json rpc server constants
SERVER_DOMAIN = 'sem.pezhang.xyz'
RPC_PATH = '/jsonrpc'

SSL_CERT = ''
SSL_KEY = ''
