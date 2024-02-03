from BR import *
import sys
import os


class SuppressPrint:
    def __enter__(self) -> None:
        self.__OGstdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        sys.stdout.close()
        sys.stdout = self.__OGstdout


if __name__ == "__main__":
    games = -1
    while games == -1:
        try:
            games = int(input("How many game would you like to simulate: "))
            if games <= 0:
                raise ValueError
        except ValueError:
            logger.error("Please select a positive integer")
            games = -1
    players:dict[str, int] = {name: {"Wins":0, "Plays":0} for name in ["Kai", "Zane", "Cole", "Jay", "Lloyd", "No One"]}
    for game in range(games):
        print("Simulating Game " + str(game + 1), end = " - ")
        try:
            with SuppressPrint():
                game: dict[str, dict[str, PlayerData | ModeData | list[RoundData]]] = BR(sim=True).PlayGame()
            gameName: str = list(game.keys())[0]
            playersData: PlayerData = game[gameName]["Players"]
            winner: str = max(playersData, key=playersData.get)
            for player in list(playersData.keys()):
                players[player]["Plays"] += 1
        except Exception as e:
            # Log the exception
            import traceback
            logger.fatal(traceback.format_exc())
            winner = "No One"
        players[winner]["Wins"] += 1
        print(gameName + " - " + player)
    filename:str = "SimulationOverview.json"
    with open(filename, 'w') as json_file:
        dump(players, json_file, indent=4)
    print("--")
    print("Simulation Logged")
    print(players)
