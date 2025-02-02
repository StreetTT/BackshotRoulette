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
        self.__clients: list["Client"] = []
        self.__StartConnectingLoop()
    
    def __StartConnectingLoop(self):
        connect_thread = threading.Thread(target= lambda : asyncio.run(self.__ConnectingLoop()))
        connect_thread.daemon = True
        connect_thread.start()

    async def __ConnectingLoop(self):
        while True:
            await self.__ConnectToGame()
            await asyncio.sleep(5)  # Adjust the sleep time as needed
    
    async def handler(self, websocket):
        client = Client(websocket)
        if not any(c.GetClientID() == client.GetClientID() for c in self.__clients):
            self.__clients.append(client)
            print(f"Client Connected from {websocket.remote_address}")
            print(f"{len(self.__clients)} clients connected\n")

        try:
            async for message in websocket:
                data = json.loads(message)
                await self.route_message(client, data)

        except websockets.exceptions.ConnectionClosedOK:
            print("Connection closed normally")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.__clients = [c for c in self.__clients if c.GetClientID() != client.GetClientID()]
            print(f"Client Disconnected from {websocket.remote_address}")
            print(f"{len(self.__clients)} clients connected\n")

    async def route_message(self, client: "Client", data):
        if data.get('type') == 'heartbeat':
            await client.GetWebsocket().send(json.dumps({'type': 'heartbeat_ack'}))  # Respond to heartbeat
        elif data.get('type') == 'ConnectToGame':
            client.SetName(data['name'])
            client.SetReadyToConnect(True)
        # Add more message types and their handling here
    
    async def __ConnectToGame(self):
        # Check if we have two clients connected
        availableClients = [client for client in self.__clients if client.IsReadyToConnect() and client.GetGame() == None]
        if len(availableClients) >= 2:
            
            # Create game and add the two clients to it
            currentBR: SocketBR.SocketBR = SocketBR.SocketBR()
            playerClients = [availableClients[0], availableClients[1]]
            currentBR.AddPlayer(playerClients[0])
            playerClients[0].SetGame(currentBR)
            currentBR.AddPlayer(playerClients[1])
            playerClients[1].SetGame(currentBR)

            # Setup the game and get start info
            startInfo, playerWithStartingTurn = currentBR.GetStartInfo()


            # Send start info to both players
            for client in playerClients:
                if startInfo['players'][0]['ID'] == client.GetClientID():
                    startInfo['players'] = startInfo['players'][::-1]
                ## Need to make sure the opponent is the first player in the list
                await client.GetWebsocket().send(json.dumps(startInfo))
            
            playerWithStartingTurn.GetClient().GetWebsocket().send(json.dumps({
                "type": "currentTurn",
                "currentTurn": True
            }))

    async def main(self):
        print("Server is Starting...")
        server = await websockets.serve(self.handler, "localhost", 5050)
        print(f"Listening....")
        await server.wait_closed()

class Client():
    def __init__(self, websocket):
        self.__websocket = websocket
        self.__clientID = str(f"{websocket.remote_address},{id(websocket)}")
        self.__readyToConnect = True #False
        self.__game: SocketBR.SocketBR | None = None
        self.__name = ""

    def GetWebsocket(self):
        return self.__websocket 
    
    def GetClientID(self):
        return self.__clientID
    
    def SetReadyToConnect(self, ready:bool):
        self.__readyToConnect = ready
    
    def IsReadyToConnect(self):
        return self.__readyToConnect
    
    def SetGame(self, game):
        self.__game = game

    def GetGame(self):
        return self.__game
    
    def SetName(self, name):
        self.__name = name
    
    def GetName(self):
        return self.__name

if __name__ == "__main__":
    server = BRServer()
    asyncio.run(server.main())