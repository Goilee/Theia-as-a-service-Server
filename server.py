from argparse import ArgumentParser
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import time

# запускает команду в shell и возвращает вывод
def run_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return process.communicate()[0].decode('utf-8')

# запускает контейнер RIDE на случайном порту и возвращает кортеж из ID и выделенного порта
def run_RIDE():
    container = run_cmd('docker run -dp 3000 ride')[:-1]
    port = run_cmd("docker inspect -f '{{ (index (index .NetworkSettings.Ports \"3000/tcp\") 0).HostPort }}' " + container)
    print(f'Started RIDE container (id={container}) on port {port}')
    return (container, port)

# возвращает, готов ли контейнер принимает соединения
def is_RIDE_ready(container):
    result = run_cmd(f'docker logs {container} | grep "Theia app listening"')
    return 'Error' not in result and len(result) > 0

class Redirect(BaseHTTPRequestHandler):
    def do_GET(self):
        (container, port) = run_RIDE()
        while not is_RIDE_ready(container):
            time.sleep(0.5)
        self.send_response(302)
        self.send_header('Location', f'http://{HOST}:{port}/')
        self.end_headers()

parser = ArgumentParser(description='RIDE server.')
parser.add_argument('-a', '--address', help='host ip address', default='localhost')
parser.add_argument('-p', '--port', help='port to listen', default='3000')

args = parser.parse_args()
HOST = args.address
PORT = int(args.port)

server = HTTPServer((HOST, PORT), Redirect)
print(f'Listening on {HOST}:{PORT}...')
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Stopping the server...")
    server.server_close()
