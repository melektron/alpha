"""
ELEKTRON © 2022
Written by melektron && Nilusink
www.elektron.work
28.11.22, 21:59

code for loading learning sets from csv files
"""
from contextlib import suppress
from typing import TypedDict, Union
import random as r
import csv
import os


CONTENT_DIR = "./content/240609_4AHEL_VOC_TEST_2"


class WordStructure(TypedDict):
    langa: dict[str, Union[str, list[str]]]
    langb: dict[str, Union[str, list[str]]]


def get_available_sets():
    """
    :return: a list with the names of all the available learning sets
    """
    set_files: list[str] = []
    for file in os.listdir(CONTENT_DIR):
        if os.path.isfile(os.path.join(CONTENT_DIR, file)) and file.endswith(".csv"):
            set_files.append(file.removesuffix(".csv"))

    return set_files


def set_compose(sets):
    """
    generates a dictionary with words from both languages

    :param sets: learning sets to use
    :return: the dictionary, containing the original word as key and the translation as value
    """
    words: dict[str, str] = {}
    available_sets = get_available_sets()
    valid_sets = list(set(sets) & set(available_sets))

    # parse all sets' files and add the words to the output dictionary
    for current_set in valid_sets:
        with open(os.path.join(CONTENT_DIR, current_set + ".csv")) as csvfile:
            spam_reader = csv.reader(csvfile, delimiter=";", quotechar="\"")
            for entry in spam_reader:
                with suppress(IndexError):  # ignore invalid csv rows
                    lang_a = entry[0]
                    lang_b = entry[1]
                    words[lang_a] = lang_b

    return words

def get_nr_available_words(sets: list[str]) -> int:
    """
    Returns the number of words contained in a certain set

    :param sets: sets to count words in
    :return: number of words in the selected sets
    """
    words = set_compose(sets)
    return len(words)

def compose_exercise(sets, nr, random_alts=0):
    """
    :param sets: learning sets to use
    :param nr: number of words to use
    :param random_alts: number of random other translations to add
    :return: a list containing the exercise generated by the passed values
    """
    all_words = set_compose(sets)
    words: list[str] = r.sample(all_words.keys(), nr)

    exercise: list[dict[str, Union[dict[str, str], dict[str, str]]]] = []
    for word in words:
        word_structure: WordStructure = {
            "langa": {
                "correct": word,
            },
            "langb": {
                "correct": all_words[word],
            }
        }

        if random_alts > 0:
            word_structure["langa"]["alts"] = r.sample(
                [w for w in all_words if w != word],
                random_alts
            )
            word_structure["langb"]["alts"] = r.sample(
                [w for w in all_words.values() if w != all_words[word]],
                random_alts
            )

        exercise.append(word_structure)

    return exercise
