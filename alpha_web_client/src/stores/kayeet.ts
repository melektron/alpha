/*
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
31.12.23, 20:52

Manages the kayeet game state
*/

import { ref, computed, reactive } from "vue";
import { defineStore } from "pinia";
import { t, StateMachine } from "@/utils/reactive_fsm";
import { ErrorCode, QuestionType, incoming_message, login_message, question_message, text_question_message, type AnswerMessage, type IncomingMessage, type LoginMessage, type QuestionMessage } from "./kayeet_messages";


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
    LOGGED_IN,          // logged in, waiting for game to start

    QUESTION_TEXT,      // show a text input question
    QUESTION_YES_NO,    // show a yes/no question
    QUESTION_MULTI,     // show a multiple choice question
    AWAITING_RESULT,    // awaiting the question result (answer has been selected by user)
    DISPLAYING_RESULT,  // displays the question result (wether we were correct, incorrect or timed out)
    DISPLAYING_SCORES, // displays the leader board of all users
}

export enum GameEvents {
    ACK_ERROR = "ACK_ERROR",
    ATTEMPT_CONNECT = "ATTEMPT_CONNECT",
    CONNECTION_SUCCESS = "CONNECTION_SUCCESS",
    CONNECTION_ERROR = "CONNECTION_ERROR",
    ATTEMPT_LOGIN = "LOGIN_REQ_SENT",
    LOGIN_NAK_RECEIVED = "LOGIN_NAK_RECEIVED",
    LOGIN_ACK_RECEIVED = "LOGIN_ACK_RECEIVED",

    RECEIVED_TEXT_Q = "RECEIVED_TEXT_Q",
    RECEIVED_YES_NO_Q = "RECEIVED_YES_NO_Q",
    RECEIVED_MULTI_Q = "RECEIVED_MULTI_Q",
    SUBMIT_ANSWER = "SUBMIT_ANSWER",
    ANSWER_TIMEOUT = "ANSWER_TIMEOUT",
    RESULT_RECEIVED = "RESULT_RECEIVED",
    SHOW_STATS = "STATS_RECEIVED",

    DISCONNECTED = "DISOCNNECTED",
    UNCONDITIONAL_RESET = "UNCONDITIONAL_RESET"
}


export const useKaYeetGame = defineStore("kayeet", () => {

    let socket: WebSocket | null = null;
    const transitions = [
        /* fromState                    event                           toState                         callback */
        t(GameStates.READY_TO_CONNECT,  GameEvents.ATTEMPT_CONNECT,     GameStates.CONNECTING,          _attemptConnect),
        t(GameStates.CONNECTING,        GameEvents.CONNECTION_SUCCESS,  GameStates.READY_TO_LOG_IN,     undefined),
        t(GameStates.CONNECTING,        GameEvents.CONNECTION_ERROR,    GameStates.CONNECTION_FAILED,   _connectionFailed),
        // going from connection to disconnected should do the same thing as connection failed.
        // browsers don't call close or fail reliably, so both do the same thing, whichever is first.
        t(GameStates.CONNECTING,        GameEvents.DISCONNECTED,        GameStates.CONNECTION_FAILED,   undefined),
        t(GameStates.READY_TO_LOG_IN,   GameEvents.ATTEMPT_LOGIN,       GameStates.AWAITING_LOGIN_ACK,  _attemptLogin),
        t(GameStates.AWAITING_LOGIN_ACK,GameEvents.LOGIN_NAK_RECEIVED,  GameStates.LOGIN_ERROR,         undefined),
        t(GameStates.AWAITING_LOGIN_ACK,GameEvents.LOGIN_ACK_RECEIVED,  GameStates.LOGGED_IN,           undefined),
        
        // error acknowledgement
        t(GameStates.DISCONNECTED,      GameEvents.ACK_ERROR,           GameStates.READY_TO_CONNECT,    undefined),
        t(GameStates.CONNECTION_FAILED, GameEvents.ACK_ERROR,           GameStates.READY_TO_CONNECT,    undefined),
        t(GameStates.LOGIN_ERROR,       GameEvents.ACK_ERROR,           GameStates.READY_TO_CONNECT,    undefined),

        // questioning procedure
        // enter question from initial logged in screen
        t(GameStates.LOGGED_IN,         GameEvents.RECEIVED_TEXT_Q,     GameStates.QUESTION_TEXT,       undefined),
        t(GameStates.LOGGED_IN,         GameEvents.RECEIVED_YES_NO_Q,   GameStates.QUESTION_YES_NO,     undefined),
        t(GameStates.LOGGED_IN,         GameEvents.RECEIVED_MULTI_Q,    GameStates.QUESTION_MULTI,      undefined),
        // enter question after displaying scores or results if scores are not shown yet
        t(GameStates.DISPLAYING_SCORES, GameEvents.RECEIVED_TEXT_Q,     GameStates.QUESTION_TEXT,       undefined),
        t(GameStates.DISPLAYING_SCORES, GameEvents.RECEIVED_YES_NO_Q,   GameStates.QUESTION_YES_NO,     undefined),
        t(GameStates.DISPLAYING_SCORES, GameEvents.RECEIVED_MULTI_Q,    GameStates.QUESTION_MULTI,      undefined),
        t(GameStates.DISPLAYING_RESULT, GameEvents.RECEIVED_TEXT_Q,     GameStates.QUESTION_TEXT,       undefined),
        t(GameStates.DISPLAYING_RESULT, GameEvents.RECEIVED_YES_NO_Q,   GameStates.QUESTION_YES_NO,     undefined),
        t(GameStates.DISPLAYING_RESULT, GameEvents.RECEIVED_MULTI_Q,    GameStates.QUESTION_MULTI,      undefined),
        // TODO: add the otehr three ones
        // continue from question when submitting an answer
        t(GameStates.QUESTION_TEXT,     GameEvents.SUBMIT_ANSWER,       GameStates.AWAITING_RESULT,     undefined),
        t(GameStates.QUESTION_YES_NO,   GameEvents.SUBMIT_ANSWER,       GameStates.AWAITING_RESULT,     undefined),
        t(GameStates.QUESTION_MULTI,    GameEvents.SUBMIT_ANSWER,       GameStates.AWAITING_RESULT,     undefined),
        // continue from question when answer times out
        t(GameStates.QUESTION_TEXT,     GameEvents.ANSWER_TIMEOUT,      GameStates.DISPLAYING_RESULT,   undefined),
        t(GameStates.QUESTION_YES_NO,   GameEvents.ANSWER_TIMEOUT,      GameStates.DISPLAYING_RESULT,   undefined),
        t(GameStates.QUESTION_MULTI,    GameEvents.ANSWER_TIMEOUT,      GameStates.DISPLAYING_RESULT,   undefined),
        // after submission wait, transition to showing results
        t(GameStates.AWAITING_RESULT,   GameEvents.RESULT_RECEIVED,     GameStates.DISPLAYING_RESULT,   undefined),
        // we might get a timeout after submitting a question if a race condition occurs due to network delays. This accounts for that.
        t(GameStates.AWAITING_RESULT,   GameEvents.ANSWER_TIMEOUT,      GameStates.DISPLAYING_RESULT,   undefined),
        // after the own results are displayed, show the leader board
        t(GameStates.DISPLAYING_RESULT, GameEvents.SHOW_STATS,      GameStates.DISPLAYING_SCORES,   undefined),
        
        // disconnects that go to disconnected state (to show it a general disconnect message) can happen during any of the fully connected states
        t(GameStates.READY_TO_LOG_IN,   GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.AWAITING_LOGIN_ACK,GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.LOGIN_ERROR,       GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.LOGGED_IN,         GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.QUESTION_TEXT,     GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.QUESTION_YES_NO,   GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.QUESTION_MULTI,    GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.AWAITING_RESULT,   GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.DISPLAYING_RESULT, GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),
        t(GameStates.DISPLAYING_SCORES, GameEvents.DISCONNECTED,        GameStates.DISCONNECTED,        undefined),

        // resets
        t(GameStates.DISCONNECTED,      GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.READY_TO_CONNECT,  GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.CONNECTING,        GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.CONNECTION_FAILED, GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.READY_TO_LOG_IN,   GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.AWAITING_LOGIN_ACK,GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.LOGIN_ERROR,       GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.LOGGED_IN,         GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.QUESTION_TEXT,     GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.QUESTION_YES_NO,   GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.QUESTION_MULTI,    GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.AWAITING_RESULT,   GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.DISPLAYING_RESULT, GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
        t(GameStates.DISPLAYING_SCORES, GameEvents.UNCONDITIONAL_RESET, GameStates.READY_TO_CONNECT,    _unconditionalReset),
    ];

    // state machine representing the game's state
    const machine = new StateMachine(GameStates.READY_TO_CONNECT, transitions);

    interface CurrentQuestion {
        text: string,
        choices: string[],
        id: number,
        result: "unknown" | "correct" | "wrong" | "timeout",
        type: QuestionType
    }
    const current_question = reactive<CurrentQuestion>({
        text: "",
        choices: [],
        id: 0,
        result: "unknown",
        type: QuestionType.TextQuestion
    });
    type Ranking = [number, string][];
    const ranking = ref<Ranking>([]);

    /*
     * WebSocket callbacks 
     */
    function _onOpen(this: WebSocket, e: Event): void {
        console.info("Socket Connected");
        machine.dispatchIfPossible(GameEvents.CONNECTION_SUCCESS);
    }
    function _onMessage(this: WebSocket, e: MessageEvent) {
        console.log("Got message:", e.data)

        let msg;
        try {
            const data_obj = JSON.parse(e.data);
            msg = incoming_message.parse(data_obj);
            switch (msg.type) {
                case "confirm":
                    machine.dispatch(GameEvents.LOGIN_ACK_RECEIVED)
                    break;
                
                case "error":
                    console.log(`Received API error: ${ErrorCode[msg.error_type]}, cause: "${msg.cause ?? ""}"`)
                    switch (msg.error_type) {
                        case ErrorCode.InvalidLogin:
                            machine.dispatch(GameEvents.LOGIN_NAK_RECEIVED);
                            break;
                        
                        case ErrorCode.QuestionTimeout:
                            current_question.result = "timeout";
                            machine.dispatchIfPossible(GameEvents.ANSWER_TIMEOUT);
                            break;
                    
                        default:
                            break;
                    }
                    break;
                
                case "question":
                    msg = question_message.parse(msg);
                    current_question.text = msg.question;
                    current_question.id = msg.id;
                    current_question.result = "unknown";
                    current_question.type = msg.question_type;
                    if (msg.question_type === QuestionType.TextQuestion) {
                        machine.dispatch(GameEvents.RECEIVED_TEXT_Q);
                    } else if (msg.question_type === QuestionType.YesNoQuestion) {
                        machine.dispatch(GameEvents.RECEIVED_YES_NO_Q);
                    } else if (msg.question_type === QuestionType.MultiQuestion) {
                        current_question.choices = msg.choices;
                        machine.dispatch(GameEvents.RECEIVED_MULTI_Q);
                    }
                    break;
                
                case "result":
                    current_question.result = msg.result ? "correct" : "wrong";
                    machine.dispatch(GameEvents.RESULT_RECEIVED);
                    break;
                
                case "stats":
                    ranking.value = msg.ranking;
                    break;
            
                default:
                    break;
            }
        } catch (error) {
            console.error("Error parsing kayeet message (ignored):", error);
            return;
        }
        
        
    }
    function _onError(this: WebSocket, e: Event) {
        console.error("Socket Error CB");
        machine.dispatchIfPossible(GameEvents.CONNECTION_ERROR);
    }
    function _onClose(this: WebSocket, e: CloseEvent) {
        console.info(`Socket Disconnected with code ${e.code} (${e.reason})`);
        socket = null;
        machine.dispatchIfPossible(GameEvents.DISCONNECTED);
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
        // immediately acknowledge this error, going back to ready state
        machine.dispatch(GameEvents.ACK_ERROR)
    }
    function _attemptLogin(username: string) {
        const msg: LoginMessage = {
            type: "login",
            username: username
        }
        sendMessage(msg);
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
    function sendMessage(content: any) {
        if (!socket)
            return;

        const outstring = JSON.stringify(content);
        socket.send(outstring);
        console.log("sending message:", outstring)
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
            input_host = 'wss://' + input_host;
        }
        // Now construct the URL
        var url = new URL(input_host);
        // set the port to default if not provided
        if (url.port === "" && url.protocol === "ws:")
            url.port = "1647";
        return url;
    }

    /*
     * Public functions
     */

    async function reset() {
        await machine.dispatch(GameEvents.UNCONDITIONAL_RESET);
    }

    function connectToGameServer(host: string) {
        // if already connected, this doesn't make sense
        if (machine.state >= GameStates.READY_TO_LOG_IN) {
            console.warn("connectToGameServer() called while not in ready state, ignoring");
            return
        }

        machine.dispatch(GameEvents.ATTEMPT_CONNECT, completeURL(host));
    }

    function login(username: string) {
        if (machine.state !== GameStates.READY_TO_LOG_IN) {
            console.warn("login() called during invalid state, ignoring")
            return
        }

        machine.dispatch(GameEvents.ATTEMPT_LOGIN, username);
    }

    function showRanking() {
        machine.dispatchIfPossible(GameEvents.SHOW_STATS);
    }

    function acknowledgeError() {
        machine.dispatch(GameEvents.ACK_ERROR);
    }

    function answerQuestion(answer: string | boolean | number) {
        let msg: AnswerMessage = {
            answer_to: current_question.id,
            answer: answer,
            type: "answer",
        };
        sendMessage(msg);
        machine.dispatchIfPossible(GameEvents.SUBMIT_ANSWER);
    }

    return {
        current_question,
        ranking,
        reset,
        state: computed(() => machine.state),
        connectToGameServer,
        login,
        acknowledgeError,
        answerQuestion,
        showRanking,
    };
})
