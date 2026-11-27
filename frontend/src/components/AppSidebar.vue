<script setup>
    import { useAuthStore } from "../stores/auth.js";

    const auth = useAuthStore();
</script>

<template>
    <nav class="nav nav-pills flex-column">
        <RouterLink to="/publications" class="nav-link" active-class="active"> Каталог </RouterLink>

        <RouterLink v-if="auth.isLibrarian" to="/readers" class="nav-link" active-class="active">
            Читатели
        </RouterLink>

        <RouterLink v-if="auth.isLibrarian" to="/loans" class="nav-link" active-class="active">
            Выдачи
        </RouterLink>

        <RouterLink
            v-if="auth.user?.role === 'reader'"
            to="/my-loans"
            class="nav-link"
            active-class="active"
        >
            Мои выдачи
        </RouterLink>
    </nav>
</template>
