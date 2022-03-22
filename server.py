from argparse import ArgumentParser
import socket
from SingleUserProxy import SingleUserProxy

parser = ArgumentParser(description='Echo server.')
parser.add_argument('-a', '--address', help='host ip address', default='localhost')
parser.add_argument('-p', '--port', help='port to listen', default='3000')

args = parser.parse_args()
HOST = args.address
PORT = int(args.port)

TARGET_ADDR = ('localhost', 8080)

hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostSocket.bind((HOST, PORT))
hostSocket.listen(1)
print(f'Listening to {HOST}:{PORT}');

try:
    while True:
        clientSocket, addr = hostSocket.accept()
        print(f'New client: {addr}')
        
        serverSocket = socket.socket()
        serverSocket.connect(TARGET_ADDR)
        proxy = SingleUserProxy((clientSocket, addr), (serverSocket, TARGET_ADDR))
        print(f'Connected {addr} with {TARGET_ADDR}')
        
        proxy.serveForever()
except KeyboardInterrupt:
    pass
