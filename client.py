import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.bind(('localhost', 0)) # ini port 0 katanya bisa bikin nyuruh OS milih port mana aja yang tersedia


def send_message():
    while True:
        message = input("")
        client.sendto(f"{message}".encode(), ("localhost", 2301))  # Kirim pesan ke server

def receive_message():
    while True:
        data, addr = client.recvfrom(1024) 
        print(f"Received from {addr}: {data.decode()}") # server ngirim balik

t1 = threading.Thread(target=send_message)
t2 = threading.Thread(target=receive_message)

t1.start()
t2.start()

t1.join()
t2.join()
