"""
ELEKTRON © 2022
Written by melektron
www.elektron.work
28.11.22, 21:43

Simple training webapp using flask and plain html + js.
Loads translations from CSV and asks user random translation
questions. Translation direction can be set.
"""

from flask import Flask, request, render_template, jsonify
import setloader as sl
import json


app = Flask(__name__)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/vocabs")
def vocabs():
    nr_string = request.args.get("nr")
    alts_string = request.args.get("alts")
    swap_string = request.args.get("swap")
    sets_string = request.args.get("sets")

    return render_template("vocabulary.html", n=nr_string, a=alts_string, swapflag = swap_string, s=sets_string)



@app.route("/sets")
def get_sets():
    return jsonify(sl.get_available_sets())


@app.route("/compose")
def get_compose():
    nr_string = request.args.get("nr")
    alts_string = request.args.get("alts")
    sets_string = request.args.get("sets")
    if nr_string is None or alts_string is None or sets_string is None: 
        return {}

    nr_words = int(nr_string)
    nr_alts = int(alts_string)
    sets = sets_string.split(",")
    wordlist = sl.compose_exercise(sets, nr_words, nr_alts)
    return jsonify(wordlist)
