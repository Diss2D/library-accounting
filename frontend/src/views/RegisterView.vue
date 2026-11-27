<script setup>
    import { reactive } from "vue";
    import { useRouter } from "vue-router";

    import FormField from "../components/FormField.vue";
    import { register } from "../api/index.js";

    const router = useRouter();

    const form = reactive({
        full_name: "",
        email: "",
        password: "",
    });

    const errors = reactive({
        full_name: "",
        email: "",
        password: "",
    });

    async function submit() {
        errors.full_name = "";
        errors.email = "";
        errors.password = "";

        if (!form.full_name.trim()) {
            errors.full_name = "Введите ФИО";
        } else if (form.full_name.trim().length > 150) {
            errors.full_name = "ФИО должно содержать не более 150 символов";
        }

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

        if (errors.full_name || errors.email || errors.password) {
            return;
        }

        try {
            await register(form);
        } catch (error) {
            errors.email = error.message;
            return;
        }

        await router.push("/login");
    }
</script>

<template>
    <div class="card p-4">
        <h1 class="h4 mb-4">Регистрация</h1>

        <form novalidate @submit.prevent="submit">
            <FormField
                id="full_name"
                v-model="form.full_name"
                label="Фамилия, имя, отчество"
                placeholder="Введите ФИО"
                autocomplete="name"
                :error="errors.full_name"
            />

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
                autocomplete="new-password"
                :error="errors.password"
            />

            <button type="submit" class="btn btn-primary w-100">Зарегистрироваться</button>
        </form>

        <div class="text-center small mt-3">
            Уже есть учетная запись?
            <RouterLink to="/login">Войти</RouterLink>
        </div>
    </div>
</template>
