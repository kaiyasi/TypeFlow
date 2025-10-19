<template>
  <div class="not-found-container">
    <div class="content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">Page Not Found</h2>
      <p class="error-description">
        Sorry, the page you are looking for does not exist or has been moved.
      </p>
      <div class="actions">
        <router-link to="/" class="btn btn-primary">Go to Homepage</router-link>
        <button @click="$router.back()" class="btn btn-secondary">Go Back</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-8);
  flex-grow: 1;
}

.content {
  max-width: 450px;
}

.error-code {
  font-size: 6rem; /* 96px */
  font-weight: 700;
  color: var(--primary);
  line-height: 1;
  margin-bottom: var(--space-4);
}

.error-title {
  font-size: var(--text-3xl);
  font-weight: 600;
  color: var(--foreground);
  margin-bottom: var(--space-4);
}

.error-description {
  font-size: var(--text-lg);
  color: var(--muted-foreground);
  margin-bottom: var(--space-8);
}

.actions {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
}
</style>
