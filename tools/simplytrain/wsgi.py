"""
ELEKTRON © 2022
Written by melektron && Nilusink
www.elektron.work
28.11.22, 21:43

Simple training webapp using flask and plain html + js.
Loads translations from CSV and asks user random translation
questions. Translation direction can be set.
"""
from flask import Flask, request, render_template, jsonify, Response
import setloader as sl


app = Flask(__name__)


@app.route("/")
def root():
    """
    Route for the url root

    :return: Project root, aka index.html
    """
    return render_template("index.html")


@app.route("/vocabs")
def vocabs():
    """
    params:

    - **nr**: int = number of words
    - **alts**: int = number of alternative (wrong) translations
    - **swap**: bool = if True, swap word languages
    - **sets**: list[str] = list of sets to use for generating the wordlist

    :return: Vocabulary training page
    """
    nr_string: str = request.args.get("nr")
    alts_string: str = request.args.get("alts")
    swap_string: str = request.args.get("swap")
    sets_string: str = request.args.get("sets")

    return render_template("vocabulary.html", n=nr_string, a=alts_string, swapflag=swap_string, s=sets_string)


@app.route("/sets")
def get_sets():
    """
    :return: All currently available sets, as a list
    """
    return jsonify(sl.get_available_sets())


@app.route("/compose")
def get_compose():
    """
    params:

    - **nr**: int = number of words
    - **alts**: int = number of alternative (wrong) translations
    - **swap**: bool = if True, swap word languages
    - **sets**: list[str] = list of sets to use for generating the wordlist

    :return: generates a wordlist with the given arguments
    """
    nr_string = request.args.get("nr")
    alts_string = request.args.get("alts")
    sets_string = request.args.get("sets")
    if nr_string is None or alts_string is None or sets_string is None: 
        return jsonify({})

    nr_words = int(nr_string)
    nr_alts = int(alts_string)
    sets = sets_string.split(",")
    wordlist = sl.compose_exercise(sets, nr_words, nr_alts)
    return jsonify(wordlist)
