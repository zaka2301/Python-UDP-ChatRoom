import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.bind(('localhost', 0)) # ini port 0 katanya bisa bikin nyuruh OS milih port mana aja yang tersedia

def send_name():
    global name 
    while True:
        name = input("Name: ")
        client.sendto(f"<NAME>{name}".encode(), ("localhost", 2301))
        data, addr = client.recvfrom(1024)
        if data.decode() == "<NAME_VALID>":
            break
        elif data.decode() == "<NAME_ALREADY_EXIST>":
            print(data.decode())

def send_message():
    global name
    while True:
        message = input("")
        print(f"\033[1A\033[K{name}: {message}")
        client.sendto(f"{message}".encode(), ("localhost", 2301))  # Kirim pesan ke server

def receive_message():
    while True:
        data, addr = client.recvfrom(1024)
        print(f"{data.decode()}") # server ngirim balik

t0 = threading.Thread(target=send_name)
t0.start()
t0.join()

t1 = threading.Thread(target=send_message)
t2 = threading.Thread(target=receive_message)

t1.start()
t2.start()

t1.join()
t2.join()
