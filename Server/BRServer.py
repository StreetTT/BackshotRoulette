import asyncio
import websockets
import json
from websockets.asyncio.server import Server
import SocketBR

class BRServer:
    def __init__(self):
        self.__clients: dict[str, dict] = {}
        self.__games: list[SocketBR.SocketBR] = []
    
    async def __handler(self, websocket):
        try: # Handshake
            message = await websocket.recv()
            data = json.loads(message)
            clientID = data.get("clientID")

            await self.__RouteMessage(clientID, websocket, data)
            
            async for message in websocket: # Main loop
                data = json.loads(message)
                await self.__RouteMessage(clientID, websocket, data)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with error: {e}")
        except websockets.exceptions.ConnectionClosedOK:
            print("Connection closed normally")
        except EOFError as e:
            print(f"Connection closed unexpectedly with EOFError: {e}")
        except Exception as e:
            print(f"Unexpected handshake error: {e}")
        
        finally: # Cleanup
            if clientID in self.__clients:
                self.__clients[clientID]["websocket"] = None
            print(f"{clientID} Disconnected")
            print(f"{len(self.__clients)} clients connected\n")

    async def __RouteMessage(self, clientID, websocket, data):
        if data.get('type') == 'LoggingIn': # Login attempt
            name = data.get("name", None)
            self.__clients[clientID]["name"] = name
            await self.__StartGameIfReady()

        if data.get("type") == "ReconnectAttempt":  # (Re)Connection attempt 
            
            if clientID in self.__clients: # If client is already in the list, it's a reconnection
                print(f"Client {clientID} reconnected.")
                self.__clients[clientID]["websocket"] = websocket
                game = self.__clients[clientID]["game"]
                if game and game.IsGameOngoing(): # If the client is in a game, send the game info
                    gameInfo = game.GetGameInfo()
                    asyncio.create_task(websocket.send(json.dumps(gameInfo)))
                
                else:
                    self.__clients[clientID]["game"] = None
                    await self.__StartGameIfReady()
            
            else:  # If client is not in the list, it's a new connection
                print(f"{clientID} Connected")
                self.__clients[clientID] = {
                    "websocket": websocket,
                    "name": data.get("name", None),
                    "game": None
                }
                print(f"{len(self.__clients)} clients connected\n")
        
    
    async def __StartGameIfReady(self):
        
        # Check  if there are two available clients: clients that are not in a game and have a name
        availableClients = [cid for cid in self.__clients if (self.__clients[cid]["game"] is None) and (self.__clients[cid]["name"] is not None)]
        
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

            # Log Game start
            print(f"Starting Game: {id(game)}")
            print(f"Players: {player1.GetName()} and {player2.GetName()}")
            print(f"Clients: {player1.GetClientID()} and {player2.GetClientID()}\n")
            # Setup the game and get start info
            game.StartGame()
            gameInfo = game.GetGameInfo()

            # Send start info to both players
            for clientID in [player1.GetClientID(), player2.GetClientID()]:
                ws = self.__clients[clientID]["websocket"]
                asyncio.create_task(ws.send(json.dumps(gameInfo)))

    async def Main(self):
        print("Server is Starting...")
        server = await websockets.serve(self.__handler, "localhost", 5050)
        print(f"Listening....")
        await server.wait_closed()

if __name__ == "__main__":
    server = BRServer()
    asyncio.run(server.Main())