/*
index.js
29. November 2022

Functions for index.html

Author:
Nilusink
*/

function getSetSelection() {
    let selected_sets = []
    let checks = document.getElementById("setsBox").children;
    
    for (var i = 0; i < checks.length; i++) {
        let checkbox = checks[i].getElementsByTagName("input")[0];
        let checklabel = checks[i].getElementsByTagName("label")[0];
        if (checkbox.checked) {
            selected_sets.push(checklabel.innerText)
        }
    }
    console.log(selected_sets)
    return selected_sets
}


function getWords() {
    fetch("/compose?nr=500&alts=0&sets=BS_100-101,BS_102-105")
        .then((response) => {
            return response.json()
        })
        .then({

        })
}
