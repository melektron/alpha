"""
_questions_master.py
11. April 2024

handles all questions

Author:
Florian,
Nilusink
"""
from icecream import ic
import typing as tp
import random
import json
import os


class _QuestionsMaster:
    __instance = ...

    def __new__(cls, *args, **kwargs):
        if cls.__instance is ...:
            ic("new QuestionsMaster instance")
            cls.__instance = super(_QuestionsMaster, cls).__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        self._questions: dict = ...
        self._question_set_name = ""
        self._callbacks: list[tp.Callable[[str], None]] = []

    @property
    def question_set_name(self) -> str:
        """
        return the currently active question set's name
        """
        return self._question_set_name

    def on_question_set_change(self, callback: tp.Callable[[str], None]) -> None:
        """
        add a callback for when the question-set is changed
        :param callback: function with a string parameter (question set's name)
        """
        self._callbacks.append(callback)

    def _update_callbacks(self) -> None:
        """
        updates all callback functions
        """
        for callback in self._callbacks:
            callback(self.question_set_name)

    def load_from_file(self, filepath: str) -> None:
        """
        Loads questions from a file
        """
        ic("Loading questions from", filepath)

        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"invalid path: {filepath}")

        # update the question set name based on file name
        self._question_set_name = ".".join(os.path.basename(filepath).split(".")[:-1])

        # safe questions
        self._questions = json.load(open(filepath, "r"))

        # run callbacks
        self._update_callbacks()

    def reset_questions(self) -> None:
        """
        clear all currently loaded questions
        """
        ic("resetting questions")

        self._questions.clear()
        self._question_set_name = ""

        # run callbacks
        self._update_callbacks()

    @property
    def questions(self) -> dict:
        return self._questions.copy()

    def get_random_question(
            self,
            n_questions: int = 1,
            question_types: tuple[str, ...] = ...
    ) -> list[dict]:
        """
        selects n_questions questions from all selected pools
        """
        # question_types = ("yesno",)
        if question_types is ...:
            question_pool = [
                {
                    "question_type": {
                        "text": 0,
                        "yesno": 1,
                        "choices": 2
                    }[t],
                    **question
                } for t in self.questions for question in self.questions[t]
            ]

        else:
            ic(question_types)
            question_pool = []

            if "text" in question_types:
                question_pool.extend([{
                    "question_type": 0,
                    **q
                } for q in self.questions["text"]])

            if "yesno" in question_types:
                question_pool.extend([{
                    "question_type": 1,
                    **q
                } for q in self.questions["yesno"]])

            if "choices" in question_types:
                question_pool.extend([{
                    "question_type": 2,
                    **q
                } for q in self.questions["choices"]])

            if len(question_pool) < 1:
                raise ValueError(f"No Questions for pools {question_types}")

        # question_pool = [question_pool[0],] * 100

        return random.sample(question_pool, n_questions)


QuestionsMaster = _QuestionsMaster()
