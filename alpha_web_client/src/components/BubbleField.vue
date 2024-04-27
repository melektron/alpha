<!--
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
27.04.24, 23:25

Block element that randomly shows twinkling/sparkling/bubbling questionmarks and exclamation marks.
-->

<script setup lang="ts">
import { ref } from "vue";
import CharacterBubble from "./CharacterBubble.vue";

const props = defineProps<{
    enabled: boolean
}>();

</script>


<template>
    <!-- 
        Outer div is the "public" div. This is so that one can modify 
        it's properties (especially positioning) without worrying about implications.
    -->
    <div>
        <div class="relative w-full h-full overflow-hidden">
            <CharacterBubble :enabled="props.enabled">?</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">?</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">?</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">?</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">?</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">?</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">!</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">!</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">!</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">!</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">!</CharacterBubble>
            <CharacterBubble :enabled="props.enabled">!</CharacterBubble>
        </div>
    </div>
</template>

<style scoped>

</style>