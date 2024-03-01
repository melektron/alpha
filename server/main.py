import json
import asyncio
from websockets.server import serve 

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())


data = json.load(open("questions.json", "r"))

data = [
    {"question": "In welche klasse gehe ich?", "type": 0, "answer": ["4AHEL", "4BHEL", "4AHBT", "4AHET"]}
]

message = json.dumps(data[0])
