<script setup>
    import { reactive, ref } from "vue";

    import FormField from "./FormField.vue";
    import { createPublication, updatePublication } from "../api/index.js";

    const props = defineProps({
        publication: {
            type: Object,
            default: null,
        },
    });

    const emit = defineEmits(["saved", "cancel"]);

    const form = reactive({
        title: props.publication?.title ?? "",
        author: props.publication?.author ?? "",
        publication_year: props.publication?.publication_year ?? "",
        genre: props.publication?.genre ?? "",
        isbn: props.publication?.isbn ?? "",
    });

    const errors = reactive({
        title: "",
        author: "",
        publication_year: "",
        genre: "",
        isbn: "",
    });

    const errorMessage = ref("");

    async function submit() {
        for (const field in errors) {
            errors[field] = "";
        }

        errorMessage.value = "";

        if (!form.title.trim()) {
            errors.title = "Введите название";
        } else if (form.title.trim().length > 255) {
            errors.title = "Не более 255 символов";
        }

        if (!form.author.trim()) {
            errors.author = "Введите автора";
        } else if (form.author.trim().length > 255) {
            errors.author = "Не более 255 символов";
        }

        const year = Number(form.publication_year);

        if (!Number.isInteger(year) || year <= 0) {
            errors.publication_year = "Введите положительное целое число";
        }

        if (!form.genre.trim()) {
            errors.genre = "Введите жанр";
        } else if (form.genre.trim().length > 100) {
            errors.genre = "Не более 100 символов";
        }

        if (form.isbn.trim().length > 17) {
            errors.isbn = "Не более 17 символов";
        }

        if (Object.values(errors).some(Boolean)) {
            return;
        }

        const data = {
            title: form.title.trim(),
            author: form.author.trim(),
            publication_year: year,
            genre: form.genre.trim(),
            isbn: form.isbn.trim() || null,
        };

        try {
            if (props.publication) {
                await updatePublication(props.publication.id, data);
            } else {
                await createPublication(data);
            }

            emit("saved");
        } catch (error) {
            if (error.field === "isbn") {
                errors.isbn = error.message;
            } else {
                errorMessage.value = error.message;
            }
        }
    }
</script>

<template>
    <div class="card p-3 mt-4">
        <h2 class="h5 mb-3">
            {{ publication ? "Редактирование издания" : "Добавление издания" }}
        </h2>

        <div v-if="errorMessage" class="alert alert-danger">
            {{ errorMessage }}
        </div>

        <form novalidate @submit.prevent="submit">
            <div class="row">
                <div class="col-md-6">
                    <FormField
                        id="publication-title"
                        v-model="form.title"
                        label="Название"
                        :error="errors.title"
                    />
                </div>

                <div class="col-md-6">
                    <FormField
                        id="publication-author"
                        v-model="form.author"
                        label="Автор"
                        :error="errors.author"
                    />
                </div>

                <div class="col-md-6">
                    <FormField
                        id="publication-year"
                        v-model="form.publication_year"
                        label="Год издания"
                        type="number"
                        :error="errors.publication_year"
                    />
                </div>

                <div class="col-md-6">
                    <FormField
                        id="publication-genre"
                        v-model="form.genre"
                        label="Жанр"
                        :error="errors.genre"
                    />
                </div>

                <div class="col-md-6">
                    <FormField
                        id="publication-isbn"
                        v-model="form.isbn"
                        label="ISBN (необязательно)"
                        :error="errors.isbn"
                    />
                </div>
            </div>

            <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-outline-secondary" @click="emit('cancel')">
                    Отмена
                </button>

                <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
        </form>
    </div>
</template>
