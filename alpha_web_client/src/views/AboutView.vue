<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Info about this application
-->

<script setup lang="ts">

import { useCounterStore } from '@/stores/counter';

const counter = useCounterStore();

</script>


<template>
    <main>
        <h1>Alpha - The OpenSource learning platform</h1>
        <p>
            Alpha is a set of open source tools to store and learn study material,
            mainly directed at school topics such as vocabulary.
            There is also a fun collaborative game feature called KaYeet?! (for no
            particular reason at all).
        </p>


        <h2>Some random number: {{ counter.count }}</h2>
        <button @click="counter.count++">Ooo nice button to clicki clicki</button>
    </main>
</template>

