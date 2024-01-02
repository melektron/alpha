/*
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
15.12.23, 09:43

Router configuration
*/

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('../views/HomeView.vue')
        },
        {
            path: '/about',
            name: 'about',
            component: () => import('../views/AboutView.vue')
        },
        {
            path: "/wstest",
            name: "wstest",
            component: () => import("../views/WSTestView.vue")
        }
    ]
})

export default router
