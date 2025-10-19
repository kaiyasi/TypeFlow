<template>
  <div :class="containerClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg' | 'full'
  padding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'lg',
  padding: true
})

const containerClasses = computed(() => [
  'layout-container',
  `container-${props.size}`,
  {
    'container-padding': props.padding
  }
])
</script>

<style scoped>
.layout-container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.container-sm {
  max-width: 640px;
}

.container-md {
  max-width: 896px;
}

.container-lg {
  max-width: 1280px;
}

.container-full {
  max-width: none;
}

.container-padding {
  padding-left: var(--spacing-4);
  padding-right: var(--spacing-4);
}

@media (min-width: 640px) {
  .container-padding {
    padding-left: var(--spacing-6);
    padding-right: var(--spacing-6);
  }
}

@media (min-width: 1024px) {
  .container-padding {
    padding-left: var(--spacing-8);
    padding-right: var(--spacing-8);
  }
}
</style>
