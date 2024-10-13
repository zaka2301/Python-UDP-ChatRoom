import socket
import threading

class Client:
    all_client = []  

    def __init__(self, addr):
        self.addr = addr
        # self.name = name
        Client.all_client.append(self)

    @classmethod
    def check(cls, addr):
        for client in cls.all_client:
            if client.addr == addr:
                return True
        return False

class Server:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.socket.bind((ip, port))
        self.q = MessageQueue()
    
    def receive(self):
        while True:
            message, addr = self.socket.recvfrom(1024)

            if not Client.check(addr):
                Client(addr) 

            self.q.enqueue((message.decode(), addr))

    def get(self):
        return self.q.dequeue()

    def broadcast(self, message, source_addr):
        for client in Client.all_client:
            if client.addr != source_addr: 
                print(f"Broadcasting to {client.addr}")
                self.socket.sendto(message.encode(), client.addr)

    def printLog(self):
        while True:
            while not self.q.empty():
                message, addr = self.get()
                print(f"Received from {addr}: {message}")
                self.broadcast(message, addr)

    def start(self):
        t1 = threading.Thread(target=self.receive)  
        t2 = threading.Thread(target=self.printLog)  
        t1.start()
        t2.start()


class MessageQueue:
    def __init__(self):
        self.content = []
        self.len = 0

    def empty(self):
        return self.len == 0

    def enqueue(self, message):
        self.content.append(message)
        self.len += 1

    def dequeue(self):
        if self.len <= 1:
            pass
        message = self.content[0]
        self.content.pop(0)
        self.len -= 1
        return message

server = Server("localhost", 2301)
server.start()