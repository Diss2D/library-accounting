<script setup>
    import { ref, computed, watch, onMounted } from "vue";

    import AppPagination from "../components/AppPagination.vue";
    import PublicationForm from "../components/PublicationForm.vue";
    import { useAuthStore } from "../stores/auth.js";
    import { getPublications, getPublicationGenres, deletePublication } from "../api/index.js";

    const auth = useAuthStore();
    const showForm = ref(false);
    const editingPublication = ref(null);
    const successMessage = ref("");
    const deleteError = ref("");

    const publications = ref([]);
    const genres = ref([]);

    const search = ref("");
    const genre = ref("");
    const sort = ref("title:asc");

    const page = ref(1);
    const total = ref(0);
    const pageSize = 5;

    const errorMessage = ref("");
    const loading = ref(false);

    const totalPages = computed(() => Math.ceil(total.value / pageSize));

    let requestId = 0;

    async function loadPublications(number = 1) {
        const currentRequest = ++requestId;
        const [field, direction] = sort.value.split(":");

        loading.value = true;
        errorMessage.value = "";

        try {
            const result = await getPublications({
                search: search.value,
                genre: genre.value,
                sort: field,
                direction,
                page: number,
                pageSize,
            });

            if (currentRequest === requestId) {
                publications.value = result.items;
                total.value = result.total;
                page.value = number;
            }
        } catch (error) {
            if (currentRequest === requestId) {
                errorMessage.value = error.message;
            }
        } finally {
            if (currentRequest === requestId) {
                loading.value = false;
            }
        }
    }

    function openForm(publication = null) {
        editingPublication.value = publication;
        successMessage.value = "";
        deleteError.value = "";
        showForm.value = true;
    }

    function closeForm() {
        showForm.value = false;
        editingPublication.value = null;
    }

    async function publicationSaved() {
        closeForm();

        successMessage.value = "Издание сохранено";

        try {
            genres.value = await getPublicationGenres();
            await loadPublications(1);
        } catch (error) {
            errorMessage.value = error.message;
        }
    }
    async function removePublication(publication) {
        successMessage.value = "";
        deleteError.value = "";

        if (!confirm(`Удалить издание «${publication.title}»?`)) {
            return;
        }

        try {
            await deletePublication(publication.id);

            if (editingPublication.value?.id === publication.id) {
                closeForm();
            }

            successMessage.value = "Издание удалено";

            genres.value = await getPublicationGenres();

            if (genre.value && !genres.value.includes(genre.value)) {
                genre.value = "";
            } else {
                await loadPublications(1);
            }
        } catch (error) {
            deleteError.value = error.message;
        }
    }

    watch([search, genre, sort], () => {
        loadPublications(1);
    });

    onMounted(async () => {
        try {
            genres.value = await getPublicationGenres();
            await loadPublications();
        } catch (error) {
            errorMessage.value = error.message;
        }
    });
</script>

<template>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
        <h1 class="h3 mb-0">Каталог изданий</h1>

        <button v-if="auth.isLibrarian" type="button" class="btn btn-primary" @click="openForm()">
            Добавить издание
        </button>
    </div>

    <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
    </div>
    <div v-if="deleteError" class="alert alert-danger">
        {{ deleteError }}
    </div>
    <div class="row g-3 mb-3">
        <div class="col-lg-6">
            <label for="search" class="form-label">Поиск</label>
            <input
                id="search"
                v-model="search"
                type="search"
                class="form-control"
                placeholder="По названию или автору"
            />
        </div>

        <div class="col-sm-6 col-lg-3">
            <label for="genre" class="form-label">Жанр</label>
            <select id="genre" v-model="genre" class="form-select">
                <option value="">Все жанры</option>
                <option v-for="item in genres" :key="item" :value="item">
                    {{ item }}
                </option>
            </select>
        </div>

        <div class="col-sm-6 col-lg-3">
            <label for="sort" class="form-label">Сортировка</label>
            <select id="sort" v-model="sort" class="form-select">
                <option value="title:asc">По названию (А–Я)</option>
                <option value="title:desc">По названию (Я–А)</option>
                <option value="author:asc">По автору (А–Я)</option>
                <option value="author:desc">По автору (Я–А)</option>
                <option value="publication_year:asc">По году издания (возрастание)</option>
                <option value="publication_year:desc">По году издания (убывание)</option>
            </select>
        </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">
        {{ errorMessage }}
    </div>

    <p v-else-if="loading" class="text-secondary">Загрузка...</p>

    <div v-else class="table-responsive">
        <table class="table table-hover table-bordered align-middle">
            <thead class="table-light">
                <tr>
                    <th>Название</th>
                    <th>Автор</th>
                    <th>Год</th>
                    <th>Жанр</th>
                    <th>Доступно</th>
                    <th>Действия</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="publication in publications" :key="publication.id">
                    <td>{{ publication.title }}</td>
                    <td>{{ publication.author }}</td>
                    <td>{{ publication.publication_year }}</td>
                    <td>{{ publication.genre }}</td>
                    <td class="text-nowrap">
                        {{ publication.available_copies }} из
                        {{ publication.total_copies }}
                    </td>
                    <td>
                        <div class="d-flex flex-wrap gap-2">
                            <RouterLink :to="`/publications/${publication.id}`" class="small">
                                Открыть
                            </RouterLink>

                            <template v-if="auth.isLibrarian">
                                <button
                                    type="button"
                                    class="btn btn-link btn-sm p-0"
                                    @click="openForm(publication)"
                                >
                                    Изменить
                                </button>

                                <button
                                    type="button"
                                    class="btn btn-link btn-sm text-danger p-0"
                                    @click="removePublication(publication)"
                                >
                                    Удалить
                                </button>
                            </template>
                        </div>
                    </td>
                </tr>

                <tr v-if="publications.length === 0">
                    <td colspan="6" class="text-center text-secondary py-4"></td>
                </tr>
            </tbody>
        </table>
    </div>

    <div
        v-if="!loading && !errorMessage"
        class="d-flex flex-wrap justify-content-between align-items-center gap-2"
    >
        <span class="text-secondary small"> Найдено изданий: {{ total }} </span>

        <AppPagination :page="page" :total-pages="totalPages" @change="loadPublications" />
    </div>
    <PublicationForm
        v-if="auth.isLibrarian && showForm"
        :key="editingPublication?.id ?? 'new'"
        :publication="editingPublication"
        @saved="publicationSaved"
        @cancel="closeForm"
    />
</template>
