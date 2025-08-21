/*
Based on eram/typescript-fsm:
    StateMachine.ts (https://github.com/eram/typescript-fsm/blob/master/src/stateMachine.ts)
    TypeScript finite state machine class with async transformations using promises.

Modifications to fit this project's needs:
    ELEKTRON © 2024 - now
    Modifications written by melektron
    www.elektron.work
    23.04.24, 12:46

A reactive Finite State Machine implementation for typescript
*/

import { ref, shallowRef } from "vue"
import type { Ref, UnwrapRef } from "vue";

export type Callback = ((...args: any) => Promise<void>) | ((...args: any) => void);


export interface ITransition<STATE, EVENT> {
    from_state: STATE;
    event: EVENT;
    to_state: STATE;
    cb: Callback | undefined;
}

export function t<STATE, EVENT>(
    from_state: STATE,
    event: EVENT,
    to_state: STATE,
    cb?: Callback
): ITransition<STATE, EVENT> {
    return { from_state, event, to_state, cb };
}

export class StateMachine<
    STATE extends string | number | symbol,
    EVENT extends string | number | symbol
> {

    protected current_state: Ref<STATE>;

    // initialize the state-machine
    constructor(
        initial_state: STATE,
        protected transitions: ITransition<STATE, EVENT>[] = []
    ) {
        this.current_state = shallowRef<STATE>(initial_state);
    }

    get state() {
        // can return value here directly because we are in a getter
        return this.current_state.value
    }

    addTransitions(transitions: ITransition<STATE, EVENT>[]): void {
        // bind any unbound method
        transitions.forEach((_tran) => {
            const tran: ITransition<STATE, EVENT> = Object.create(_tran);
            if (tran.cb && !tran.cb.name?.startsWith("bound ")) {
                tran.cb = tran.cb.bind(this);
            }
            this.transitions.push(tran);
        });
    }

    can(event: EVENT): boolean {
        return this.transitions.some((trans) => (
            (trans.from_state === this.current_state.value) 
            && trans.event === event
        ));
    }

    getNextState(event: EVENT): STATE | undefined {
        const transition = this.transitions.find((tran) => (
            (tran.from_state === this.current_state.value)
            && tran.event === event
            ));
        return transition?.to_state;
    }

    isFinal(): boolean {
        // search for a transition that starts from current state.
        // if none is found it's a terminal state.
        return this.transitions.every((trans) => (trans.from_state !== this.current_state.value));
    }
    
    async dispatchIfPossible<E extends EVENT>(event: E, ...args: unknown[]): Promise<void> {
        if (this.can(event))
            this.dispatch(event, ...args);
        else
            console.log(`Doing nothing because there is no transition from ${String(this.state)} with event ${String(event)}`)
    }
 
    // post event async
    async dispatch<E extends EVENT>(event: E, ...args: unknown[]): Promise<void> {
        return new Promise<void>((resolve, reject) => {

            // delay execution to make it async
            setTimeout(() => {

                // find transition
                const found = this.transitions.some((tran) => {
                    if (tran.from_state === this.current_state.value && tran.event === event) {
                        this.current_state.value = tran.to_state;
                        if (tran.cb) {
                            try {
                                const p = tran.cb(...args);
                                if (p instanceof Promise) {
                                    p.then(resolve).catch((e: Error) => reject(e));
                                } else {
                                    resolve();
                                }
                            } catch (e) {
                                console.error("Exception caught in callback", e);
                                reject(e);
                            }
                        } else {
                            resolve();
                        }
                        return true;
                    }
                    return false;
                });

                // no such transition
                if (!found) {
                    const errorMessage = this.#formatNoTransitionError(this.current_state.value, event);
                    reject(new Error(errorMessage));
                }
            }, 0);
        });
    }

    #formatNoTransitionError(fromState: STATE, event: EVENT) {
        return `No transition: from ${String(fromState)} event ${String(event)}`;
    }
}