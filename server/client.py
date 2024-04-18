"""
client.py
11. April 2024

Defines how a client should be handled

Author:
Nilusink
"""
from websockets.legacy.server import WebSocketServerProtocol
from questions_master import QuestionsMaster
from time import perf_counter
from icecream import ic
import typing as tp
import math as m
import asyncio
import socket
import json


class Clients:
    __instance = ...

    def __new__(cls, *args, **kwargs):
        if cls.__instance is ...:
            cls.__instance = super(Clients, cls).__new__(cls)
            ic("new clients instance")

        return cls.__instance

    def __init__(self) -> None:
        self._clients: list["Client"] = []
        self._qid = 0
        self._unanswered = {}
        self._question_time = 15
        self._current_timeout = ...

    def check_username(self, username: str) -> bool:
        """
        check if a username already exists
        """
        for client in self._clients:
            if client.logged_in:
                if username.lower() == client.username.lower():
                    return True

        return False

    def append(self, client: "Client") -> None:
        """
        add a client to the clients
        """
        self._clients.append(client)

    def remove(self, client: "Client") -> None:
        if client in self._clients:
            self._clients.remove(client)

    async def ask_question(self, question: dict) -> None:
        """
        ask a question to all clients and handles scores
        """
        futures = []
        for client in self._clients:
            futures.append(client.ask_question(question, self._qid))
            self._unanswered[self._qid] = {
                "question": question,
                "client": client,
                "time": perf_counter(),
                "time_to_answer": self._question_time
            }

            self._qid += 1

        await asyncio.gather(*futures)

        # start time
        self._current_timeout = perf_counter()

    async def send_all(self, data: dict) -> None:
        """
        send a message to all clients
        """
        futures = []
        for client in self._clients:
            futures.append(client.send_client(data))

        await asyncio.gather(*futures)

    async def question_done(self) -> None:
        """
        waits until the question is over
        """
        while perf_counter() - self._current_timeout < self._question_time:
            # all clients done
            if len(self._unanswered) == 0:
                break

            await asyncio.sleep(.5)

        # remove any unanswered questions
        futures = []
        for question in self._unanswered.values():
            futures.append(question["client"].send_client({
                "type": "error",
                "error_type": 3
            }))

        self._unanswered.clear()
        await asyncio.gather(*futures)

    def answer_question(self, qid: int, answer: str) -> bool:
        """
        answer a specific question

        :param qid:
        :param answer:
        :return: false on timeout
        """
        if qid not in self._unanswered.keys():
            raise ValueError("invalid question id")

        ic(answer)

        stop = perf_counter()
        question = self._unanswered[qid]
        self._unanswered.pop(qid)
        delta = stop - question["time"]

        answered = False
        if delta > question["time_to_answer"]:
            return False

        match question["question"]["question_type"]:
            case 0:
                answer = answer.lstrip().strip()

                if question["question"]["match_case"]:
                    answered = answer in question["question"]["valid"]

                else:
                    answered = answer.lower() in [
                        a.lower() for a in question["question"]["valid"]
                    ]

            case 1:
                answered = answer == question["question"]["valid"]

            case 2:
                answered = answer in question["question"]["valid"]

        # calculate points
        points = 0
        if answered:
            points = m.ceil((
                (question["time_to_answer"] - delta)/question["time_to_answer"]
            ) * 1000)

        question["client"].score += points
        ic(points)
        return True

    async def send_statistics(self) -> None:
        """
        update all clients about the current rankings
        """
        ranking = [(c.score, c.username) for c in self._clients]
        ranking = sorted(ranking, key=lambda _: _[1], reverse=True)

        await self.send_all({
            "type": "stats",
            "ranking": ranking
        })

    def __iter__(self) -> tp.Iterator:
        return iter(self._clients)


CLIENTS = Clients()


class Client:
    def __init__(self, client: socket.socket) -> None:
        ic("client instance")
        self._qmaster = QuestionsMaster  # will be the same instance
        self._active_question = ...
        self._username = ...
        self._socket = client
        self.running = True
        self._score = 0
        CLIENTS.append(self)

        self._loop = asyncio.get_event_loop()

    @property
    def username(self) -> str:
        return self._username

    @property
    def logged_in(self) -> bool:
        return self._username is not ...

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        self._score = value

    async def send_client(self, message: dict) -> None:
        """
        send a message to the user
        """
        await self._loop.sock_sendall(
            self._socket,
            json.dumps(message).encode('utf8')
        )

    async def receive_client(self) -> dict | None:
        """
        receive a message from the client
        """
        try:
            request = await self._loop.sock_recv(self._socket, 1024)

        except (
                socket.gaierror,
                ConnectionAbortedError,
                ConnectionResetError
        ) as e:
            ic("closed: ", e)
            self.close()
            return None

        if request == b"":
            ic("client disconnect", self.username)
            self.close()
            return

        ic("new message: ", request)
        return json.loads(request.decode('utf8'))

    async def ask_question(self, question: dict, qid: int) -> None:
        """

        :param question:
        :param qid:
        :return:
        """
        self._active_question = qid
        data = {
            "id": qid,
            "type": "question",
            "question_type": question["question_type"],
            "question": question["question"]
        }

        if question["question_type"] == 2:
            data["choices"] = question["choices"]

        await self.send_client(data)

    async def run(self) -> None:
        """
        handles all messages from a client
        """
        while self.running:
            request_data = await self.receive_client()
            if not request_data:
                return

            try:
                match request_data["type"]:
                    case "login":
                        username = request_data["username"]

                        # check if a user with the same
                        # name is already signed in
                        if CLIENTS.check_username(username):
                            await self.send_client({
                                "type": "error",
                                "error_type": 0,  # InvalidLogin,
                                "cause": "Username already taken"
                            })
                            continue

                        # confirm login
                        self._username = username
                        ic("client logged in as ", username)
                        await self.send_client({
                            "type": "answer"
                        })

                    case "answer":
                        if request_data["answer_to"] == self._active_question:
                            self._active_question = ...
                            CLIENTS.answer_question(
                                request_data["answer_to"],
                                request_data["answer"]
                            )

                        else:
                            await self.send_client({
                                "type": "error",
                                "error_type": 4,  # QuestionTimeout
                            })

                    case _:
                        # send error to client
                        await self.send_client({
                            "type": "error",
                            "error_type": 2  # InvalidRequest
                        })

            except KeyError:
            # except KeyboardInterrupt:
                await self.send_client({
                    "type": "error",
                    "error_type": 3  # InvalidMessage
                })

    def close(self) -> None:
        self.running = False
        self._socket.close()
        CLIENTS.remove(self)


class WsClient(Client):
    def __init__(self, client: WebSocketServerProtocol) -> None:
        super().__init__(...)
        self._socket = client

    async def send_client(self, message: dict) -> None:
        """
        send a message to the user
        """
        await self._socket.send(json.dumps(message))

    async def receive_client(self) -> dict | None:
        """
        receive a message from the client
        """
        try:
            request = await self._socket.recv()

        except (
                socket.gaierror,
                ConnectionAbortedError,
                ConnectionResetError
        ) as e:
            ic("closed: ", e)
            self.close()
            return None

        if request == b"":
            ic("client disconnect", self.username)
            self.close()
            return

        ic("new message: ", request)
        return json.loads(request.decode('utf8'))
