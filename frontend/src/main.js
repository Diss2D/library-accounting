import { createApp } from "vue";
import { createPinia } from "pinia";

import "bootstrap/dist/css/bootstrap.min.css";

import App from "./App.vue";
import router from "./router";
import { setUnauthorizedHandler } from "./api/index.js";
import { useAuthStore } from "./stores/auth.js";

const app = createApp(App);

app.use(createPinia());
setUnauthorizedHandler(() => {
    useAuthStore().logout();
    router.replace({ name: "login", query: { redirect: router.currentRoute.value.fullPath } });
});

useAuthStore().restoreSession();

app.use(router);

app.mount("#app");
