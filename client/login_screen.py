"""
login_screen.py
11.04.2024

the connection and login screens

Author:
Nilusink
"""
from client_comms import Client
import customtkinter as ctk
import typing as tp
import asyncio


class LoginScreen(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            client: Client,
            event_loop: asyncio.AbstractEventLoop,
            done_callback: tp.Callable[[], None],
            *args,
            **kwargs
    ) -> None:
        super().__init__(
            parent,
            *args,
            fg_color="#2d0e5b",
            corner_radius=0,
            border_width=0,
            **kwargs
        )

        self._client = client
        self._loop = event_loop
        self._callback = done_callback

        self.grid_rowconfigure((0, 2), weight=4)
        self.grid_columnconfigure((0, 2), weight=4)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.centerer = ctk.CTkFrame(self, fg_color="transparent")
        self.centerer.grid(row=1, column=1, sticky="nsew")

        self.centerer.grid_rowconfigure((0, 1), weight=1)
        self.centerer.grid_columnconfigure(0, weight=1)

        # logo
        ctk.CTkLabel(
            self.centerer,
            text="KaYeet!",
            fg_color="transparent",
            font=("Arial", 64, "bold")
        ).grid(
            row=0, column=0, sticky="nsew", pady=40
        )

        # Login Box
        login_box = ctk.CTkFrame(
            self.centerer,
            fg_color="#ffffff",
            corner_radius=10
        )
        login_box.grid(row=1, column=0, sticky="nsew")

        login_box.grid_rowconfigure((0, 1), weight=1)
        login_box.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            login_box,
            fg_color="#ffffff",
            border_color="#cccccc",
            font=("Arial", 32),
            placeholder_text="host ip",
            placeholder_text_color="#cccccc",
            justify="center"
        )
        self.entry.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.button = ctk.CTkButton(
            login_box,
            text="Enter",
            fg_color="#333333",
            text_color="#ffffff",
            font=("Arial", 32, "bold"),
            border_width=0,
            command=self.on_connect
        )
        self.button.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        # connecting screen
        self.connecting = ctk.CTkLabel(
            self,
            text="Connecting ...",
            fg_color="transparent",
            font=("Arial", 32)
        )

    def on_connect(self):
        self._loop.create_task(self._on_connect())

    async def _on_connect(self) -> None:
        """
        connect to server
        """
        # show loading screen
        self.centerer.grid_forget()
        self.connecting.grid(row=1, column=1, sticky="nsew")

        # try to connect
        if await self._client.connect(self.entry.get().strip()):
            self.button.configure(command=self.on_login)
            self.entry.configure(placeholder_text="Nickname")
            self.entry.delete(0, ctk.END)
            self.centerer.focus_set()

        self.connecting.grid_forget()
        self.centerer.grid(row=1, column=1, sticky="nsew")

    def on_login(self) -> None:
        self._loop.create_task(self._on_login())

    async def _on_login(self) -> None:
        """
        try to log in to server
        """
        # show loading screen
        self.centerer.grid_forget()
        self.connecting.grid(row=1, column=1, sticky="nsew")

        # try to connect
        if await self._client.login(self.entry.get().strip()):
            self.button.configure(command=self.on_login)
            return self._callback()

        self.connecting.grid_forget()
        self.centerer.grid(row=1, column=1, sticky="nsew")
