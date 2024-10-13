import socket
import threading
class Client:
    all_client = []  

    def __init__(self):
        self.is_passcheck = False

    def addClient(self, addr, name):
        self.addr = addr
        self.name = name
        Client.all_client.append(self)

    def passcheck (self) :
        self.is_passcheck = True
        
    @classmethod
    def checkAddr(cls, addr):
        for client in cls.all_client:
            if client.addr == addr:
                return True
        return False
    
    @classmethod
    def checkName(cls, name):
        for client in cls.all_client:
            if client.name == name:
                return True
        return False
    
    @classmethod
    def getClientByAddr (cls,addr) :
        for client in cls.all_client :
            if client.addr == addr :
                return client
        return None

class Server:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.socket.bind((ip, port))
        self.q = MessageQueue()
        # self.received_sequence = {}
    
    def receive(self):
        password = "123"
        while True:
            message, addr = self.socket.recvfrom(1024)

            if message.decode().startswith("<NAME>"):
                name = message.decode()[message.decode().index(">")+1:]
                if not Client.checkName(name):
                    Client().addClient(addr, name)
                    self.socket.sendto(("<NAME_VALID>").encode(), addr)
                    print(f"{addr} logged in as {name}")
                else:
                    self.socket.sendto(("<NAME_ALREADY_EXIST>").encode(), addr)
                    print(f"{addr} gave invalid name")


            elif message.decode().startswith ("<PASS>"):
                client = Client.getClientByAddr(addr)
                if client and not client.is_passcheck :
                    input_password = message.decode() [message.decode().index (">")+1:]

                    if input_password == password :
                        client.passcheck()
                        self.socket.sendto(("<PASS_VALID>").encode(), addr)
                        print(f"Client {client.name} berhasil masuk ke server")
                    else :
                        self.socket.sendto(("<PASS_INVALID>").encode(),addr)
                        print(f"Client {client.name} tidak berhasil masuk ke server")

            else:
                client = Client.getClientByAddr(addr)
                if client and client.is_passcheck :
                    self.q.enqueue((message.decode(), addr))
                else :
                    self.socket.sendto(("kamu harus memasukan password yang benar terlebih dahulu").encode(), addr)

    def get(self):
        return self.q.dequeue()

    def broadcast(self, message, source_addr):
        for client in Client.all_client:
            if client.addr == source_addr:
                name = client.name
        for client in Client.all_client:
            if client.addr != source_addr: 
                print(f"Broadcasting to {client.addr}")
                self.socket.sendto((name+": "+message).encode(), client.addr)

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
        t1.join()
        t2.join()
        
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
