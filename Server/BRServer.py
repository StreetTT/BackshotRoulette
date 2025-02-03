import asyncio
import websockets
import json
import threading
from websockets.asyncio.server import Server
import SocketBR

ITEMS = [
    "knife", "glass", "drugs", "cuffs", "voddy", "twist", 
    "spike", "8ball", "pluck", "null"
]

class BRServer:
    def __init__(self):
        self.__clients: dict[str, dict] = {}
        self.__games: list[SocketBR.SocketBR] = []
    
    async def __handler(self, websocket):

        try:
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") == "ReconnectAttempt":
                clientID = data.get("clientID")
                if clientID in self.__clients:
                    print(f"Client {clientID} reconnected.")
                    self.__clients[clientID]["websocket"] = websocket
                else:
                    print(f"New connection: {clientID}")
                    self.__clients[clientID] = {
                        "websocket": websocket,
                        "name": data.get("name", "Unknown"),  # Store player's name
                        "game": None
                    }
                    print(f"{len(self.__clients)} clients connected\n")
            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                await self.__RouteMessage(clientID, data)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with error: {e}")
        except websockets.exceptions.ConnectionClosedOK:
            print("Connection closed normally")
        except Exception as e:
            print(f"Unexpected handshake error: {e}")
        finally:
            if clientID in self.__clients:
                self.__clients[clientID]["websocket"] = None  # Mark as inactive
            print(f"{len(self.__clients)} clients connected\n")

    async def __RouteMessage(self, clientID, data):
        if data.get('type') == 'ConnectToGame':
            name = data.get("name", "Unknown")
            self.__clients[clientID]["name"] = name
            await self.__StartGameIfReady()
    
    async def __StartGameIfReady(self):
        # Check if we have two eligible clients connected
        availableClients = [cid for cid in self.__clients if self.__clients[cid]["game"] is None]
        
        if len(availableClients) >= 2:
            
            # Create game and add the two clients to it
            game: SocketBR.SocketBR = SocketBR.SocketBR()
            player1 = SocketBR.Player(availableClients[0], self.__clients[availableClients[0]]["name"])
            player2 = SocketBR.Player(availableClients[1], self.__clients[availableClients[1]]["name"])

            game.AddPlayer(player1.GetClientID())
            game.AddPlayer(player2.GetClientID())

            self.__clients[player1.GetClientID()]["game"] = game
            self.__clients[player2.GetClientID()]["game"] = game

            self.__games.append(game)

            # Setup the game and get start info
            startInfo, currentPlayer = game.GetStartInfo()


            # Send start info to both players
            for clientID in [player1.GetClientID(), player2.GetClientID()]:
                ws = self.__clients[clientID]["websocket"]
                if ws:
                    if startInfo['players'][0]['ID'] == clientID:
                        startInfo['players'] = startInfo['players'][::-1]
                    asyncio.create_task(ws.send(json.dumps(startInfo)))

            # Notify the starting player
            starting_ws = self.__clients[currentPlayer.GetClientID()]["websocket"]
            if starting_ws:
                asyncio.create_task(starting_ws.send(json.dumps({
                    "type": "currentTurn",
                    "currentTurn": True
                })))

    async def Main(self):
        print("Server is Starting...")
        server = await websockets.serve(self.__handler, "localhost", 5050)
        print(f"Listening....")
        await server.wait_closed()

if __name__ == "__main__":
    server = BRServer()
    asyncio.run(server.Main())