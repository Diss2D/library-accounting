<script setup>
    import { ref, onMounted } from "vue";

    import { getMyLoans } from "../api/index.js";
    import { useAuthStore } from "../stores/auth.js";

    const auth = useAuthStore();

    const loans = ref([]);
    const errorMessage = ref("");
    const loading = ref(false);

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
            loans.value = await getMyLoans(auth.user.reader_id);
        } catch (error) {
            errorMessage.value = error.message;
        } finally {
            loading.value = false;
        }
    }

    onMounted(loadLoans);
</script>

<template>
    <h1 class="h3 mb-3">Мои выдачи</h1>

    <div v-if="errorMessage" class="alert alert-danger">
        {{ errorMessage }}
    </div>

    <p v-else-if="loading" class="text-secondary">Загрузка...</p>

    <div v-else class="table-responsive">
        <table class="table table-bordered table-hover align-middle">
            <thead class="table-light">
                <tr>
                    <th>Издание</th>
                    <th>Экземпляр</th>
                    <th>Дата выдачи</th>
                    <th>Срок возврата</th>
                    <th>Дата возврата</th>
                    <th>Состояние</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="loan in loans" :key="loan.id">
                    <td>{{ loan.publication_title }}</td>

                    <td class="text-nowrap">
                        {{ loan.inventory_number }}
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
                </tr>

                <tr v-if="loans.length === 0">
                    <td colspan="6" class="text-center text-secondary py-3">У вас нет выдач</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
