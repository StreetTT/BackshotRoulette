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
            self.__SendToPlayersConcurrently(self.__SetName, direct=True)
        self.__name = f"{self.__players[0].GetName()} vs {self.__players[1].GetName()}"
        print(self.__name + "\n-----")
        sys.stdout = DualOutput(datetime.now().strftime(f'log/{self.__name.replace(" ","_")}-%d_%b_%y_%Hh_%Mm_%Ss_%fms.log'))
        self.__SetRounds()
        for index, self.__currentRound in enumerate(self.__rounds):
            print(f"Round {index + 1}" + "\n----")
            self.__StartRound()
            while not self.__IsRoundOver():
                self.__Reload()
                print("---")
                for player in self.__players:
                    print(player.Info())
                print(self.__gun.Info())
                self.__SendToPlayersConcurrently(self.__SendRoundInfo)
                choice = self.__TakeAction()
                if choice in [str(item.__name__)[2] for item in self.__items]:
                    self.__UseItem(choice)
                else:
                    impact = self.__ShootSomeone(int(choice))
                if choice in ("1","0") and (impact != 0 or choice == "0"):
                    self.__NextTurn()
            self.__EndTurn()

    def __SetName(self, player: "Player"): # Request the name of each player
        player.SendMessage("!!RQ")  
        buffer = player.ReceiveMessage()
        while buffer != "!!RES":
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
        print(self.__currentRound.Info())
    
    def __Reload(self):
        if not self.__gun._IsEmpty():
            return
        self.__gun._Load()
        self.__gun._Shuffle() 
        for player in self.__players:
            items: int = self.__currentRound.GetItemsPerLoad()
            while items > 0 and not player._GetGallery()._IsFull():
                item = None
                while item == None or (self.__currentRound.GetMaxHealth() == 2 and item.__name__[2:] == "Knife"):
                    # If Round Health == 2, no Knifes
                    item = choices(self.__items)[0]
                player._GetGallery()._Add(item)
                items -= 1
        self.__SendToPlayersConcurrently(lambda player: player.SendMessage("Gun Reloaded"))
    
    def __IsRoundOver(self) -> bool:
        roundOver: bool = self.__GetOpponent()._GetHealth() == 0 or self.__currentPlayer._GetHealth() == 0
        if self.__GetOpponent()._GetHealth() == 0:
            self.__currentPlayer._AddWin()
        elif self.__currentPlayer._GetHealth() == 0:
            self.__GetOpponent()._AddWin()
        if roundOver:
            self.__gun._Empty()
            print("---")
        return roundOver

    def __GetOpponent(self, p=None) -> "Player":
        p = self.__currentPlayer if p == None else p
        return [player for player in self.__players if player != p][0]
    
    def __SendToPlayersConcurrently(self, method, direct=False):
        threads = []
        for player in self.__players:
            if direct: 
                thread = threading.Thread(target=method, args=((player,)))
            else:
                thread = threading.Thread(target=self.__RQRESProtocol, args=(player, method, ))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
  
    def __SendRoundInfo(self, player: "Player"):
        player.SendMessage(self.__currentRound.Info())
        player.SendMessage(player.Info())
        player.SendMessage(self.__GetOpponent(player).Info())
        player.SendMessage(self.__gun.Info())

    def __RQRESProtocol(self, player, preMethod = None, names=True):
        buffer = []
        player.SendMessage(f"!!RQ")
        preMethod(player) if preMethod != None else None
        buffer.append(player.ReceiveMessage())
        while buffer[-1] != f"!!RES":
            print(f"{self.__code}/{str(player)}{(' $ ' + player.GetName()) if names else ''} - {buffer[-1]}")
            buffer.append(player.ReceiveMessage())
        try:
            return buffer[-2]
        except IndexError:
            return buffer[-1]
    
    def __TakeAction(self, plucking=False):
        player = self.__currentPlayer if not plucking else self.__GetOpponent()
        options: list[str] = player._GetGallery()._Options() + (["0", "1"] if not plucking else [])
        while True:
            try:
                choice:str = self.__RQRESProtocol(self.__currentPlayer).upper()
                if choice not in options:
                    raise ValueError
                if plucking:
                    if not self.__GetOpponent()._GetGallery()._Options() or all(option == "P" for option in self.__GetOpponent()._GetGallery()._Options()):
                        raise LookupError
                    elif choice == "P":
                        raise IndexError
                return choice
            except ValueError as e:
                announcement = f"{choice} is not an option. Please select a valid option {str(options)}"
            except IndexError as e:
                announcement = f"You cannot pluck a pluck when plucking. Please select another option"
            except LookupError as e:
                announcement = f"There isn't enough items to Pluck. Please select another option"
    
            if 'announcement' in locals():
                announcementMethod = lambda player, message=announcement: player.SendMessage(message)
                self.__RQRESProtocol(self.__currentPlayer, announcementMethod)
                print(announcement)

    def __UseItem(self, choice:str, plucked=False):
        player: Player = self.__currentPlayer if not plucked else self.__GetOpponent()
        item: Callable | None = player._GetGallery()._Use(choice)
        if item is not None:
            if choice in ['P']:
                item()
            else:
                announcement = f"{'PLUCKED\n\t' if plucked else ''}{item()}"
                if announcement:
                    print(announcement)
                    announcementMethod = lambda player: player.SendMessage(announcement)
                    if choice in ['G', '8']:
                        self.__RQRESProtocol(self.__currentPlayer, announcementMethod)
                    else:
                        self.__SendToPlayersConcurrently(announcementMethod)
    
    def __ShootSomeone(self, choice:int):
        impact:int = self.__gun._Shoot()
        player: Player = self.__currentPlayer if choice == 1 else self.__GetOpponent()
        player._ModifyHealth(-impact, self.__currentRound.GetMaxHealth())
        announcement = f"{self.__currentPlayer.GetName()} shot {player.GetName()} with a {'LIVE' if impact else 'DEAD'}"
        print(announcement)
        announcementMethod = lambda player: player.SendMessage(announcement)
        self.__SendToPlayersConcurrently(announcementMethod)
        return impact

    def __Knife(self):
        self.__gun._SetCrit(True)   
        return "Gun = Crit"
        
    def __Glass(self):
        return f"Peek Bullet = {'LIVE' if self.__gun._Peek() else 'DEAD'}"

    def __Drugs(self):
        self.__currentPlayer._ModifyHealth(1, self.__currentRound.GetMaxHealth())
        return f"{self.__currentPlayer.GetName()}'s health = {str(self.__currentPlayer._GetHealth())}"

    def __Cuffs(self):
        self.__GetOpponent()._SetCuffed(True)
        return f"{self.__GetOpponent().GetName()} cuffed = True"

    def __Voddy(self):
        return f"Rack Bullet = {'LIVE' if self.__gun._Rack() else 'DEAD'}"
    
    def __Twist(self):
        self.__gun._Twist()
        return "Twisted Top Bullet"
    
    def __Spike(self):
        spike = 2 if randint(0, 99) < 40 else -1
        self.__currentPlayer._ModifyHealth(spike, self.__currentRound.GetMaxHealth())
        return f"{self.__currentPlayer.GetName()}'s health = {str(self.__currentPlayer._GetHealth())}"
    
    def __8Ball(self):
        bullet = self.__gun._RandPeek()
        return f"Peek Bullet {bullet[0]} = {'LIVE' if bullet[1] else 'DEAD'}"

    def __Pluck(self):
        choice = self.__TakeAction(plucking=True)
        self.__UseItem(choice, plucked=True)

    def __NextTurn(self) -> None:
        if not self.__GetOpponent()._IsCuffed():
            self.__currentPlayer = self.__GetOpponent()

    def __EndTurn(self) -> None:
        self.__gun._SetCrit(False)
        if self.__GetOpponent()._IsCuffed():
            self.__GetOpponent()._SetCuffed(False)


class Player(BRProtocol):
    def __init__(self, connection, address) -> None:
        self.__address = address
        self._connection = connection
        self.__name = None
        self.__health = 0
        self.__wins = 0
        self.__cuffed = False
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
        d.update({"name": self.__name}) if self.__name != None else None
        d.update({"wins": self.__wins})
        d.update({"gallery": str(self.__gallery)})
        d.update({"health": self.__health})
        d.update({"cuffed": self.__cuffed})
        return d

    def _ModifyHealth(self, health, maxHealth) -> None:
        self.__health += health
        if self.__health >  maxHealth:
            self.__health = maxHealth
        elif self.__health < 0:
            self.__health = 0

    def _SetCuffed(self, cuffed:bool) -> None:
        self.__cuffed = cuffed

    def _IsCuffed(self) -> bool:
        return self.__cuffed
    
    
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

    def _Peek(self) -> bool:
        return self.__chamber[0]

    def _Rack(self) -> bool:
        return self.__chamber.pop(0)
    
    def _Twist(self):
        self.__chamber[0] = not self.__chamber[0]
    
    def _RandPeek(self) -> tuple[int, bool]:
        bullet = randint(0, len(self.__chamber) - 1)
        return (bullet + 1, self.__chamber[bullet])

    def _Shoot(self) -> int:
        impact: int = 2 if self.__crit else 1
        if self.__chamber.pop(0):
            return impact
        return 0

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

    def _Options(self) -> list[str]:
        return [item[0] for item in eval(str(self))]
    
    def _Use(self, choice:str) -> Callable | None:
        try:
            index: int = self._Options().index(choice)
        except ValueError:
            return None
        return self.__items.pop(index)



class DualOutput:
    def __init__(self, filename):
        self.__terminal = sys.stdout
        self.__log = open(filename, "w", buffering=1)  # Line buffered

    def write(self, message):
        self.__terminal.write(message)
        self.__log.write(message)
        self.__log.flush()  # Ensure flushing after each write

    def flush(self):
        self.__terminal.flush()
        self.__log.flush()


if __name__ == "__main__":
    sys.stdout = sys.__stdout__
    router = Router()
    router.Start()