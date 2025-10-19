<template>
  <component
    :is="tag"
    :type="tag === 'button' ? nativeType : undefined"
    :to="tag === 'router-link' ? to : undefined"
    :href="tag === 'a' ? href : undefined"
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="button-loader"></span>
    <slot v-else />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
  to?: string
  href?: string
  nativeType?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  fullWidth: false,
  nativeType: 'button'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const tag = computed(() => {
  if (props.to) return 'router-link'
  if (props.href) return 'a'
  return 'button'
})

const buttonClasses = computed(() => [
  'button',
  `button-${props.variant}`,
  `button-${props.size}`,
  {
    'button-loading': props.loading,
    'button-disabled': props.disabled,
    'button-full-width': props.fullWidth
  }
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  font-weight: var(--font-weight-medium);
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
  position: relative;
}

.button:focus-visible {
  outline: 2px solid var(--color-brand-500);
  outline-offset: 2px;
}

/* Sizes */
.button-sm {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  height: 2rem;
}

.button-md {
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--font-size-base);
  height: 2.5rem;
}

.button-lg {
  padding: var(--spacing-4) var(--spacing-6);
  font-size: var(--font-size-lg);
  height: 3rem;
}

/* Variants */
.button-primary {
  background-color: var(--color-brand-600);
  color: white;
}

.button-primary:hover:not(.button-disabled):not(.button-loading) {
  background-color: var(--color-brand-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.button-primary:active:not(.button-disabled):not(.button-loading) {
  transform: translateY(0);
}

.button-secondary {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.button-secondary:hover:not(.button-disabled):not(.button-loading) {
  background-color: var(--color-neutral-100);
  border-color: var(--color-neutral-300);
}

[data-theme="dark"] .button-secondary:hover:not(.button-disabled):not(.button-loading) {
  background-color: var(--color-neutral-800);
  border-color: var(--color-neutral-600);
}

.button-ghost {
  background-color: transparent;
  color: var(--color-text-secondary);
}

.button-ghost:hover:not(.button-disabled):not(.button-loading) {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
}

.button-danger {
  background-color: var(--color-error);
  color: white;
}

.button-danger:hover:not(.button-disabled):not(.button-loading) {
  background-color: #dc2626;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* States */
.button-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-loading {
  cursor: wait;
  color: transparent;
}

.button-full-width {
  width: 100%;
}

/* Loader */
.button-loader {
  position: absolute;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
