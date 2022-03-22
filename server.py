from argparse import ArgumentParser
import socket
import select

parser = ArgumentParser(description='Echo server.')
parser.add_argument('-a', '--address', help='host ip address', default='localhost')
parser.add_argument('-p', '--port', help='port to listen', default='3000')

args = parser.parse_args()
HOST = args.address
PORT = int(args.port)

TARGET_PORT = 8080

# Класс-помощник для планирования и выполнения отправки сообщений
class WriteTaskPlanner():
    _writeTasks = {}  # ключ - сокет, значение - массив данных, которые надо отправить
    
    def GetSocketsExpectingWriting(self):
        return self._writeTasks.keys()
    
    def CreateWriteTask(self, socketToWrite, data):
        if self._writeTasks.get(socketToWrite) is None:
            self._writeTasks[socketToWrite] = [data]
        else:
            self._writeTasks[socketToWrite].append(data)
        print(f'Created task: {data}')
    
    def PerformAllTasks(self, socket):
        for data in self._writeTasks[socket]:
            if not data:
                socket.close()
                print('Connection closed')
            else:
                socket.sendall(data)
                print(f'Data sent: {data}')
        self._writeTasks.pop(socket)  # удалим выполненную задачу
        print('Deleted task')

# Создаёт задачу по пересылке сообщения (1024 байта) из fromSocket в toSocket.
# Возвращает true, если соединение ещё не закрыто, иначе false.
def HandleMessage(fromSocket, toSocket, planner):
    clientMessage = fromSocket.recv(1024)
    print(f'Data recieved: {clientMessage}')
    planner.CreateWriteTask(toSocket, clientMessage)
    if not clientMessage:
        return False
    else:
        return True

hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostSocket.bind((HOST, PORT))
hostSocket.listen(1)
print(f'Listening to {HOST}:{PORT}');

planner = WriteTaskPlanner()
interlocutors = {}

try:
    while True:
        clientSocket, addr = hostSocket.accept()
        print(f'New client: {addr}')
        
        serverSocket = socket.socket()
        serverSocket.connect(('localhost', TARGET_PORT))
        interlocutors[clientSocket] = serverSocket
        interlocutors[serverSocket] = clientSocket
        print(f'Connected {addr} with localhost:{TARGET_PORT}')
        
        connAlive = True
        while connAlive:
            readyToRead, readyToWrite, inError = select.select([clientSocket, serverSocket], planner.GetSocketsExpectingWriting(), [], 60)
            for s in readyToWrite:
                planner.PerformAllTasks(s)
            for fromSocket in readyToRead:
                toSocket = interlocutors[fromSocket]
                connAlive = HandleMessage(fromSocket, toSocket, planner)
                if not connAlive:
                    print(f'Connection closed: {addr}')
                    fromSocket.close()
                    interlocutors.pop(fromSocket)
                    interlocutors.pop(toSocket)
except KeyboardInterrupt:
    pass
