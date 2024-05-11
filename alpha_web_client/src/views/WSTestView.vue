<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Home page with overview
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

const server_addr = ref("ws://localhost:1647/");
const auto_scroll = ref(true);
const keep_buffer = ref(false);
const send_buffer = ref("");

const confirm = useConfirm();

function onCommand(command: string) {
    console.log(command);
    switch (command) {
        case "connect":
            socket.openConnection(server_addr.value);
            TerminalService.emit("response", "Connecting ...");
            break;
        case "disconnect":
            socket.openConnection(server_addr.value);
            TerminalService.emit("response", "Disconnecting ...");
            break;
        case "auth":
            socket.openConnection(server_addr.value);
            break;
        case "a":
            socket.communication_log.push({ data: "a", type: "ctrl" });
            break;

        default:
            break;
    }
}

function logPrefixForType(t: CommEventType): string {
    switch (t) {
        case "ctrl":
            return ".."
        case "error":
            return "!!"
        case "incoming":
            return "->"
        case "outgoing":
            return "<-"
    }
}

function focusSendBufferInputElement() {
    // @ts-ignore   (Not officially supported to use $el)
    send_buffer_input_element.value?.$el.focus();
}

function sendCurrentBuffer() {
    socket.sendMessage(send_buffer.value);
    if (!keep_buffer.value)
        send_buffer.value = "";
}

function confirmClearLog() {
    confirm.require({
        message: 'Are you sure you want to clear the log?',
        header: 'Clear communication log?',
        icon: 'pi pi-exclamation-triangle',
        rejectClass: 'p-button-secondary p-button-outlined',
        acceptClass: 'p-button-danger',
        rejectLabel: 'Cancel',
        acceptLabel: 'Clear Log',
        accept: () => {
            socket.clearLog();
        },
        reject: () => {}
    });
}

onMounted(() => {
    TerminalService.on("command", onCommand);
});

onBeforeUnmount(() => {
    TerminalService.off("command", onCommand);
});

// whenever the communication log changes, scroll last entry into view
watch(socket.communication_log, async () => {
    if (!auto_scroll.value)
        return;

    const element = communication_log_container.value?.pop()?.parentElement
    if (!element)
        return;

    // wait until render b/c wrong dimensions will be calculated otherwise
    // https://stackoverflow.com/a/66754681
    await nextTick();
    element.scrollTop = element.scrollHeight;
});

</script>


<template>
    <main>
        <h1>WebSocket Test </h1>
        <Toolbar>
            <template #start>
                <span class="note-disconnected" v-if="socket.socket_state === SocketState.DISCONNECTED"> Disconnected
                </span>
                <span class="note-connecting" v-if="socket.socket_state === SocketState.CONNECTING"> Connecting ... </span>
                <span class="note-connected" v-if="socket.socket_state === SocketState.CONNECTED"> Connected </span>
            </template>
            <template #end>
                <InputText v-model="server_addr" style="margin-right: 20px; width: 16rem;" placeholder="Server Address" />
                <Button v-if="socket.socket_state === SocketState.DISCONNECTED" @click="socket.openConnection(server_addr)"
                    severity="success">
                    Connect
                </Button>
                <Button v-else @click="socket.closeConnection()" severity="danger">
                    Disconnect
                </Button>

                <span style="padding-left: 20px; padding-right: 10px;">Keep Buffer</span>
                <InputSwitch v-model="keep_buffer" />
                <span style="padding-left: 20px; padding-right: 10px;">Autoscroll</span>
                <InputSwitch v-model="auto_scroll" />
            </template>
        </Toolbar>

        <Splitter>
            <SplitterPanel :size="30" :min-size="10">
                <Terminal welcome-message="Welcome to Socket Test" prompt=">&nbsp" :pt="{
                    root: 'term-root',
                    welcomeMessage: 'term-welcome-msg',
                    prompt: 'term-prompt',
                    command: 'term-command',        // previous commands
                    commandText: 'term-command',    // new command
                    response: 'term-response'
                }" />
            </SplitterPanel>
            <SplitterPanel :size="70" class="controls-panel">
                <div class="controls-container">
                    <form @submit.prevent="sendCurrentBuffer" class="send-form">
                        <InputGroup>
                            <InputText v-model="send_buffer" ref="send_buffer_input_element" placeholder="Outgoing Data ..." />
                            <Button type="submit">Send</Button>
                        </InputGroup>
                    </form>
                    <Button @click="confirmClearLog()" severity="danger" outlined>Clear Log</Button>
                </div>
            </SplitterPanel>
        </Splitter>
        
        <!-- Confirmation dialog for things like clear log -->
        <ConfirmDialog />

        <Panel header="Communication Log" :pt="{
            content: 'log-container',
            toggleableContent: 'log-toggleable-content',    // the outer element wrapping the content for sizing config
            root: 'log-root'
        }">
            <div v-for="entry in socket.communication_log" class="log-entry-wrapper" ref="communication_log_container">
                <span class="log-entry-prefix">{{ logPrefixForType(entry.type) }}&nbsp</span>
                <span :class="{
                    'log-entry-content-ctrl': entry.type == 'ctrl',
                    'log-entry-content-error': entry.type == 'error',
                    'log-entry-content-incoming': entry.type == 'incoming',
                    'log-entry-content-outgoing': entry.type == 'outgoing'
                }" @dblclick="() => {
                    if (entry.type === 'incoming' || entry.type === 'outgoing') {
                        send_buffer = entry.data;
                        focusSendBufferInputElement();
                    }
                }">
                    {{ entry.data }}
                </span>
                <!-- The following element is shown to indicate the entry can be re-sent -->
                <span v-if="entry.type === 'outgoing' || entry.type === 'incoming'" class="log-entry-redo">&#8634</span>
            </div>
        </Panel>


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