<script setup>
    import { ref, reactive, onMounted } from "vue";

    import FormField from "../components/FormField.vue";
    import { getReaders, updateReader } from "../api/index.js";

    const readers = ref([]);
    const editingReader = ref(null);

    const errorMessage = ref("");
    const successMessage = ref("");

    const form = reactive({
        full_name: "",
        card_number: "",
    });

    const errors = reactive({
        full_name: "",
        card_number: "",
    });

    async function loadReaders() {
        errorMessage.value = "";

        try {
            readers.value = await getReaders();
        } catch (error) {
            errorMessage.value = error.message;
        }
    }

    function openForm(reader) {
        editingReader.value = reader;

        form.full_name = reader.full_name;
        form.card_number = reader.card_number;

        errors.full_name = "";
        errors.card_number = "";
        successMessage.value = "";
        errorMessage.value = "";
    }

    function closeForm() {
        editingReader.value = null;
    }

    async function saveReader() {
        errors.full_name = "";
        errors.card_number = "";
        errorMessage.value = "";

        const fullName = form.full_name.trim();
        const cardNumber = form.card_number.trim();

        if (!fullName) {
            errors.full_name = "Введите ФИО";
        } else if (fullName.length > 150) {
            errors.full_name = "Не более 150 символов";
        }

        if (!cardNumber) {
            errors.card_number = "Введите номер читательского билета";
        } else if (cardNumber.length > 50) {
            errors.card_number = "Не более 50 символов";
        }

        if (errors.full_name || errors.card_number) {
            return;
        }

        try {
            await updateReader(editingReader.value.id, {
                full_name: fullName,
                card_number: cardNumber,
            });
        } catch (error) {
            if (error.field === "card_number") {
                errors.card_number = error.message;
            } else {
                errorMessage.value = error.message;
            }

            return;
        }

        closeForm();
        successMessage.value = "Сведения о читателе сохранены";

        await loadReaders();
    }

    onMounted(loadReaders);
</script>

<template>
    <h1 class="h3 mb-3">Читатели</h1>

    <div v-if="errorMessage" class="alert alert-danger">
        {{ errorMessage }}
    </div>

    <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
    </div>

    <div class="table-responsive">
        <table class="table table-bordered table-hover align-middle">
            <thead class="table-light">
                <tr>
                    <th>ФИО</th>
                    <th>Номер читательского билета</th>
                    <th>Действия</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="reader in readers" :key="reader.id">
                    <td>{{ reader.full_name }}</td>
                    <td class="text-nowrap">{{ reader.card_number }}</td>

                    <td>
                        <button
                            type="button"
                            class="btn btn-link btn-sm p-0"
                            @click="openForm(reader)"
                        >
                            Изменить
                        </button>
                    </td>
                </tr>

                <tr v-if="readers.length === 0">
                    <td colspan="3" class="text-center text-secondary py-3">
                        Читатели отсутствуют
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="editingReader" class="card p-3 mt-4">
        <h2 class="h5 mb-3">Редактирование читателя</h2>

        <form novalidate @submit.prevent="saveReader">
            <div class="row">
                <div class="col-md-6">
                    <FormField
                        id="reader-name"
                        v-model="form.full_name"
                        label="ФИО"
                        :error="errors.full_name"
                    />
                </div>

                <div class="col-md-6">
                    <FormField
                        id="reader-card"
                        v-model="form.card_number"
                        label="Номер читательского билета"
                        :error="errors.card_number"
                    />
                </div>
            </div>

            <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-outline-secondary" @click="closeForm">
                    Отмена
                </button>

                <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
        </form>
    </div>
</template>
