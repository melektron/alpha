"""
gui.pyw
25.04.2024

the server ui

Author:
Nilusink
"""
from server import CollectionWindow, Server, HOST, PORT, WS_PORT
from server import QuestionsScreen
import customtkinter as ctk
import asyncio


class Window(ctk.CTk):
    running = True

    def __init__(
            self,
            host: str,
            port: int,
            websocket_port: int,
            loop: asyncio.AbstractEventLoop
    ) -> None:
        super().__init__()

        self.port = port
        self.ws_port = websocket_port

        # initialize server
        self._server = Server(host, port, websocket_port, loop)
        self._loop = loop

        # window config
        self.title("KaYeet Server")
        self.attributes("-fullscreen", True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # handle window close
        self.protocol("WM_DELETE_WINDOW", self.end)

        # grid stuff
        self._waiting_room = CollectionWindow(self)
        self._waiting_room.grid(row=0, column=0, sticky="nsew")

        self._questions_screen = QuestionsScreen(
            self,
            self._server,
            loop
        )

    async def run(self) -> None:
        """
        fun stuff happens here
        """
        # start server
        await self._server.start_tasks()

        while self.running:
            await self._waiting_room.update()

            self.update_idletasks()
            self.update()

            await asyncio.sleep(.02)

    def start_game(self) -> None:
        """
        start se game
        """
        self._server.start_game()

        self._waiting_room.grid_forget()
        self._questions_screen.grid(row=0, column=0, sticky="nsew")

    def game_done(self) -> None:
        """
        a question game is done
        """
        self._server.game_done()

        self._questions_screen.grid_forget()
        self._waiting_room.grid(row=0, column=0, sticky="nsew")

    def end(self) -> None:
        """
        close stuff
        """
        self.running = False
        self._loop.stop()
        exit(0)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    w = Window(HOST, PORT, WS_PORT, loop)
    loop.create_task(w.run())
    loop.run_forever()
