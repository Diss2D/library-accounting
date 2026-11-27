<script setup>
    import { ref, watch } from "vue";
    import { useRoute } from "vue-router";

    import FormField from "../components/FormField.vue";

    import { getPublication, getCopies, createCopy, updateCopy } from "../api/index.js";
    import { useAuthStore } from "../stores/auth.js";

    const route = useRoute();
    const auth = useAuthStore();

    const publication = ref(null);
    const copies = ref([]);
    const errorMessage = ref("");
    const loading = ref(false);
    const showForm = ref(false);
    const editingCopy = ref(null);
    const inventoryNumber = ref("");
    const inventoryError = ref("");
    const successMessage = ref("");

    async function loadPublication() {
        loading.value = true;
        errorMessage.value = "";
        publication.value = null;
        copies.value = [];

        try {
            const id = Number(route.params.id);

            publication.value = await getPublication(id);

            if (auth.isLibrarian) {
                copies.value = await getCopies(id);
            }
        } catch (error) {
            errorMessage.value = error.message;
        } finally {
            loading.value = false;
        }
    }
    function openCopyForm(copy = null) {
        editingCopy.value = copy;
        inventoryNumber.value = copy?.inventory_number ?? "";
        inventoryError.value = "";
        successMessage.value = "";
        showForm.value = true;
    }
    function closeCopyForm() {
        showForm.value = false;
        editingCopy.value = null;
        inventoryNumber.value = "";
        inventoryError.value = "";
    }

    async function saveCopy() {
        inventoryError.value = "";

        const number = inventoryNumber.value.trim();

        if (!number) {
            inventoryError.value = "Введите инвентарный номер";
            return;
        }
        if (number.length > 50) {
            inventoryError.value = "Не более 50 символов";
            return;
        }
        try {
            if (editingCopy.value) {
                await updateCopy(editingCopy.value.id, number);
            } else {
                await createCopy(publication.value.id, number);
            }
        } catch (error) {
            inventoryError.value = error.message;
            return;
        }

        closeCopyForm();
        successMessage.value = "Экземпляр сохранен";

        await loadPublication();
    }

    watch(
        () => route.params.id,
        () => {
            closeCopyForm();
            successMessage.value = "";
            loadPublication();
        },
        { immediate: true },
    );
</script>

<template>
    <h1 class="h3">Карточка издания</h1>

    <RouterLink to="/publications" class="d-inline-block mb-3"> Назад к каталогу </RouterLink>
    <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
    </div>
    <div v-if="errorMessage" class="alert alert-danger">
        {{ errorMessage }}
    </div>

    <p v-else-if="loading" class="text-secondary">Загрузка...</p>

    <template v-else-if="publication">
        <div class="card p-3 mb-4">
            <h2 class="h4">{{ publication.title }}</h2>

            <p class="mb-1">{{ publication.author }}, {{ publication.publication_year }}</p>

            <p class="mb-1">Жанр: {{ publication.genre }}</p>
            <p class="mb-3">ISBN: {{ publication.isbn || "—" }}</p>

            <div class="d-flex flex-wrap gap-3">
                <span>
                    Всего экземпляров:
                    <strong>{{ publication.total_copies }}</strong>
                </span>

                <span>
                    Доступно:
                    <strong>{{ publication.available_copies }}</strong>
                </span>
            </div>
        </div>

        <section v-if="auth.isLibrarian">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
                <h2 class="h5 mb-0">Экземпляры</h2>

                <button type="button" class="btn btn-primary" @click="openCopyForm()">
                    Добавить экземпляр
                </button>
            </div>

            <div class="table-responsive">
                <table class="table table-bordered table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Инвентарный номер</th>
                            <th>Доступность</th>
                            <th>Действия</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="copy in copies" :key="copy.id">
                            <td>{{ copy.inventory_number }}</td>

                            <td :class="copy.available ? 'text-success' : 'text-secondary'">
                                {{ copy.available ? "Доступен" : "Выдан" }}
                            </td>
                            <td>
                                <button
                                    type="button"
                                    class="btn btn-link btn-sm p-0"
                                    @click="openCopyForm(copy)"
                                >
                                    Изменить
                                </button>
                            </td>
                        </tr>

                        <tr v-if="copies.length === 0">
                            <td colspan="3" class="text-center text-secondary py-3">
                                Экземпляры отсутствуют
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-if="showForm" class="card p-3 mt-3">
                <h2 class="h5 mb-3">
                    {{ editingCopy ? "Редактирование экземпляра" : "Добавление экземпляра" }}
                </h2>

                <form novalidate @submit.prevent="saveCopy">
                    <div class="row">
                        <div class="col-md-6">
                            <FormField
                                id="inventory-number"
                                v-model="inventoryNumber"
                                label="Инвентарный номер"
                                :error="inventoryError"
                            />
                        </div>
                    </div>

                    <div class="d-flex justify-content-end gap-2">
                        <button
                            type="button"
                            class="btn btn-outline-secondary"
                            @click="closeCopyForm"
                        >
                            Отмена
                        </button>

                        <button type="submit" class="btn btn-primary">Сохранить</button>
                    </div>
                </form>
            </div>
        </section>
    </template>
</template>
