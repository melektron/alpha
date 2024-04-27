<!--
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
27.04.24, 23:25

A single question mark that bubbles/twinkles at random positions with random properties
-->

<script setup lang="ts">
import { useElementSize, useParentElement } from '@vueuse/core';
import { onMounted } from 'vue';
import { watchEffect } from 'vue';
import { watch } from 'vue';
import { nextTick } from 'vue';
import { computed } from 'vue';
import { ref } from 'vue';

const props = defineProps<{
    enabled: boolean
}>();

let watch_for_enabling = false;

const parent = useParentElement();
const canvas = useElementSize(parent);

const show = ref<boolean>(false);

const top = ref<number>(0);
const left = ref<number>(0);
const start_angle = ref<number>(0);
const stop_angle = ref<number>(0);
const time = ref<number>(0);
const size = ref<number>(0);

const top_pixels = computed(() => (top.value + "px"));
const left_pixels = computed(() => (left.value + "px"));
const start_angle_deg = computed(() => (start_angle.value + "deg"));
const stop_angle_deg = computed(() => (stop_angle.value + "deg"));
const time_sec = computed(() => (time.value + "s"));

// activate initially after random delay
onMounted(() => {
    setTimeout(playAnimation, Math.random() * 2);
});

// potentially reactivate after enabled
watchEffect(() => {
    if (props.enabled && watch_for_enabling) {
        watch_for_enabling = false; 
        setTimeout(playAnimation, Math.random() * 8);
    }
})

async function playAnimation(e: Event) {
    show.value = false;
    await nextTick();
    
    if (!props.enabled) {
        watch_for_enabling = true;
    }

    top.value = Math.random() * canvas.height.value;
    left.value = Math.random() * canvas.width.value;
    start_angle.value = Math.random() * 90 - 45;
    stop_angle.value = Math.random() * 90 - 45;
    time.value = Math.random() * 5 + 10;
    size.value = Math.random() * 20 + 10;

    await nextTick();
    show.value = true;
}

</script>


<template>
    <div v-if="show" ref="mark" class="mark" @animationend="playAnimation">
        <slot></slot>
    </div>
</template>

<style scoped>
.mark {
    position: absolute;
    top: v-bind(top_pixels);
    left: v-bind(left_pixels);

    color: var(--primary-200);

    transform-origin: top left;
    transform: scale(0) rotate(0deg) translate(-50%, -50%);
    animation: encroach v-bind(time_sec) linear forwards;
}

/* inspiration: https://codepen.io/BjornRombaut/pen/mOLGgX */
@keyframes encroach {
    from {
        transform: scale(0) rotate(v-bind(start_angle_deg)) translate(-50%, -50%);
        opacity: 0.5;
    }

    to {
        transform: scale(v-bind(size)) rotate(v-bind(stop_angle_deg)) translate(-50%, -50%);
        opacity: 0;
    }
}
</style>