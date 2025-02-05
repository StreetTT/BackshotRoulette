import random
from typing import Callable

class SocketBR:
    def __init__(self):
        self.__gun: Gun = Gun()
        self.__players: list[Player] = []
        self.__currentPlayer: Player = None
        self.__rounds = []
        self.__currentRound = 0
        self.__Items: list[Callable] = [
            self.__Knife, 
            self.__Glass, 
            self.__Drugs,
            self.__Cuffs, 
            self.__Voddy  # Demo Reference
        ]
    
    def AddPlayer(self, iD:str) -> None:
        self.__players.append(Player(iD))
    
    def GetPlayers(self, iD:str = None):
        if iD == None:
            return self.__players
        for player in self.__players:
            if player.GetID() == iD:
                return player
        return None
    
    def __SetGameMode(self, choice) -> None:
        self.__doubleOrNothing: bool = True if choice == 2 else False
        if not self.__doubleOrNothing:
            self.__rounds = [
                {
                    "MaxHealth": 2,
                    "ItemsPerLoad": 0
                },
                {
                    "MaxHealth": 4,
                    "ItemsPerLoad": 2
                }, 
                {
                    "MaxHealth": 6,
                    "ItemsPerLoad": 4
                }
            ]
        else:
            for _ in range(3):
                self.__rounds.append({
                    "MaxHealth": random.randint(2,4),
                    "ItemsPerLoad": random.randint(1,4)
                })
        if self.__doubleOrNothing:
            self.__Items += [
                self.__Twist,
                self.__Spike,
                self.__8Ball,
                self.__Pluck
            ]
    
    def __SetRound(self) -> None:
        for player in self.__players:
            player.SetHeath(
                self.__rounds[self.__currentRound]["MaxHealth"]
            )
            player.GetGallery().Clear()
    
    def __NewLoad(self):
        if not self.__gun.IsEmpty():
            return
        self.__gun.Load()
        for player in self.__players:
            items: int = self.__rounds[self.__currentRound]["ItemsPerLoad"]
            while items != 0 and not player.GetGallery().IsFull():
                player.GetGallery().Add(random.choice(self.__Items))
                items -= 1
    
    def __GetOpponent(self) -> "Player":
        return [player for player in self.__players if player.GetClientID() != self.__currentPlayer.GetClientID()][0]
    
    def __IsRoundOver(self) -> bool:
        roundOver: bool = self.__GetOpponent().GetHealth() == 0 or self.__currentPlayer.GetHealth() == 0
        if self.__GetOpponent().GetHealth() == 0:
            self.__currentPlayer.AddWin()
        elif self.__currentPlayer.GetHealth() == 0:
            self.__GetOpponent().AddWin()
        if roundOver:
            self.__gun.Empty()
        return roundOver
    
    def StartGame(self):
        if len(self.__players) != 2:
            return None
        self.__currentPlayer = self.__players[0]
        self.__SetGameMode(2)
        self.__SetRound()
        self.__NewLoad()
    
    def GetGameInfo(self):
        return {
            "type": "gameInfo",
            "players": [{
                    "ID": player.GetClientID(),
                    "health": player.GetHealth(),
                    "gallery": player.GetGalleryList(),
                    "cuffed": player.IsCuffed()
            } for player in self.__players],
            "gun": {
                "crit": self.__gun.GetCrit(),
                "chamber": list(sorted(self.__gun.GetChamber(), reverse=True)),
            },
            "currentTurn": self.__currentPlayer.GetClientID()
        }
    
    def IsGameOngoing(self) -> bool:
        return len(self.__players) == 2


    def __Knife(self) -> None:
        pass

    def __Glass(self) -> None:
        pass

    def __Drugs(self) -> None:
       pass

    def __Cuffs(self) -> None:
        pass

    def __Voddy(self) -> None:
        pass
    
    def __Twist(self) -> None:
        pass
    
    def __Spike(self) -> None:
        pass
    
    def __8Ball(self) -> None:
        pass

    def __Pluck(self) -> None:
        pass


class Gun:
    def __init__(self) -> None:
        self.__chamber:list[bool] = []
        self.__crit: bool = False
    
    def GetChamber(self) -> list[bool]:
        return self.__chamber
    
    def GetCrit(self) -> bool:
        return self.__crit
    
    def Load(self) -> None:
        self.__chamber = [True, False]
        for bullet in range(random.randint(0,6)):
            self.__chamber.append(
                random.choice([True, False])
            )
        
    def __Shuffle(self) -> None:
        for _ in range(random.randint(0,100)):
            random.shuffle(self.__chamber)
    
    def __Peek(self) -> bool:
        return self.__chamber[0]
    
    def __Rack(self) -> bool:
        return self.__chamber.pop(0)
    
    def __Shoot(self) -> int:
        impact: int = 2 if self.__crit else 1
        if self.__chamber.pop(0):
            return impact
        return 0
    
    def IsEmpty(self) -> bool:
        if len(self.__chamber) == 0:
            return True
        return False

    def Empty(self) -> None:
        self.__chamber = []

    def __CountBullets(self) -> dict[str, int]:
        liveCount: int = len([bullet for bullet in self.__chamber if bullet])
        return {
            "Live": liveCount,
            "Dead": len(self.__chamber) - liveCount
        }
    
    def __Twist(self):
        self.__chamber[0] = not self.__chamber[0]
    
    def __RandPeek(self) -> tuple[int, bool]:
        bullet = random.randint(0, len(self.__chamber) - 1)
        return (bullet + 1, self.__chamber[bullet])
    
class Player:
    def __init__(self, clientID, name = "Unknown") -> None:
        self.__name: str = name
        self.__clientID = clientID
        self.__health: int = 0
        self.__gallery: Gallery = Gallery()
        self.__cuffed: bool = False
        self.__wins: int = 0
    
    def GetName(self) -> str:
        return self.__name
    
    def GetClientID(self) -> str:
        return self.__clientID
    
    def SetHeath(self, health: int) -> None:
        self.__health = health
    
    def GetHealth(self) -> int:
        return self.__health
    
    def ModifyHealth(self, health, maxHealth) -> None:
        self.__health += health
        if self.__health >  maxHealth:
            self.__health = maxHealth
        elif self.__health < 0:
            self.__health = 0
    
    def GetGallery(self) -> "Gallery":
        return self.__gallery
    
    def GetGalleryList(self) -> list[str]:
        return self.__gallery.GetGallery()
    
    def IsCuffed(self) -> bool:
        return self.__cuffed
    
    def SetCuffed(self, cuffed:bool) -> None:
        self.__cuffed = cuffed
    
    def AddWin(self) -> None:
        self.__wins += 1
    
    def GetWins(self) -> int:
        return self.__wins

    def GetInput(self) -> str:
        return input().upper()



class Gallery:
    def __init__(self) -> None:
        self.__items: list[Callable] = [None] * 8
    
    def __len__(self) -> int:
        return len(self.__items)

    def Clear(self) -> None:
        self.__items = [None] * 8

    """def __Use(self, choice:str) -> Callable | None:
        try:
            index: int = self._Options().index(choice)
        except ValueError:
            return None
        return self.__items.pop(index)"""
    
    def Add(self, item:Callable) -> None:
        currItem = 0
        while self.__items[currItem]:
            currItem += 1
        self.__items[currItem] = item

    def IsFull(self) -> bool:
        if len([i for i in self.__items if i]) == 8:
            return True
        return False
    
    def GetGallery(self) -> str:
        return [item.__name__[2:] for item in self.__items if item != None]
