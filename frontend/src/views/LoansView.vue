<script setup>
    import { ref, reactive, computed, watch, onMounted } from "vue";

    import FormField from "../components/FormField.vue";
    import SearchSelect from "../components/SearchSelect.vue";

    import {
        getLoans,
        getReaders,
        getAvailableCopies,
        createLoan,
        returnLoan,
        getTodayDate,
    } from "../api/index.js";

    const loans = ref([]);
    const errorMessage = ref("");
    const loading = ref(false);

    const readers = ref([]);
    const availableCopies = ref([]);

    const showForm = ref(false);
    const successMessage = ref("");
    const formError = ref("");
    const returningLoan = ref(null);
    const returnDate = ref("");
    const returnDateError = ref("");
    const returnError = ref("");

    const form = reactive({
        reader_id: "",
        publication_id: "",
        copy_id: "",
        loan_date: "",
        due_date: "",
    });

    const errors = reactive({
        reader_id: "",
        publication_id: "",
        copy_id: "",
        loan_date: "",
        due_date: "",
    });

    const readerOptions = computed(() =>
        readers.value.map((reader) => ({
            value: reader.id,
            label: `${reader.full_name} (${reader.card_number})`,
        })),
    );

    const publicationOptions = computed(() => {
        const items = new Map();

        for (const copy of availableCopies.value) {
            if (!items.has(copy.publication_id)) {
                items.set(copy.publication_id, {
                    value: copy.publication_id,
                    title: copy.publication_title,
                    author: copy.publication_author,
                    year: copy.publication_year,
                    count: 0,
                });
            }

            items.get(copy.publication_id).count++;
        }

        return [...items.values()].map((item) => ({
            value: item.value,
            label: `${item.title} — ${item.author}, ${item.year} (доступно: ${item.count})`,
        }));
    });

    const copyOptions = computed(() =>
        availableCopies.value
            .filter((copy) => copy.publication_id === form.publication_id)
            .map((copy) => ({
                value: copy.id,
                label: copy.inventory_number,
            })),
    );

    watch(
        () => form.publication_id,
        () => {
            form.copy_id = "";
            errors.copy_id = "";
        },
    );

    const statusLabels = {
        active: "Активная",
        overdue: "Просроченная",
        completed: "Завершенная",
    };

    const statusClasses = {
        active: "text-secondary",
        overdue: "text-danger",
        completed: "text-success",
    };

    function formatDate(date) {
        return date ? date.split("-").reverse().join(".") : "—";
    }

    async function loadLoans() {
        loading.value = true;
        errorMessage.value = "";

        try {
            loans.value = await getLoans();
        } catch (error) {
            errorMessage.value = error.message;
        } finally {
            loading.value = false;
        }
    }

    async function openLoanForm() {
        if (showForm.value) {
            return;
        }

        closeReturnForm();

        form.reader_id = "";
        form.publication_id = "";
        form.copy_id = "";
        form.loan_date = getTodayDate();
        form.due_date = "";

        for (const field in errors) {
            errors[field] = "";
        }

        successMessage.value = "";
        formError.value = "";

        readers.value = [];
        availableCopies.value = [];

        showForm.value = true;

        try {
            readers.value = await getReaders();
            availableCopies.value = await getAvailableCopies();
        } catch (error) {
            formError.value = error.message;
        }
    }

    function closeLoanForm() {
        showForm.value = false;
    }

    async function saveLoan() {
        for (const field in errors) {
            errors[field] = "";
        }

        formError.value = "";

        if (!form.reader_id) {
            errors.reader_id = "Выберите читателя";
        }

        if (!form.publication_id) {
            errors.publication_id = "Выберите издание";
        }

        if (!form.copy_id) {
            errors.copy_id = "Выберите экземпляр";
        }

        if (!form.loan_date) {
            errors.loan_date = "Укажите дату выдачи";
        }

        if (!form.due_date) {
            errors.due_date = "Укажите срок возврата";
        } else if (form.loan_date && form.due_date < form.loan_date) {
            errors.due_date = "Срок возврата не может быть раньше даты выдачи";
        }

        if (Object.values(errors).some(Boolean)) {
            return;
        }

        try {
            await createLoan({
                reader_id: form.reader_id,
                copy_id: form.copy_id,
                loan_date: form.loan_date,
                due_date: form.due_date,
            });
        } catch (error) {
            formError.value = error.message;
            return;
        }

        closeLoanForm();
        successMessage.value = "Выдача оформлена";

        await loadLoans();
    }
    function openReturnForm(loan) {
        closeLoanForm();

        returningLoan.value = loan;
        returnDate.value = getTodayDate();
        returnDateError.value = "";
        returnError.value = "";
        successMessage.value = "";
    }

    function closeReturnForm() {
        returningLoan.value = null;
    }

    async function saveReturn() {
        returnDateError.value = "";
        returnError.value = "";

        if (!returnDate.value) {
            returnDateError.value = "Укажите дату возврата";
            return;
        }

        if (returnDate.value < returningLoan.value.loan_date) {
            returnDateError.value = "Дата возврата не может быть раньше даты выдачи";
            return;
        }

        try {
            await returnLoan(returningLoan.value.id, returnDate.value);
        } catch (error) {
            returnError.value = error.message;
            return;
        }

        closeReturnForm();
        successMessage.value = "Возврат оформлен";

        await loadLoans();
    }
    onMounted(loadLoans);
</script>

<template>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
        <h1 class="h3 mb-0">Выдачи и возвраты</h1>

        <button type="button" class="btn btn-primary" @click="openLoanForm">Оформить выдачу</button>
    </div>

    <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="alert alert-danger">
        {{ errorMessage }}
    </div>

    <p v-else-if="loading" class="text-secondary">Загрузка...</p>

    <div v-else class="table-responsive">
        <table class="table table-bordered table-hover align-middle">
            <thead class="table-light">
                <tr>
                    <th>Читатель</th>
                    <th>Экземпляр</th>
                    <th>Дата выдачи</th>
                    <th>Срок возврата</th>
                    <th>Дата возврата</th>
                    <th>Состояние</th>
                    <th>Действия</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="loan in loans" :key="loan.id">
                    <td>{{ loan.reader_name }}</td>

                    <td>
                        <div>{{ loan.inventory_number }}</div>

                        <div class="small text-secondary">
                            {{ loan.publication_title }}
                        </div>
                    </td>

                    <td class="text-nowrap">
                        {{ formatDate(loan.loan_date) }}
                    </td>

                    <td class="text-nowrap">
                        {{ formatDate(loan.due_date) }}
                    </td>

                    <td class="text-nowrap">
                        {{ formatDate(loan.return_date) }}
                    </td>

                    <td :class="statusClasses[loan.status]">
                        {{ statusLabels[loan.status] }}
                    </td>

                    <td>
                        <button
                            v-if="loan.return_date === null"
                            type="button"
                            class="btn btn-link btn-sm p-0"
                            @click="openReturnForm(loan)"
                        >
                            Вернуть
                        </button>

                        <span v-else class="text-secondary">—</span>
                    </td>
                </tr>

                <tr v-if="loans.length === 0">
                    <td colspan="5" class="text-center text-secondary py-3">Выдачи отсутствуют</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="showForm" class="card p-3 mt-4">
        <h2 class="h5 mb-3">Оформление выдачи</h2>

        <div v-if="formError" class="alert alert-danger">
            {{ formError }}
        </div>

        <form novalidate @submit.prevent="saveLoan">
            <SearchSelect
                id="loan-reader"
                v-model="form.reader_id"
                label="Читатель"
                placeholder="Введите ФИО или номер билета"
                :options="readerOptions"
                :error="errors.reader_id"
            />

            <SearchSelect
                id="loan-publication"
                v-model="form.publication_id"
                label="Издание"
                placeholder="Введите название или автора"
                :options="publicationOptions"
                :error="errors.publication_id"
            />

            <SearchSelect
                id="loan-copy"
                :key="form.publication_id"
                v-model="form.copy_id"
                label="Экземпляр"
                :placeholder="
                    form.publication_id ? 'Введите инвентарный номер' : 'Сначала выберите издание'
                "
                :options="copyOptions"
                :error="errors.copy_id"
                :disabled="!form.publication_id"
            />

            <div class="row">
                <div class="col-md-6">
                    <FormField
                        id="loan-date"
                        v-model="form.loan_date"
                        label="Дата выдачи"
                        type="date"
                        :error="errors.loan_date"
                    />
                </div>

                <div class="col-md-6">
                    <FormField
                        id="loan-due-date"
                        v-model="form.due_date"
                        label="Срок возврата"
                        type="date"
                        :error="errors.due_date"
                    />
                </div>
            </div>

            <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-outline-secondary" @click="closeLoanForm">
                    Отмена
                </button>

                <button type="submit" class="btn btn-primary">Оформить</button>
            </div>
        </form>
    </div>

    <div v-if="returningLoan" class="card p-3 mt-4">
        <h2 class="h5 mb-3">Оформление возврата</h2>

        <div v-if="returnError" class="alert alert-danger">
            {{ returnError }}
        </div>

        <p class="mb-1">Читатель: {{ returningLoan.reader_name }}</p>

        <p class="mb-1">Издание: {{ returningLoan.publication_title }}</p>

        <p class="mb-1">Инвентарный номер: {{ returningLoan.inventory_number }}</p>

        <p class="mb-3">Дата выдачи: {{ formatDate(returningLoan.loan_date) }}</p>

        <form novalidate @submit.prevent="saveReturn">
            <div class="row">
                <div class="col-md-6">
                    <FormField
                        id="return-date"
                        v-model="returnDate"
                        label="Дата возврата"
                        type="date"
                        :error="returnDateError"
                    />
                </div>
            </div>

            <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-outline-secondary" @click="closeReturnForm">
                    Отмена
                </button>

                <button type="submit" class="btn btn-primary">Вернуть</button>
            </div>
        </form>
    </div>
</template>
