"""
client.py
11. April 2024

Defines how a client should be handled

Author:
Nilusink
"""
from questions_master import QuestionsMaster
from time import perf_counter
from icecream import ic
# import typing as tp
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
        self._clients = []
        self._qid = 0
        self._unanswered = {}
        self._question_time = 100000

    def check_username(self, username: str) -> bool:
        """
        check if a username already exists
        """
        for client in self._clients:
            if username.lower() == client.username.lower():
                return True

        return False

    def append(self, client: "Client") -> None:
        """
        add a client to the clients
        """
        self._clients.append(client)

    def ask_question(self, question: dict) -> None:
        """
        ask a question to all clients and handles scores
        """
        for client in self._clients:
            client.ask_question(question, self._qid)
            self._unanswered[self._qid] = {
                "question": question,
                "client": client,
                "time": perf_counter(),
                "time_to_answer": self._question_time
            }
            self._qid += 1

    def answer_question(self, qid: int, answer: str) -> bool:
        """
        answer a specific question

        :param qid:
        :param answer:
        :return: false on timeout
        """
        if qid not in self._unanswered.keys():
            raise ValueError("invalid question id")

        stop = perf_counter()
        question = self._unanswered[qid]
        delta = stop - question["time"]

        answered = False
        if delta > question["time_to_answer"]:
            return False

        match question["question"]["type"]:
            case 0:
                if question["question"]["match_case"]:
                    answered = answer in question["question"]["valid"]

                else:
                    answered = answer.lower() in [a.lower() for a in question["question"]["valid"]]

        # calculate points
        points = 0
        if answered:
            points = (question["time_to_answer"] - delta) * 100

        question["client"].score += points
        return True


CLIENTS = Clients()


class Client:
    def __init__(self, client: socket.socket) -> None:
        ic("client instance")
        self._qmaster = QuestionsMaster()  # will be the same instance
        self._active_question = ...
        self._username = ...
        self._socket = client
        self.running = True
        self._score = 0
        CLIENTS.append(self)

        self._loop = asyncio.get_event_loop()

    @property
    def username(self) -> None:
        return self._username

    @property
    def logged_in(self) -> bool:
        return self._username is not ...

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        ic("new score: ", value)
        self._score = value

    async def send_client(self, message: dict) -> None:
        """
        send a message to the user
        """
        await self._loop.sock_sendall(
            self._socket,
            json.dumps(message).encode('utf8')
        )

    async def receive_client(self) -> dict:
        """
        receive a message from the client
        """
        request = await self._loop.sock_recv(self._socket, 1024)
        ic("new message: ", request)
        return json.loads(request.decode('utf8'))

    async def ask_question(self, question: dict, qid: int) -> None:
        """

        :param question:
        :param qid:
        :return:
        """
        self._active_question = qid
        await self.send_client({
            "id": qid,
            "type": "question",
            "question_type": question["question_type"],
            "question": question["question"]
        })

    async def run(self) -> None:
        """
        handles all messages from a client
        """
        while self.running:
            request_data = await self.receive_client()

            try:
                match request_data["type"]:
                    case "login":
                        username = request_data["username"]

                        # check if a user with the same name is already signed in
                        if CLIENTS.check_username(username):
                            await self.send_client({
                                "type": "error",
                                "error_type": 0,  # InvalidLogin,
                                "cause": "Username already taken"
                            })
                            continue

                        # confirm login
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
                await self.send_client({
                    "type": "error",
                    "error_type": 3  # InvalidMessage
                })

    def close(self) -> None:
        self.running = False
        self._socket.close()
        self._socket.shutdown(1)
