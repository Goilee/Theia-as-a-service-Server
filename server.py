import socket
from argparse import ArgumentParser

parser = ArgumentParser(description='Echo server.')

parser.add_argument('-a', '--address', help='host ip address', default='localhost')
parser.add_argument('-p', '--port', help='port to listen', default='3000')

args = parser.parse_args()
HOST = args.address
PORT = int(args.port)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print(f'Listening to {HOST}:{PORT}');

conn, addr = s.accept()
print(f'Connected by {addr}')

while 1:
    data = conn.recv(1024)
    print(f'Recieved data: {data}')
    if not data:
        break
    conn.sendall(data)

conn.close()
