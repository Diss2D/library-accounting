import { createRouter, createWebHistory } from "vue-router";

import CatalogView from "../views/CatalogView.vue";
import PublicationView from "../views/PublicationView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import NotFoundView from "../views/NotFoundView.vue";
import ReadersView from "../views/ReadersView.vue";
import { useAuthStore } from "../stores/auth.js";
import LoansView from "../views/LoansView.vue";
import MyLoansView from "../views/MyLoansView.vue";

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
            path: "/publications/:id",
            name: "publication",
            component: PublicationView,
            meta: { requiresAuth: true },
        },
        {
            path: "/readers",
            name: "readers",
            component: ReadersView,
            meta: {
                requiresAuth: true,
                librarianOnly: true,
            },
        },
        {
            path: "/loans",
            name: "loans",
            component: LoansView,
            meta: {
                requiresAuth: true,
                librarianOnly: true,
            },
        },
        {
            path: "/my-loans",
            name: "my-loans",
            component: MyLoansView,
            meta: {
                requiresAuth: true,
                readerOnly: true,
            },
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

    if (to.meta.librarianOnly && !auth.isLibrarian) {
        return { name: "catalog" };
    }

    if (to.meta.readerOnly && auth.user?.role !== "reader") {
        return { name: "catalog" };
    }

    if (to.meta.guestOnly && auth.isAuthenticated) {
        return { name: "catalog" };
    }
});

export default router;
