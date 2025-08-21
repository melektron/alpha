/*
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:52

Main application entry point
*/

import './assets/main.css';
//import 'primevue/resources/themes/lara-dark-cyan/theme.css'
//import 'primevue/resources/themes/aura-light-lime/theme.css'
import 'primevue/resources/themes/aura-dark-purple/theme.css'
import 'primeflex/primeflex.css'

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
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import InputText from 'primevue/inputtext';
import InputGroup from 'primevue/inputgroup';
import ConfirmDialog from 'primevue/confirmdialog';
import ConfirmationService from 'primevue/confirmationservice';
import FloatLabel from 'primevue/floatlabel';
import Message from 'primevue/message';
import Dialog from 'primevue/dialog';
import Image from 'primevue/image';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const app = createApp(App);

app.use(createPinia());
app.use(PrimeVue);
app.use(router);
app.use(ConfirmationService);

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
app.component('InputText', InputText);
app.component('InputGroup', InputGroup);
app.component('Splitter', Splitter);
app.component('SplitterPanel', SplitterPanel);
app.component('ConfirmDialog', ConfirmDialog);
app.component('FloatLabel', FloatLabel);
app.component('Message', Message);
app.component('Dialog', Dialog);
app.component('Image', Image);
app.component('DataTable', DataTable);
app.component('Column', Column);


app.mount('#app');
