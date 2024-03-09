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
        <h1>This is an about page</h1>
        <h2>{{ counter.count }}</h2>
        <button @click="counter.count++">incr</button>
    </main>
</template>

