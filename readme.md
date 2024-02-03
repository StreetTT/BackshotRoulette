# Buckshot Roulette

## Description
Buckshot Roulette is a text-based Python game script that recreates the well known game of the same name. The Russian Roulette-style game revolves around players taking turns shooting, using items, and managing their health until a round is over. Players must strategies, using various items with different effects to win 3 rounds.

## Implementation
The game is implemented using Python 3 and utilizes various modules such as `random`, `logging`, and `json` for functionality. It consists of several classes:

- **BR**: Represents the main class for the Buckshot Roulette game. It manages game logic, player turns, rounds, shooting mechanics, and item usage.
- **Player**: Represents a player in the game, storing their name, health, inventory, win count, and whether they are cuffed.
- **Gun**: Represents the gun used in the game, handling actions such as loading bullets, shuffling the chamber, shooting, and checking for emptiness.
- **Gallery**: Represents a player's inventory of items, allowing them to add, use, and clear items.

The game flow involves a loop where players take turns performing actions such as shooting, using items, and interacting with the game environment. The script logs various game events using the Python `logging` module. Game data is saved in a JSON file with a filename based on the current date and time.

## Updates
- **3 Feb 2024**: This Read Me exists!! The game now has logging and a save mechanism as well as the game being generally tidied up.

## Future Plans
- Add double or nothing mode.
- Create an Online Gui
- Develop Bot to play against

Feel free to contribute to the project and suggest improvements!