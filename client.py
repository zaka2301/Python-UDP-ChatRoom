import socket
import threading
import binascii
import pandas as pd
from datetime import datetime
from RC4 import RC4_

key = "RC4Key"
S_key = "ServerKey"
C_RC4 = RC4_(key)
S_RC4 = RC4_(S_key)


def save_message_to_csv(sender, message, timestamp):
    new_message = pd.DataFrame({
        'timestamp': [timestamp],
        'sender': [sender],
        'message': [message]
    })

    try:
        new_message.to_csv('chat_history.csv', mode='a', header=False, index=False)
    except FileNotFoundError:
        new_message.to_csv('chat_history.csv', mode='w', header=True, index=False)

class FormatValidator:
    @staticmethod
    def validate_ip(ip):
        try:
            socket.inet_pton(socket.AF_INET, ip)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
                return True
            except socket.error:
                return False

    @staticmethod
    def validate_port(port):
        return port.isdigit() and 1 <= int(port) <= 65535

    @staticmethod
    def get_valid_ip():
        while True:
            server_ip = input("Masukkan IP server: ")
            if server_ip == "1":
                return "127.0.0.1"
            if FormatValidator.validate_ip(server_ip):
                #print(f"Format IP '{server_ip}' valid.")
                return server_ip
            else:
                print(f"Format IP '{server_ip}' tidak valid. Harap masukkan IP yang benar (IPv4 atau IPv6).")

    @staticmethod
    def get_valid_port():
        while True:
            server_port = input("Masukkan port server: ")
            if FormatValidator.validate_port(server_port):
                #print(f"Format port '{server_port}' valid.")
                return int(server_port)
            else:
                print(f"Format port '{server_port}' tidak valid. Port harus berupa angka antara 1 dan 65535.")

    @staticmethod
    def is_ip_port_open(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = S_RC4.encrypt("<<CHECK>>")
        checksum = calculate_checksum(message)
        s.sendto(f"{message}|{checksum}".encode(), (ip, port))
        s.settimeout(1)
        try:
            data, addr = s.recvfrom(1024)
            s.close()
            print(f"{ip}:{port} is open")
            return True
        except ConnectionResetError:
            s.close()
            print(f"{ip}:{port} is closed")
            return False
        except socket.timeout:
            s.close()
            print(f"{ip}:{port} is closed")
            return False
        


def calculate_checksum(message):
    return binascii.crc32(message.encode()) & 0xffffffff  # Pastikan hasil CRC32 positif


class ChatClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.name = None

    def send_name(self):
        while True:
            self.name = input("Name: ")
            if self.name != "<NAME>" and isinstance(self.name, str):
                encrypted = S_RC4.encrypt("<NAME>"+self.name)
                checksum = calculate_checksum(encrypted)
                self.client.sendto(f"{encrypted}|{checksum}".encode(), (self.server_ip, self.server_port))
                data, addr = self.client.recvfrom(1024)
                response = S_RC4.decrypt(data.decode())
                if response == "<NAME_VALID>":
                    break
                elif response == "<NAME_ALREADY_EXIST>":
                    print("Nama sudah dibuat di database, cari nama lain!")
            else:
                print("Format penamaan salah, ulangi input.")

    def send_password(self):
        while True:
            password = input("Pass: ")
            encrypted = S_RC4.encrypt("<PASS>"+password)
            checksum = calculate_checksum(encrypted)
            self.client.sendto(f"{encrypted}|{checksum}".encode(), (self.server_ip, self.server_port))
            data, addr = self.client.recvfrom(1024)
            response = S_RC4.decrypt(data.decode())
            if response == "<PASS_VALID>":
                print("Password valid")
                break
            elif response == "<PASS_INVALID>":
                print("Password invalid!")

    def send_message(self):
        while True:
            message = input("")
            if message.lower() == "exit":
                self.client.sendto(f"<EXIT>".encode(), (self.server_ip, self.server_port))
                print("menutup koneksi.")
                break

            print(f"\033[1A\033[K{self.name}: {message}")
            encrypted_message = C_RC4.encrypt(message)
            encrypted_message = S_RC4.encrypt(encrypted_message)
            checksum = calculate_checksum(encrypted_message)
            message_with_checksum = f"{encrypted_message}|{checksum}"
            self.client.sendto(message_with_checksum.encode(), (self.server_ip, self.server_port))

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_message_to_csv(self.name, message, timestamp)

    def receive_message(self):
        while True:
            data, addr = self.client.recvfrom(1024)
            received_message = data.decode(errors="ignore")

            try:
                sender_part, message_with_checksum = received_message.split(":", 1)
                sender = sender_part.strip()

                message, received_checksum = message_with_checksum.rsplit("|", 1)
                received_checksum = int(received_checksum)
                calculated_checksum = calculate_checksum(message.strip())

                if received_checksum == calculated_checksum:
                    print(f"{sender}: {C_RC4.decrypt(message.strip())}")
                    decrypted_message = C_RC4.decrypt(message)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    save_message_to_csv(sender, decrypted_message, timestamp)  # Save the message

                else:
                    print("Pesan gagal, checksum tidak valid.")
            except ValueError:
                print("Pesan tidak memiliki format yang benar, tidak ada checksum.")

    def start(self):
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


# Dapatkan input server IP dan port yang valid menggunakan class FormatValidator
IP = socket.gethostbyname(socket.gethostname())
is_open = False
while not is_open:
    server_ip = FormatValidator.get_valid_ip()
    server_port = FormatValidator.get_valid_port()
    is_open = FormatValidator.is_ip_port_open(server_ip, server_port)
chat_client = ChatClient(server_ip, server_port)
chat_client.start() 