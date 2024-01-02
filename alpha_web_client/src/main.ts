/*
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:52

Main application entry point
*/

import './assets/main.css';
import 'primevue/resources/themes/lara-dark-cyan/theme.css'

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';

import PrimeVue from 'primevue/config';
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import Terminal from 'primevue/terminal';
import Panel from 'primevue/panel';
import ScrollPanel from 'primevue/scrollpanel';
import Fieldset from 'primevue/fieldset';
import Textarea from 'primevue/textarea';
import Card from 'primevue/card';
import Toolbar from 'primevue/toolbar';
import InputSwitch from 'primevue/inputswitch';

const app = createApp(App);

app.use(createPinia());
app.use(PrimeVue);
app.use(router);

app.component('Button', Button);
app.component('Menu', Menu)
app.component('Terminal', Terminal);
app.component('Panel', Panel);
app.component('ScrollPanel', ScrollPanel);
app.component('Fieldset', Fieldset);
app.component('Textarea', Textarea);
app.component('Card', Card);
app.component('Toolbar', Toolbar);
app.component('InputSwitch', InputSwitch);


app.mount('#app');
