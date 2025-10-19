<template>
  <div class="auth-callback-page">
    <Container size="sm">
      <div class="callback-content">
        <div v-if="!error" class="loading-state">
          <div class="loader"></div>
          <h2>Authenticating...</h2>
          <p>Please wait while we complete your login</p>
        </div>
        <div v-else class="error-state">
          <h2>Authentication Failed</h2>
          <p class="error-message">{{ error }}</p>
          <Button @click="$router.push('/')" variant="primary">
            Back to Home
          </Button>
        </div>
      </div>
    </Container>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import Container from '@/components/layout/Container.vue'
import Button from '@/components/ui/Button.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const error = ref<string | null>(null)

onMounted(async () => {
  const code = route.query.code as string

  if (code) {
    try {
      await userStore.handleGoogleCallback(code)
      window.location.href = '/'
    } catch (e: any) {
      console.error('Google callback error:', e)
      error.value = e.message || 'An unknown error occurred'
    }
  } else {
    error.value = 'No authorization code found in URL'
  }
})
</script>

<style scoped>
.auth-callback-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
  padding: var(--spacing-8) 0;
}

.callback-content {
  text-align: center;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
}

.loader {
  width: 4rem;
  height: 4rem;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-brand-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state h2,
.error-state h2 {
  font-size: var(--font-size-2xl);
}

.loading-state p {
  color: var(--color-text-secondary);
}

.error-message {
  padding: var(--spacing-4);
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-lg);
  color: var(--color-error);
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono);
  max-width: 400px;
}
</style>
