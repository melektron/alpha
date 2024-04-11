"""
questions_master.py
11. April 2024

handles all questions

Author:
Nilusink
"""
from icecream import ic
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
        self._questions = ...

    def load_from_file(self, filepath: str) -> None:
        """
        Loads questions from a file
        """
        ic("Loading questions from", filepath)

        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"invalid path: {filepath}")

        self._questions = json.load(open(filepath, "r"))

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
                question_pool.extend(self.questions["text"])

            if len(question_pool) < 1:
                raise ValueError(f"No Questions for pools {question_types}")

        return random.sample(question_pool, n_questions)


QuestionsMaster = _QuestionsMaster()
