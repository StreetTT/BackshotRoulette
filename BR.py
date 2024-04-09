from random import choices, randint, shuffle
from typing import Callable
from LogSetup import CreateLogger
from logging import Logger
from json import dumps, load, dump
from datetime import datetime as dt
from os import makedirs, path
from time import sleep


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
    def __init__(self, sim: bool = False) -> None:
        self.__name: str = ""
        self.__sim = sim
        self.__gameData: dict[str, dict[str, PlayerData | ModeData | list[RoundData]]] = {}
        self.__players: list[Player] = [Bot() if sim else Player()]
        self.__Items: list[Callable] = [
            self.__Knife, 
            self.__Glass, 
            self.__Drugs,
            self.__Cuffs, 
            self.__Voddy  # Demo Reference
        ]
        self.__currentPlayer: Player = self.__players[0]
        self.__currentRound: int = 0
        self.__gun: Gun = Gun()
        self.__rounds:list[RoundInfo] = []
    
    def PlayGame(self) -> dict[str, dict[str, ModeData | list[RoundData]]]:
        print("Welcome to Buckshot Roulette")
        print()
        PlayModeData: ModeData = self.__SelectPlayMode()
        print()
        GameModeData: ModeData = self.__SelectGameMode()
        print()
        self.__EnterNames()
        print(self.__name)
        self.__gameData.update({self.__name: {"Mode": [PlayModeData, GameModeData]}})
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
            loadInfo: LoadData | None = self.__NewLoad()
            round["History"].append(loadInfo) if loadInfo is not None else None
            for player in self.__players:
                state = self.__GetState()
                self.__currentPlayer._SetState(state) if isinstance(self.__currentPlayer, Bot) else None
                self.__currentPlayer = self.__GetOpponent()
            while not self.__IsRoundOver():
                choice:int = -1
                while choice not in ("1","0"):
                    loadInfo: LoadData | None = self.__NewLoad()
                    round["History"].append(loadInfo) if loadInfo is not None else None
                    state = self.__GetState()
                    
                    self.__ShowInfo()
                    print("-")
                    choice = self.__ActionMenu(state)
                    print("-")
                    if choice in [str(item.__name__)[2] for item in self.__Items]:
                        actionData, reward = self.__UseItem(choice)
                    else:
                        impact , actionData, reward = self.__ShootSomeone(int(choice))
                    round["History"].append(actionData) if actionData is not None else None
                    state = self.__GetState()
                    state.update({"Action" : actionData})
                    self.__currentPlayer._Learn(choice, reward, state) if isinstance(self.__currentPlayer, Bot) else None
                    print(end = "-")
                    self.__Sleep(2)

                # If player shoots themselves with a blank, they get a second turn
                if impact != 0 or choice != "1":
                    print("-")
                    self.__NextTurn()
                else:
                    print(" ")
                
                # Uncuff players and Uncrit gun
                self.__EndTurn()
            self.__gameData[self.__name]["Game"].append(round)
        self.__gameData[self.__name].update({"Players": {}})
        for player in self.__players:
            self.__gameData[self.__name]["Players"].update({player._GetName() : player._GetWins()})
            if isinstance(player, Bot):
                player._SaveBot()
        logger.info("Game Saved under '" + self.__SaveGame() + "'")
        return self.__gameData

    def __Sleep(self,secs):
        if not self.__sim:
            sleep(secs)

    def __SelectPlayMode(self) -> ModeData:
        options: list[str] = ["Player vs. Player", "Player vs. Bot"]
        print("Select play mode:")
        for index, option in enumerate(options):
            print(f"({str(index + 1)}) {option}")
        while True:
            try:
                choice = int((2) if isinstance(self.__players[0], Bot) else (self.__currentPlayer._GetInput({})))
                if choice not in (2,1):
                    raise IndexError
                if choice == 1:
                    self.__players.append(Player())
                else:
                    self.__players.append(Bot())
                return {"Play Mode" : ("Bot vs. Bot") if isinstance(self.__players[0], Bot) else (options[choice-1]) }
            except ValueError:
                logger.error("Invalid input. Please enter an integer.")
            except IndexError:
                logger.error("Please select a valid option (1,2)")
    
    def __SelectGameMode(self) -> ModeData:
        options: list[str] = ["Story Mode", "Double Or Nothing"]
        print("Select game mode:")
        for index, option in enumerate(options):
            print(f"({str(index + 1)}) {option}")
        while True:
            try:
                choice = int((2) if isinstance(self.__players[0], Bot) else (self.__currentPlayer._GetInput({})))
                if choice not in (2,1):
                    raise IndexError
                self.__SetGameMode(choice)
                return {"Game Mode" : options[choice-1] }
            except ValueError:
                logger.error("Invalid input. Please enter an integer.")
            except IndexError:
                logger.error("Please select a valid option (1,2)")
    
    def __SetGameMode(self, choice) -> None:
        self.__doubleOrNothing: bool = True if choice == 2 else False
        if not self.__doubleOrNothing:
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
        else:
            for _ in range(3):
                self.__rounds.append({
                    "MaxHealth": randint(2,4),
                    "ItemsPerLoad": randint(1,4)
                })
        if self.__doubleOrNothing:
            self.__Items += [
                self.__Twist,
                self.__Spike,
                self.__8Ball
            ]
    
    def __SaveGame(self) -> str:
        if not path.exists('log'):
            makedirs('log')
        filename: str = dt.now().strftime(f'log/{self.__name.replace(" ","_")}-%d_%b_%y_%Hh_%Mm_%Ss_%fms.json') 
        with open(filename, 'w') as json_file:
            dump(self.__gameData, json_file, indent=4)
        return filename
        
    def __ActionMenu(self, state) -> str:
        print(self.__currentPlayer._GetName() + "'s Turn") 
        items = eval(str(self.__currentPlayer._GetGallery()))
        itemsAvailable = list(set(items))
        options: list[str] = self.__currentPlayer._GetGallery()._Options() + ["0","1"]
        print("Select an Action:")
        print(f"(1) Shoot Yourself ({self.__currentPlayer._GetName()})")
        for item in itemsAvailable:
            print(f"({item[0]}) {item}")
        print(f"(0) Shoot Opponent ({self.__GetOpponent()._GetName()})")
        while True:
            try:
                choice:str = self.__currentPlayer._GetInput(state, options)
                if choice not in options:
                    raise ValueError
                return choice
            except ValueError:
                logger.error(f"{choice} is not an option. Please select a valid option {str(options)}")
            
    def __EnterNames(self) -> None:
        while True:
            for index, player in enumerate(self.__players):
                player._SetName(
                    ("") if isinstance(player, Bot) else (input(f"Enter Player {index+1}'s Name: "))
                )
            if self.__players[0]._GetName() != self.__players[1]._GetName():
                self.__name: str = f"{self.__players[0]._GetName()} vs. {self.__players[1]._GetName()}"
                return
            logger.warning("Both players need different names")

    def __SetRound(self) -> None:
        print(f"Round {self.__currentRound + 1}")
        logger.info(self.__rounds[self.__currentRound])
        for player in self.__players:
            player._SetHeath(
                self.__rounds[self.__currentRound]["MaxHealth"]
            )
            player._GetGallery()._Clear()

    def __NewLoad(self) -> LoadData | None:
        if not self.__gun._IsEmpty():
            return
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
                    choices(self.__Items)[0]
                )
                items -= 1
            loadInfo["Items"][player._GetName()] = str(player._GetGallery())
        logger.info(loadInfo) if loadInfo is not None else None
        self.__Sleep(2)
        return loadInfo
    
    def __ShowInfo(self) -> None:
        for player in self.__players:
            print(f"{player._GetName()}: {str(player._GetHealth())}/{self.__rounds[self.__currentRound]['MaxHealth']} hearts, {str(player._GetWins())} {'Wins' if player._GetWins() != 1 else 'Win'}")
            print(player._GetName() + "'s Items: " + str(player._GetGallery()))
            print(f"{player._GetName()} is Cuffed") if player._IsCuffed() else None
            print()
        print(f"Gun is{'' if self.__gun._GetCrit() else ' NOT'} dealing double damage")

    def __GetState(self) -> dict[str, dict[str, bool | dict[str, int] ] | dict[str, bool | list[Callable] | int ]]:
        stateInfo = {}
        for player in self.__players:
            stateInfo.update({
                "Player" if player == self.__currentPlayer else "Opponent": {
                    "Hearts": player._GetHealth(),
                    "Items": eval(str(player._GetGallery())),
                    "Cuffed": player._IsCuffed()
                }
            })
        stateInfo.update({"Gun": {
            "Bullets" : self.__gun._CountBullets(),
            "Crit": self.__gun._GetCrit()
        }})
        return stateInfo
                
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

    def __Drugs(self) -> None:
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
    
    def __Twist(self) -> None:
        print("The bullet has been Twisted")
        self.__gun._Twist()
    
    def __Spike(self) -> None:
        spike = 2 if randint(0, 99) < 40 else -1
        self.__currentPlayer._ModifyHealth(spike, self.__rounds[self.__currentRound]['MaxHealth'])
        print(self.__currentPlayer._GetName() + "'s health = " + str(self.__currentPlayer._GetHealth()))
    
    def __8Ball(self) -> None:
        bullet = self.__gun._RandPeek()
        print(f"Bullet {bullet[0]} is", end=": ")
        if bullet[1]:
            print("LIVE")
        else:
            print("DEAD")

    def __UseItem(self, choice:str) -> tuple[ItemData | None, int]:
        item: Callable | None = self.__currentPlayer._GetGallery()._Use(choice)
        data = {}
        reward = 0
        if item is not None:
            data: dict[str, str] = {
                "Type": item.__name__[2:],
                "Player": self.__currentPlayer._GetName()
            }
            logger.info(data)
            item()
            reward = -1
        return (data, reward)
    
    def __ShootSomeone(self, choice:int) -> tuple[int, ShotData | None, int]:
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
        reward: int =  2 if (choice == 1 and impact == 0) else ((-impact * 5) if choice == 1 else (impact * 5))
        return (impact, data, reward)
        

class Player:
    def __init__(self) -> None:
        self._name: str = ""
        self.__health: int = 0
        self.__gallery: Gallery = Gallery()
        self.__cuffed: bool = False
        self.__wins: int = 0
    
    def _SetName(self, name:str) -> None:
        self._name = name

    def _GetName(self) -> str:
        return self._name
    
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

    def _GetInput(self, state={}, options=[]) -> str:
        return input().upper()


class Bot(Player):
    def __init__(self) -> None:
        super().__init__()
        self.__qTable = {}
        self.__alpha = 0.1 # How much like Mahoraga his he (learning rate/ adaptability)
        self.__gamma = 0.95 # How ungreedy are they (how much they value future reward)
        self.__epsilon = 0.1 # How often does he fuck around and find out (randomness)
        self.__oldStateStr = None
    
    def _SetName(self, name:str="") -> None:
        super()._SetName(choices(["Kai", "Zane", "Cole", "Jay", "Lloyd"])[0])
        if not path.exists('bots'):
            makedirs('bots')
        filename: str = f'bots/{self._name}.json'
        if path.exists(filename):
            with open(filename, 'r') as json_file:
                file = load(json_file)
                self.__qTable = file["qTable"]
                self.__alpha = file["alpha"]
                self.__gamma = file["gamma"]
                self.__epsilon = file["epsilon"]

    def _GetInput(self, state, options) -> int:
        stateStr = self._GetStateStr(state)

        if randint(0, 99) < self.__epsilon * 100:
            choice = choices(options)[0] # Explore
        else:
            choice = max(self.__qTable[stateStr], key=self.__qTable[stateStr].get)  # Exploit
        print(str(choice))
        return choice

    def _AddToStateSpace(self, stateStr, options) -> None:
        self.__qTable.update({stateStr : {action: 0.0 for action in options}})

    def _GetStateStr(self, state:dict) -> str:
        if "Action" in state.keys():
            if state['Action']['Type'] == "Shot":
                state['Action']['Shooter'] = "Player" if state['Action']['Shooter'] == self._name else "Opponent"
                state['Action']['Victim'] = "Player" if state['Action']['Victim'] == self._name else "Opponent"
            else:
                state['Action']['Player'] = "Player" if state['Action']['Player'] == self._name else "Opponent"
        stateStr = dumps(state, sort_keys=True)
        options = [item[0] for item in state['Player']['Items']] + ['0', '1']
        if stateStr not in self.__qTable:
            self._AddToStateSpace(stateStr, options)
        return stateStr 

    def _Learn(self, action, reward, newState) -> None:
        new_state_str = self._GetStateStr(newState)

        # Ensure action is valid for the state before updating Q-values
        if action in self.__qTable[self.__oldStateStr]:
            max_future_q = max(self.__qTable[new_state_str].values(), default=0)
            old_q = self.__qTable[self.__oldStateStr][action]
            new_q = (1 - self.__alpha)* old_q + self.__alpha * (reward + self.__gamma * max_future_q)
            self.__qTable[self.__oldStateStr][action] = new_q
        else:
            # If the action does not exist in the current state, ignore or log this learning attempt
            # This can be replaced or enhanced with logging if needed
            logger.warning(f"Action {action} was not valid for the current state and was skipped in learning.")
        
        self.__oldStateStr = self._GetStateStr(newState)  # Update the old state to the new state
    
    def _SaveBot(self) -> None:
        if not path.exists('bots'):
            makedirs('bots')
        filename: str = f'bots/{self._name}.json'
        bot = {
            "alpha" : self.__alpha,
            "gamma" : self.__gamma,
            "epsilon" : self.__epsilon,
            "qTable": self.__qTable
        }
        with open(filename, 'w') as json_file:
            dump(bot, json_file, indent=4)
    
    def _SetState(self, state:dict) -> None:
        self.__oldStateStr = self._GetStateStr(state)

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

    def _CountBullets(self) -> dict[str, int]:
        liveCount: int = len([bullet for bullet in self.__chamber if bullet])
        return {
            "Live": liveCount,
            "Dead": len(self.__chamber) - liveCount
        }
    
    def _Twist(self):
        self.__chamber[0] = not self.__chamber[0]
    
    def _RandPeek(self) -> tuple[int, bool]:
        bullet = randint(0, len(self.__chamber) - 1)
        return (bullet + 1, self.__chamber[bullet])

class Gallery:
    def __init__(self) -> None:
        self.__items: list[Callable] = []
    
    def __len__(self) -> int:
        return len(self.__items)

    def _Clear(self) -> None:
        self.__items = []

    def _Use(self, choice:str) -> Callable | None:
        try:
            index: int = self._Options().index(choice)
        except ValueError:
            return None
        return self.__items.pop(index)
    
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

    def _Options(self) -> list[str]:
        return [item[0] for item in eval(str(self))]

if __name__ == "__main__":
    try:
        BR().PlayGame()
    except Exception as e:
        # Log the exception
        import traceback
        logger.fatal(traceback.format_exc())
        print("An unexpected error occurred. Please check the BR.log file for details.")
