"""
_collection_window.pyw
25.04.2024

the waiting room thingy

Author:
Nilusink
"""
import os

from ._client import CLIENTS, Client
from customtkinter import filedialog
from ._server import Server
import customtkinter as ctk
import asyncio
import socket
import math


def get_host() -> str:
    """
    get the best host address
    """
    hostname = socket.gethostname()

    match hostname:
        case "DESKTOP-RV1IG8H":
            return "kayeet.nilus.ink"

        case "elektronlab":
            return "kayeet.elektron.work"

        case _:
            return socket.gethostbyname(hostname)


class ClientBox(ctk.CTkFrame):
    def __init__(self, parent, client: Client, **kwargs) -> None:
        self._client = client

        super().__init__(
            parent,
            corner_radius=20,
            **kwargs
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=client.username,
            font=("Arial", 24)
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=30,
        )


class CollectionWindow(ctk.CTkFrame):
    max_columns = 6

    def __init__(self, parent, server: Server, *args, **kwargs) -> None:
        self._parent = parent
        self._server = server

        # initialize parent class
        super().__init__(parent, *args, **kwargs)

        # create variables for the ui
        self._drawn_clients: list[Client] = []
        self._client_boxes: list[ClientBox] = []

        self._current_columns: int = -1
        self._current_rows: int = -1

        # reference to ensure task will continue to run
        self._start_task: asyncio.Task | None = None

        # initialize tkinter stuff
        self._init_ui()

    def _init_ui(self) -> None:
        """
        create and initialize all ctk widgets
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_box = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        title_box.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=80
        )

        title_box.grid_rowconfigure(0, weight=1)
        title_box.grid_columnconfigure(2, weight=1)

        # question set choice
        ctk.CTkLabel(
            title_box,
            text="Questions: ",
            font=("Arial", 48)
        ).grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10
        )

        self._file_btn = ctk.CTkButton(
            title_box,
            text=self._server.qmaster.question_set_name,
            font=("Arial", 32),
            command=self._open_questions
        )
        self._file_btn.grid(
            row=0,
            column=1,
        )

        # title
        self._title = ctk.CTkLabel(
            title_box,
            text=f"Host: {get_host()}",
            font=("Arial", 64)
        )
        self._title.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=20,
            pady=80
        )

        def start_callback() -> None:
            self._start_task = asyncio.create_task(
                self._parent.start_game()
            )

        ctk.CTkButton(
            self,
            text="Start",
            font=("Arial", 48),
            command=start_callback,
            corner_radius=30
        ).grid(
            row=0,
            column=1,
            padx=100
        )

        self._clients_box = ctk.CTkFrame(self, corner_radius=30)
        self._clients_box.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=60,
            pady=60
        )

        self._current_columns = 0
        self._current_rows = 0

    def _open_questions(self) -> None:
        """
        choose a new file to load questions from
        """
        file = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Json files", ".json")],
            initialdir=os.getcwd(),
            title="Load Questions"
        )

        # don't change anything if no file has been chosen
        if not isinstance(file, str) or not file:
            return

        # discard old questions and load new ones
        self._server.qmaster.reset_questions()
        self._server.qmaster.load_from_file(file)

    def reset_grid(self) -> None:
        """
        reset all weights in the grid
        """
        self._clients_box.grid_rowconfigure(
            list(range(self._current_rows+1)),
            weight=0
        )
        self._clients_box.grid_columnconfigure(
            list(range(self._current_columns + 1)),
            weight=0
        )

    async def update(self) -> None:
        """
        update stuff here
        """
        # fancy set stuff
        drawn_clients = set(self._drawn_clients)
        current_clients = {
            client for client in CLIENTS if client.username is not ...
        }

        new_clients = current_clients - drawn_clients
        disconnected_clients = drawn_clients - current_clients

        # only update, if a change has been made
        if len(new_clients) + len(disconnected_clients) > 0:
            start_i = len(self._drawn_clients)

            for client in disconnected_clients:
                self._drawn_clients.remove(client)

            for client in new_clients:
                self._drawn_clients.append(client)

            # adjust grid
            self.reset_grid()

            n_clients = len(self._drawn_clients)
            self._current_columns = (
                self.max_columns if n_clients > self.max_columns else n_clients
            )
            self._current_rows = math.ceil(n_clients / self.max_columns)

            if self._current_columns == 0:
                return

            self._clients_box.grid_columnconfigure(
                list(range(self._current_columns)),
                weight=1
            )
            self._clients_box.grid_rowconfigure(
                list(range(self._current_rows)),
                weight=1
            )

            if len(disconnected_clients) > 0:
                # de-grid everything
                for frame in self._client_boxes:
                    frame.grid_forget()

                # re-draw all clients
                for i, client in enumerate(self._drawn_clients):
                    column = i % self.max_columns
                    row = i // self.max_columns

                    tmp = ClientBox(self._clients_box, client)
                    tmp.grid(row=row, column=column, padx=10, pady=10)

                    self._client_boxes.append(tmp)

            else:
                # only draw new clients
                for add_i, client in enumerate(new_clients):
                    i = start_i + add_i
                    column = i % self.max_columns
                    row = i // self.max_columns

                    tmp = ClientBox(self._clients_box, client)
                    tmp.grid(row=row, column=column, padx=10, pady=10)

                    self._client_boxes.append(tmp)
