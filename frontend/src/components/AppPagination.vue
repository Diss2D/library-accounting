<script setup>
    defineProps({
        page: Number,
        totalPages: Number,
    });

    const emit = defineEmits(["change"]);
</script>

<template>
    <nav v-if="totalPages > 1" aria-label="Страницы каталога">
        <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: page === 1 }">
                <button class="page-link" :disabled="page === 1" @click="emit('change', page - 1)">
                    Назад
                </button>
            </li>

            <li
                v-for="number in totalPages"
                :key="number"
                class="page-item"
                :class="{ active: number === page }"
            >
                <button
                    class="page-link"
                    :aria-current="number === page ? 'page' : null"
                    @click="emit('change', number)"
                >
                    {{ number }}
                </button>
            </li>

            <li class="page-item" :class="{ disabled: page === totalPages }">
                <button
                    class="page-link"
                    :disabled="page === totalPages"
                    @click="emit('change', page + 1)"
                >
                    Вперед
                </button>
            </li>
        </ul>
    </nav>
</template>
