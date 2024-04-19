/*
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
31.12.23, 20:52

Manages the integrated test websocket client
*/

import { ref, computed } from "vue"
import { defineStore } from "pinia"
import { useLocalStorage } from "@vueuse/core";


let socket: WebSocket | null = null;


// possible library to help with this? https://github.com/eram/typescript-fsm
export enum GameState {
    /* Disconnected States */
    DISCONNECTED,       // not connected, shows disconnected screen
    READY_TO_CONNECT,   // still not connected but now showing user the option to enter server addr
    CONNECTING,         // awaiting connection to open
    /* Connected States */ 
    READY_TO_LOG_IN,    // connected, now waiting for user login
    AWAITING_LOGIN_ACK, // login message sent, waiting for login to be acknowledged
    LOGIN_ERROR,        // login failed, shows the failed error page
    LOGGED_IN           // logged in, waiting for game to start
}

export const useKaYeetGame = defineStore("kayeet", () => {
    
    const game_state = ref(GameState.READY_TO_CONNECT);

    /*
     * WebSocket callbacks 
     */

    function _onOpen(this: WebSocket, e: Event): void {
        game_state.value = GameState.READY_TO_LOG_IN;
        console.info("Socket Connected");
    }
    function _onMessage(this: WebSocket, e: MessageEvent) {
        console.log("Got message:", e.data)
    }
    function _onError(this: WebSocket, e: Event) {
        console.error("Socket Error CB");
    }
    function _onClose(this: WebSocket, e: CloseEvent) {
        console.info(`Socket Disconnected with code ${e.code} (${e.reason})`);
        socket = null;
        game_state.value = GameState.DISCONNECTED;
    }

    /*
     * Internal functions
     */

    function sendMessage(content: string) {
        if (!socket)
            return;
        
        socket.send(content);

        console.log("sending message:", content)
    }

    /**
     * completes a sortof correct user-provided game server host to a valid URL.
     * @param input_host some string representing a server address
     * @returns URL object pointing to the server with valid proto and other 
     * missing options default completed
     */
    function completeURL(input_host: string): URL {
        // default for testing
        if (input_host.length === 0)
            input_host = "ws://localhost:1647"

        // Check if the input host starts with ws or wss
        if (!/^wss?:\/\//i.test(input_host)) {
            // If not, prepend ws://
            console.log("no proto")
            input_host = 'ws://' + input_host;
        }
        // Now construct the URL
        var url = new URL(input_host);
        // set the port to default if not provided
        if (url.port === "")
            url.port = "1647";
        return url;
    }

    /*
     * Public functions
     */

    function connectToGameServer(host: string) {
        // if already connected, disconnect and connect to new server
        if (game_state.value >= GameState.READY_TO_LOG_IN && socket !== null) {
            socket.close(0);
            socket = null;
        }

        const url = completeURL(host);
        game_state.value = GameState.CONNECTING;
        socket = new WebSocket(url);
        socket.onopen = _onOpen;
        socket.onmessage = _onMessage;
        socket.onerror = _onError;
        socket.onclose = _onClose;
    }    


    function disconnect() {
        if (!socket)
            return;

        socket.close();
    }

    return {
        game_state,
        connectToGameServer,
        disconnect,
        is_connection_phase: computed(() => [
            GameState.READY_TO_CONNECT, 
            GameState.CONNECTING
        ].includes(game_state.value)),
        is_login_phase: computed(() => [
            GameState.READY_TO_LOG_IN, 
            GameState.AWAITING_LOGIN_ACK, 
            GameState.LOGIN_ERROR, 
            GameState.LOGGED_IN
        ].includes(game_state.value))
    };
})
