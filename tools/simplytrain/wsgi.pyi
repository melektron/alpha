"""
wsgi.pyi
29. November 2022

Type hints for wsgi.py

Author:
Nilusink
"""
from flask import Flask, Response


app: Flask


@app.route("/")
def root() -> str:
    ...


@app.route("/vocabs")
def vocabs() -> str:
    ...


@app.route("/sets")
def get_sets() -> Response:
    ...


@app.route("/compose")
def get_compose() -> Response:
    ...
