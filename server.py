from sys import stderr
from argparse import ArgumentParser
from configparser import ConfigParser
from subprocess import Popen, PIPE
from flask import Flask, Blueprint, render_template
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from os import _exit


SETTINGS_FILE = 'config.ini'

parser = ArgumentParser(description=f'Docker application server. Look for parameters in the {SETTINGS_FILE}.')
parser.add_argument('-d', '--debug', help='run in debug mode', action='store_const', const=True, default=False)
args = parser.parse_args()

config = ConfigParser()
config.read(SETTINGS_FILE)


# запускает команду в shell и возвращает вывод
def run_cmd(cmd):
    process = Popen(cmd, stdout=PIPE, shell=True)
    return process.communicate()[0].decode('utf-8')


# запускает контейнер на случайном порту и возвращает кортеж (ip, port)
def run_container():
    host = config['NETWORK']['Host']
    image = config['DOCKER']['Image']
    exposed_port = config['DOCKER']['Exposed_port']
    container = run_cmd(f'docker run --ip={host} --detach --publish {exposed_port} {image}')[:-1]
    port = int(run_cmd("docker inspect -f '{{ (index (index .NetworkSettings.Ports \"3000/tcp\") 0).HostPort }}' " + container))
    print(f'Started container (id={container}) on ({host},{port})')
    return (host, port)


# удаляет контейнер и возвращает вывод команды
def force_remove_container(container):
    result = run_cmd(f'docker rm -f {container}')[:-1]
    print(f'Force removed: {result}')
    return result


# возвращает номер последней строки, содержащей подстроку line (-1 при отсутствии)
def find_last_line_in_logs(container, substr):
    result = run_cmd(f'docker logs {container} 2>&1 | grep -n "{substr}" | tail --lines=1')
    try:
        lineNumber = int(result[0:result.index(':')])
        return lineNumber
    except ValueError:
        return -1


# возвращает список айднишников запущенных контейнеров
def get_running_containers():
    image = config['DOCKER']['Image']
    result = run_cmd(f'docker ps -q --filter "ancestor={image}"')
    return result.splitlines()


# удаляет запущенные контейнеры, из которых вышел юзер (или все, если параметр True)
def clean_containers(cleanAll = False):
    for container in get_running_containers():
        clientEnter = find_last_line_in_logs(container, config['DOCKER']['New_client_output_substr'])
        clientExit = find_last_line_in_logs(container, config['DOCKER']['Client_exited_output_substr'])
        print (f'Container {container}: entered {clientEnter}, exited {clientExit}')
        if clientExit > clientEnter or cleanAll:
            force_remove_container(container)


main = Blueprint('main', __name__)

@main.route('/')
def index():
    (host, port) = run_container()
    return render_template('loader.html'), { "Refresh": f"10; url=http://{host}:{port}" }


scheduler = BlockingScheduler()
scheduler.add_job(clean_containers, 'interval', seconds=int(config['CLEANER']['Time_interval_in_seconds']))
cleaner_thread = Thread(target=scheduler.start, args=())
cleaner_thread.start()

try:
    app = Flask(__name__)
    app.register_blueprint(main)
    network = config['NETWORK']
    app.run(host = network['Host'], port = network['Port'], debug = args.debug)
except Exception as e:
    print(e, file = stderr)
finally:
    print('Clean all containers...')
    clean_containers(True)
    _exit(0)

