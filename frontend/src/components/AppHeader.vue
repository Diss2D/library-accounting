<script setup>
    import { useRouter } from "vue-router";
    import { useAuthStore } from "../stores/auth.js";

    const auth = useAuthStore();
    const router = useRouter();

    function logout() {
        auth.logout();
        router.push("/login");
    }
</script>

<template>
    <header class="navbar bg-white border-bottom px-3 gap-2">
        <RouterLink to="/" class="navbar-brand fw-semibold mb-0"> Библиотечный учет </RouterLink>

        <div v-if="auth.isAuthenticated" class="d-flex align-items-center gap-3">
            <span class="text-secondary small">
                {{ auth.isLibrarian ? "Библиотекарь" : "Читатель" }}
            </span>

            <button type="button" class="btn btn-link btn-sm p-0" @click="logout">Выйти</button>
        </div>
    </header>
</template>
