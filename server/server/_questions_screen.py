"""
_questions_screen.py
11.04.2024

It's literally in the file name, what did you expect?

Author:
Nilusink
"""
from ._client import CLIENTS
from ._server import Server
import customtkinter as ctk
import typing as tp
import asyncio
import math


class QuestionsScreen(ctk.CTkFrame):
    def __init__(
            self,
            parent,
            server: Server,
            event_loop: asyncio.AbstractEventLoop,
            *args,
            **kwargs
    ) -> None:
        super().__init__(
            parent,
            *args,
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        self.parent = parent
        self._loop = event_loop
        self._server = server
        self._current_question: dict = ...

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # waiting for game start
        self._waiting_box = ctk.CTkFrame(self)
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
        self._questions_box = ctk.CTkFrame(self)

        self._questions_box.grid_rowconfigure(0, weight=1)
        self._questions_box.grid_rowconfigure(1, weight=3)
        self._questions_box.grid_columnconfigure(0, weight=1)

        self._question_title = ctk.CTkLabel(
            self._questions_box,
            font=("Arial", 32),
            text="Le Question",
        )
        self._question_title.grid(row=0, column=0)

        self._next_question_btn = ctk.CTkButton(
            self._questions_box,
            text="Next Question",
            font=("Arial", 48),
            command=lambda: self._synchronize(self._show_leaderboard())
        )

        # text answered questions
        self._text_question_box = ctk.CTkFrame(
            self._questions_box,
            corner_radius=25,
        )

        self._text_question_box.grid_rowconfigure((0, 1), weight=1)
        self._text_question_box.grid_columnconfigure((0, 2), weight=1)
        self._text_question_box.grid_columnconfigure(1, weight=2)

        self._text_question_entry = ctk.CTkLabel(
            self._text_question_box,
            text="Type your answer...",
            font=("Arial", 48),

        )
        self._text_question_entry.grid(row=0, column=1, sticky="sew", padx=20, pady=20)

        # multiple choice questions
        self._choice_box = ctk.CTkFrame(
            self._questions_box,
            corner_radius=25,
        )
        self._choice_widgets: list[ctk.CTkLabel] = []

    def grid(self, **kwargs) -> None:
        self.after(10, self._sync_new_question)

        super().grid(**kwargs)

    def _synchronize(self, future: tp.Coroutine) -> None:
        """
        run an async function from a synchronized thread
        """
        self._loop.create_task(future)

    def _sync_new_question(self) -> None:
        self._loop.create_task(self._new_question())

    async def _new_question(self) -> None:
        """
        a new question appeared
        """
        self._current_question: dict = ...
        self._next_question_btn.grid_forget()

        # get new question
        question = self._server.next_question()

        if question is None:
            self.parent.game_done()
            return

        # adjust UI
        self._waiting_box.grid_forget()
        self._questions_box.grid(row=0, column=0, sticky="nsew")
        self._next_question_btn.configure(
            command=lambda: self._synchronize(self._show_leaderboard())
        )

        self._question_title.configure(text=question["question"])

        if question["question_type"] == 0:
            self._choice_box.grid_forget()
            self._text_question_box.grid(
                row=1,
                column=0,
                sticky="nsew",
                padx=40,
                pady=50
            )

        elif question["question_type"] == 1:
            raise NotImplementedError("Yes No Questions do not exist yet!")

        elif question["question_type"] == 2:
            self._text_question_box.grid_forget()
            self._choice_box.grid(
                row=1,
                column=0,
                sticky="nsew",
                padx=40,
                pady=50
            )

            # generate answer boxes
            # de-configure the grid
            self._choice_box.grid_rowconfigure(list(range(10)), weight=0)
            self._choice_box.grid_columnconfigure(list(range(10)), weight=0)

            n_answers = len(question["choices"])
            per_row = math.ceil(math.sqrt(n_answers))
            per_column = math.ceil(n_answers / per_row)

            # configure grid
            self._choice_box.grid_rowconfigure(list(range(per_row)), weight=1)
            self._choice_box.grid_columnconfigure(list(range(per_column)), weight=1)

            # destroy all previously created widgets
            for widget in self._choice_widgets:
                widget.grid_forget()
                widget.destroy()

            self._choice_widgets.clear()

            for row in range(per_row):
                for column in range(per_column):
                    index = row * per_row + column

                    if index + 1 > len(question["choices"]):
                        break

                    tmp = ctk.CTkLabel(
                        self._choice_box,
                        text=question["choices"][index],
                        font=("Arial", 48),
                    )
                    tmp.grid(row=row, column=column, sticky="nsew", padx=15, pady=15)
                    self._choice_widgets.append(tmp)

        else:
            raise ValueError(
                f"Question of type {question.__class__.__name__} "
                f"not recognized"
            )

        self._current_question = question

        await CLIENTS.ask_question(question)
        await CLIENTS.question_done()
        await CLIENTS.send_statistics()
        # await self._new_question()

    async def _show_leaderboard(self) -> None:
        """
        shows the correct answer to the question
        """
        self._next_question_btn.configure(
            command=lambda: self._synchronize(self._new_question())
        )
        self._next_question_btn.grid(
            row=0,
            column=1,
            padx=100
        )

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
