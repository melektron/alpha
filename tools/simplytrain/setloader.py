"""
ELEKTRON © 2022
Written by melektron
www.elektron.work
28.11.22, 21:59

code for loading learning sets from csv files
"""

import csv
import os
import random as r

CONTENT_DIR = "./content/"


def get_available_sets() -> list[str]:
    set_files: list[str] = []
    for file in os.listdir(CONTENT_DIR):
        if not os.path.isfile(os.path.join(CONTENT_DIR, file)): continue
        if not file.endswith(".csv"): continue
        set_files.append(file.removesuffix(".csv"))

    return set_files


def set_compose(sets: list[str]) -> dict[str, str]:
    words: dict[str, str] = {}
    available_sets = get_available_sets()
    valid_sets = list(set(sets) & set(available_sets))

    for current_set in valid_sets:
        with open(os.path.join(CONTENT_DIR, current_set + ".csv")) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=";", quotechar="|")
            for entry in spamreader:
                try:
                    langa = entry[0]
                    langb = entry[1]
                    words[langa] = langb
                except IndexError:
                    pass    # ignore invalid csv rows

    return words

def compose_exercise(sets: list[str], nr: int, random_alts: int = 0) -> list:
    all_words = set_compose(sets)
    words = r.sample(all_words.keys(), nr)

    exercise = []
    for word in words:
        word_structure = {
            "langa": {
                "correct": word
            },
            "langb": {
                "correct": all_words[word]
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
