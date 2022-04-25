from argparse import ArgumentParser
from subprocess import Popen, PIPE
from flask import Flask, Blueprint, render_template, request, session, abort, current_app


parser = ArgumentParser(description='RIDE server.')
parser.add_argument('-a', '--address', dest='HOST', help='host ip address', default='localhost')
parser.add_argument('-p', '--port', dest='PORT', help='port to listen', type=int, default=3000)
parser.add_argument('-d', '--debug', dest='DEBUG', help='run in debug mode', action='store_const', const=True, default=False)
args = parser.parse_args()


# запускает команду в shell и возвращает вывод
def run_cmd(cmd):
    process = Popen(cmd, stdout=PIPE, shell=True)
    return process.communicate()[0].decode('utf-8')


# запускает контейнер RIDE на случайном порту и возвращает кортеж (ip, port)
def run_container():    
    host = args.HOST
    container = run_cmd(f'docker run --ip={host} --detach --publish 3000 ride')[:-1]
    port = int(run_cmd("docker inspect -f '{{ (index (index .NetworkSettings.Ports \"3000/tcp\") 0).HostPort }}' " + container))
    print(f'Started RIDE container (id={container}) on ({host},{port})')
    return (host, port)


main = Blueprint('main', __name__)

@main.route('/')
def index():
    (host, port) = run_container()
    return render_template('loader.html'), { "Refresh": f"10; url=http://{host}:{port}" }


app = Flask(__name__)
app.register_blueprint(main)
app.run(host = args.HOST, port = args.PORT, debug = args.DEBUG)

