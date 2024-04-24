/*
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
31.12.23, 20:52

Manages the kayeet game state
*/

import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { useLocalStorage } from "@vueuse/core";
import { t, StateMachine } from "@/utils/reactive_fsm";
import mitt from "mitt";


// possible library to help with this? https://github.com/eram/typescript-fsm
export enum GameStates {
    /* Disconnected States */
    DISCONNECTED,       // not connected, shows disconnected screen
    READY_TO_CONNECT,   // still not connected but now showing user the option to enter server addr
    CONNECTING,         // awaiting connection to open
    CONNECTION_FAILED,  // websocket connection has failed
    /* Connected States */ 
    READY_TO_LOG_IN,    // websocket connected, now waiting for user to log in
    AWAITING_LOGIN_ACK, // login message sent, waiting for login to be acknowledged
    LOGIN_ERROR,        // login failed, shows the failed error page
    LOGGED_IN           // logged in, waiting for game to start
}

export enum GameEvents {
    ACK_ERROR = "ACK_ERROR",
    ATTEMPT_CONNECT = "ATTEMPT_CONNECT",
    CONNECTION_SUCCESS = "CONNECTION_SUCCESS",
    CONNECTION_ERROR = "CONNECTION_ERROR",
    LOGIN_REQ_SENT = "LOGIN_REQ_SENT",
    LOGIN_NAK_RECEIVED = "LOGIN_NAK_RECEIVED",
    LOGIN_ACK_RECEIVED = "LOGIN_ACK_RECEIVED",

    UNCONDITIONAL_RESET = "UNCONDITIONAL_RESET"
}


export const useKaYeetGame = defineStore("kayeet", () => {

    let socket: WebSocket | null = null;
    const transitions = [
        /* fromState                    event                           toState                         callback */
        t(GameStates.READY_TO_CONNECT,  GameEvents.ATTEMPT_CONNECT,     GameStates.CONNECTING,          _attemptConnect),
        t(GameStates.CONNECTING,        GameEvents.CONNECTION_SUCCESS,  GameStates.READY_TO_LOG_IN,     undefined),
        t(GameStates.CONNECTING,        GameEvents.CONNECTION_ERROR,    GameStates.CONNECTION_FAILED,   _connectionFailed),
        t(GameStates.READY_TO_LOG_IN,   GameEvents.LOGIN_REQ_SENT,      GameStates.AWAITING_LOGIN_ACK,  undefined),
        t(GameStates.AWAITING_LOGIN_ACK,GameEvents.LOGIN_NAK_RECEIVED,  GameStates.LOGIN_ERROR,         undefined),
        t(GameStates.AWAITING_LOGIN_ACK,GameEvents.LOGIN_ACK_RECEIVED,  GameStates.LOGGED_IN,           undefined),
        
        // error acknowledgement
        t(GameStates.DISCONNECTED,      GameEvents.ACK_ERROR,           GameStates.READY_TO_CONNECT,    undefined),
        t(GameStates.CONNECTION_FAILED, GameEvents.ACK_ERROR,           GameStates.READY_TO_CONNECT,    undefined),
        t(GameStates.LOGIN_ERROR,       GameEvents.ACK_ERROR,           GameStates.READY_TO_CONNECT,    undefined),

        // resets
        t(GameStates.DISCONNECTED,      GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.READY_TO_CONNECT,  GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.CONNECTING,        GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.CONNECTION_FAILED, GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.READY_TO_LOG_IN,   GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.AWAITING_LOGIN_ACK,GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.LOGIN_ERROR,       GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.LOGGED_IN,         GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
    ];

    // state machine representing the game's state
    const machine = new StateMachine(GameStates.READY_TO_CONNECT, transitions);

    /*
     * WebSocket callbacks 
     */
    function _onOpen(this: WebSocket, e: Event): void {
        machine.dispatch(GameEvents.CONNECTION_SUCCESS);
        console.info("Socket Connected");
    }
    function _onMessage(this: WebSocket, e: MessageEvent) {
        console.log("Got message:", e.data)
    }
    function _onError(this: WebSocket, e: Event) {
        machine.dispatch(GameEvents.CONNECTION_ERROR);
        console.error("Socket Error CB");
    }
    function _onClose(this: WebSocket, e: CloseEvent) {
        // TODO: maybe transition do disconnected (when transition is allowed will still need to be though about)
        console.info(`Socket Disconnected with code ${e.code} (${e.reason})`);
        socket = null;
    }

    /**
     * FSM callbacks
     */

    function _attemptConnect(url: URL) {
        socket = new WebSocket(url);
        socket.onopen = _onOpen;
        socket.onmessage = _onMessage;
        socket.onerror = _onError;
        socket.onclose = _onClose;
    }
    function _connectionFailed() {
        // immediately switch back to 
        machine.dispatch(GameEvents.ACK_ERROR)
    }

    /**
     * game is being reset to starting state. This function is 
     * meant to clean up any side effects (such as the socket connection)
     * outside the FSM
     */
    function _unconditionalReset(): void {
        // close the socket if it is still open.
        if (socket)
        {
            socket.close();
            socket = null;
        }
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
        // if already connected, this doesn't make sense
        if (machine.state >= GameStates.READY_TO_LOG_IN) {
            console.warn("connectToGameServer() called while not in ready state, ignoring");
            return
        }

        const url = completeURL(host);
        machine.dispatch(GameEvents.ATTEMPT_CONNECT, url);
    }

    async function reset() {
        await machine.dispatch(GameEvents.UNCONDITIONAL_RESET);
    }

    return {
        state: computed(() => machine.state),
        connectToGameServer,
        reset,
    };
})
