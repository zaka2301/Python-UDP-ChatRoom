import socket
import threading

'''
class Client:
    all_client = []
    def __init__(self, addr, name):
        self.addr = addr
        self.name = name
        Client.all_client.append(addr)
    
    @classmethod
    def check(cls, addr):
        return (addr not in all_client)
'''

        

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
            self.q.enqueue((message, addr))

    def get(self):
        return self.q.dequeue()

    def printLog(self):
        while True:
            while not self.q.empty():
                tup = self.get()
                message = tup[0].decode()
                addr = tup[1]
                print(f"{addr}:{message}")
            
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



