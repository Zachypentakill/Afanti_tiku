
import os
import signal

USER_HOME = os.path.expanduser('~')

DEFAULT_CONFIG_FILE = os.path.join(USER_HOME,
                                   '.config',
                                   'achihuo-mini',
                                   'config')

ACHIHUO_MINI_NAMESPACES = 'ACHIHUO_MINI_NAMESPACES'

DEFAULT_CACHE_BACKEND = 'redis'
DEFAULT_QUEUE_BACKEND = 'rabbitmq'


LOCAL_CACHE_DIR = os.path.join(USER_HOME,
                               '.cache',
                               'achihuo_mini')
PIDS = {'master': [], 'slave': []}
KILL_SIGNAL = signal.SIGINT
KILL_TERM = signal.SIGTERM
