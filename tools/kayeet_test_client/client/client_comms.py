"""
client_comms.py
11. April 2024

Defines, how a client should communicate with the server

Author:
Nilusink
"""
from ._question_handler import QuestionHandler
import asyncio
import socket
import json


class Client:
    def __init__(
            self,
            event_loop: asyncio.AbstractEventLoop,
            handler: QuestionHandler
    ) -> None:
        self._handler = handler

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.settimeout(2)

        self._loop_future = ...
        self._loop = event_loop

        self._username = ...

        self.running = True

    @property
    def username(self) -> str:
        """
        the username the client has logged in with
        """
        return self._username

    async def connect(self, host: str, port: int = 5555) -> bool:
        """
        connect to a KaYeet! Server
        """
        try:
            await self._loop.sock_connect(self._socket, (host, port))
            return True

        except (
            ConnectionRefusedError,
            socket.gaierror,
            TimeoutError,
            OSError
        ):
            return False

    async def login(self, username: str) -> bool:
        """
        try to log in the user
        """
        await self.send_message({
            "type": "login",
            "username": username
        })

        reply = await self.receive_message()
        if reply["type"] == "answer":
            self._username = username
            print(username, self._username)
            self._loop_future = self._loop.create_task(self.run())
            return True

        elif reply["type"] == "error":
            return False

        return False

    async def send_message(self, message: dict) -> None:
        """
        send a message to the server
        """
        await self._loop.sock_sendall(
            self._socket,
            json.dumps(message).encode('utf8')
        )

    async def receive_message(self) -> dict | None:
        """
        receive a message from the server
        """
        try:
            request = await self._loop.sock_recv(self._socket, 1024)

        except (socket.gaierror, ConnectionAbortedError):
            self.close()
            return None

        if request == b"":
            self.close()
            return

        return json.loads(request.decode('utf8'))

    async def run(self) -> None:
        """
        handles all messages from a client
        """
        while self.running:
            request_data = await self.receive_message()
            if not request_data:
                return

            try:
                match request_data["type"]:
                    case "question":
                        print("question")
                        self._handler.queue_question(request_data)

                    # case "answer":
                    #     # happens only once on successful login
                    #     ...

            except KeyError:
                continue

    def close(self) -> None:
        self.running = False
        self._socket.close()
