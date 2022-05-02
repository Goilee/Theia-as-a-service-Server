import os

from project import app
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from project.docker_manager import *

# TODO: включить когда будет готово

# SETTINGS_FILE = 'config.ini'
#
# parser = ArgumentParser(description=f'Docker application server. Look for parameters in the {SETTINGS_FILE}.')
# parser.add_argument('-d', '--debug', help='run in debug mode', action='store_const', const=True, default=False)
# args = parser.parse_args()
#
# config = ConfigParser()
# config.read(SETTINGS_FILE)


INTERVAL_IN_SECONDS = 300
scheduler = BlockingScheduler()
scheduler.add_job(clean_containers, 'interval', seconds=INTERVAL_IN_SECONDS)
cleaner_thread = Thread(target=scheduler.start, args=())
cleaner_thread.start()

with app.app_context():
    try:
        app.run(host='127.0.0.1', port='5000', debug=True)
    finally:
        clean_containers(True)
        os._exit(0)
