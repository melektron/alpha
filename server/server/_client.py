"""
_client.py
11. April 2024

Defines how a client should be handled

Author:
Nilusink
"""
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from websockets.legacy.server import WebSocketServerProtocol
from ._questions_master import QuestionsMaster, Question
from time import perf_counter
from icecream import ic
import typing as tp
import math as m
import asyncio
import socket
import json


class UnansweredQ(tp.TypedDict):
    question: Question
    client: "Client"
    time: float
    time_to_answer: int

class AnsweredQ(tp.TypedDict):
    question: Question
    id: int
    client: "Client"
    points: int
    result: bool

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
        self._unanswered: dict[int, UnansweredQ] = {}
        self._answered: list[AnsweredQ] = []
        self._question_time = 20
        self._current_timeout = ...
        self.__skip_question: bool = False

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

    async def ask_question(self, question: Question) -> None:
        """
        ask a question to all clients and handles scores
        """
        futures = []
        self._answered.clear()
        self.__skip_question = False
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

    async def wait_question_done(self) -> tp.AsyncIterator[tuple[
        int, int, int
    ]]:
        """
        waits until the question is over.
        yields the time left, number of answers and added answers when 
        changed during waiting
        """
        last_nr_answers = 0
        # initial yield to update UI
        yield (last_nr_answers, 0, self._question_time - (perf_counter() - self._current_timeout))

        # #websockets.exceptions.ConnectionClosedError
        
        while self._question_time - (perf_counter() - self._current_timeout) > 0:

            nr_answers = 0
            new_answers = 0
            # if nr of answers changed, update that
            if last_nr_answers != len(self._answered):
                new_answers = len(self._answered) - last_nr_answers
                nr_answers = len(self._answered)
                last_nr_answers = nr_answers
            # update time left
            time_left: float = self._question_time - (perf_counter() - self._current_timeout)
            if time_left < 0:
                time_left = 0
            # yield the update
            yield (
                nr_answers,     # nr of answers
                new_answers,    # nr of answers delta
                int(time_left)  # time left (in seconds)
            )

            # if all clients are done, exit
            if len(self._unanswered) == 0:
                break

            # if the question was skipped, exit
            elif self.__skip_question:
                break

            await asyncio.sleep(.2)

        # remove any unanswered questions
        futures = []
        for question in self._unanswered.values():
            futures.append(question["client"].send_client({
                "type": "error",
                "error_type": 4  # QuestionTimeout
            }))

        # send results to all clients who answered
        for answer in self._answered:
            futures.append(answer["client"].send_client({
                "type": "result",
                "result_to": answer["id"],
                "result": answer["result"]
            }))

        self._unanswered.clear()
        await asyncio.gather(*futures)

    def skip_question(self) -> None:
        """
        skip the currently active question
        """
        self.__skip_question = True

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

        self._answered.append({
            "question": question,
            "id": qid,
            "client": question["client"],
            "points": points,
            "result": answered
        })

        return True

    def get_leaderboard(self) -> list[tuple[int, str]]:
        """
        get the current leaderboard, sorted by score
        """
        ranking = [(c.score, c.username) for c in self._clients]
        ranking = sorted(ranking, key=lambda _: _[0], reverse=True)

        return ranking

    async def send_statistics(self) -> None:
        """
        update all clients about the current rankings
        """

        await self.send_all({
            "type": "stats",
            "ranking": self.get_leaderboard()
        })

    def __iter__(self) -> tp.Iterator:
        return iter(self._clients)

    def __len__(self) -> int:
        return len(self._clients)


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
                            "type": "confirm"
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
        CLIENTS.remove(self)


class WsClient(Client):
    def __init__(self, client: WebSocketServerProtocol) -> None:
        super().__init__(...)
        self._socket = client

    async def send_client(self, message: dict) -> None:
        """
        send a message to the user
        """
        try:
            await self._socket.send(json.dumps(message))

        except (
                socket.gaierror,
                ConnectionAbortedError,
                ConnectionResetError,
                ConnectionClosedOK,
                ConnectionClosedError
        ):
            await self.close()

    async def receive_client(self) -> dict | None:
        """
        receive a message from the client
        """
        try:
            request = await self._socket.recv()

        except (
                socket.gaierror,
                ConnectionAbortedError,
                ConnectionResetError,
                ConnectionClosedOK,
                ConnectionClosedError
        ) as e:
            ic("closed: ", e)
            await self.close()
            return

        if request == b"":
            ic("client disconnect", self.username)
            await self.close()
            return

        ic("new message: ", request)
        return json.loads(request)

    async def close(self) -> None:
        self.running = False
        await self._socket.close()
        CLIENTS.remove(self)
