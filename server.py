from argparse import ArgumentParser
import socket
import subprocess
from SingleUserProxy import SingleUserProxy
import time

parser = ArgumentParser(description='Echo server.')
parser.add_argument('-a', '--address', help='host ip address', default='localhost')
parser.add_argument('-p', '--port', help='port to listen', default='3000')

args = parser.parse_args()
HOST = args.address
PORT = int(args.port)

hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostSocket.bind((HOST, PORT))
hostSocket.listen(1)
print(f'Listening to {HOST}:{PORT}');

try:
    while True:
        clientSocket, addr = hostSocket.accept()
        print(f'New client: {addr}')
        
        process = subprocess.Popen(['sh', 'runProcess.sh'], stdout=subprocess.PIPE)
        stdout = process.communicate()[0].decode('utf-8').splitlines()
        processAddr = ('localhost', int(stdout[0]))
        processId = stdout[1]
        print(f'Started process (id={processId}) on {processAddr}')
        
        time.sleep(5)
        
        serverSocket = socket.socket()
        serverSocket.connect(processAddr)
        proxy = SingleUserProxy((clientSocket, addr), (serverSocket, processAddr))
        print(f'Connected {addr} with {processAddr}')
        
        proxy.serveForever()
        
        subprocess.Popen(['sh', 'stopProcess.sh', processId], stdout=subprocess.PIPE)
        print(f'Stopped process (id={processId}) on {processAddr}')
except KeyboardInterrupt:
    pass
