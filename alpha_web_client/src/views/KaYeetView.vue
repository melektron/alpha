<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Home page with overview
-->

<script setup lang="ts">

function connectToGame(payload: Event) {
    console.log("Connecting to:", payload)
}

</script>


<template>
    <main>
        <div class="connect-wrapper">
            <h1> KaYeet?! KaYeet!! </h1>
            <form @submit.prevent="connectToGame" class="connect-form">
                <InputText placeholder="Game Host Address" />
                <Button type="submit">Join Game</Button>
            </form>
        </div>
    </main>
</template>


<style scoped>

main {
    display: grid;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    background-color: #381272;
}

.connect-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 20px;
    background-color: var(--surface-400);
    border-radius: 10px;
}

</style>