import json
import asyncio
from websockets.server import serve 

#Example for the questions in json 
"""
data = [
    {"question": "In welche klasse gehe ich?", "type": 0, "answer": ["4AHEL", "4BHEL", "4AHBT", "4AHET"]}
]
"""


def get_questions(): 
    data = json.load(open("questions.json", "r"))
    message = json.dumps(data[0])

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__": 
    asyncio.run(main())