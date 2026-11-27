<script setup>
    import { ref, computed, nextTick } from "vue";

    const props = defineProps({
        id: String,
        label: String,
        options: Array,
        placeholder: String,
        error: String,
        disabled: Boolean,
    });

    const model = defineModel();

    const search = ref("");
    const isOpen = ref(false);
    const activeIndex = ref(-1);
    const inputElement = ref(null);

    const selected = computed(() => props.options.find((option) => option.value === model.value));

    const filteredOptions = computed(() => {
        const query = selected.value ? "" : search.value.trim().toLowerCase();

        return props.options.filter((option) => option.label.toLowerCase().includes(query));
    });

    function openList() {
        if (!props.disabled) {
            isOpen.value = true;
            activeIndex.value = -1;
        }
    }

    function closeList() {
        isOpen.value = false;
        activeIndex.value = -1;
    }

    function toggleList() {
        if (isOpen.value) {
            closeList();
        } else {
            inputElement.value.focus();
            openList();
        }
    }

    function handleInput(event) {
        search.value = event.target.value;
        model.value = "";

        openList();
    }

    function selectOption(option) {
        model.value = option.value;
        search.value = "";

        inputElement.value.focus();
        closeList();
    }

    function handleFocusOut(event) {
        if (!event.currentTarget.contains(event.relatedTarget)) {
            closeList();
        }
    }

    async function moveSelection(direction) {
        if (!isOpen.value) {
            openList();
        }

        const count = filteredOptions.value.length;

        if (!count) {
            return;
        }

        if (activeIndex.value === -1) {
            activeIndex.value = direction === 1 ? 0 : count - 1;
        } else {
            activeIndex.value = (activeIndex.value + direction + count) % count;
        }

        await nextTick();

        document
            .getElementById(`${props.id}-option-${activeIndex.value}`)
            ?.scrollIntoView({ block: "nearest" });
    }

    function handleEnter(event) {
        if (!isOpen.value) {
            return;
        }

        event.preventDefault();

        if (activeIndex.value >= 0) {
            selectOption(filteredOptions.value[activeIndex.value]);
        } else if (filteredOptions.value.length === 1) {
            selectOption(filteredOptions.value[0]);
        }
    }
</script>

<template>
    <div class="mb-3 position-relative" @focusout="handleFocusOut">
        <label :for="id" class="form-label">
            {{ label }}
        </label>

        <div class="input-group">
            <input
                :id="id"
                ref="inputElement"
                type="text"
                role="combobox"
                autocomplete="off"
                aria-autocomplete="list"
                :aria-expanded="isOpen"
                :aria-controls="`${id}-list`"
                :aria-activedescendant="
                    isOpen && activeIndex >= 0 ? `${id}-option-${activeIndex}` : undefined
                "
                :value="selected ? selected.label : search"
                :placeholder="placeholder"
                :disabled="disabled"
                class="form-control"
                :class="{ 'is-invalid': error }"
                @input="handleInput"
                @focus="openList"
                @keydown.down.prevent="moveSelection(1)"
                @keydown.up.prevent="moveSelection(-1)"
                @keydown.enter="handleEnter"
                @keydown.esc.prevent="closeList"
            />

            <button
                type="button"
                class="btn btn-outline-secondary dropdown-toggle"
                :disabled="disabled"
                :aria-label="`Открыть список: ${label}`"
                @mousedown.prevent
                @click="toggleList"
            ></button>
        </div>

        <div v-if="error" class="invalid-feedback d-block">
            {{ error }}
        </div>

        <div
            v-if="isOpen && !disabled"
            :id="`${id}-list`"
            role="listbox"
            :aria-label="label"
            class="list-group position-absolute w-100 shadow-sm z-3 overflow-auto"
            style="max-height: 240px"
        >
            <button
                v-for="(option, index) in filteredOptions"
                :id="`${id}-option-${index}`"
                :key="option.value"
                type="button"
                role="option"
                tabindex="-1"
                :aria-selected="option.value === model"
                class="list-group-item list-group-item-action text-wrap"
                :class="{ active: index === activeIndex }"
                @mousedown.prevent
                @click="selectOption(option)"
            >
                {{ option.label }}
            </button>

            <div v-if="filteredOptions.length === 0" class="list-group-item text-secondary">
                Ничего не найдено
            </div>
        </div>
    </div>
</template>
