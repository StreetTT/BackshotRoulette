from random import choices, randint, shuffle
from typing import Callable


class BR():
    def __init__(self, doubleOrNothing: bool = False) -> None:
        self.__doubleOrNothing: bool = doubleOrNothing
        self.__players: list[Player] = [
            Player(), 
            Player()
        ]
        self.__rounds:list[dict[str, int]] = [
            # { # Test Round
            #     "MaxHealth": 3,
            #     "ItemsPerLoad": 3
            # },
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
        self.PlayGame()
    
    def PlayGame(self) -> None:
        print("Welcome to Buckshot Roulette")
        self.__EnterNames()
        print("-----")
        for index, round in enumerate(self.__rounds):
            self.__currentRound = index
            self.__SetRound()
            self.__NewLoad()
            while not self.__IsRoundOver():
                print(self.__currentPlayer._GetName() + "'s Turn") 
                choice:int = -1
                while choice not in (1,0):
                    
                    # Menu
                    print("---")
                    self.__ShowInfo()
                    print("---")
                    print("Select an Action:")
                    print(f"(1) Shoot {self.__currentPlayer._GetName()}")
                    for index, item in enumerate(eval(str(self.__currentPlayer._GetGallery()))):
                        print(f"({index+2}) {item}")
                    print(f"(0) Shoot {self.__GetOpponent()._GetName()}")
                    choice = int(input())
                    
                    if choice in tuple(range(2,9)):
                        # Player uses an item
                        item: Callable | None = self.__currentPlayer._GetGallery()._Use(choice-2)
                        if item is not None:
                            item()
                    
                    elif choice in (1,0):
                        # Player shoots someone
                        impact:int = self.__gun._Shoot()
                        (self.__currentPlayer if choice == 1 else self.__GetOpponent())._ModifyHealth(-impact, self.__rounds[self.__currentRound]["MaxHealth"])
                    
                    else:
                        print("Please select a valid option (0-9)")
                
                # If player shoots themselves with a blank, they get a second turn
                if impact != 0 or choice != 1:
                    print("--")
                    self.__NextTurn()
                else:
                    print()
                
                # Uncuff players and Uncrit gun
                self.__EndTurn()
            
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
            player._GetGallery()._Clear()

    def __NewLoad(self) -> None:
        self.__gun._Load()
        print("The gun holds: ")
        print(str(self.__gun))
        self.__gun._Shuffle() 
        for player in self.__players:
            items: int = self.__rounds[self.__currentRound]["ItemsPerLoad"]
            while items != 0 and not player._GetGallery()._IsFull():
                player._GetGallery()._Add(
                    choices(self.__ITEMS)[0]
                )
                items -= 1
    
    def __ShowInfo(self) -> None:
        for index, player in enumerate(self.__players):
            print(f"{player._GetName()}: {str(player._GetHealth())}/{self.__rounds[self.__currentRound]['MaxHealth']} hearts, {str(player._GetWins())} {'Wins' if player._GetWins() != 1 else 'Win'}")
            print(str(player._GetGallery()))
            print(f"{player._GetName()} is Cuffed") if player._IsCuffed() else None
            print()
        print(f"Gun is {'' if self.__gun._GetCrit() else 'NOT'} dealing double damage")
                


    def __IsRoundOver(self) -> bool:
        if self.__GetOpponent()._GetHealth() == 0:
            self.__currentPlayer._AddWin()
            return True
        elif self.__currentPlayer._GetHealth() == 0:
            self.__GetOpponent()._AddWin()
            return True
        else:
            if self.__gun._IsEmpty():
                self.__NewLoad()
            return False
    
    def __NextTurn(self) -> None:
        if not self.__GetOpponent()._IsCuffed():
            self.__currentPlayer = self.__GetOpponent()
    
    def __EndTurn(self):
        self.__gun._SetCrit(False)
        if self.__GetOpponent()._IsCuffed():
            self.__GetOpponent()._SetCuffed(False)
    
    def __GetOpponent(self) -> "Player":
        if self.__currentPlayer == self.__players[0]:
            return self.__players[1]
        else:
            return self.__players[0] 

    def __Knife(self) -> None:
        self.__gun._SetCrit(True)

    def __Glass(self) -> None:
        print("This bullet is", end=": ")
        if self.__gun._Peek():
            print("LIVE")
        else:
            print("DEAD")

    def __Ciggy(self) -> None:
        self.__currentPlayer._ModifyHealth(1, self.__rounds[self.__currentRound]['MaxHealth'])

    def __Cuffs(self) -> None:
        self.__GetOpponent()._SetCuffed(True)

    def __Voddy(self) -> None:
        print("The bullet was", end=": ")
        if self.__gun._Rack():
            print("LIVE")
        else:
            print("DEAD")

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
    
    def _ModifyHealth(self, health, maxHealth) -> None:
        self.__health += health
        if self.__health >  maxHealth:
            self.__health = maxHealth
        elif self.__health < 0:
            self.__health = 0

    
    def _GetGallery(self) -> "Gallery":
        return self.__gallery
    
    def _IsCuffed(self) -> bool:
        return self.__cuffed
    
    def _SetCuffed(self, cuffed:bool) -> None:
        self.__cuffed = cuffed
    
    def _AddWin(self) -> None:
        self.__wins += 1
    
    def _GetWins(self) -> int:
        return self.__wins


class Gun:
    def __init__(self) -> None:
        self.__chamber:list[bool] = []
        self.__crit: bool = False
    
    def _Load(self) -> None:
        self.__chamber = [True, False]
        bullets: int = randint(0,6)
        for bullet in range(bullets):
            self.__chamber.append(
                choices([True, False])[0]
            )
        
    def _Shuffle(self) -> None:
        for _ in range(randint(0,100)):
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
    
    def _IsEmpty(self) -> bool:
        if len(self.__chamber) == 0:
            return True
        return False
    
    def __str__(self) -> str:
        m:str = "     ---- "
        for bullet in self.__chamber:
            m += "\n    |"
            if bullet:
                m += "LIVE"
            else:
                 m += "DEAD"
            m += "|\n     ---- "
        return m
    
    def _SetCrit(self, crit:bool) -> None:
        self.__crit = crit
    
    def _GetCrit(self) -> bool:
        return self.__crit


class Gallery:
    def __init__(self) -> None:
        self.__items: list[Callable] = []
    
    def __len__(self) -> int:
        return len(self.__items)

    def _Clear(self) -> None:
        self.__items = []

    def _Use(self, index:int) -> Callable | None:
        try:
            return self.__items.pop(index)
        except:
            return None
    
    def _Add(self, item:Callable) -> None:
        self.__items.append(item)

    def _IsFull(self) -> bool:
        if len(self.__items) == 8:
            return True
        return False
    
    def __str__(self) -> str:
        return str([item.__name__[2:] for item in self.__items])

if __name__ == "__main__":
    BR()