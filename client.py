import socket
import threading


class ChatClient :
    def __init__ (self,server_ip,server_port) :
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.bind(('localhost', 0))
        self.name = None

    def send_name(self):
        while True:
            self.name = input("Name: ")
            self.client.sendto(f"<NAME>{self.name}".encode(), (self.server_ip, self.server_port))
            data, addr = self.client.recvfrom(1024)
            response = data.decode()
            if response == "<NAME_VALID>":
                break
            elif response == "<NAME_ALREADY_EXIST>":
                print("Nama sudah dibuat di database, cari nama lain !")

    def send_password (self) :
        while True :
            password = input("Pass: ")
            self.client.sendto(f"<PASS>{password}".encode(), (self.server_ip, self.server_port))
            data, addr = self.client.recvfrom(1024)
            response = data.decode()
            if response == "<PASS_VALID>" :
                print("Password valid")
                break
            elif response == "<PASS_INVALID>" :
                print("Password invalid !")


    def send_message(self):
        while True:
            message = input("")
            # print(f"\033[1A\033[K{self.name}: {message}")
            self.client.sendto(f"{message}".encode(), (self.server_ip, self.server_port))  # Kirim pesan ke server

    def receive_message(self):
        while True:
            data, addr =self.client.recvfrom(1024)
            print(f"{data.decode()}") # server ngirim balik

    def start (self) :
        t0 = threading.Thread(target=self.send_name)
        t0.start()
        t0.join()

        t1 = threading.Thread(target=self.send_password)
        t1.start()
        t1.join()

        t2 = threading.Thread(target=self.send_message)
        t3 = threading.Thread(target=self.receive_message)

        t2.start()
        t3.start()

        t2.join()
        t3.join()


server_ip  = input("Masukkan IP server: ")
server_port = int(input("Masukkan port server: "))

chat_client = ChatClient(server_ip,server_port)

chat_client.start()