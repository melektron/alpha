/*
index.js
29. November 2022

Functions for index.html

Author:
Nilusink
*/
function getWords() {
    fetch("/compose?nr=500&alts=0&sets=BS_100-101,BS_102-105")
        .then((response) => {
            return response.json()
        })
        .then({

        })
}
