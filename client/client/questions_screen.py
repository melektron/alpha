"""
questions_screen.py
11.04.2024

It's literally in the file name, what did you expect?

Author:
Nilusink
"""
from ._question_handler import QuestionHandler, TextQuestion, YesNoQuestion
from ._question_handler import ChoiceQuestion, Question
from .client_comms import Client
import customtkinter as ctk
import asyncio


class QuestionsScreen(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            client: Client,
            event_loop: asyncio.AbstractEventLoop,
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
        self._loop = event_loop
        self._handler = handler
        self._handler.on_new_question(self._on_new_question)
        self._current_question: Question = ...

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

        self._questions_box.grid_rowconfigure(0, weight=1)
        self._questions_box.grid_rowconfigure(1, weight=3)
        self._questions_box.grid_columnconfigure(0, weight=1)

        self._question_title = ctk.CTkLabel(
            self._questions_box,
            font=("Arial", 32),
            text="Le Question",
            text_color="#111111"
        )
        self._question_title.grid(row=0, column=0)

        # text answered questions
        self._text_question_box = ctk.CTkFrame(
            self._questions_box,
            corner_radius=25,
            fg_color="#bbbbbb"
        )

        self._text_question_box.grid_rowconfigure((0, 1), weight=1)
        self._text_question_box.grid_columnconfigure(0, weight=1)

        self._text_question_entry = ctk.CTkEntry(
            self._text_question_box,
            font=("Arial", 24),
            text_color="#111111",
            placeholder_text="Your Answer",
            fg_color="#ffffff",
            border_color="#dddddd"

        )
        self._text_question_entry.grid(row=0, column=0, sticky="s", padx=20, pady=20)
        self._text_question_entry.bind(
            '<Return>',
            lambda *_: self._answer_text_question()
        )

        self._text_question_done_button = ctk.CTkButton(
            self._text_question_box,
            font=("Arial", 20),
            text="Submit",
            command=self._answer_text_question
        )
        self._text_question_done_button.grid(row=1, column=0, sticky="n", padx=20)

        # multiple choice questions
        self._choice_box = ctk.CTkFrame(
            self._questions_box,
            corner_radius=25,
            fg_color="#bbbbbb"
        )

    def grid(self, **kwargs):
        super().grid(**kwargs)

        # update username on grid
        self._nickname_label.configure(text=self._client.username)

    def _on_new_question(self, handler: QuestionHandler) -> None:
        """
        a new question appeared
        """
        self._current_question: Question = ...

        # get new question
        question = handler.next()

        # adjust UI
        self._waiting_box.grid_forget()
        self._questions_box.grid(row=0, column=0, sticky="nsew")

        self._question_title.configure(text=question.question)

        if isinstance(question, TextQuestion):
            self._text_question_box.grid(
                row=1,
                column=0,
                sticky="nsew",
                padx=40,
                pady=50
            )

        elif isinstance(question, YesNoQuestion):
            ...

        elif isinstance(question, ChoiceQuestion):
            ...

        else:
            raise ValueError(
                f"Question of type {question.__class__.__name__} "
                f"not recognized"
            )

        self._current_question = question

    def _answer_text_question(self) -> None:
        """
        sends an answer to a text question
        """
        if self._current_question is ...:
            return

        # send message to server
        self._loop.create_task(self._client.send_message(
            self._current_question.answer(
                self._text_question_entry.get().strip()
            )
        ))
        self._text_question_entry.delete(0, ctk.END)

        # re-arrange UI
        self._text_question_box.grid_forget()
        self._questions_box.grid_forget()
        self._waiting_box.grid(row=0, column=1, sticky="nsew")

    def _answer_choice_question(self, choice: int) -> None:
        """
        answer a choice question
        """
        if self._current_question is ...:
            return

        # send message to server
        self._loop.create_task(self._client.send_message(
            self._current_question.answer(choice)
        ))

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
