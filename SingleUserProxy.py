#import socket
from queue import Queue, Empty
from select import select
import socket

class SingleUserProxy:
    PACKET_SIZE = 1024

    def __init__(self, clientConn, serverConn):
        self._clientSock = clientConn[0]
        self._serverSock = serverConn[0]
        
        self._addresses = {}
        self._addresses[self._clientSock] = clientConn[1]
        self._addresses[self._serverSock] = serverConn[1]
        
        self._dataToSend = {}
        self._dataToSend[self._clientSock] = Queue()
        self._dataToSend[self._serverSock] = Queue()
        
        self._socketsToRead = [ self._clientSock, self._serverSock ]
        self._socketsToWrite = [ self._clientSock, self._serverSock ]
    
    def _closeConnection(self):
        self._clientSock.close()
        self._serverSock.close()
        print(f'Closed connection with {self._addresses[self._clientSock]}')
    
    def _handleMessage(self, fromSocket):
        if not (fromSocket is self._clientSock or fromSocket is self._serverSock):
            raise ValueError("Incorrect socket value")
        
        toSocket = self._serverSock if fromSocket is self._clientSock else self._clientSock
        
        message = b''
        try:
            chunk = b'1'  # чтобы цикл выполнился минимум один раз
            while chunk:
                chunk = fromSocket.recv(self.PACKET_SIZE)
                message += chunk
        except BlockingIOError:
            pass
        print(f'Message recieved from {self._addresses[fromSocket]}: {len(message)}')
        connClosed = not message
        if not connClosed and toSocket in self._dataToSend.keys():
            self._dataToSend[toSocket].put(message)
        return not connClosed
    
    def _sendMessageFromQueue(self, toSocket):
        if not (toSocket is self._clientSock or toSocket is self._serverSock):
            raise ValueError("Incorrect socket value")
        
        try:
            message = self._dataToSend[toSocket].get(block=False)
            toSocket.sendall(message)
            print(f'Message sent to {self._addresses[toSocket]}: {len(message)}')
        except Empty:
            print(f'Tried to send to {self._addresses[toSocket]}, but no message queued')
    
    def _serverReconnect(self):
        addr = self._addresses.pop(self._serverSock)
        dataToSend = self._dataToSend.pop(self._serverSock)
        self._socketsToRead.remove(self._serverSock)
        self._socketsToWrite.remove(self._serverSock)
        
        self._serverSock.close()
        self._serverSock = socket.socket()
        self._serverSock.connect(addr)
        print(f'Reconnected to {addr}')
        
        self._addresses[self._serverSock] = addr
        self._dataToSend[self._serverSock] = dataToSend
        self._socketsToRead.append(self._serverSock)
        self._socketsToWrite.append(self._serverSock)
    
    def serveForever(self):
        self._clientSock.setblocking(False)
        self._serverSock.setblocking(False)
        while True:
            print('Waiting to read...')
            readyToRead, readyToWrite, inError = select(self._socketsToRead, [], [], 5)
            print(f'{len(readyToRead)} ready to read')
            
            for fromSocket in readyToRead:
                connAlive = self._handleMessage(fromSocket)
                if not connAlive:
                    if fromSocket is self._clientSock:
                        self._closeConnection()
                        return
                    else:
                        self._serverReconnect()
            
            socketsToWrite = list(filter(lambda s: not self._dataToSend[s].empty(), self._socketsToWrite))
            if len(socketsToWrite) > 0:
                print('Waiting to write...')
                readyToRead, readyToWrite, inError = select([], socketsToWrite, [], 5)
                print(f'{len(readyToWrite)} ready to write')
            
                for toSocket in readyToWrite:
                    if toSocket:
                        self._sendMessageFromQueue(toSocket)
