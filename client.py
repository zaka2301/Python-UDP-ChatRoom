import socket
import threading

server_ip = input("Masukkan IP server: ")
server_port = int(input("Masukkan port server: "))

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.bind(('localhost', 0)) # ini port 0 katanya bisa bikin nyuruh OS milih port mana aja yang tersedia


def send_name():
    global name 
    while True:
        name = input("Name: ")
        client.sendto(f"<NAME>{name}".encode(), (server_ip, server_port))
        data, addr = client.recvfrom(1024)
        if data.decode() == "<NAME_VALID>":
            break
        elif data.decode() == "<NAME_ALREADY_EXIST>":
            print(data.decode())

def send_password () :
    global name
    while True :
        password = input("Pass: ")
        client.sendto(f"<PASS>{password}".encode(), (server_ip, server_port))
        data, addr = client.recvfrom(1024)
        if data.decode() == "<PASS_VALID>" :
            print("Password valid")
            break
        elif data.decode() == "<PASS_INVALID>" :
            print("Password invalid !")


def send_message():
    global name
    while True:
        message = input("")
        print(f"\033[1A\033[K{name}: {message}")
        # seq_msg = f"<SEQ> {seq_number}:{message}"
        # send_with_ack (seq_msg)
        # sequence_number +=1
        client.sendto(f"{message}".encode(), (server_ip, server_port))  # Kirim pesan ke server

# def send_with_ack (message) :
#     global seq_number
#     client.settimeout(timeout)
#     while True :
#         client.sendto(message.encode(), (server_ip,server_port))
#         try :
#             ack,addr = client.recvfrom(1024)
#             if ack.decode().startwith(f"<ACK>{seq_number}") :
#                 print(f"ACK diterima untuk sequence : {seq_number}")
#                 break
#         except socket.timeout :
#             print(f"kirim ulang pesan : {message}")


def receive_message():
    while True:
        data, addr = client.recvfrom(1024)
        print(f"{data.decode()}") # server ngirim balik

t0 = threading.Thread(target=send_name)
t0.start()
t0.join()

t1 = threading.Thread(target=send_password)
t1.start()
t1.join()

t2 = threading.Thread(target=send_message)
t3 = threading.Thread(target=receive_message)

t2.start()
t3.start()

t2.join()
t3.join()
