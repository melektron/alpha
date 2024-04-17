"""
gui.pyw
11.04.2024

basically a Kahoot clone

Author:
Nilusink
"""
from client.questions_screen import QuestionsScreen
from client.login_screen import LoginScreen
from client.client_comms import Client
import customtkinter as ctk
import tkinter as tk
import asyncio


class Window(ctk.CTk):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self._loop = loop
        self.running = True
        self._client = Client(loop)

        # window config
        self.title("KaYeet")
        self.iconbitmap("./assets/icon.ico")
        self.attributes("-fullscreen", True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._login_screen = LoginScreen(
            self,
            self._client,
            loop,
            self.logged_in
        )
        self._login_screen.grid(row=0, column=0, sticky="nsew")

        self._questions_screen = QuestionsScreen(self, self._client)
        # self.logged_in()

    async def run(self) -> None:
        while self.running:
            self.update_idletasks()
            self.update()
            await asyncio.sleep(.01)

    def logged_in(self) -> None:
        """
        called, when the login screen is done
        """
        self._login_screen.grid_forget()
        self._questions_screen.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    w = Window(loop)

    loop.create_task(w.run())
    loop.run_forever()
