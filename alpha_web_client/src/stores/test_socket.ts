/*
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
31.12.23, 20:52

Manages the integrated test websocket client
*/

import { ref, computed } from "vue"
import { defineStore } from "pinia"


let socket: WebSocket | null = null;

export enum SocketState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED
}

export type CommEventType = "incoming" | "outgoing" | "ctrl" | "error";

export interface CommEvent {
    data: string,
    type: CommEventType
};

export const useTestSocket = defineStore("test_socket", () => {
    
    const socket_state = ref(SocketState.DISCONNECTED);
    const incoming_count = ref(0);
    const outgoing_count = ref(0);
    const communication_log = ref<CommEvent[]>([]);

    function onOpen(this: WebSocket, e: Event): void {
        socket_state.value = SocketState.CONNECTED;

        communication_log.value.push({
            data: "Socket Connected",
            type: "ctrl"
        });
    }
    function onMessage(this: WebSocket, e: MessageEvent) {
        incoming_count.value++;
        communication_log.value.push({
            data: e.data as string,
            type: "incoming"
        })
    }
    function onError(this: WebSocket, e: Event) {
        communication_log.value.push({
            data: "Socket Error CB",
            type: "error"
        });
    }
    function onClose(this: WebSocket, e: Event) {
        socket = null;
        socket_state.value = SocketState.DISCONNECTED;

        communication_log.value.push({
            data: "Socket Disconnected",
            type: "ctrl"
        });
    }

    function openConnection() {
        if (socket_state.value !== SocketState.DISCONNECTED && socket !== null) {
            socket.close(0);
        }

        socket_state.value = SocketState.CONNECTING;

        socket = new WebSocket("ws://localhost:1647/");
        socket.onopen = onOpen;
        socket.onmessage = onMessage;
        socket.onerror = onError;
        socket.onclose = onClose;

    }    

    function sendMessage(content: string) {
        if (!socket)
            return;
        
        socket.send(content);

        outgoing_count.value++;
        communication_log.value.push({
            data: content,
            type: "outgoing"
        });
    }

    function closeConnection() {
        if (!socket)
            return;

        socket.close();
    }

    return {
        socket_state,
        incoming_count,
        outgoing_count,
        communication_log,
        openConnection,
        closeConnection,
        sendMessage
    };
})
