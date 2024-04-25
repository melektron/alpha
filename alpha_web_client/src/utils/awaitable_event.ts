
//TODO: maybe implement this, would be cool. This is basically resolving all stored promises whenever a method is called

type Waiter<ET> = (value: ET | PromiseLike<ET>) => void

export class AwaitableEvent<ET> {
    protected waiters: Waiter<ET>[]

    constructor() {
        this.waiters = [];
    }

    get next(): Promise<ET> {
        return new Promise<ET>((resolve, reject) => {
            this.waiters.push(resolve);
        });
    }

    //// makes a thenable object that can be awaited
    //then(resolve: Waiter<ET>, other: any): any {
    //    this.waiters.push(resolve);
    //}

    happened(e: ET) {
        this.waiters.forEach((p) => p(e))
        this.waiters = []
    }
}