#import socket
from queue import Queue, Empty
from select import select

class SingleUserProxy:
    def __init__(self, conn1, conn2):
        self._socket1 = conn1[0]
        self._socket2 = conn2[0]
        
        self._addresses = {}
        self._addresses[self._socket1] = conn1[1]
        self._addresses[self._socket2] = conn2[1]
        
        self._dataToSend = {}
        self._dataToSend[self._socket1] = Queue()
        self._dataToSend[self._socket2] = Queue()
        
        self._socketsToRead = [ self._socket1, self._socket2 ]
        self._socketsToWrite = [ self._socket1, self._socket2 ]
    
    def _closeConnection(self, socket):
        if not (socket is self._socket1 or socket is self._socket2):
            raise ValueError("Incorrect socket value")
        
        socket.close()
        self._socketsToRead.clear()
        self._socketsToWrite.remove(socket)
        
        print(f'Closed connection with {self._addresses[socket]}')
        if not self._socketsToWrite:
            return False
        else:
            return True
    
    def _handleMessage(self, fromSocket, toSocket):
        if not (fromSocket is self._socket1 and toSocket is self._socket2 or fromSocket is self._socket2 and toSocket is self._socket1):
            raise ValueError("Incorrect sockets' values")
        
        message = fromSocket.recv(1024)
        self._dataToSend[toSocket].put(message)
        
        print(f'Message recieved from {self._addresses[fromSocket]}: {len(message)}')
        if not message:
            return False
        else:
            return True
    
    def _sendMessageFromQueue(self, toSocket):
        if not (toSocket is self._socket1 or toSocket is self._socket2):
            raise ValueError("Incorrect socket value")
        
        try:
            message = self._dataToSend[toSocket].get(block=False)
            print(f'Message sent to {self._addresses[toSocket]}: {len(message)}')
            if not message:
                return self._closeConnection(toSocket)
            else:
                toSocket.sendall(message)
                return True
        except Empty:
            return True
    
    def serveForever(self):
        socket1Alive = True
        socket2Alive = True
        while socket1Alive or socket2Alive:
            readyToRead, readyToWrite, inError = select(self._socketsToRead, self._socketsToWrite, [], 60)
            
            for toSocket in readyToWrite:
                keepWorking = self._sendMessageFromQueue(toSocket)
                if not keepWorking:
                    return
            
            for fromSocket in readyToRead:
                if fromSocket is self._socket1:
                    connAlive = self._handleMessage(self._socket1, self._socket2)
                else:
                    connAlive = self._handleMessage(self._socket2, self._socket1)
                if not connAlive:
                    keepWorking = self._closeConnection(fromSocket)
                    if not keepWorking:
                        return
