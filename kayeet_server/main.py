"""
main.py
?. April 2024

Server shenanigans

Author:
Nilusink
"""
from server import Server, HOST, PORT, WS_PORT
import asyncio


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = Server(HOST, PORT, WS_PORT, loop)
    loop.create_task(server.run())
    loop.run_forever()
