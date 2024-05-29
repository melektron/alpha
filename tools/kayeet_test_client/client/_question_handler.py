"""
_question_handler.py
17.04.2024

gets messages from comms and translates them for the UI

Author:
Nilusink
"""
from traceback import format_exc
import typing as tp


class Question:
    def __init__(self, **message):
        self._type: int = message["question_type"]
        self._question: str = message["question"]
        self._parent_id: int = message["id"]

        self._choices: list[str] = ...
        if self._type == 2:
            self._choices = message["choices"]

    @property
    def question(self) -> str:
        """
        get the asked question
        :return:
        """
        return self._question

    def answer(self, answer: str | int | bool) -> dict:
        """
        packs the question in a message-dict
        """
        return {
            "type": "answer",
            "answer_to": self._parent_id,
            "answer": answer
        }


class TextQuestion(Question):
    def __init__(
            self,
            question_type: int,
            question: str,
            id: int
    ) -> None:
        super().__init__(
            question_type=question_type,
            question=question,
            id=id,
        )

    def answer(self, answer: str):
        if not isinstance(answer, str):
            raise ValueError(
                f"Answer to {self.__class__.__name__} must be a string"
            )

        return super().answer(answer)


class YesNoQuestion(Question):
    def __init__(
            self,
            question_type: int,
            question: str,
            id: int
    ) -> None:
        super().__init__(
            question_type=question_type,
            question=question,
            id=id,
        )

    def answer(self, answer: bool):
        if not isinstance(answer, bool):
            raise ValueError(
                f"Answer to {self.__class__.__name__} must be a boolean"
            )

        return super().answer(answer)


class ChoiceQuestion(Question):
    def __init__(
            self,
            question_type: int,
            question: str,
            id: int,
            choices: list[str]
    ) -> None:
        super().__init__(
            question_type=question_type,
            question=question,
            id=id,
            choices=choices
        )

    @property
    def choices(self) -> list[str]:
        """
        get all available choices
        """
        return self._choices

    def answer(self, answer: int):
        if not isinstance(answer, int):
            raise ValueError(
                f"Answer to {self.__class__.__name__} must be an integer"
            )

        return super().answer(answer)


def question_creator(question: dict) -> Question:
    """
    generate a question based on a question (just leave me alone, my brain
    doesn't brain anymore, ok?)
    """
    # remove unwanted fields
    question.pop("type")

    try:
        match question["question_type"]:
            case 0:
                return TextQuestion(**question)

            case 1:
                return YesNoQuestion(**question)

            case 2:
                return ChoiceQuestion(**question)

            case _:
                raise NotImplementedError(
                    f"Question of type {question['question_type']} hasn't been "
                    f"implemented yet!"
                )

    except Exception as e:
        print("error", e)
        raise e


class QuestionHandler:
    def __init__(self) -> None:
        self._pending_questions: list[Question] = []
        self._callbacks: list[tp.Callable[[tp.Self], None]] = []

    def question_available(self) -> bool:
        """
        returns true if one or more questions are pending
        """
        return len(self._pending_questions) > 0

    def next(self) -> Question | None:
        """
        return the next possible question or None if not available
        """
        if self.question_available():
            out = self._pending_questions[0]
            self._pending_questions.pop(0)
            return out

        return None

    def queue_question(self, question: dict) -> None:
        """
        add new question to the queue
        """
        print("new question", self._callbacks)
        try:
            self._pending_questions.append(question_creator(question))

        except Exception as e:
            print(format_exc())

        print("idk")

        # call callbacks (quite obvious, innit?)
        for callback in self._callbacks:
            print("cb1")
            callback(self)
            print("cb2")

    def on_new_question(
            self,
            callback: tp.Callable[["QuestionHandler"], None]
    ) -> None:
        """
        add a callback for new questions
        """
        print("new callback")
        self._callbacks.append(callback)
        print("idk what happened")
