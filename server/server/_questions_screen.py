"""
_questions_screen.py
11.04.2024

It's literally in the file name, what did you expect?

Author:
Nilusink
"""
from ._questions_master import Question
from ._client import CLIENTS
from ._server import Server
from ._audio import AUDIO
import customtkinter as ctk
from icecream import ic
import typing as tp
import asyncio
import math


class LeaderboardBox(tp.TypedDict):
    frame: ctk.CTkFrame
    nick_label: ctk.CTkLabel
    score_label: ctk.CTkLabel


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
        self._server: Server = server
        self._current_question: Question | None = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # initialize tkinter stuff
        self._init_ui()

    def _init_ui(self) -> None:
        """
        create and initialize all ctk widgets
        """
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

        self._questions_box.grid_rowconfigure(0, weight=2)
        self._questions_box.grid_rowconfigure(1, weight=3)
        self._questions_box.grid_rowconfigure(2, weight=3)
        self._questions_box.grid_columnconfigure(0, weight=1)

        self._question_title = ctk.CTkLabel(
            self._questions_box,
            font=("Arial", 48),
            text="Le Question",
        )
        self._question_title.grid(row=0, column=0)

        self._current_question_label = ctk.CTkLabel(
            self._questions_box,
            text="0 of 0",
            font=("Arial", 32),
        )
        self._current_question_label.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self._skip_button = ctk.CTkButton(
            self._questions_box,
            text="Skip",
            font=("Arial", 48),
            command=lambda: self._synchronize(self.show_leaderboard())
        )
        self._skip_button.grid(
            row=0,
            column=2,
            padx=100
        )

        self._time_left_label = ctk.CTkLabel(
            self._questions_box,
            text="",
            font=("Arial", 32),
        )
        self._set_time_left(0)
        self._time_left_label.grid(
            row=1,
            column=2,
            sticky="nsew"
        )

        self._answers_label = ctk.CTkLabel(
            self._questions_box,
            text="",
            font=("Arial", 32),
        )
        self._set_nr_answers(0)
        self._answers_label.grid(
            row=2,
            column=2,
            sticky="nsew"
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

        # leader board
        self._leaderboard_box = ctk.CTkFrame(self)

        self._leaderboard_box.grid_rowconfigure((0, 1), weight=1)
        self._leaderboard_box.grid_columnconfigure(0, weight=1)

        self._leaderboard_title = ctk.CTkLabel(
            self._leaderboard_box,
            text="Leaderboard",
            font=("Arial", 64),
        )
        self._leaderboard_title.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self._next_question_button = ctk.CTkButton(
            self._leaderboard_box,
            text="Next Question",
            font=("Arial", 48),
            command=lambda: self._synchronize(self.new_question())
        )
        self._done_button = ctk.CTkButton(
            self._leaderboard_box,
            text="New Game",
            font=("Arial", 48),
            command=self._game_done
        )
        self._next_question_button.grid(
            row=0,
            column=1,
            padx=100
        )

        self._leaderboard_frame = ctk.CTkFrame(
            self._leaderboard_box,
            corner_radius=30
        )

        # configure grid for 5 boxes
        self._leaderboard_frame.grid_columnconfigure(0, weight=1)
        self._leaderboard_frame.grid_rowconfigure(list(range(5)), weight=1)

        self._leaderboard_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=80,
            pady=40
        )

        # create 5 boxes
        self._leaderboard_boxes: list[LeaderboardBox] = []
        for i in range(5):
            frame = ctk.CTkFrame(self._leaderboard_frame, corner_radius=15)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure((1, 2), weight=1)

            ctk.CTkLabel(frame, text=str(i+1), font=("Arial", 32)).grid(
                row=0,
                column=0,
                padx=40
            )

            self._leaderboard_boxes.append({
                "frame": frame,
                "nick_label": ctk.CTkLabel(
                    frame,
                    font=("Arial", 32),
                    text="Nickname"
                ),
                "score_label": ctk.CTkLabel(
                    frame,
                    font=("Arial", 32),
                    text="Score"
                ),
            })

            self._leaderboard_boxes[-1]["nick_label"].grid(
                row=0,
                column=1,
                padx=30,
                pady=30,
                sticky="nsew"
            )
            self._leaderboard_boxes[-1]["score_label"].grid(
                row=0,
                column=2,
                padx=30,
                pady=30,
                sticky="nsew"
            )
    
    def _set_time_left(self, s: int) -> None:
        self._time_left_label.configure(text=f"{s}s\nleft")

    def _set_nr_answers(self, s: int) -> None:
        self._answers_label.configure(text=f"{s}\nanswers")

    def grid(self, **kwargs):
        # override parent grid method to call new_question right after
        # the widget has been placed
        self.after(10, self._synchronize(self.new_question()))

        # call parent class grid method, so the user doesn't even notice
        # what we did here
        super().grid(**kwargs)

    def _synchronize(self, future: tp.Coroutine) -> None:
        """
        run an async function from a synchronized thread
        """
        self._loop.create_task(future)

    async def new_question(self) -> None:
        """
        a new question appeared
        """
        self._current_question = None

        # get new question
        question = self._server.next_question()

        if question is None:
            return self._game_done()

        # adjust UI
        self._waiting_box.grid_forget()
        self._leaderboard_box.grid_forget()
        self._questions_box.grid(row=0, column=0, sticky="nsew")

        self._question_title.configure(text=question["question"])

        # configure the "x of y" questions label
        self._current_question_label.configure(
            text=f"{self._server.current_question} of {self._server.n_questions}"
        )

        if question["question_type"] == 0:
            self._choice_box.grid_forget()
            self._text_question_entry.configure(text="Type your answer...")
            self._text_question_box.grid(
                row=1,
                column=0,
                columnspan=2,
                rowspan=2,
                sticky="nsew",
                padx=40,
                pady=50
            )

        elif question["question_type"] == 1:
            self._choice_box.grid_forget()
            self._text_question_entry.configure(text="Yes or No")
            self._text_question_box.grid(
                row=1,
                column=0,
                columnspan=2,
                rowspan=2,
                sticky="nsew",
                padx=40,
                pady=50
            )

        elif question["question_type"] == 2:
            self._text_question_box.grid_forget()
            self._choice_box.grid(
                row=1,
                column=0,
                columnspan=2,
                rowspan=2,
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

        # start question sound
        AUDIO.start_question_sound()

        self._set_nr_answers(0)
        self._set_time_left(0)

        await CLIENTS.ask_question(question)

        async for nr_answers, new_answers, time_left in CLIENTS.wait_question_done():
            # update the status on the screen
            self._set_time_left(time_left)
            self._set_nr_answers(nr_answers)
            # play sound for each new answer that was submitted
            for _ in range(new_answers):
                AUDIO.play_answer_submitted_effect()

        await CLIENTS.send_statistics()
        await self.show_leaderboard()

        # stop the question sound
        await AUDIO.end_question_sound()

    async def show_leaderboard(self) -> None:
        """
        shows the correct answer to the question
        """
        # make sure, the question is done
        CLIENTS.skip_question()

        # adjust ui
        self._questions_box.grid_forget()

        # it should never be called from the waiting screen, but who tf
        # knows what future me is going to do ...
        self._waiting_box.grid_forget()

        self._leaderboard_box.grid(row=0, column=0, sticky="nsew")

        # customize for final leaderboard
        if self._server.current_question == self._server.n_questions:
            self._next_question_button.grid_forget()
            self._done_button.grid(
                row=0,
                column=2,
                padx=100
            )
            self._leaderboard_title.configure(text="Final Leaderboard")

        # un-grid stuff
        for box in self._leaderboard_boxes:
            box["frame"].grid_forget()

        # draw leaderboard
        for i, (score, username) in enumerate(CLIENTS.get_leaderboard()):
            # only draw first five clients
            if i > 4:
                break

            # grid frame
            box = self._leaderboard_boxes[i]
            box["frame"].grid(
                row=i,
                column=0,
                sticky="nsew",
                pady=20,
                padx=30
            )

            # adjust username and score
            box["score_label"].configure(text=str(score))
            box["nick_label"].configure(text=username)

    def _game_done(self) -> None:
        """
        call the parent's game done function and re-configure the ui
        """
        self._done_button.grid_forget()
        self._next_question_button.grid(
            row=0,
            column=2,
            padx=100
        )
        self._leaderboard_title.configure(text="Leaderboard")
        self.parent.game_done()

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
