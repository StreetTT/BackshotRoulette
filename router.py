import asyncio
import websockets
import json
import random

ITEMS = [
    "knife", "glass", "drugs", "cuffs", "voddy", "twist", 
    "spike", "8ball", "pluck", "null"
]

connected_clients = []
startInfoSent = False

async def handler(websocket):
    
    connected_clients.append(websocket)
    print(f"Client connected: {len(connected_clients)} clients connected")

    try:
        # Check if we have two clients connected
        if not startInfoSent and len(connected_clients) == 2:

            startInfo = {
                "type": "startInfo",
                "players": [
                     {
                        "health": random.randint(1, 5),
                        "gallery": random.choices(ITEMS, k=8),
                        "cuffed": random.choice([True, False])
                    },
                    {
                        "health": random.randint(1, 5),
                        "gallery": random.choices(ITEMS, k=8),
                        "cuffed": random.choice([True, False])
                    }
                ],
                "gun": {
                    "crit": random.choice([True, False]),
                    "chamber": random.choices([True, False], k=random.randint(2, 8))
                }
            }
            
            # Send start info to both players   
            print(f"Start info: {startInfo}")
            await connected_clients[0].send(json.dumps(startInfo))
            startInfo.update({"players": startInfo["players"][::-1]})  # Reverse players
            await connected_clients[1].send(json.dumps(startInfo))

            startInfoSent = True

        async for message in websocket:
            data = json.loads(message)
            print(f"Received message: {message}")
            if data.get('type') == 'heartbeat':
                await websocket.send(json.dumps({'type': 'heartbeat_ack'}))  # Respond to heartbeat
            if data.get('type') == 'reset':
                startInfoSent = False
                print("Resetting")

    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed normally")
    finally:
        # Remove client from connected clients list on disconnect
        connected_clients.remove(websocket)
        print(f"Client disconnected: {len(connected_clients)} clients connected")

async def main():
    print("Server is Starting...")
    server = await websockets.serve(handler, "localhost", 5050)
    print(f"Listening on {server.local_address}:{server.local_port}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())