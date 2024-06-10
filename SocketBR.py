import socket
from string import ascii_uppercase
from random import choices
from typing import Callable
from datetime import datetime
from random import choices, randint, shuffle
import threading
from time import sleep

import sys



DISCONNECTMSG = "!DISCONNECT"


class Router():
    def __init__(self) -> None:
        self.__serverName = socket.gethostbyname(socket.gethostname())
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__serverName, 5050))
        self.__games: dict[str, SocketBR] = {"ABCD": SocketBR("ABCD")}
        self.__clients: dict[str, str] = {}
        self.__lock = threading.Lock()
    
    def Start(self):
        print("Server is Starting...")
        self.__server.listen()
        print(f"Listening on {self.__serverName}")
        while True:
            conn, addr = self.__server.accept()
            player = Player(conn, addr)
            threading.Thread(target=self.__HandleClient, args=(player,)).start()
    
    def __HandleClient(self, player):
        connected = False
        with self.__lock:
            keys = list(self.__games.keys())
            for code in keys:
                connected = self.__games[code].Connect(player)
                if connected:
                    break
        if not connected:
            while not connected:
                code = str(choices(ascii_uppercase, k=4)) 
                if not code in self.__games:
                    self.__games[code] = SocketBR(code)
                    connected = self.__games[code].Connect(player)
                
        self.__clients[str(player)] = code

        print(f"NEW CONNECTION: {str(player)} - {code}")

class BRProtocol():
    def SendMessage(self, msg):
        msg:str = str(msg)
        msg = msg.encode("utf-8")
        msg_length = len(msg)
        send_length = str(msg_length).encode("utf-8")
        send_length += b' ' * (1024 - len(send_length))
        self._connection.send(send_length)
        self._connection.send(msg)
        sleep(0.1)
    
    def ReceiveMessage(self):
        msg_length = self._connection.recv(1024).decode("utf-8")
        if msg_length:
            msg = self._connection.recv(int(msg_length)).decode("utf-8")
        return str(msg)

    def CloseConnection(self):
        self._connection.close()


class SocketBR():
    def __init__(self, code:str) -> None:
        self.__code = code
        self.__players: list[Player] = []
        self.__currentPlayer = None
        self.__rounds: list[Round] = []
        self.__currentRound = None
        self.__gun = Gun()
        self.__items: list[Callable] = [
            self.__Knife, 
            self.__Glass, 
            self.__Drugs,
            self.__Cuffs, 
            self.__Voddy  # Demo Reference
        ]
        self.__gameThread = threading.Thread(target=self.__StartGame)
        self.__lock = threading.Lock()

    def Connect(self, player:"Player"):
        if len(self.__players) != 2:
            self.__players.append(player)
            if len(self.__players) == 2:
                self.__gameThread.start()
            return True
        return False 
    
    def __StartGame(self):
        with self.__lock:
            self.__SendToPlayersConcurrently(self.__SetName)
        self.__name = f"{self.__players[0].GetName()} vs {self.__players[1].GetName()}"
        print(self.__name)
        sys.stdout = DualOutput(datetime.now().strftime(f'log/{self.__name.replace(" ","_")}-%d_%b_%y_%Hh_%Mm_%Ss_%fms.log'))
        self.__SetRounds()
        for index, self.__currentRound in enumerate(self.__rounds):
            print(f"Round {index + 1}")
            self.__StartRound()
            while not self.__IsRoundOver():
                self.__SendToPlayersConcurrently(self.__SendRoundInfo)


    def __SetName(self, player: "Player"): # Request the name of each player
        player.SendMessage("!!NAMERQ")  
        buffer = player.ReceiveMessage()
        while buffer != "!!NAMERES":
            player.SetName(buffer)
            print(f"{self.__code}/{str(player)} - {buffer}")
            buffer = player.ReceiveMessage()

    def __SetRounds(self, doubleOrNothing=True):
        if not doubleOrNothing:
            self.__rounds = [Round(i+2,i) for i in range(0,6,2)]
        else:
            self.__rounds = [Round(randint(2,4),randint(1,4)) for _ in range(3)]
            self.__items += [
                self.__Twist,
                self.__Spike,
                self.__8Ball,
                self.__Pluck
            ]
    
    def __StartRound(self) -> None:
        for player in self.__players:
            player._SetHeath(self.__currentRound.GetMaxHealth())
            player._GetGallery()._Clear()
        self.__currentPlayer = self.__players[0]
        self.__Reload()
    
    def __Reload(self):
        if not self.__gun._IsEmpty():
            return
        self.__gun._Load()
        self.__gun._Shuffle() 
        for player in self.__players:
            items: int = self.__currentRound.GetItemsPerLoad()
            while items > 0 and not player._GetGallery()._IsFull():
                player._GetGallery()._Add(choices(self.__items)[0])
                items -= 1
    
    def __IsRoundOver(self) -> bool:
        roundOver: bool = self.__GetOpponent()._GetHealth() == 0 or self.__currentPlayer._GetHealth() == 0
        if self.__GetOpponent()._GetHealth() == 0:
            self.__currentPlayer._AddWin()
        elif self.__currentPlayer._GetHealth() == 0:
            self.__GetOpponent()._AddWin()
        if roundOver:
            self.__gun._Empty()
        return roundOver

    def __GetOpponent(self, p=None) -> "Player":
        p = self.__currentPlayer if p == None else p
        return [player for player in self.__players if player != p][0]
    
    def __SendToPlayersConcurrently(self, method, args=()):
        threads = []
        for player in self.__players:
            thread = threading.Thread(target=method, args=((player,)+args))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    
    def __SendRoundInfo(self, player: "Player"):
        player.SendMessage("!!ROUNDINFORQ")
        player.SendMessage(self.__currentRound.Info())
        player.SendMessage(player.Info())
        player.SendMessage(self.__GetOpponent(player).Info())
        player.SendMessage(self.__gun.Info())
        buffer = player.ReceiveMessage()
        while buffer != "!!ROUNDINFORES":
            print(f"{self.__code}/{str(player)} $ {player.GetName()} - {buffer}")
            buffer = player.ReceiveMessage()
    
    def __Knife(self):
        pass  # Function body to be implemented

    def __Glass(self):
        pass  # Function body to be implemented

    def __Drugs(self):
        pass  # Function body to be implemented

    def __Cuffs(self):
        pass  # Function body to be implemented

    def __Voddy(self):
        pass  # Function body to be implemented

    def __Twist(self):
        pass  # Function body to be implemented

    def __Spike(self):
        pass  # Function body to be implemented

    def __8Ball(self):
        pass  # Function body to be implemented

    def __Pluck(self):
        pass  # Function body to be implemented


class Player(BRProtocol):
    def __init__(self, connection, address) -> None:
        self.__address = address
        self._connection = connection
        self.__wins = 0
        self.__gallery: Gallery = Gallery()
    
    def SetName(self, name):
        self.__name = name
    
    def GetName(self):
        return self.__name
    
    def __str__(self) -> str:
        return f"{self.__address[0]}::{str(self.__address[1])}"

    def _AddWin(self) -> None:
        self.__wins += 1
    
    def _SetHeath(self, health: int) -> None:
        self.__health = health
    
    def _GetGallery(self) -> "Gallery":
        return self.__gallery 
    
    def _GetHealth(self) -> int:
        return self.__health
    
    def Info(self):
        d = {}
        d.update({"wins": self.__wins})
        d.update({"gallery": str(self.__gallery)})
        d.update({"health": self.__health})
        return d


class Round():
    def __init__(self, maxHealth:int, itemsPerLoad:int) -> None:
        self.__maxHealth = maxHealth
        self.__itemsPerLoad = itemsPerLoad
    
    def GetMaxHealth(self):
        return self.__maxHealth

    def GetItemsPerLoad(self):
        return self.__itemsPerLoad

    def Info(self):
        d = {}
        d.update({"maxHealth": self.__maxHealth})
        d.update({"itemsPerLoad": self.__itemsPerLoad})
        return d


class Gun:
    def __init__(self) -> None:
        self.__chamber:list[bool] = []
        self.__crit: bool = False
    
    def _IsEmpty(self) -> bool:
        if len(self.__chamber) == 0:
            return True
        return False
        

    def __str__(self) -> None:
        m:str = "     ---- "
        for bullet in self.__chamber:
            m += "\n    |"
            if bullet:
                m += "LIVE"
            else:
                 m += "DEAD"
            m += "|\n     ---- "
        return m
    
    def _Load(self) -> None:
        self.__chamber = [True, False]
        for _ in range(randint(0,6)):
            self.__chamber.append(
                choices([True, False])[0]
            )
        
    def _Shuffle(self) -> None:
        for _ in range(randint(0,100)):
            shuffle(self.__chamber)
    
    def _Empty(self) -> None:
        self.__chamber = []
    
    def Info(self):
        d = {}
        d.update({"chamber": self.__chamber})
        d.update({"crit": self.__crit})
        return d
    
    
    
    

    def __repr__ (self) -> str:
        return str(self.__chamber)
    
    def _SetCrit(self, crit:bool) -> None:
        self.__crit = crit
    
    def _GetCrit(self) -> bool:
        return self.__crit


class Gallery():
    def __init__(self) -> None:
        self.__items: list[Callable] = []
    
    def __len__(self) -> int:
        return len(self.__items)

    def _Clear(self) -> None:
        self.__items = []
    
    def __str__(self) -> str:
        return str([item.__name__[2:] for item in self.__items])

    def _Add(self, item:Callable) -> None:
        self.__items.append(item)

    def _IsFull(self) -> bool:
        if len(self.__items) == 8:
            return True
        return False



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
    sys.stdout = sys.__stdout__
    router = Router()
    router.Start()