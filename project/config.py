from os.path import exists
from configparser import ConfigParser
from os import urandom


### SECRET KEY

SECRET_KEY_FILE = 'secret_key'

# generate secret key
if exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'r') as f:
        SECRET_KEY = f.readline()
else:
    SECRET_KEY = str(urandom(24))
    with open (SECRET_KEY_FILE, 'w') as f:
        f.write(SECRET_KEY)

### CONFIGS

CONFIG_FILE = 'config.ini'

config = ConfigParser()
config.read(CONFIG_FILE)

HOST = config['NETWORK']['Host']
PORT = int(config['NETWORK']['Port'])

DOCKER_IMAGE = config['DOCKER']['Image']
DOCKER_EXPOSED_PORT = int(config['DOCKER']['Exposed_port'])
DOCKER_NEW_CLIENT_OUTPUT_SUBSTR = config['DOCKER']['New_client_output_substr']
DOCKER_CLIENT_EXITED_OUTPUT_SUBSTR = config['DOCKER']['Client_exited_output_substr']

CLEANER_TIME_INTERVAL_IN_SECONDS = int(config['CLEANER']['Time_interval_in_seconds'])

