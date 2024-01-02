<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:52

Main UI entry component
-->

<script setup lang="ts">

import { RouterLink, RouterView } from 'vue-router'
import { ref } from 'vue';
import type { MenuItem } from 'primevue/menuitem';

const menuitems = ref<MenuItem[]>([
    {
        label: 'Home',
        icon: 'pi pi-home', 
        url: '/'
    },
    {
        label: 'About',
        icon: 'pi pi-info-circle', 
        url: '/about'
    },
    {
        label: 'WS Test',
        icon: 'pi pi-sort-alt', 
        url: '/wstest'
    }
])

</script>


<template>
    <div class="main-layout">
        <div class="logo-wrapper">
            <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />
        </div>

        <div class="menu-wrapper">
            <Menu :model="menuitems">
                <template #item="{ item, props }">
                    <RouterLink v-if="item.url" v-slot="{ href, navigate }" :to="item.url" custom>
                        <a v-ripple :href="href" v-bind="props.action" @click="navigate">
                            <span :class="item.icon + ' p-menuitem-icon'" />
                            <span class="ml-2">{{ item.label }}</span>
                        </a>
                    </RouterLink>
                    <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
                        <span>(ERROR)</span>
                        <span :class="item.icon + ' p-menuitem-icon'" />
                        <span class="ml-2">{{ item.label }}</span>
                    </a>
                </template>
            </Menu>
        </div>

        <div class="main-wrapper">

            <RouterView />

        </div>
    </div>
</template>


<style scoped>
.main-layout {
    display: grid;
    grid-template-areas:
        "logo main"
        "menu main";
    grid-template-rows: auto minmax(0, 1fr);
    grid-template-columns: auto 1fr;
    gap: 20px;
    padding: 20px;
    height: 100vh;
    max-height: 100vh;
    width: 100vw;
    max-width: 100vw;
}

.logo-wrapper {
    grid-area: logo;
}

.main-layout>.menu-wrapper {
    grid-area: menu;
}

.main-layout>.main-wrapper {
    height: minmax(0, auto);
    grid-area: main;
    overflow: none;
}


.logo {
    display: block;
    margin: 0 auto 2rem;
}
</style>
