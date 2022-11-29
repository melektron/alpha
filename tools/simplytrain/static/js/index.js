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
    
    for (let i = 0; i < checks.length; i++) {
        let checkbox = checks[i].getElementsByTagName("input")[0];
        let checklabel = checks[i].getElementsByTagName("label")[0];
        if (checkbox.checked) {
            selected_sets.push(checklabel.innerText)
        }
    }
    console.log(selected_sets)
    return selected_sets
}


function startStuff() {
    let n = document.getElementById("howMany").value;
    let sets = getSetSelection();
    sets = sets.toString();

    if (!sets) {
        alert("please select at least 1 set!");
        return;
    }

    if (!n) {
        alert("please enter a value of min. 1!");
        return;
    }

    location.href = `/vocabs?nr=${n}&alts=0&sets=${sets}`;
}
