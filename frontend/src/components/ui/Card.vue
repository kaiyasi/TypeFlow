<template>
  <div :class="cardClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'bordered' | 'elevated'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hoverable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: 'md',
  hoverable: false
})

const cardClasses = computed(() => [
  'card',
  `card-${props.variant}`,
  `card-padding-${props.padding}`,
  {
    'card-hoverable': props.hoverable
  }
])
</script>

<style scoped>
.card {
  background-color: var(--color-surface);
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
}

/* Variants */
.card-default {
  border: 1px solid var(--color-border);
}

.card-bordered {
  border: 2px solid var(--color-border);
}

.card-elevated {
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

/* Padding */
.card-padding-none {
  padding: 0;
}

.card-padding-sm {
  padding: var(--spacing-4);
}

.card-padding-md {
  padding: var(--spacing-6);
}

.card-padding-lg {
  padding: var(--spacing-8);
}

/* Hoverable */
.card-hoverable {
  cursor: pointer;
}

.card-hoverable:hover {
  border-color: var(--color-brand-400);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
</style>
