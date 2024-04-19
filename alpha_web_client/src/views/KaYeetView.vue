<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Home page with overview
-->

<script setup lang="ts">

import { ref } from 'vue';
import { useKaYeetGame } from '@/stores/kayeet';

const game = useKaYeetGame();

// the value of the server textbox
const host_entry = ref<string>("");


function connectToGame(payload: Event) {
    game.connectToGameServer(host_entry.value);
}

</script>


<template>
    <main>
        <div v-if="game.is_connection_phase" class="connect-wrapper">
            <h1> KaYeet?! KaYeet!! </h1>
            <Card>
                <template #content>
                    <form @submit.prevent="connectToGame" class="connect-form">
                        <span class="p-float-label">
                            <InputText id="host" v-model="host_entry" placeholder="Game Host Address" />
                            <label for="host">Host</label>
                        </span>
                        <Button type="submit">Join Game</Button>
                    </form>
                </template>
            </Card>
        </div>

        <div v-if="game.is_login_phase" class="connect-wrapper">
            <h1> KaYeet?! KaYeet!! </h1>
            <form @submit.prevent="connectToGame" class="connect-form">
                <InputText v-model="host_entry" placeholder="Username" />
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