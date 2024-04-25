<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Home page with overview
-->

<script setup lang="ts">

import { computed, ref } from 'vue';
import { useKaYeetGame, GameStates } from '@/stores/kayeet';
import { watch } from 'vue';
import { watchEffect } from 'vue';
import { nextTick } from 'vue';
import { AwaitableEvent } from "@/utils/awaitable_event"
import { any } from 'zod';

const game = useKaYeetGame();
// old game state to detect changes
let old_game_state = game.state;

// stage form visibility flags
const show_connect_card = ref<boolean>(true);
const show_login_card = ref<boolean>(false);
const show_disconnected_dialog = ref<boolean>(false);

// event awaiters
const connect_card_left = new AwaitableEvent<Element>();
const login_card_left = new AwaitableEvent<Element>();

// connect form state
const host_entry = ref<string>("");
const connect_button_label = computed(() => {
    if (game.state === GameStates.READY_TO_CONNECT)
        return "Connect to Server";
    else if (game.state === GameStates.CONNECTING)
        return "Connecting ...";
    return "N/A";
})
const connect_button_icon = computed(() => {
    if (game.state === GameStates.CONNECTING)
        return "pi pi-spin pi-spinner-dotted";
    else if (game.state === GameStates.CONNECTION_FAILED)
        return "pi pi-times";
    return "";
})
const show_conn_failed_message = ref<boolean>(false);
const conn_failed_life_end = () => setTimeout(() => show_conn_failed_message.value = false, 1000);
function connectToGame(payload: Event) {
    game.connectToGameServer(host_entry.value);
}

// login form state
const username_entry = ref<string>("");
function loginButtonHandler(payload: Event) {
    game.login(username_entry.value);
}

// disconnected modal
function disconnectModelAcknowledge(e: Event) {
    game.acknowledgeError();
}

watchEffect(async () => {
    console.log(`Game state changed from ${GameStates[old_game_state]} to ${GameStates[game.state]}`);
    old_game_state = game.state;

    if (game.state === GameStates.READY_TO_CONNECT) {
        show_login_card.value = false;
        show_disconnected_dialog.value = false;
        await login_card_left.next;
        show_connect_card.value = true;
    }

    else if (game.state === GameStates.CONNECTION_FAILED)
        show_conn_failed_message.value = true;  // this is automatically 

    else if (game.state === GameStates.READY_TO_LOG_IN) {
        show_connect_card.value = false;
        console.log("before")
        await connect_card_left.next;   // wait for animation
        console.log("after")
        show_login_card.value = true;
    }
    else if (game.state == GameStates.DISCONNECTED)
    {
        show_disconnected_dialog.value = true;
    }
})


</script>


<template>
    <main>
        <div class="connect-center-wrapper">
            <h1> KaYeet?! KaYeet!! </h1>
            <div class="connect-card-wrapper"> 
                <Transition name="fade-inout" @after-leave="(e) => connect_card_left.happened(e)">
                    <Card v-if="show_connect_card">
                        <template #content>
                            <form @submit.prevent="connectToGame" class="setup-form">
                                <FloatLabel>
                                    <InputText id="host" v-model="host_entry" placeholder="localhost" :style="{width: '100%'}" />
                                    <label for="host">Game Server</label>
                                </FloatLabel>
                                <Button 
                                    type="submit" 
                                    :label="connect_button_label" 
                                    :icon="connect_button_icon" 
                                    icon-pos="right"
                                />
                                <Message 
                                    v-if="show_conn_failed_message" 
                                    severity="error" 
                                    :sticky="false" 
                                    :life="2000"
                                    @close="show_conn_failed_message = false"
                                    @life-end="conn_failed_life_end"
                                >
                                    Connection failed
                                </Message>

                            </form>
                        </template>
                    </Card>
                </Transition>

                <Transition name="fade-inout" @after-leave="(e) => login_card_left.happened(e)">
                    <Card v-if="show_login_card">
                        <template #content>
                            <form @submit.prevent="loginButtonHandler" class="setup-form">
                                <FloatLabel>
                                    <InputText id="host" v-model="username_entry" :style="{width: '100%'}" />
                                    <label for="host">Username</label>
                                </FloatLabel>
                                <Button type="submit">Join Game</Button>
                            </form>
                        </template>
                    </Card>
                </Transition>

                <Dialog v-model:visible="show_disconnected_dialog" modal :style="{ width: '18rem' }">
                    <template #container="{ closeCallback }">
                        <div class="flex flex-column align-items-center p-5 surface-overlay border-round">
                            <div class="border-circle bg-yellow-500 inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                <i class="pi pi-exclamation-triangle text-5xl"></i>
                            </div>
                            <span class="font-bold text-2xl block mb-2 mt-4">Connection lost</span>
                            <p class="mb-0">You have been disconnected from the game server.</p>
                            <div class="flex align-items-center gap-2 mt-4">
                                <Button label="Go back to start" @click="disconnectModelAcknowledge"></Button>
                            </div>
                        </div>
                    </template>
                </Dialog>
            </div>
        </div>
    </main>
</template>


<style scoped>

main {
    /* centering */
    display: grid;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    background-color: var(--surface-ground);
}

.connect-center-wrapper {
    width: 20rem;
}

.connect-card-wrapper {
    position: relative;
}

.setup-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.setup-form  > * {
    width: 100%;
}

.fade-inout-enter-active,
.fade-inout-leave-active {
    transition: opacity 0.5s ease;
}

.fade-inout-enter-from,
.fade-inout-leave-to {
    opacity: 0;
}

.fade-inout-enter-to,
.fade-inout-leave-from {
    opacity: 1;
}

</style>