import socket
import threading
import binascii

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
            if FormatValidator.validate_ip(server_ip):
                print(f"Format IP '{server_ip}' valid.")
                return server_ip
            else:
                print(f"Format IP '{server_ip}' tidak valid. Harap masukkan IP yang benar (IPv4 atau IPv6).")

    @staticmethod
    def get_valid_port():
        while True:
            server_port = input("Masukkan port server: ")
            if FormatValidator.validate_port(server_port):
                print(f"Format port '{server_port}' valid.")
                return int(server_port)
            else:
                print(f"Format port '{server_port}' tidak valid. Port harus berupa angka antara 1 dan 65535.")


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
                self.client.sendto(f"<NAME>{self.name}".encode(), (self.server_ip, self.server_port))
                data, addr = self.client.recvfrom(1024)
                response = data.decode()
                if response == "<NAME_VALID>":
                    break
                elif response == "<NAME_ALREADY_EXIST>":
                    print("Nama sudah dibuat di database, cari nama lain!")
            else:
                print("Format penamaan salah, ulangi input.")

    def send_password(self):
        while True:
            password = input("Pass: ")
            self.client.sendto(f"<PASS>{password}".encode(), (self.server_ip, self.server_port))
            data, addr = self.client.recvfrom(1024)
            response = data.decode()
            if response == "<PASS_VALID>":
                print("Password valid")
                break
            elif response == "<PASS_INVALID>":
                print("Password invalid!")

    def send_message(self):
        while True:
            message = input("")
            checksum = calculate_checksum(message)
            message_with_checksum = f"{message}|{checksum}"
            self.client.sendto(message_with_checksum.encode(), (self.server_ip, self.server_port))

    def receive_message(self):
        while True:
            data, addr = self.client.recvfrom(1024)
            received_message = data.decode()

            try:
                sender_part, message_with_checksum = received_message.split(":", 1)
                sender = sender_part.strip()

                message, received_checksum = message_with_checksum.rsplit("|", 1)
                received_checksum = int(received_checksum)
                calculated_checksum = calculate_checksum(message.strip())

                if received_checksum == calculated_checksum:
                    print(f"{sender}: {message.strip()}")
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
server_ip = FormatValidator.get_valid_ip()
server_port = FormatValidator.get_valid_port()

chat_client = ChatClient(server_ip, server_port)
chat_client.start()
