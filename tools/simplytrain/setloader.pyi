"""
setloader.pyi
29. November 2022

Type hints for setloader.py

Author:
Nilusink
"""
"""
ELEKTRON © 2022
Written by melektron && Nilusink
www.elektron.work
28.11.22, 21:59

code for loading learning sets from csv files
"""
from typing import TypedDict, Union


CONTENT_DIR: str


class WordStructure(TypedDict):
    langa: dict[str, str | list[str]]
    langb: dict[str, str | list[str]]


def get_available_sets() -> list[str]:
    ...


def set_compose(sets: list[str]) -> dict[str, str]:
    ...


def compose_exercise(
        sets: list[str],
        nr: int,
        random_alts: int = 0
) -> list[dict[str, dict[str, str] | dict[str, str]]]:
    ...
