<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Home page with overview
-->

<script setup lang="ts">

import { useTestSocket, SocketState} from '@/stores/test_socket';
import type { CommEventType } from '@/stores/test_socket';
import TerminalService from 'primevue/terminalservice';
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';

const socket = useTestSocket();
const communication_log_container = ref<HTMLDivElement[] | null>(null);

const auto_scroll = ref(true);

function onCommand(command: string) {
    console.log(command);
    switch (command) {
        case "connect":
            socket.openConnection();
            TerminalService.emit("response", "Connecting ...");
            break;
        case "disconnect":
            socket.openConnection();
            TerminalService.emit("response", "Disconnecting ...");
            break;
        case "auth":
            socket.openConnection();
            break;
        case "a":
            socket.communication_log.push({data: "a", type:"ctrl"});
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
                <span class="note-disconnected" v-if="socket.socket_state === SocketState.DISCONNECTED"> Disconnected </span>
                <span class="note-connecting" v-if="socket.socket_state === SocketState.CONNECTING"> Connecting ... </span>
                <span class="note-connected" v-if="socket.socket_state === SocketState.CONNECTED"> Connected </span>
            </template>
            <template #end>
                <Button 
                    v-if="socket.socket_state === SocketState.DISCONNECTED" 
                    @click="socket.openConnection()" 
                    severity="success"
                >
                    Connect
                </Button>
                <Button 
                    v-else
                    @click="socket.closeConnection()" 
                    severity="danger"
                >
                    Disconnect
                </Button>

                <span style="padding-left: 20px; padding-right: 10px;">Autoscroll</span>
                <InputSwitch v-model="auto_scroll" />
            </template>
        </Toolbar>
        <Terminal 
            welcome-message="Welcome to Socket Test"
            prompt=">&nbsp"
            :pt="{
                root: 'term-root',
                welcomeMessage: 'term-welcome-msg',
                prompt: 'term-prompt',
                command: 'term-command',        // previous commands
                commandText: 'term-command',    // new command
                response: 'term-response'
            }"
        />

        <Panel header="Communication Log" :pt="{
            content: 'log-container',
            toggleableContent: 'log-toggleable-content',    // the outer element wrapping the content for sizing config
            root: 'log-root'
        }">
            <div 
                v-for="entry in socket.communication_log" 
                class="log-entry-wrapper"
                ref="communication_log_container"
            >
                <span class="log-entry-prefix">{{ logPrefixForType(entry.type) }}&nbsp</span>
                <span :class="{
                    'log-entry-content-ctrl': entry.type == 'ctrl',
                    'log-entry-content-error': entry.type == 'error',
                    'log-entry-content-incoming': entry.type == 'incoming',
                    'log-entry-content-outgoing': entry.type == 'outgoing'
                }">
                    {{ entry.data }}
                </span>
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
    border-radius: 6px;
    height: 300px;
}

:deep(.term-welcome-msg), :deep(.term-prompt) {
    color: gray;
}

:deep(.term-command) {
    color: var(--yellow-300);
}

:deep(.term-response) {
    color: var(--green-300);
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

</style>