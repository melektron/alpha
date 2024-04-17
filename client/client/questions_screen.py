"""
questions_screen.py
11.04.2024

It's literally in the file name, what did you expect?

Author:
Nilusink
"""
from ._question_handler import QuestionHandler
from .client_comms import Client
import customtkinter as ctk
# import asyncio


class QuestionsScreen(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            client: Client,
            handler: QuestionHandler,
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
        self._handler = handler
        self._handler.on_new_question(self._on_new_question)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # waiting for game start
        self._waiting_box = ctk.CTkFrame(
            self,
            fg_color="#2d0e5b"
        )
        self._waiting_box.grid(row=0, column=0, sticky="nsew")

        self._waiting_box.grid_columnconfigure(0, weight=1)
        self._waiting_box.grid_rowconfigure((0, 1), weight=1)

        self._nickname_label = ctk.CTkLabel(
            self._waiting_box,
            text="Not Set?????",
            font=("Arial", 48)
        )
        self._nickname_label.grid(row=0, column=0, pady=10, padx=20, sticky="s")

        self.center_label = ctk.CTkLabel(
            self._waiting_box,
            text="Waiting for game start ...",
            font=("Arial", 20)
        )
        self.center_label.grid(row=1, column=0, pady=10, padx=20, sticky="n")

        self._animation_parameter = 0
        self._update_animation()

        # actual question
        self._questions_box = ctk.CTkFrame(
            self,
            fg_color="#dcdcdc"
        )

    def grid(self, **kwargs):
        super().grid(**kwargs)

        # update username on grid
        self._nickname_label.configure(text=self._client.username)

    def _on_new_question(self, handler: QuestionHandler) -> None:
        """
        a new question appeared
        """
        print("screen")
        question = handler.next()

        self._waiting_box.grid_forget()
        self._questions_box.grid(row=0, column=0, sticky="nsew")

    def _update_animation(self) -> None:
        """
        update the updating animation
        """
        if self._animation_parameter < 0:
            return

        # re-call own function
        self.after(200, self._update_animation)

        if self._animation_parameter == 0:
            self.center_label.configure(text="Waiting for game start  ..")

        elif self._animation_parameter == 1:
            self.center_label.configure(text="Waiting for game start . .")

        elif self._animation_parameter == 2:
            self.center_label.configure(text="Waiting for game start .. ")

        elif self._animation_parameter == 5:
            self._animation_parameter = 0
            return

        else:
            self.center_label.configure(text="Waiting for game start ...")

        self._animation_parameter += 1
