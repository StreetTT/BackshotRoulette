import socket
from string import ascii_uppercase
from random import choices
from typing import Callable
import threading

import sys


HEADER = 1024
FORMAT = "utf-8"
DISCONNECTMSG = "!DISCONNECT"
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())


class Router():
    def __init__(self) -> None:
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((SERVER, PORT))
        self.__games: dict[str, SocketBR] = {"ABCD": SocketBR()}
        self.__clients: dict[str, str] = {}
        self.__lock = threading.Lock()
    
    def Start(self):
        print("Server is Starting...")
        self.__server.listen()
        print(f"Listening on {SERVER}")
        while True:
            conn, addr = self.__server.accept()
            player = Player(conn, addr)
            thread = threading.Thread(target=self.__HandleClient, args=(player,)).start()
            print(self.__clients)
    
    def __HandleClient(self, player):
        connected = False
        with self.__lock:
            keys = list(self.__games.keys())
            for code in keys:
                if self.__games[code].Connect(player):
                    connected = True
                    break
        if not connected:
            while not connected:
                code = str(choices(ascii_uppercase, k=4)) 
                if not code in self.__games:
                    self.__games[code] = SocketBR()
                    connected = self.__games[code].Connect(player)
                
        self.__clients[repr(player)] = code

        print(f"NEW CONNECTION: {repr(player)}")


class SocketBR():
    def __init__(self) -> None:
        self.__name: str = ""
        self.__players: list[Player] = []
        self.__gameThread = threading.Thread(target=self.__StartGame)
        self.__lock = threading.Lock()

    def Connect(self, player:"Player"):
        with self.__lock:
            if len(self.__players) != 2:
                self.__players.append(player)
                if len(self.__players) == 2:
                    self.__gameThread.start()
                return True
            return False 
    
    def __StartGame(self):
        for player in self.__players: # Request the name of each player
            player.SendMessage("!!NAMERQ")  
            buffer = player.ReceiveMessage()
            while buffer != "!!NAMERES":
                player.SetName(buffer)
                print(buffer)
                buffer = player.ReceiveMessage()


class Player():
    def __init__(self, connection, address) -> None:
        self.__address = address
        self.__connection = connection

    def SendMessage(self, message:str):
        message = message.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.__connection.send(send_length)
        self.__connection.send(message)
    
    def ReceiveMessage(self):
        msg_length = self.__connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg = self.__connection.recv(int(msg_length)).decode(FORMAT)
        return msg

    def CloseConnection(self):
        self.__connection.close()
    
    def SetName(self, name):
        self.__name = name
    
    def __repr__(self) -> str:
        return f"{self.__address[0]}::{str(self.__address[1])}"


class Round():
    def __init__(self) -> None:
        self.__gun = Gun()


class Gun():
    def __init__(self) -> None:
        pass


class Gallery():
    def __init__(self) -> None:
        pass


class DualOutput:
    def __init__(self, filename):
        self.__terminal = sys.stdout
        self.__log = open(filename, "w")

    def write(self, message):
        self.__terminal.write(message)
        self.__log.write(message)

    def flush(self):
        self.__terminal.flush()
        self.__log.flush()


if __name__ == "__main__":
    router = Router()
    router.Start()