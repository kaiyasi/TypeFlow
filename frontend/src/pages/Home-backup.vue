<template>
  <div class="home">
    <!-- Hero Section - Minimalist -->
    <section class="hero">
      <div class="container container-5xl">
        <div class="hero-content fade-in">
          <h1 class="hero-title">
            Master Your<br />
            Typing Skills
          </h1>
          <p class="hero-description">
            A minimalist typing practice platform designed for focus and improvement.
            Track your progress, compete globally, and become faster every day.
          </p>
          <div class="hero-actions">
            <router-link to="/practice" class="btn btn-primary btn-lg">
              Start Practice
            </router-link>
            <router-link to="/leaderboard" class="btn btn-secondary btn-lg">
              View Leaderboard
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats">
      <div class="container container-4xl">
        <div class="stats-grid">
          <div class="stat-card slide-up" v-for="(stat, idx) in stats" :key="idx" :style="{ animationDelay: `${idx * 100}ms` }">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container container-5xl">
        <div class="section-header">
          <h2>Why TypeFlow</h2>
          <p class="section-description">
            Everything you need to improve your typing speed and accuracy
          </p>
        </div>
        <div class="features-grid">
          <div class="feature-card" v-for="(feature, idx) in features" :key="idx">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="container container-3xl">
        <div class="cta-card">
          <h2 class="cta-title">Ready to Start?</h2>
          <p class="cta-description">
            Join thousands of users improving their typing skills
          </p>
          <router-link to="/practice" class="btn btn-primary btn-lg">
            Begin Practice
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const stats = ref([
  { value: '50K+', label: 'Active Users' },
  { value: '2M+', label: 'Practice Sessions' },
  { value: '8+', label: 'Languages' },
  { value: '95%', label: 'Avg. Accuracy' }
]);

const features = ref([
  {
    icon: '⚡',
    title: 'Real-time Feedback',
    description: 'See your WPM and accuracy as you type with instant feedback on every keystroke'
  },
  {
    icon: '🌍',
    title: 'Multi-language Support',
    description: 'Practice in English, Traditional Chinese, code, and more languages'
  },
  {
    icon: '📊',
    title: 'Progress Tracking',
    description: 'Detailed statistics and history to track your improvement over time'
  },
  {
    icon: '🏆',
    title: 'Global Leaderboard',
    description: 'Compete with typists worldwide and climb the rankings'
  },
  {
    icon: '🎯',
    title: 'Custom Practice',
    description: 'Tailor your practice sessions with custom duration and difficulty'
  },
  {
    icon: '🔐',
    title: 'Secure & Private',
    description: 'Your data is safe with Google OAuth and cloud synchronization'
  }
]);
</script>

<style scoped>
/* ==========================================
   Home Page - Minimalist Design
   ========================================== */

.home {
  min-height: 100vh;
}

/* Hero Section */
.hero {
  padding: var(--space-32) 0 var(--space-24);
  text-align: center;
}

.hero-content {
  max-width: 48rem;
  margin: 0 auto;
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: -0.03em;
  margin-bottom: var(--space-6);
}

.hero-description {
  font-size: var(--text-lg);
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
  margin-bottom: var(--space-8);
  max-width: 40rem;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  flex-wrap: wrap;
}

/* Stats Section */
.stats {
  padding: var(--space-16) 0;
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-8);
}

.stat-card {
  text-align: center;
  padding: var(--space-6);
}

.stat-value {
  font-size: var(--text-5xl);
  font-weight: var(--font-bold);
  font-family: var(--font-mono);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Features Section */
.features {
  padding: var(--space-24) 0;
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-16);
}

.section-header h2 {
  margin-bottom: var(--space-4);
}

.section-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  max-width: 36rem;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-8);
}

.feature-card {
  padding: var(--space-8);
  background-color: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.feature-card:hover {
  border-color: var(--border-base);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: var(--text-5xl);
  margin-bottom: var(--space-4);
}

.feature-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-3);
}

.feature-description {
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
}

/* CTA Section */
.cta {
  padding: var(--space-24) 0 var(--space-32);
}

.cta-card {
  text-align: center;
  padding: var(--space-16) var(--space-8);
  background-color: var(--surface-elevated);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-xl);
}

.cta-title {
  margin-bottom: var(--space-4);
}

.cta-description {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  margin-bottom: var(--space-8);
}

/* Responsive */
@media (max-width: 768px) {
  .hero {
    padding: var(--space-20) 0 var(--space-16);
  }

  .hero-actions {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-6);
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: var(--space-6);
  }

  .feature-card {
    padding: var(--space-6);
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
