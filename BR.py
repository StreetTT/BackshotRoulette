from random import choices, randint, shuffle
from typing import Callable
from LogSetup import CreateLogger
from logging import Logger
from json import dump
from datetime import datetime as dt
from os import makedirs, path


logger: Logger = CreateLogger("BRLogger")


# Types used within the program to help with keeping track
ModeData = dict[str, str]
PlayerData = dict[str, int]
RoundInfo = dict[str, int]
ItemData = dict[str, str]
ShotData = dict[str, str]
LoadData = dict[str, str | dict[str, str]]
RoundData =  dict[str, list[ItemData | LoadData | ShotData ] | RoundInfo]


class BR():
    def __init__(self, doubleOrNothing: bool = False, sim: bool = False) -> None:
        self.__name: str = ""
        self.__gameData: dict[str, dict[str, PlayerData | ModeData | list[RoundData]]] = {}
        self.__doubleOrNothing: bool = doubleOrNothing
        self.__players: list[Player] = [Bot() if sim else Player()]
        self.__rounds:list[RoundInfo] = [
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
    
    def PlayGame(self) -> dict[str, dict[str, ModeData | list[RoundData]]]:
        print("Welcome to Buckshot Roulette")
        print()
        modeData: ModeData = self.__SelectMode()
        print()
        self.__EnterNames()
        print(self.__name)
        self.__gameData.update({self.__name: {"Mode": modeData}})
        logger.info(self.__gameData)
        self.__gameData[self.__name].update({"Game": []})
        for index, roundInfo in enumerate(self.__rounds):
            round: RoundData = {
                "Info": roundInfo,
                "History": []
            }
            self.__currentRound = index
            print("---")
            self.__SetRound()
            print("-")
            while not self.__IsRoundOver():
                choice:int = -1
                while choice not in (1,0):
                    if self.__gun._IsEmpty():
                        loadInfo: LoadData | None = self.__NewLoad()
                        round["History"].append(loadInfo)
                    
                    self.__ShowInfo()
                    print("-")
                    choice = self.__ActionMenu()
                    print("-")
                    if choice in tuple(range(2,9)):
                        action: ItemData = self.__UseItem(choice)
                    else:
                        impact , action = self.__ShootSomeone(choice)
                    round["History"].append(action) if action is not None else None

                # If player shoots themselves with a blank, they get a second turn
                if impact != 0 or choice != 1:
                    print("--")
                    self.__NextTurn()
                    ## We need to add a thing to say when the round id over, dont print the divide
                else:
                    print("-")
                
                # Uncuff players and Uncrit gun
                self.__EndTurn()
            self.__gameData[self.__name]["Game"].append(round)
        self.__gameData[self.__name].update({
            "Players": {
                self.__players[0]._GetName() : self.__players[0]._GetWins(),
                self.__players[1]._GetName() : self.__players[1]._GetWins()
            }
        })
        logger.info("Game Saved under '" + self.__SaveGame() + "'")
        return self.__gameData
    
    def __SelectMode(self) -> ModeData:
        options: list[str] = ["Player vs. Player", "Player vs. Bot"]
        print("Select game mode:")
        for index, option in enumerate(options):
            print(f"({str(index + 1)}) {option}")
        while True:
            try:
                choice = int((2) if isinstance(self.__players[0], Bot) else (self.__currentPlayer._GetInput()))
                if choice not in (2,1):
                    raise IndexError
                if choice == 1:
                    self.__players.append(Player())
                else:
                    self.__players.append(Bot())
                return {"Mode" : ("Bot vs. Bot") if isinstance(self.__players[0], Bot) else (options[choice-1]) }
            except ValueError:
                logger.error("Invalid input. Please enter an integer.")
            except IndexError:
                logger.error("Please select a valid option (1,2)")
    
    def __SaveGame(self) -> str:
        if not path.exists('log'):
            makedirs('log')
        filename: str = dt.now().strftime(f'log/{self.__name.replace(" ","_")}-%d_%b_%y_%Hh_%Mm_%Ss.json') 
        with open(filename, 'w') as json_file:
            dump(self.__gameData, json_file, indent=4)
            return filename
        
    def __ActionMenu(self) -> int:
        print(self.__currentPlayer._GetName() + "'s Turn") 
        print("Select an Action:")
        print(f"(1) Shoot Yourself ({self.__currentPlayer._GetName()})")
        for index, item in enumerate(eval(str(self.__currentPlayer._GetGallery()))):
            print(f"({index+2}) {item}")
        print(f"(0) Shoot Opponent ({self.__GetOpponent()._GetName()})")
        while True:
            try:
                choice = int(self.__currentPlayer._GetInput())
                if choice not in tuple(range(0,9)):
                    raise IndexError
                return choice
            except ValueError:
                logger.error("Invalid input. Please enter an integer.")
            except IndexError:
                logger.error("Please select a valid option (0-9)")
            
    def __EnterNames(self) -> None:
        while True:
            for index, player in enumerate(self.__players):
                player._SetName(
                    ("") if isinstance(player, Bot) else (input(f"Enter Player {index+1}'s Name: "))
                )
            if self.__players[0]._GetName() != self.__players[1]._GetName():
                self.__name: str = f"{self.__players[0]._GetName()} vs. {self.__players[1]._GetName()}"
                return
            logger.error("Both players need different names")

    def __SetRound(self) -> None:
        print(f"Round {self.__currentRound + 1}")
        logger.info(self.__rounds[self.__currentRound])
        for player in self.__players:
            player._SetHeath(
                self.__rounds[self.__currentRound]["MaxHealth"]
            )
            player._GetGallery()._Clear()

    def __NewLoad(self) -> LoadData:
        self.__gun._Load()
        print("The gun holds: ")
        self.__gun._ShowBulletsGraphically()
        self.__gun._Shuffle() 
        loadInfo: dict[str, str | dict[str, str]] = {
            "Type": "NewLoad",
            "Chamber": str(self.__gun),
            "Items": {
                self.__players[0]._GetName() : "",
                self.__players[1]._GetName() : ""
            }
        }
        for player in self.__players:
            items: int = self.__rounds[self.__currentRound]["ItemsPerLoad"]
            while items != 0 and not player._GetGallery()._IsFull():
                player._GetGallery()._Add(
                    choices(self.__ITEMS)[0]
                )
                items -= 1
            loadInfo["Items"][player._GetName()] = str(player._GetGallery())
        logger.info(loadInfo) if loadInfo is not None else None
        return loadInfo
    
    def __ShowInfo(self) -> None:
        for player in self.__players:
            print(f"{player._GetName()}: {str(player._GetHealth())}/{self.__rounds[self.__currentRound]['MaxHealth']} hearts, {str(player._GetWins())} {'Wins' if player._GetWins() != 1 else 'Win'}")
            print(player._GetName() + "'s Items: " + str(player._GetGallery()))
            print(f"{player._GetName()} is Cuffed") if player._IsCuffed() else None
            print()
        print(f"Gun is{'' if self.__gun._GetCrit() else ' NOT'} dealing double damage")
                
    def __IsRoundOver(self) -> bool:
        roundOver: bool = self.__GetOpponent()._GetHealth() == 0 or self.__currentPlayer._GetHealth() == 0
        if self.__GetOpponent()._GetHealth() == 0:
            self.__currentPlayer._AddWin()
        elif self.__currentPlayer._GetHealth() == 0:
            self.__GetOpponent()._AddWin()
        if roundOver:
            self.__gun._Empty()
        return roundOver
    
    def __NextTurn(self) -> None:
        if not self.__GetOpponent()._IsCuffed():
            self.__currentPlayer = self.__GetOpponent()
    
    def __EndTurn(self) -> None:
        self.__gun._SetCrit(False)
        if self.__GetOpponent()._IsCuffed():
            self.__GetOpponent()._SetCuffed(False)
    
    def __GetOpponent(self) -> "Player":
        return [player for player in self.__players if player != self.__currentPlayer][0]

    def __Knife(self) -> None:
        self.__gun._SetCrit(True)
        print("The Gun is Crit")

    def __Glass(self) -> None:
        print("This bullet is", end=": ")
        if self.__gun._Peek():
            print("LIVE")
        else:
            print("DEAD")

    def __Ciggy(self) -> None:
        self.__currentPlayer._ModifyHealth(1, self.__rounds[self.__currentRound]['MaxHealth'])
        print(self.__currentPlayer._GetName() + "'s health = " + str(self.__currentPlayer._GetHealth()))

    def __Cuffs(self) -> None:
        self.__GetOpponent()._SetCuffed(True)
        print(self.__GetOpponent()._GetName() + " has been handcuffed")

    def __Voddy(self) -> None:
        print("The bullet was", end=": ")
        if self.__gun._Rack():
            print("LIVE")
        else:
            print("DEAD")
    
    def __UseItem(self, choice:int) -> ItemData | None:
        item: Callable | None = self.__currentPlayer._GetGallery()._Use(choice-2)
        if item is not None:
            data: dict[str, str] = {
                "Type": item.__name__[2:],
                "Player": self.__currentPlayer._GetName()
            }
            logger.info(data)
            item()
            return data
    
    def __ShootSomeone(self, choice:int) -> tuple[int, ShotData | None]:
        impact:int = self.__gun._Shoot()
        player: Player = self.__currentPlayer if choice == 1 else self.__GetOpponent()
        player._ModifyHealth(
            -impact, 
            self.__rounds[self.__currentRound]["MaxHealth"]
        )
        data: dict[str, str] = {
            "Type": "Shot",
            "Shooter": self.__currentPlayer._GetName(),
            "Victim": player._GetName()
        }
        print(self.__currentPlayer._GetName() + " shot " + player._GetName())
        print("The bullet was:",end = " ")
        print("LIVE" if impact else "DEAD") 
        logger.info(data)
        return (impact, data)
        

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

    def _GetInput(self) -> int:
        return input()


class Bot(Player):
    def __init__(self) -> None:
        super().__init__()
    
    def _SetName(self, name:str="") -> None:
        super()._SetName(choices(["Kai", "Zane", "Cole", "Jay", "Lloyd"])[0])

    def _GetInput(self) -> int:
        choice: int = randint(0,9)
        print(str(choice))
        return choice


class Gun:
    def __init__(self) -> None:
        self.__chamber:list[bool] = []
        self.__crit: bool = False
    
    def _Load(self) -> None:
        self.__chamber = [True, False]
        for bullet in range(randint(0,6)):
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
    
    def _ShowBulletsGraphically(self) -> None:
        m:str = "     ---- "
        for bullet in self.__chamber:
            m += "\n    |"
            if bullet:
                m += "LIVE"
            else:
                 m += "DEAD"
            m += "|\n     ---- "
        print(m)

    def __str__(self) -> str:
        return str(self.__chamber)
    
    def _SetCrit(self, crit:bool) -> None:
        self.__crit = crit
    
    def _GetCrit(self) -> bool:
        return self.__crit

    def _Empty(self) -> None:
        self.__chamber = []


class Gallery:
    def __init__(self) -> None:
        self.__items: list[Callable] = []
    
    def __len__(self) -> int:
        return len(self.__items)

    def _Clear(self) -> None:
        self.__items = []

    def _Use(self, index:int) -> Callable | None:
        if index < len(self.__items):
            return self.__items.pop(index)
        return None
    
    def _Add(self, item:Callable) -> None:
        self.__items.append(item)

    def _IsFull(self) -> bool:
        if len(self.__items) == 8:
            return True
        return False
    
    def __str__(self) -> str:
        return str([item.__name__[2:] for item in self.__items])
    
    def  __repr__(self) -> list:
        string: str = str(self.__items).strip('[]')
        items: list[str] = string.split(', ')
        return [item.strip('\'"') for item in items if item]


if __name__ == "__main__":
    try:
        BR().PlayGame()
    except Exception as e:
        # Log the exception
        import traceback
        logger.fatal(traceback.format_exc())
        print("An unexpected error occurred. Please check the BR.log file for details.")
