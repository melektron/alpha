/*
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:52

Main application entry point
*/

import './assets/main.css';

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import PrimeVue from 'primevue/config';

import App from './App.vue';
import router from './router';


const app = createApp(App);

app.use(createPinia());
app.use(PrimeVue);
app.use(router);

app.mount('#app');
