from random import choices, randint, shuffle
from typing import Callable


class BackshotRoulette():
    def __init__(self, doubleOrNothing: bool = False) -> None:
        self.__doubleOrNothing = doubleOrNothing
        self.__players: list[Player] = [
            Player(), 
            Player()
        ]
        self.__rounds:list[dict[str, int]] = [
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
        self.__ITEMS: list[Callable] = [
            self.__Knife, 
            self.__Glass, 
            self.__Ciggy, 
            self.__Cuffs, 
            self.__Voddy
        ]
        self.__currentPlayer: Player = self.__players[0]
        self.__currentRound: int = 0
        self.__gun: Gun = Gun()
    
    def PlayGame(self) -> None:
        print("Welcome to Buckshot Roulette")
        print("-----")
        self.__EnterNames()
        print("-----")
        for index, round in enumerate(self.__rounds):
            self.__currentRound = index
            self.__SetRound()
            self.__ShowHealth()
            while not self.__IsRoundOver():
                # Main Game Logic 
                self.__NextTurn()
                pass
            self.__ScoreRound()
            
    def __EnterNames(self) -> None:
        for index, player in enumerate(self.__players):
            player._SetName(
                input(f"Enter Player {index+1}'s Name: ")
            )

    def __SetRound(self) -> None:
        print(f"Round {self.__currentRound + 1}")
        for player in self.__players:
            player._SetHeath(
                self.__rounds[self.__currentRound]["MaxHealth"]
            )
        self.__GiveItems()

    def __GiveItems(self) -> None:
        # Every time the gun is loaded, each person gets a new chance at items
        # So this is why the gun loading is inside give items
        self.__gun._Load() 
        for player in self.__players:
            items: int = self.__rounds[self.__currentRound]["ItemsPerLoad"]
            while items != 0 and not player.GetGallery().IsFull():
                player._GetGallery()._Add(
                    choices(self.__ITEMS)[0]
                )
                items -= 1
    
    def __ShowHealth(self) -> None:
        for player in self.__players:
            print(player._GetName() + ": " + str(player._GetHealth()) + " hearts")
        print("---")

    def __IsRoundOver(self) -> bool:
        return False
    
    def __NextTurn(self) -> None:
        if self.__currentPlayer == self.__players[0]:
            if self.__players[1]._IsCuffed():
                self.__players[1]._SetCuffed(False)
            else:
                self.__currentPlayer = self.__players[1]
        else:
            if self.__players[0]._IsCuffed():
                self.__players[0]._SetCuffed(False)
            else:
                self.__currentPlayer = self.__players[0]
    
    def __ScoreRound(self) -> None:
        if self.__players[0]._GetHealth() == 0:
            self.__players[1]._AddWin()
        else:
            self.__players[0]._AddWin()

    def __Knife(self) -> None:
        pass

    def __Glass(self) -> None:
        pass

    def __Ciggy(self) -> None:
        pass

    def __Cuffs(self) -> None:
        pass

    def __Voddy(self) -> None:
        pass

class Player:
    def __init__(self) -> None:
        self.__name: str = ""
        self.__health: int = 0
        self.__gallery: Gallery = Gallery()
        self.__cuffed: bool = False
        self.__wins: int = 0
    
    def _SetName(self, name:str) -> None:
        self.__name = name

    def _GetName(self) -> str:
        return self.__name
    
    def _SetHeath(self, health: int) -> None:
        self.__health = health
    
    def _GetHealth(self) -> int:
        return self.__health
    
    def _GetGallery(self) -> "Gallery":
        return self.__gallery
    
    def _IsCuffed(self) -> bool:
        return self.__cuffed
    
    def _SetCuffed(self, cuffed:bool) -> None:
        self.__cuffed = cuffed
    
    def _AddWin(self) -> None:
        self.__wins += 1


class Gun:
    def __init__(self) -> None:
        self.__chamber:list[bool] = []
        self.__crit: bool = False
    
    def _Load(self) -> None:
        self.__chamber = [True, False]
        bullets = randint(0,6)
        for bullet in range(bullets):
            self.__chamber.append(
                choices([True, False])[0]
            )
        shuffle(self.__chamber)
    
    def _Peek(self) -> bool:
        return self.__chamber[0]
    
    def _Rack(self) -> bool:
        return self.__chamber.pop(0)
    
    def _Shoot(self) -> int:
        impact: int = 2 if self.__crit else 1
        if self.__chamber.pop(0):
            return impact
        return 0
    
    def _isEmpty(self) -> bool:
        if len(self.__chamber) == 0:
            return True
        return False


class Gallery:
    def __init__(self) -> None:
        self.__items: list[Callable] = []
    
    def __len__(self) -> int:
        return len(self.__items)

    def _Clear(self) -> None:
        self.__items = []

    def _Use(self, index:int) -> Callable:
        return self.__items.pop(index-1)
    
    def _Add(self, item:Callable) -> None:
        self.__items.append(item)

    def _IsFull(self) -> bool:
        if len(self.__items) == 8:
            return True
        return False

if __name__ == "__main__":
    BackshotRoulette()