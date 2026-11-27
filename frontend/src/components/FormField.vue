<script setup>
    defineProps({
        id: String,
        label: String,
        type: {
            type: String,
            default: "text",
        },
        placeholder: String,
        autocomplete: String,
        error: String,
    });

    const model = defineModel();
</script>

<template>
    <div class="mb-3">
        <label :for="id" class="form-label">{{ label }}</label>

        <input
            :id="id"
            v-model="model"
            :type="type"
            :placeholder="placeholder"
            :autocomplete="autocomplete"
            class="form-control"
            :class="{ 'is-invalid': error }"
        />

        <div v-if="error" class="invalid-feedback">
            {{ error }}
        </div>
    </div>
</template>
