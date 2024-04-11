"""
questions_screen.py
11.04.2024

It's literally in the file name, what did you expect?

Author:
Nilusink
"""
from client_comms import Client
import customtkinter as ctk
import asyncio


class QuestionsScreen(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            *args,
            **kwargs
    ) -> None:
        super().__init__(
            parent,
            *args,
            fg_color="#dddddd",
            corner_radius=0,
            border_width=0,
            **kwargs
        )

        self._questions_box = ctk.CTkFrame(
            self,
            fg_color="#dcdcdc"
        )

        self._question_text = ctk.CTkLabel(
            self._questions_box,
            text="",
            font=("Arial", 20)
        )
