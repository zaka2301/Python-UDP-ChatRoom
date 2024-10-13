import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    message = input("")
    client.sendto(f"{message}".encode(), ("localhost", 2301))
