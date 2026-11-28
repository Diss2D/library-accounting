import { defineStore } from "pinia";
import { login as loginUser, setAccessToken } from "../api/index.js";

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
            const session = await loginUser({ email, password });
            setAccessToken(session.access_token);
            this.user = session.user;
            sessionStorage.setItem("library-session", JSON.stringify(session));
        },

        restoreSession() {
            try {
                const session = JSON.parse(sessionStorage.getItem("library-session"));
                if (session?.access_token && session.user) {
                    setAccessToken(session.access_token);
                    this.user = session.user;
                }
            } catch {
                this.logout();
            }
        },

        logout() {
            setAccessToken(null);
            this.user = null;
            sessionStorage.removeItem("library-session");
        },
    },
});
