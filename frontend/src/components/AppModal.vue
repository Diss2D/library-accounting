<script setup>
    import { ref, onMounted, onBeforeUnmount } from "vue";

    defineProps({ title: String, busy: Boolean });
    const emit = defineEmits(["close"]);
    const dialog = ref(null);

    onMounted(() => dialog.value.showModal());
    onBeforeUnmount(() => dialog.value?.close());
</script>

<template>
    <dialog
        ref="dialog"
        class="app-modal rounded border-0 shadow p-0"
        aria-labelledby="modal-title"
        @cancel.prevent="!busy && emit('close')"
    >
        <div class="modal-header border-bottom p-3">
            <h2 id="modal-title" class="h5 mb-0">{{ title }}</h2>
            <button
                type="button"
                class="btn-close"
                aria-label="Закрыть"
                :disabled="busy"
                @click="emit('close')"
            ></button>
        </div>
        <div class="p-3">
            <slot />
        </div>
    </dialog>
</template>

<style scoped>
    .app-modal {
        width: min(600px, calc(100% - 2rem));
        max-height: calc(100% - 2rem);
        overflow-y: auto;
    }

    .app-modal::backdrop {
        background: rgba(0, 0, 0, 0.5);
    }
</style>
