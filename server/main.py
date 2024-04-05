import socket
import operator
import random
from threading import Thread

def load_questions(filename, num_questions):
    questions = []
    with open(filename, 'r') as file:
        for line in file:
            question, answer = line.strip().split(';')
            questions.append((question, answer))
        questions=random.sample(questions, num_questions)
    return questions

def handle_client(connection, address):
    print(f"Connected to {address}")
    score = 0
    total_questions = len(questions)

    name = connection.recv(1024).decode().strip()
    connection.sendall(f"Hallo {name}. Wir wünschen dir viel Spaß bei diesem kleinem Quiz. \n".encode())

    for i, (question, answer) in enumerate(questions, start=1):
        connection.sendall(question.encode())
        client_answer = connection.recv(1024).decode().strip()
        if client_answer.lower() == answer.lower():
            score += 1
            connection.sendall("Correct!\n".encode())
        else:
            connection.sendall(f"Incorrect!\nThe correct answer is {answer}\n".encode())

    connection.sendall(f"Your final score is {score}/{total_questions}\n".encode())
    update_leaderboard(name, score)
    print(f"Connection with {address} closed.")
    connection.close()

def get_leaderboard():
    sorted_leaderboard = sorted(leaderboard.items(), key=operator.itemgetter(1), reverse=True)
    leaderboard_str = ""
    for i, (name, score) in enumerate(sorted_leaderboard, start=1):
        leaderboard_str += f"{i}. {name}: {score}\n"
    return leaderboard_str

def update_leaderboard(name, score):
    leaderboard[name] = score
    with open('leaderboard.txt', 'a') as file:
        for name, score in leaderboard.items():
            file.write(f"{name};{score};{len(questions)}\n")

def main():
    host = '192.168.197.76'
    port = 5555

    global questions
    number_of_questions = 10 
    questions = load_questions('questions.txt',number_of_questions)

    global leaderboard
    leaderboard = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_conn, client_addr = server.accept()
        # handle_client(client_conn, client_addr)
        Thread(target=handle_client, args=(client_conn, client_addr)).start()

if __name__ == "__main__":
    main()
