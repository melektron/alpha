import json
import asyncio
from websockets.server import serve 
import random
import websockets

#Example for the questions in json 
"""
data = [
    {"question": "In welche klasse gehe ich?", "type": 0, "answer": ["4AHEL", "4BHEL", "4AHBT", "4AHET"]}
]
"""


def get_questions(num_questions)->list: 
    data = json.load(open("questions.json", "r"))
    chosen_questions = random.sample(data, num_questions)
    return chosen_questions

        

async def echo(websocket:websockets.WebSocketServerProtocol):
    async for message in websocket:
        await websocket.send(message)

async def main():
    x=get_questions(2) 
    print(x)
    """
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever
    """
if __name__ == "__main__": 
    asyncio.run(main())