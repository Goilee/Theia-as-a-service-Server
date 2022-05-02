from configparser import ConfigParser
from os import urandom


CONFIG_FILE = 'config.ini'

config = ConfigParser()
config.read(CONFIG_FILE)

### CONFIGS

HOST = config['NETWORK']['Host']
PORT = int(config['NETWORK']['Port'])

DOCKER_IMAGE = config['DOCKER']['Image']
DOCKER_EXPOSED_PORT = int(config['DOCKER']['Exposed_port'])
DOCKER_NEW_CLIENT_OUTPUT_SUBSTR = config['DOCKER']['New_client_output_substr']
DOCKER_CLIENT_EXITED_OUTPUT_SUBSTR = config['DOCKER']['Client_exited_output_substr']

CLEANER_TIME_INTERVAL_IN_SECONDS = int(config['CLEANER']['Time_interval_in_seconds'])

###

