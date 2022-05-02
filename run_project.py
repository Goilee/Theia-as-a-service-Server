from argparse import ArgumentParser
from configparser import ConfigParser
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from os import _exit

from project import app
from project.docker_manager import *

SETTINGS_FILE = 'config.ini'

parser = ArgumentParser(description=f'Docker application server. Look for parameters in the {SETTINGS_FILE}.')
parser.add_argument('-d', '--debug', help='run in debug mode', action='store_const', const=True, default=False)
args = parser.parse_args()

config = ConfigParser()
config.read(SETTINGS_FILE)

scheduler = BlockingScheduler()
scheduler.add_job(clean_containers, 'interval', seconds=int(config['CLEANER']['Time_interval_in_seconds']))
cleaner_thread = Thread(target=scheduler.start, args=())
cleaner_thread.start()

with app.app_context():
    try:
        app.run(host=config['NETWORK']['Host'], port=config['NETWORK']['Port'], debug=args.debug)
    except Exception as e:
        print(e)
    finally:
        clean_containers(True)
        _exit(0)

