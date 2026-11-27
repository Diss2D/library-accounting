import { createRouter, createWebHistory } from "vue-router";

import CatalogView from "../views/CatalogView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import NotFoundView from "../views/NotFoundView.vue";

import { useAuthStore } from "../stores/auth.js";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/",
            redirect: "/publications",
        },
        {
            path: "/login",
            name: "login",
            component: LoginView,
            meta: { guestOnly: true },
        },
        {
            path: "/register",
            name: "register",
            component: RegisterView,
            meta: { guestOnly: true },
        },
        {
            path: "/publications",
            name: "catalog",
            component: CatalogView,
            meta: { requiresAuth: true },
        },
        {
            path: "/:pathMatch(.*)*",
            name: "not-found",
            component: NotFoundView,
        },
    ],
});

router.beforeEach((to) => {
    const auth = useAuthStore();

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return {
            name: "login",
            query: { redirect: to.fullPath },
        };
    }

    if (to.meta.guestOnly && auth.isAuthenticated) {
        return { name: "catalog" };
    }
});

export default router;
