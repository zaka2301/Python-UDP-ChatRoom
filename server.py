import socket
import threading
import binascii
import pandas as pd
from datetime import datetime
from RC4 import RC4_

key = "ServerKey"
S_RC4 = RC4_(key)

def calculate_checksum(message):
    return binascii.crc32(message.encode()) & 0xffffffff  # Pastikan hasil CRC32 positif

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
            message, addr = self.checkCheckSum(message, addr)
            if message != "invalid":
                message = S_RC4.decrypt(message)
            
            # Tangani kondisi jika client ingin keluar
            if message.startswith("<EXIT>") and message != "invalid":
                client = Client.getClientByAddr(addr)
                if client:
                    print(f"{client.name} telah keluar.")
                    Client.all_client.remove(client)  
                break  
                
            if message.startswith("<NAME>") and message != "invalid":
                name = message[message.index(">") + 1:]
                if not Client.checkName(name):
                    Client().addClient(addr, name)
                    self.socket.sendto((S_RC4.encrypt("<NAME_VALID>")).encode(), addr)
                    print(f"{addr} logged in as {name}")
                else:
                    self.socket.sendto((S_RC4.encrypt("<NAME_ALREADY_EXIST>")).encode(), addr)
                    print(f"{addr} gave invalid name")

            elif message.startswith("<PASS>") and message != "invalid":
                client = Client.getClientByAddr(addr)
                if client and not client.is_passcheck:
                    input_password = message[message.index(">") + 1:]

                    if input_password == password:
                        client.passcheck()
                        self.socket.sendto((S_RC4.encrypt("<PASS_VALID>")).encode(), addr)
                        print(f"Client {client.name} berhasil masuk ke server")
                    else:
                        self.socket.sendto((S_RC4.encrypt("<PASS_INVALID>")).encode(), addr)
                        print(f"Client {client.name} tidak berhasil masuk ke server")

            elif message != "invalid":
                self.q.enqueue((message, addr))

    
    def checkCheckSum(self, message, addr):
        client = Client.getClientByAddr(addr)
        try:
            message, received_checksum = message.decode(errors="ignore").rsplit("|", 1)
            received_checksum = int(received_checksum)
            calculated_checksum = calculate_checksum(message)

            if received_checksum == calculated_checksum:
                print(f"checksum valid ({received_checksum},{calculated_checksum})")
                return (message, addr)
            else:
                self.socket.sendto("Checksum gagal, pesan gagal".encode(), addr)
                print(f"checksum failed, checksum error {message}")
                return "invalid", False
        except ValueError: 
            self.socket.sendto("Format pesan tidak valid, checksum tidak ditemukan".encode(), addr)
            print(f"checksum failed, format error {message}")
            return "invalid", False


    def get(self):
        return self.q.dequeue()

    def broadcast(self, message, source_addr):
        for client in Client.all_client:
            if client.addr == source_addr:
                name = client.name
        for client in Client.all_client:
            if client.addr != source_addr: 
                print(f"Broadcasting to {client.addr}")
                checksum = calculate_checksum(message)
                message_with_checksum = f"{name}: {message}|{checksum}"
                self.socket.sendto(message_with_checksum.encode(), client.addr)

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

server = Server("localhost", 23010)
server.start()