import aioconsole
import asyncio
import socket
import json


PORT = 5555


async def send_json(
        s: socket.socket,
        data: dict,
        loop: asyncio.AbstractEventLoop
) -> None:
    """
    wrapper for sending json objects through sockets

    :param s: target socket
    :param data: json object
    :param loop: asyncio eventloop
    """
    await loop.sock_sendall(
        s,
        json.dumps(data).encode('utf8')
    )


async def recv_json(
        s: socket.socket,
        loop: asyncio.AbstractEventLoop
) -> dict:
    """
    wrapper for receiving json objects through sockets

    :param s: target socket
    :param loop: asyncio eventloop
    :returns: json object
    """
    data = await loop.sock_recv(s, 1024)
    return json.loads(data.decode('utf-8'))


async def send_answer(
        client,
        question,
        loop: asyncio.AbstractEventLoop
) -> None:
    """
    wrapper for sending json objects through sockets

    :param s: target socket
    :param data: json object
    :param loop: asyncio eventloop
    """
    a = await aioconsole.ainput('Answer: ')
    await send_json(client, {
        "type": "answer",
        "answer_to": question["id"],
        "answer": [
            str,
            bool,
            int
        ][question["question_type"]](a)
    }, loop)


async def main(loop: asyncio.AbstractEventLoop) -> None:
    host = input("Enter host: ")

    # clients = []

    # for _ in range(19):
    print("connecting...", end="\r")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, PORT))
    client.setblocking(False)

    print("connected     ")
    username = input("Enter username: ")
    # username = f"User {_}"

    await send_json(client, {"type": "login", "username": username}, loop)
    answer = await recv_json(client, loop)

    if answer["type"] == "error":
        print(f"Failed to log in: {answer["reason"]}")
        return

        # clients.append(client)

    #     await asyncio.sleep(.5)
    #
    # await asyncio.sleep(5)
    # for client in clients:
    #     client.close()
    #     await asyncio.sleep(.5)

    # exit(0)

    print("waiting for game to start ...")

    while True:
        question = await recv_json(client, loop)
        match question["type"]:
            case "question":
                print("\n", question["question"])

                if question["question_type"] == 2:
                    print(f"Choices: {question["choices"]}")

                _ = loop.create_task(send_answer(client, question, loop))

            case "stats":
                print(f"\nSTATISTICS: {question['ranking']}")

            case "error":
                match question["error_type"]:
                    case 3:
                        print("Question Timeout!!!")

                    case _:
                        print(question)

            case _:
                print(question)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main(loop))
    loop.run_forever()
