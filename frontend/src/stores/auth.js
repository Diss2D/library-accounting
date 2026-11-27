import { defineStore } from "pinia";
import { login as loginUser } from "../api/index.js";

export const useAuthStore = defineStore("auth", {
    state: () => ({
        user: null,
    }),

    getters: {
        isAuthenticated: (state) => state.user !== null,
        isLibrarian: (state) => state.user?.role === "librarian",
    },

    actions: {
        async login(email, password) {
            this.user = await loginUser({ email, password });
        },

        logout() {
            this.user = null;
        },
    },
});
