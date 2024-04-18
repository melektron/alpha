<!--
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:52

Main UI entry component
-->

<script setup lang="ts">

import { RouterLink, RouterView, onBeforeRouteUpdate, useRoute } from 'vue-router'
import { computed, effect, ref } from 'vue';
import type { MenuItem } from 'primevue/menuitem';

const menuitems = ref<MenuItem[]>([
    {
        label: 'Home',
        icon: 'pi pi-home', 
        url: '/home'
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
    },
    {
        label: 'KaYeet?!',
        icon: 'pi pi-sort-alt', 
        url: '/kayeet'
    }
])

// to check whether we are on kayeet, as that shouldn't show the sidebar there
const route = useRoute();
const shouldShowSidebar = computed(() => !(route.path.startsWith("/kayeet") || route.path === "/"));    // bit hacky but works
effect(() => {
    console.log(`shouldntshowsidebar: ${route.path}`)
})

</script>


<template>

    <!-- Change layout to hide or show sidebar -->
    <div :class="{
        'main-layout': true,
        'ml-sidebar': shouldShowSidebar,
        'ml-fullscreen': !shouldShowSidebar
    }">

        <!-- Sidebar (logo + menu)-->
        <div v-if="shouldShowSidebar" class="logo-wrapper">
            <img alt="Vue logo" class="logo" src="@/assets/kayeet_logo.png" width="125" height="125" />
        </div>
        <div v-if="shouldShowSidebar" class="menu-wrapper">
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
        
        <!-- Main content -->
        <div class="main-wrapper">
            <RouterView />
        </div>

    </div>
</template>


<style scoped>
.main-layout {
    display: grid;
    gap: 20px;
    height: 100vh;
    max-height: 100vh;
    width: 100vw;
    max-width: 100vw;
}
.ml-sidebar {
    grid-template-areas:
        "logo main"
        "menu main";
    grid-template-rows: auto minmax(0, 1fr);
    grid-template-columns: auto 1fr;
    padding: 20px;
}
.ml-fullscreen {
    grid-template-areas:
        "main";
    grid-template-rows: 1fr;
    grid-template-columns: 1fr;
    padding: 0px;
}

.main-layout>.logo-wrapper {
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

@media screen and (max-width: 1000px) {
    
    .main-layout {
        display: grid;
        grid-template-areas:
            "main"
            "main";
        grid-template-columns: 1fr;
    }
    
    .main-layout>.logo-wrapper {
        display: none;
    }

    .main-layout>.menu-wrapper {
        display: none;
    }
}
</style>
