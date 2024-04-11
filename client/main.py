import socket
import time


def main():
    host = '127.0.0.1'
    port = 5555

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    name = input("Enter your name: ")
    client.sendall(name.encode())
    response = client.recv(1024).decode().strip()
    print(response)  # Acknowledge name received

    while True:
        ranking = client.recv(1024).decode()
        question = client.recv(1024).decode()

        print(question)
        start_time = time.time()

        if question.startswith("Your final score"):
            break

        answer = input("Your answer: ")
        stop_time = time.time()
        used_time = round(stop_time - start_time, 2)
        message = answer + ";" + used_time
        client.sendall(message.encode())

        response = client.recv(1024).decode()
        print(response)

    client.close()


if __name__ == "__main__":
    main()
