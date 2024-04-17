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
            name: 'index',
            path: '/',
            redirect: { name: 'home' }
        },
        {
            name: 'home',
            path: '/home',
            component: () => import('../views/HomeView.vue')
        },
        {
            name: 'about',
            path: '/about',
            component: () => import('../views/AboutView.vue'),
        },
        {
            name: "wstest",
            path: "/wstest",
            component: () => import("../views/WSTestView.vue")
        },
        {
            name: "kayeet",
            path: "/kayeet",
            component: () => import("../views/KaYeetView.vue"),
        }
    ]
})

export default router
