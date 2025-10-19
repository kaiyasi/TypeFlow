<template>
  <div class="input-wrapper">
    <label v-if="label" :for="id" class="input-label">
      {{ label }}
      <span v-if="required" class="input-required">*</span>
    </label>
    <div class="input-container">
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :class="inputClasses"
        @input="handleInput"
        @focus="isFocused = true"
        @blur="isFocused = false"
      />
    </div>
    <p v-if="error" class="input-error">{{ error }}</p>
    <p v-else-if="hint" class="input-hint">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  id?: string
  modelValue?: string | number
  type?: string
  label?: string
  placeholder?: string
  error?: string
  hint?: string
  disabled?: boolean
  required?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const isFocused = ref(false)

const inputClasses = computed(() => [
  'input',
  `input-${props.size}`,
  {
    'input-error': props.error,
    'input-focused': isFocused.value,
    'input-disabled': props.disabled
  }
])

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<style scoped>
.input-wrapper {
  width: 100%;
}

.input-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.input-required {
  color: var(--color-error);
  margin-left: var(--spacing-1);
}

.input-container {
  position: relative;
}

.input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background-color: var(--color-background);
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-brand-500);
  box-shadow: 0 0 0 3px var(--color-brand-100);
}

[data-theme="dark"] .input:focus {
  box-shadow: 0 0 0 3px var(--color-brand-900);
}

.input::placeholder {
  color: var(--color-text-tertiary);
}

/* Sizes */
.input-sm {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  height: 2rem;
}

.input-md {
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--font-size-base);
  height: 2.5rem;
}

.input-lg {
  padding: var(--spacing-4) var(--spacing-5);
  font-size: var(--font-size-lg);
  height: 3rem;
}

/* States */
.input-error {
  border-color: var(--color-error);
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.input-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--color-surface);
}

.input-hint,
.input-error {
  margin-top: var(--spacing-2);
  font-size: var(--font-size-sm);
}

.input-hint {
  color: var(--color-text-secondary);
}

.input-error {
  color: var(--color-error);
}
</style>
