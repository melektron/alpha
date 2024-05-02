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
import logo from '@/assets/kayeet_logo.png'
import { QuestionType } from '@/stores/kayeet_messages';

import BubbleField from '@/components/BubbleField.vue';

const game = useKaYeetGame();
// old game state to detect changes
let previous_game_state = game.state;

// element visibility flags
const show_setup_elements = ref<boolean>(true);
const show_questioning_elements = ref<boolean>(false);
const show_connect_card = ref<boolean>(true);
const show_login_card = ref<boolean>(false);
const show_disconnected_dialog = ref<boolean>(false);
const show_logged_in_text = ref<boolean>(false);
const show_text_question = ref<boolean>(false);
const show_yes_no_question  = ref<boolean>(false);
const show_multi_question = ref<boolean>(false);
const show_awaiting_results_card = ref<boolean>(false);
const show_results_card = ref<boolean>(false);
const show_ranking_card = ref<boolean>(false);

// event awaiters
const setup_elements_left = new AwaitableEvent<Element>();
const questioning_elements_left = new AwaitableEvent<Element>();
const any_base_element_left = new AwaitableEvent<Element>();

const connect_card_left = new AwaitableEvent<Element>();
const login_card_left = new AwaitableEvent<Element>();
const logged_in_text_left  = new AwaitableEvent<Element>();


// connect form state
const host_entry = ref<string>("");
const connect_button_label = computed(() => {
    if (game.state === GameStates.READY_TO_CONNECT)
        return "Connect to Server";
    else if (game.state === GameStates.CONNECTING)
        return "Connecting ...";
    return "N/A";
});
const connect_button_icon = computed(() => {
    if (game.state === GameStates.CONNECTING)
        return "pi pi-spin pi-spinner-dotted";
    else if (game.state === GameStates.CONNECTION_FAILED)
        return "pi pi-times";
    return "";
});
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
    show_disconnected_dialog.value = false;
    game.acknowledgeError();
}

// question data
const answer_text = ref<string>("");
function submitTextAnswer(e: Event) {
    game.answerQuestion(answer_text.value);
    answer_text.value = "";
}

// ranking data
const ranking_formatted = computed(() => {
    return game.ranking.map((el) => {return {
        player: el[1], 
        score: el[0]
    }});
});

watchEffect(async () => {
    console.log(`Game state changed from ${GameStates[previous_game_state]} to ${GameStates[game.state]}`);

    switch (game.state) {
        case GameStates.READY_TO_CONNECT:
            // only when transitioning from disconnected, should the event be awaited.
            // otherwise this would cause unwanted side effects
            if (previous_game_state !== GameStates.DISCONNECTED)
                break;
            if (show_setup_elements.value === true || show_questioning_elements.value === true) {
                show_setup_elements.value = false;
                show_questioning_elements.value = false;
                await any_base_element_left.next;
            }
            // everything off
            show_connect_card.value = true;
            show_login_card.value = false;
            show_disconnected_dialog.value = false;
            show_logged_in_text.value = false;
            show_text_question.value = false;
            show_yes_no_question.value = false;
            show_multi_question.value = false;
            show_awaiting_results_card.value = false;
            show_results_card.value = false;
            show_ranking_card.value = false;
            // show setup and connect
            show_setup_elements.value = true;
            show_connect_card.value = true;
            break;
        
        case GameStates.CONNECTION_FAILED:
            show_conn_failed_message.value = true;  // this is automatically 
            break;

        case GameStates.READY_TO_LOG_IN:
            show_connect_card.value = false;
            await connect_card_left.next;   // wait for animation
            show_login_card.value = true;
            break;
        
        case GameStates.LOGGED_IN:
            show_login_card.value = false;
            await login_card_left.next;     // wait for animation
            show_logged_in_text.value = true;
            break;
        
        case GameStates.DISCONNECTED:
            show_disconnected_dialog.value = true;
            break;
        
        case GameStates.QUESTION_TEXT:
        case GameStates.QUESTION_YES_NO:
        case GameStates.QUESTION_MULTI:
            // when transitioning from logged in state
            if (previous_game_state === GameStates.LOGGED_IN) {
                // transition from setup to questioning once
                show_setup_elements.value = false;
                await setup_elements_left.next;
                show_logged_in_text.value = false;  // reset this for later, will not trigger any effect since element is not in dom
                show_questioning_elements.value = true;
            } else if (previous_game_state === GameStates.DISPLAYING_SCORES) {
                show_ranking_card.value = false;
                // TODO: maybe add transition
            } else if (previous_game_state === GameStates.DISPLAYING_RESULT) {
                show_results_card.value = false;
                // TODO: maybe transition
            }
            if (game.state === GameStates.QUESTION_TEXT) {
                show_text_question.value = true;
                // reset question value
                answer_text.value = "";
            } else if (game.state === GameStates.QUESTION_YES_NO) {
                show_yes_no_question.value = true;
            } else if (game.state === GameStates.QUESTION_MULTI) {
                show_multi_question.value = true;
            }
            break;
        
        case GameStates.AWAITING_RESULT:
            show_text_question.value = false;
            show_yes_no_question.value = false;
            show_multi_question.value = false;
            // TODO: maybe add transition
            show_awaiting_results_card.value = true;
            break;
        
        case GameStates.DISPLAYING_RESULT:
            if (previous_game_state === GameStates.AWAITING_RESULT) {
                // after we have submitted
                show_awaiting_results_card.value = false;
                // TODO: probably an animation here since this is not time critical
            } else if ([GameStates.QUESTION_TEXT, GameStates.QUESTION_YES_NO, GameStates.QUESTION_MULTI].includes(previous_game_state)) {
                // if answer was not submitted in time
                show_text_question.value = false;
                show_yes_no_question.value = false;
                show_multi_question.value = false;
                // TODO: maybe also animate here?
            }
            show_results_card.value = true;
            break;
        
        case GameStates.DISPLAYING_SCORES:
            show_results_card.value = false;
            // TODO: animate
            show_ranking_card.value = true;
            break;
    
        default:
            break;
    }

    previous_game_state = game.state;
});


</script>


<template>
    <div class="background">
        <!-- Backdrop between background and foreground -->
        <BubbleField :enabled="show_awaiting_results_card" class="bubble_field"/>

        <main>
            <Transition name="fade-inout" @after-leave="(e) => {setup_elements_left.happened(e); any_base_element_left.happened(e);}">
                <div v-if="show_setup_elements" class="centering-wrapper">
                    <div class="kayeet-head-wrapper">
                        <img :src="logo">
                        <h1> KaYeet?! KaYeet!! </h1>
                    </div>
                    <div class="content-wrapper">
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

                        <Transition name="fade-inout" @after-leave="(e) => logged_in_text_left.happened(e)">
                            <div>
                                <h1 v-if="show_logged_in_text" class="logged-in-text">You are logged in as <b>{{ username_entry }}</b> !</h1>
                                <h2 v-if="show_logged_in_text" class="logged-in-text">Get ready ... The thrill is about to begin!</h2>
                            </div>
                        </Transition>
                    </div>
                </div>
            </Transition>
            <Transition name="fade-inout" @after-leave="(e) => {questioning_elements_left.happened(e); any_base_element_left.happened(e);}">
                <div v-if="show_questioning_elements" class="centering-wrapper">
                    <Card v-if="show_text_question">
                        <template #content>
                            <form @submit.prevent="submitTextAnswer" class="question-form">
                                <div class="border-circle bg-primary inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-question text-5xl"></i>
                                </div>
                                <h1>
                                    {{ game.current_question.text }}
                                </h1>
                                <FloatLabel>
                                    <InputText id="host" v-model="answer_text" :style="{width: '100%'}" />
                                    <label for="host">Your Answer</label>
                                </FloatLabel>
                                <Button 
                                    type="submit" 
                                    label="Submit"
                                />
                            </form>
                        </template>
                    </Card>
                    <Card v-if="show_yes_no_question">
                        <template #content>
                            <div class="question-form">
                                <div class="border-circle bg-primary inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-question text-5xl"></i>
                                </div>
                                <h1>
                                    {{ game.current_question.text }}
                                </h1>
                                <Button 
                                    type="submit" 
                                    label="Yes"
                                    @click="game.answerQuestion(true)"
                                />
                                <Button 
                                    type="submit" 
                                    label="No"
                                    @click="game.answerQuestion(false)"
                                />
                            </div>
                        </template>
                    </Card>
                    <Card v-if="show_multi_question">
                        <template #content>
                            <div class="question-form">
                                <div class="border-circle bg-primary inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-question text-5xl"></i>
                                </div>
                                <h1>
                                    {{ game.current_question.text }}
                                </h1>
                                <Button
                                    v-for="(item, index) in game.current_question.choices"
                                    type="submit" 
                                    :label="item"
                                    @click="game.answerQuestion(index)"
                                />
                            </div>
                        </template>
                    </Card>
                    <Card v-if="show_awaiting_results_card">
                        <template #content>
                            <div class="result-wrapper">
                                <div class="border-circle bg-primary inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-spinner-dotted pi-spin text-5xl"></i>
                                </div>
                                <h1>
                                    The next Einstein? Or just an average HTL Student?
                                </h1>
                            </div>
                        </template>
                    </Card>
                    <Card v-if="show_results_card">
                        <template #content>
                            <div class="result-wrapper">
                                <div v-if="game.current_question.result === 'wrong'" class="border-circle bg-red-500 inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-times text-5xl"></i>
                                </div>
                                <div v-if="game.current_question.result === 'timeout'" class="border-circle bg-yellow-500 inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-clock text-5xl"></i>
                                </div>
                                <div v-if="game.current_question.result === 'correct'" class="border-circle bg-green-500 inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-check text-5xl"></i>
                                </div>
                                <div v-if="game.current_question.result === 'unknown'" class="border-circle bg-yellow-500 inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-exclamation-triangle text-5xl"></i>
                                </div>
                                <h1 v-if="game.current_question.result === 'wrong'">
                                    Oh no, that wasn't right...
                                </h1>
                                <h1 v-if="game.current_question.result === 'correct'">
                                    Congrat's, you are correct!
                                </h1>
                                <h1 v-if="game.current_question.result === 'timeout'">
                                    You took too long, speed up!
                                </h1>
                                <h1 v-if="game.current_question.result === 'unknown'">
                                    Something went wrong internally...<br>
                                    Impossible Error, can't occur!<br>
                                    ...<br>
                                    Wait whaa.. How?!?
                                </h1>
                                <Button 
                                    label="View Ranking" 
                                    icon="pi pi-arrow-right" 
                                    icon-pos="left"
                                    @click="game.showRanking()"
                                />
                            </div>
                        </template>
                    </Card>
                    <Card v-if="show_ranking_card">
                        <template #content>
                            <div class="result-wrapper">
                                <div class="border-circle bg-primary inline-flex justify-content-center align-items-center h-6rem w-6rem -mt-8">
                                    <i class="pi pi-star text-5xl"></i>
                                </div>
                                <h1>
                                    Ranking
                                </h1>
                                <DataTable :value="ranking_formatted" class="ranking-table">
                                    <Column field="player" header="Player">
                                        <template #body="{ data }">
                                            <span :style="{color: data.player === username_entry ? 'var(--primary-700)' : 'inherit'}">
                                                {{ data.player }}
                                            </span>
                                        </template>
                                    </Column>
                                    <Column field="score" header="Score">
                                        <template #body="{ data }">
                                            <span :style="{color: data.player === username_entry ? 'var(--primary-700)' : 'inherit'}">
                                                {{ data.score }}
                                            </span>
                                        </template>
                                    </Column>
                                </DataTable>
                            </div>
                        </template>
                    </Card>
                </div>
            </Transition>

            <Dialog v-model:visible="show_disconnected_dialog" modal :style="{ width: '18rem' }">
                <template #container="{ closeCallback }">
                    <div class="flex flex-column align-items-center p-5 surface-overlay" style="border-radius: 11px;">
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
        </main>

    </div>
</template>


<style scoped>

.background {
    position: relative; /* for z level */
    width: 100%;
    height: 100%;
    background-color: var(--surface-ground);;
}

.bubble_field {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
}

main {
    position: relative; /* for z level */
    /* centering */
    display: grid;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
}

.kayeet-head-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.kayeet-head-wrapper > h1 {
    text-align: center;
}
.kayeet-head-wrapper > img {
    width: 12rem;
    text-align: center;
}

.content-wrapper {
    max-height: 10rem;
    transition: max-height 1s linear;
}

.setup-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 18rem;
}

.setup-form > * {
    width: 100%;
}

h1.logged-in-text {
    margin-top: 1.5em;
}
.logged-in-text {
    text-align: center;
}

.question-form {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    width: 40rem;
}

.question-form > * {
    width: 100%;
}

.result-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    width: 20rem;
}

.result-wrapper h1 {
    text-align: center;
}

.result-wrapper button {
    width: 12rem;
}

.ranking-table {
    width: 100%;
    max-height: 40vh;
    overflow-y: scroll;
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