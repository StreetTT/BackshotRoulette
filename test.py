import socket

HEADDER = 1024
FORMAT = "utf-8"
DISCONNECTMSG = "!DISSCON"
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((SERVER, PORT))

def send(msg):
    msg = msg.encode(FORMAT)
    msgLength = str(len(msg)).encode(FORMAT)
    msgLength += b" " * (HEADDER - len(msgLength))
    client.send(msgLength)
    client.send(msg)

connected = True
while connected:
    msg = input()
    send(msg)
    if msg == DISCONNECTMSG:
        connected = False