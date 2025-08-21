<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:46

Home page with overview
-->

<script setup lang="ts">

import { useCounterStore } from '@/stores/counter';
import { reactive, ref } from 'vue';
import { z } from 'zod'

const counter = useCounterStore();

interface MyObjType {
    a: number
    b: number
    c: number
}

const dstruct = reactive<{ mydata: MyObjType[] }>({
    mydata: [
        {
            a: 1,
            b: 2,
            c: 3
        }
    ]
});

function appendObject() {
    dstruct.mydata.push({
        a: counter.count++,
        b: counter.count++,
        c: counter.count++
    });
}

function setCounterLow() {
    counter.count = Math.round(dstruct.mydata.length / 2);
}

function modifyTarget() {
    let pos = counter.count;
    if (pos >= dstruct.mydata.length)
        return;

    let target_row = dstruct.mydata[pos];
    target_row.a++;
    target_row.b--;
    target_row.c *= 2;
}

function replaceList() {
    dstruct.mydata = [
        {
            a: counter.count++,
            b: counter.count++,
            c: counter.count++
        },
        {
            a: counter.count++,
            b: counter.count++,
            c: counter.count++
        },
        {
            a: counter.count++,
            b: counter.count++,
            c: counter.count++
        }
    ];
}

const Dog = z.object({
    name: z.string(),
    age: z.number().positive().lt(50)
});

type Dog = z.infer<typeof Dog>;


function testZod() {

    const hello1 = Dog.parse({
        name: "asdfw",
        age: 23
    });
    console.log(hello1);

    const hello2 = Dog.parse(JSON.parse("{\"nam\": \"234\",\"age\":\"hi\"}"));
    console.log(hello2);
}




</script>


<template>
    <main>
        <h1>Home View</h1>
        <div class="part">
            <h2>Counter with external Store</h2>
            <h3>{{ counter.count }}</h3>
            <Button size="small" @click="counter.count++">++</button>
            <Button size="small" @click="counter.count--">--</Button>
            <Button size="small" @click="setCounterLow">Set Low</Button>
        </div>
        <div class="part">
            <h2>Stuff with ref and objects</h2>
            <table>
                <tr v-for="(obj, index) in dstruct.mydata" :class="{ active: index === counter.count }">
                    <th>{{ index }}:</th>
                    <td>a: {{ obj.a }}</td>
                    <td>b: {{ obj.b }}</td>
                    <td>b: {{ obj.c }}</td>
                </tr>
            </table>
            <Button size="small" @click="appendObject">Add Row</button>
            <Button size="small" @click="modifyTarget">Modify Target Row</button>
            <Button size="small" @click="replaceList">Replace List</button>
        </div>
        <div class="part">
            <Button size="small" @click="testZod">Test Zod</Button>
        </div>
    </main>
</template>


<style scoped>
main {
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    gap: 10px;

}

.part {
    border-radius: 10px;
    border: 2px solid gray;
    padding: 10px;
}

.part h2 {
    padding-bottom: 10px;
}

.part button {
    margin-right: 10px;
}

.part table,
td {
    border: 1px solid gray;
}

.part table tr th {
    padding-right: 10px;
    padding-left: 5px;
}

.part td {
    font-size: large;
    padding-left: 5px;
    padding-right: 5px;
}

.active {
    color: red;
    border-color: red;
}
</style>