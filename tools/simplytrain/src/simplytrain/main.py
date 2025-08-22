"""
ELEKTRON © 2022
Written by melektron && Nilusink
www.elektron.work
28.11.22, 21:43

Simple training webapp using flask and plain html + js.
Loads translations from CSV and asks user random translation
questions. Translation direction can be set.
"""

from pathlib import Path

from tap import tapify
from flask import Flask, request, render_template, jsonify
from waitress import serve

from .setloader import SetLoader


class Application:
    def __init__(
        self,
        content_dir: Path,
        host: str = "0.0.0.0",
        port: int = 8080
    ) -> None:
        """
        Quick-n-dirty vocabulary translation training server
        with bare-bones webinterface.

        Parameters
        ----------
        content_dir : Path
            Directory with vocabulary translation CSV files to serve.
        host : str
            Address to bind to.
        port : int
            Port to listen on. For HTTPS, use a reverse proxy.
        """
        self.content_dir = content_dir
        self.host = host
        self.port = port

        self.set_loader = SetLoader(self)
        self.flask = Flask(__name__)

        @self.flask.route("/")
        def root():
            """
            Route for the url root

            :return: Project root, aka index.html
            """
            return render_template("index.html")

        @self.flask.route("/vocabs")
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

        @self.flask.route("/sets")
        def get_sets():
            """
            :return: All currently available sets, as a list
            """
            return jsonify(self.set_loader.get_available_sets())

        @self.flask.route("/nrwords")
        def nrwords():
            """
            params:

            - **sets**: list[str] = list of sets to count words in (usually the ones selected)

            :return: nubmer of words
            """
            sets_string: str = request.args.get("sets")
            if sets_string is None: 
                return jsonify({})

            sets = sets_string.split(",")

            return jsonify({
                "count": self.set_loader.get_nr_available_words(sets)
            })

        @self.flask.route("/compose")
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
            wordlist = self.set_loader.compose_exercise(sets, nr_words, nr_alts)
            return jsonify(wordlist)

    def run(self) -> None:
        print(f"serving alpha simplytrain on {self.host}:{self.port}")
        serve(
            self.flask,
            host=self.host,
            port=self.port
        )


def entry():
    app = tapify(Application)
    app.run()

if __name__ == "__main__":
    entry()

