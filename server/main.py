from questions_master import QuestionsMaster
from client import Client, CLIENTS
from icecream import ic
import aioconsole
import asyncio
import socket


HOST = '0.0.0.0'
PORT = 5555


# def load_questions(filename, num_questions):
#     questions = []
#     with open(filename, 'r') as file:
#         for line in file:
#             question, answer = line.strip().split(';')
#             questions.append((question, answer))
#         questions = random.sample(questions, num_questions)
#     return questions
#
#
# def handle_client(connection, address):
#     print(f"Connected to {address}")
#     score = 0
#     total_questions = len(questions)
#
#     name = connection.recv(1024).decode().strip()
#     connection.sendall(f"Hallo {name}. Wir wünschen dir viel Spaß bei diesem kleinem Quiz. \n".encode())
#
#     for i, (question, answer) in enumerate(questions, start=1):
#         connection.sendall(question.encode())
#         client_answer = connection.recv(1024).decode().strip()
#         if client_answer.lower() == answer.lower():
#             score += 1
#             connection.sendall("Correct!\n".encode())
#         else:
#             connection.sendall(f"Incorrect!\nThe correct answer is {answer}\n".encode())
#
#     connection.sendall(f"Your final score is {score}/{total_questions}\n".encode())
#     update_leaderboard(name, score)
#     print(f"Connection with {address} closed.")
#     connection.close()
#
#
# def get_leaderboard():
#     sorted_leaderboard = sorted(leaderboard.items(), key=operator.itemgetter(1), reverse=True)
#     leaderboard_str = ""
#     for i, (name, score) in enumerate(sorted_leaderboard, start=1):
#         leaderboard_str += f"{i}. {name}: {score}\n"
#     return leaderboard_str
#
#
# def update_leaderboard(name, score):
#     leaderboard[name] = score
#     with open('leaderboard.txt', 'a') as file:
#         for name, score in leaderboard.items():
#             file.write(f"{name};{score};{len(questions)}\n")


class Server:
    def __init__(self, host: str, port: int, loop: asyncio.AbstractEventLoop):
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
        self._qmaster = QuestionsMaster()
        self._qmaster.load_from_file("./questions.json")

        self._loop = loop

    async def receive_clients(self):
        ic("receiving")
        while self.running:
            try:
                ic("waiting")
                c, _ = await self._loop.sock_accept(self._socket)
                # c, _ = self._socket.accept()
                ic("new client")

            except TimeoutError:
                ic("timeout")
                continue

            except Exception as e:
                ic("error accepting: ", e)
                continue

            client = Client(c)

            if self._accepting:
                self._loop.create_task(client.run())

            # reject clients, if time is over
            else:
                await client.send_client({
                    "type": "error",
                    "error_type": 0,
                    "cause": "login over"
                })

    async def run(self):
        # global questions
        # number_of_questions = 10
        # questions = load_questions('questions.txt', number_of_questions)
        #
        # global leaderboard
        # leaderboard = {}
        #
        #
        # print(f"Server listening on {host}:{port}")
        #
        # while True:
        #     client_conn, client_addr = server.accept()
        #     # handle_client(client_conn, client_addr)
        #     Thread(target=handle_client, args=(client_conn, client_addr)).start()

        f = self._loop.create_task(self.receive_clients())
        ic("created task")

        try:
            # await aioconsole.ainput('Press enter to start! ')
            await asyncio.sleep(100000)

            # stop accepting clients
            self._accepting = False

            # start questioning
            questions = self._qmaster.get_random_question(
                n_questions=10,
            )

            for question in questions:
                ...

        finally:
            for client in CLIENTS:
                client.close()

            await f


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = Server(HOST, PORT, loop)
    asyncio.run(server.run())
