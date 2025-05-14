from os.path import exists
from configparser import ConfigParser
from os import urandom

# Генерация секретного ключа
SECRET_KEY_FILE = 'secret_key'

if exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'r') as f:
        SECRET_KEY = f.readline().strip()  # Убираем лишние пробелы и переводы строк
else:
    SECRET_KEY = str(urandom(24))
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(SECRET_KEY)

# Читаем остальные параметры из config.ini
CONFIG_FILE = 'config.ini'

config = ConfigParser()
config.read(CONFIG_FILE)

HOST = config['NETWORK']['host']
PORT = int(config['NETWORK']['port'])
MIN_PORT = int(config['NETWORK']['min_port'])
MAX_PORT = int(config['NETWORK']['max_port'])
GUEST_PORT = int(config['NETWORK']['guest_port'])

DOCKER_IMAGE = config['DOCKER']['image']
DOCKER_EXPOSED_PORT = int(config['DOCKER']['exposed_port'])
DOCKER_NEW_CLIENT_OUTPUT_SUBSTR = config['DOCKER']['new_client_output_substr']
DOCKER_CLIENT_EXITED_OUTPUT_SUBSTR = config['DOCKER']['client_exited_output_substr']
DOCKER_WAIT_TIME_IN_SECONDS = int(config['DOCKER']['wait_time_in_seconds'])

CLEANER_TIME_INTERVAL_IN_SECONDS = int(config['CLEANER']['time_interval_in_seconds'])

CLIENT_SECRET_FILE = config['SECURITY']['client_secret_file']
