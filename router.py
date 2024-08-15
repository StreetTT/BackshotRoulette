import socket
import threading
from BR import BR
from string import ascii_uppercase
from random import choices

games: dict[str, BR] = {"ABCD": BR()}
clients: dict[str, str] = {}
HEADDER = 1024
FORMAT = "utf-8"
DISCONNECTMSG = "!DISSCON"
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))

def addrStr(addr):
    return f"{addr[0]}::{str(addr[1])}"

def handleClient(conn, addr):
    connected = False
    i = 0
    keys = list(games.keys())
    while not connected and i < len(keys):
        code = keys[i]
        connected = games[code].Connect(addrStr(addr))
        i += 1
    if not connected:
        while not connected:
            code = str(choices(ascii_uppercase, k=4)) 
            if not code in games:
                games[code] = BR()
                connected = games[code].Connect(addrStr(addr))
            
    clients[addrStr(addr)] = code
    games[code].GetPlayer()._SetName()

    print(f"NEW CONNECTION: {addrStr(addr)}")

    while connected:
        msgLength = conn.recv(HEADDER).decode(FORMAT)
        if msgLength:
            msg = conn.recv(int(msgLength)).decode(FORMAT)
            if msg == DISCONNECTMSG:
                connected = False
            print(f"[{addr}] {msg}")
    conn.close()

def start():
    print("Server is Starting...")
    server.listen()
    print(f"Listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handleClient, args=(conn, addr)).start()
        print(clients)

if __name__ == "__main__":
    start()