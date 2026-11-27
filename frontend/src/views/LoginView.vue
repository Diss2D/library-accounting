<script setup>
    import { reactive } from "vue";
    import { useRoute, useRouter } from "vue-router";

    import FormField from "../components/FormField.vue";
    import { useAuthStore } from "../stores/auth.js";

    const auth = useAuthStore();
    const router = useRouter();
    const route = useRoute();

    const form = reactive({
        email: "",
        password: "",
    });

    const errors = reactive({
        email: "",
        password: "",
    });

    async function submit() {
        errors.email = "";
        errors.password = "";

        if (!form.email.trim()) {
            errors.email = "Введите электронную почту";
        } else if (
            !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()) ||
            form.email.trim().length > 254
        ) {
            errors.email = "Введите корректную электронную почту";
        }

        if (!form.password) {
            errors.password = "Введите пароль";
        }

        if (errors.email || errors.password) {
            return;
        }

        try {
            await auth.login(form.email, form.password);
        } catch (error) {
            errors.password = error.message;
            return;
        }

        const redirect = route.query.redirect;

        if (
            typeof redirect === "string" &&
            redirect.startsWith("/") &&
            !redirect.startsWith("//")
        ) {
            await router.replace(redirect);
        } else {
            await router.replace("/publications");
        }
    }
</script>

<template>
    <div class="card p-4">
        <h1 class="h4 mb-4">Вход в систему</h1>

        <form novalidate @submit.prevent="submit">
            <FormField
                id="email"
                v-model="form.email"
                label="Электронная почта"
                type="email"
                placeholder="name@example.test"
                autocomplete="email"
                :error="errors.email"
            />

            <FormField
                id="password"
                v-model="form.password"
                label="Пароль"
                type="password"
                placeholder="Введите пароль"
                autocomplete="current-password"
                :error="errors.password"
            />

            <button type="submit" class="btn btn-primary w-100">Войти</button>
        </form>

        <div class="text-center small mt-3">
            Нет учетной записи?
            <RouterLink to="/register"> Зарегистрироваться </RouterLink>
        </div>
    </div>
</template>
