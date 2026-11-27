<script setup>
    import AppHeader from "./components/AppHeader.vue";
    import AppSidebar from "./components/AppSidebar.vue";
    import AppFooter from "./components/AppFooter.vue";

    import { useAuthStore } from "./stores/auth.js";

    const auth = useAuthStore();
</script>

<template>
    <div class="min-vh-100 d-flex flex-column bg-body-tertiary">
        <AppHeader />

        <div v-if="auth.isAuthenticated" class="container-fluid flex-grow-1 d-flex flex-column">
            <div class="row flex-grow-1">
                <aside class="col-md-3 col-lg-2 bg-white border-end p-3">
                    <AppSidebar />
                </aside>

                <main class="col-md-9 col-lg-10 p-3 p-lg-4">
                    <RouterView />
                </main>
            </div>
        </div>

        <main v-else class="flex-grow-1 d-flex align-items-center justify-content-center p-3">
            <div class="w-100" style="max-width: 420px">
                <RouterView />
            </div>
        </main>

        <AppFooter />
    </div>
</template>
