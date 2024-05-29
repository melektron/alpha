<!--
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Learning Game with competitive multiple-choice questions
-->

<script setup lang="ts">


import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useTestSocket, SocketState } from '@/stores/test_socket';
import type { CommEventType } from '@/stores/test_socket';
import type InputText from 'primevue/inputtext';
import TerminalService from 'primevue/terminalservice';
import { useConfirm } from 'primevue/useconfirm';

const socket = useTestSocket();

const communication_log_container = ref<HTMLDivElement[] | null>(null);
const send_buffer_input_element = ref<InstanceType<typeof InputText> | null>(null);

const auto_scroll = ref(true);
const keep_buffer = ref(false);
const send_buffer = ref("");

const confirm = useConfirm();




onMounted(() => {
});

onBeforeUnmount(() => {
});


</script>


<template>
    <main>
        asdf
    </main>
</template>


<style scoped>
main {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    overflow: auto;
    gap: 20px;
}

.note-disconnected {
    color: var(--red-300);
}

.note-connecting {
    color: var(--yellow-300);
}

.note-connected {
    color: var(--green-300);
}

:deep(.term-root) {
    border-radius: 6px; /* Needed to not cut splitter corners */
    border: none;
    height: 300px;
}

:deep(.term-welcome-msg),
:deep(.term-prompt) {
    color: gray;
}

:deep(.term-command) {
    color: var(--yellow-300);
}

:deep(.term-response) {
    color: var(--green-300);
}

.controls-panel {
    padding: var(--content-padding);
}

.controls-container {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: var(--content-padding);
}

.controls-panel .send-form {
    width: 100%;
}

:deep(.log-root) {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    flex: 1;
}

:deep(.log-toggleable-content) {
    flex: 1;
    overflow: hidden;
}

:deep(.log-container) {
    font-family: monospace;
    overflow: auto;
    width: 100%;
    height: 100%
}

@keyframes flash {
    0% {
        background-color: transparent;
    }

    50% {
        background-color: var(--primary-800);
    }

    100% {
        background-color: transparent;
    }
}

.log-entry-wrapper {
    animation: flash .4s ease-in-out;
}

.log-entry-prefix {
    color: var(--bluegray-500);
}

.log-entry-content-ctrl {
    color: var(--bluegray-500);
}

.log-entry-content-error {
    color: var(--red-300);
}

.log-entry-content-incoming {
    color: var(--green-300);
}

.log-entry-content-outgoing {
    color: var(--blue-300);
}

.log-entry-content-outgoing:hover, .log-entry-content-incoming:hover {
    background-color: var(--primary-800);
    border-radius: 4px;
    cursor: copy;
}

.log-entry-content-outgoing:hover + .log-entry-redo, .log-entry-content-incoming:hover + .log-entry-redo {
    display: inline-block;  /* show .log-entry-redo only when hovering an incoming/outgoing entry */
}

.log-entry-redo {
    display: none;
    padding-left: 5px;
    font-weight: bold;
    transform: scale(1.5) translateY(-10%);
}
</style>