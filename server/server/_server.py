from ._questions_master import QuestionsMaster
from ._client import Client, CLIENTS, WsClient
from websockets.legacy.server import WebSocketServerProtocol
from websockets.server import serve
from icecream import ic
import aioconsole
import asyncio
import socket


HOST = '0.0.0.0'
PORT = 5555
WS_PORT = 1647


class Server:
    def __init__(
            self,
            host: str,
            port: int,
            websocket_port: int,
            loop: asyncio.AbstractEventLoop
    ) -> None:
        self._ws_port = websocket_port
        self._address = (host, port)
        self._accepting = True
        self.running = True

        # initialize socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((HOST, PORT))
        self._socket.settimeout(2)
        self._socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )
        self._socket.setblocking(False)
        self._socket.listen()

        # create questions master
        self._qmaster = QuestionsMaster
        self._qmaster.load_from_file("./questions.json")
        self._questions = ...
        self._current_question = -1

        self._loop = loop

    async def receive_clients(self):
        ic("receiving")
        while self.running:
            try:
                ic("waiting")
                c, _ = await self._loop.sock_accept(self._socket)
                ic("new client")

            except TimeoutError:
                ic("timeout")
                continue

            except Exception as e:
                ic("error accepting: ", e)
                continue

            client = Client(c)

            if self._accepting:
                self._ = self._loop.create_task(client.run())

            # reject clients, if time is over
            else:
                await client.send_client({
                    "type": "error",
                    "error_type": 0,
                    "cause": "login over"
                })

    async def receive_ws_clients(self) -> None:
        """
        the same as receive_clients, but for websockets
        """
        async def wrapper(c: WebSocketServerProtocol):
            ic("new websocket client")
            client = WsClient(c)

            if self._accepting:
                await self._loop.create_task(client.run())

            # reject clients, if time is over
            else:
                await client.send_client({
                    "type": "error",
                    "error_type": 0,
                    "cause": "login over"
                })

        async with serve(wrapper, self._address[0], self._ws_port):
            await asyncio.Future()  # run forever

    async def start_tasks(self) -> None:
        self._ = self._loop.create_task(self.receive_clients())
        self._ = self._loop.create_task(self.receive_ws_clients())

    def create_questions(self, n: int) -> None:
        """
        generate new questions
        """
        self._questions = self._qmaster.get_random_question(
            n_questions=n,
        )
        self._current_question = 0

    def next_question(self) -> dict | None:
        try:
            out = self._questions[self._current_question]

        except IndexError:
            return None

        self._current_question += 1

        return out

    def start_game(self) -> None:
        """
        start game and stuff
        """
        # stop accepting clients
        self._accepting = False

        # start questioning
        self.create_questions(10)

    async def run(self):
        """
        run everything
        """
        # save to garbage
        await self.start_tasks()
        ic("created task")

        try:
            while True:
                await aioconsole.ainput('Press enter to start! ')
                ic("starting questions")

                self.start_game()

                for question in self._questions:
                    await CLIENTS.ask_question(question)
                    await CLIENTS.question_done()
                    await CLIENTS.send_statistics()

        except Exception as e:
            ic(e)

        finally:
            for client in CLIENTS:
                client.close()

            raise
