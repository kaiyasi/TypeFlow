<template>
  <div class="home">
    <Container size="md">
      <!-- Hero Section -->
      <section class="hero">
        <div class="hero-decor">
          <span class="pill pill-rose">{{ t('home.pills.accuracy') }}</span>
          <span class="pill pill-sage">{{ t('home.pills.flow') }}</span>
          <span class="pill pill-lavender">{{ t('home.pills.focus') }}</span>
        </div>
        <h1 class="hero-title">Master Your Typing Skills</h1>
        <div class="hero-typing" aria-label="typing showcase">
          <span class="typing-prefix">Type </span>
          <span class="typing-text">{{ typedText }}</span>
          <span class="caret" :class="{ off: !caretVisible }">|</span>
        </div>
        <p class="hero-description">
          {{ t('home.description') }}
        </p>
        <div class="hero-actions">
          <Button size="lg" @click="$router.push('/practice')">
            {{ t('home.hero.cta') }}
          </Button>
          <Button size="lg" variant="secondary" @click="$router.push('/leaderboard')">
            {{ t('home.actions.viewLeaderboard') }}
          </Button>
        </div>
      </section>

      <!-- Features Section -->
      <section class="features">
        <div class="feature-grid">
          <Card class="feature-card card-rose" hoverable @click="goStart60s">
            <div class="feature-accent"></div>
            <div class="feature-icon-bubble">⌨️</div>
            <h3 class="feature-title">{{ t('home.features.practice.title') }}</h3>
            <p class="feature-description">{{ t('home.features.practice.description') }}</p>
            <div class="feature-footer action">{{ t('home.features.practice.cta') }}</div>
          </Card>

          <Card class="feature-card card-sage" hoverable @click="goLeaderboard">
            <div class="feature-accent"></div>
            <div class="feature-icon-bubble">🏆</div>
            <h3 class="feature-title">{{ t('home.features.compete.title') }}</h3>
            <p class="feature-description">{{ t('home.features.compete.description') }}</p>
            <div class="feature-footer action">{{ t('home.features.compete.cta') }}</div>
          </Card>

          <Card class="feature-card card-slate" hoverable @click="goSubmit">
            <div class="feature-accent"></div>
            <div class="feature-icon-bubble">✍️</div>
            <h3 class="feature-title">{{ t('home.features.submit.title') }}</h3>
            <p class="feature-description">{{ t('home.features.submit.description') }}</p>
            <div class="feature-footer action">{{ t('home.features.submit.cta') }}</div>
          </Card>
        </div>
      </section>

      <!-- Stats Section -->
      <section v-if="stats" class="stats">
        <Card variant="elevated">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ stats.totalUsers || 0 }}</div>
              <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.totalArticles || 0 }}</div>
              <div class="stat-label">Practice Articles</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.totalRecords || 0 }}</div>
              <div class="stat-label">Records Completed</div>
            </div>
          </div>
        </Card>
      </section>
    </Container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { siteConfig } from '@/config/site.config'
import Container from '@/components/layout/Container.vue'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import api from '@/api'

interface Stats {
  totalUsers: number
  totalArticles: number
  totalRecords: number
}

const stats = ref<Stats | null>(null)

const { t } = useI18n()

// Typing decoration
const phrases = [
  'English fast',
  '繁體中文優雅',
  '简体中文高效',
  '日本語 かな・カナ',
  '한국어 한글',
  'Deutsch präzise',
  'Русский быстро',
  'Español fluido',
  'Français raffiné',
  'Português claro',
  'Tiếng Việt nhịp nhàng',
  'Code snippets',
]
const typedText = ref('')
const caretVisible = ref(true)
let phraseIndex = 0
let charIndex = 0
let typing = true
let ticker: number | null = null
let caretTimer: number | null = null
let pauseUntil: number | null = null
const router = useRouter()

const tick = () => {
  // Handle pause window between phases
  if (pauseUntil && Date.now() < pauseUntil) return
  pauseUntil = null
  const current = phrases[phraseIndex]
  if (typing) {
    if (charIndex < current.length) {
      typedText.value = current.slice(0, charIndex + 1)
      charIndex++
    } else {
      // Finished typing the phrase — hold for a few seconds before deleting
      typing = false
      pauseUntil = Date.now() + 2500 // rest 2.5s at full line
    }
  } else {
    if (charIndex > 0) {
      typedText.value = current.slice(0, charIndex - 1)
      charIndex--
    } else {
      // Finished deleting — brief pause before next phrase
      pauseUntil = Date.now() + 800
      typing = true
      phraseIndex = (phraseIndex + 1) % phrases.length
    }
  }
}

onMounted(async () => {
  try {
    // Fetch public platform stats
    const response = await api.get('/api/config/public-stats')
    stats.value = response.data as any
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
  // Start typing effect
  ticker = window.setInterval(tick, 90)
  caretTimer = window.setInterval(() => { caretVisible.value = !caretVisible.value }, 500)
})

onBeforeUnmount(() => {
  if (ticker) window.clearInterval(ticker)
  if (caretTimer) window.clearInterval(caretTimer)
})

const goStart60s = () => {
  router.push({ path: '/practice', query: { start: '1', duration: '60' } })
}

const goLeaderboard = () => {
  router.push({ path: '/leaderboard' })
}

const goProgress = () => {
  // Navigate to practice; future enhancement could open a dedicated stats view
  router.push({ path: '/practice' })
}

const goSubmit = () => {
  router.push({ path: '/submit' })
}
</script>

<style scoped>
.home {
  padding: var(--spacing-12) 0;
}

/* Hero Section */
.hero {
  text-align: center;
  padding: var(--spacing-16) 0;
  position: relative;
}

.hero-title {
  font-size: var(--font-size-5xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-6);
  background: linear-gradient(135deg, var(--color-brand-600), var(--color-brand-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: var(--font-size-4xl);
  }
}

.hero-description {
  font-size: var(--font-size-xl);
  color: var(--color-text-secondary);
  max-width: 600px;
  margin: 0 auto var(--spacing-8);
  line-height: var(--line-height-relaxed);
}

.hero-typing {
  display: inline-flex;
  align-items: baseline;
  gap: var(--spacing-2);
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
}

.typing-prefix { opacity: 0.7; }
.caret { opacity: 1; transition: opacity var(--transition-fast); }
.caret.off { opacity: 0; }

.hero-decor {
  position: absolute;
  inset-inline: 0;
  top: 0;
  display: flex;
  justify-content: center;
  gap: var(--spacing-3);
}

.pill {
  margin-top: -1.5rem;
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: var(--font-size-sm);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xs);
}
.pill-rose { background: #e9d7d7; color: #6a5353; }
.pill-sage { background: #dfe5e0; color: #58635b; }
.pill-lavender { background: #dedde7; color: #585a6b; }

.hero-actions {
  display: flex;
  gap: var(--spacing-4);
  justify-content: center;
  flex-wrap: wrap;
}

/* Features Section */
.features {
  padding: var(--spacing-16) 0;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-6);
  align-items: stretch;
}

@media (max-width: 1024px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  position: relative;
  text-align: left;
  padding: var(--spacing-8);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  background: linear-gradient(180deg, var(--color-surface) 0%, rgba(255,255,255,0.5) 100%);
  box-shadow: var(--shadow-xs) inset, var(--shadow-sm);
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  min-height: 280px;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-brand-300);
}

.feature-accent {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 6px;
  background: linear-gradient(90deg, transparent, var(--accent-1), var(--accent-2), transparent);
}

.feature-icon-bubble {
  width: 3rem;
  height: 3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  margin-bottom: var(--spacing-4);
  font-size: 1.5rem;
  background: var(--bubble-bg);
  color: var(--bubble-fg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xs);
}

.feature-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-3);
}

.feature-description {
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-4);
}

.feature-footer {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-top: auto;
}

/* Card color variants (Morandi tones) */
.card-rose { --accent-1: #e8c9c9; --accent-2: #d8b0b0; --bubble-bg: #efe2e2; --bubble-fg: #6a5353; }
.card-sage { --accent-1: #c9d7cd; --accent-2: #b7c8bb; --bubble-bg: #dee6df; --bubble-fg: #58635b; }
.card-lavender { --accent-1: #cfcde1; --accent-2: #bbb9d1; --bubble-bg: #e6e5ef; --bubble-fg: #585a6b; }
.card-slate { --accent-1: #c9c7c3; --accent-2: #b5b3ae; --bubble-bg: #e7e5e2; --bubble-fg: #4f5157; }

/* Dark theme tuning: reduce contrast and soften accents */
[data-theme="dark"] .feature-card {
  background: linear-gradient(180deg, var(--color-surface) 0%, rgba(255, 255, 255, 0.04) 100%);
  box-shadow: var(--shadow-xs);
  border-color: var(--color-border);
}

[data-theme="dark"] .feature-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: var(--color-brand-500);
}

[data-theme="dark"] .feature-icon-bubble {
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-text-secondary);
  border-color: rgba(255, 255, 255, 0.08);
}

/* Subtle Morandi variants for dark mode (lower saturation/alpha) */
[data-theme="dark"] .card-rose { --accent-1: rgba(232, 201, 201, 0.28); --accent-2: rgba(216, 176, 176, 0.24); --bubble-bg: rgba(239, 226, 226, 0.06); --bubble-fg: #e6dcdc; }
[data-theme="dark"] .card-sage { --accent-1: rgba(201, 215, 205, 0.26); --accent-2: rgba(183, 200, 187, 0.22); --bubble-bg: rgba(222, 230, 223, 0.06); --bubble-fg: #dbe1dc; }
[data-theme="dark"] .card-lavender { --accent-1: rgba(207, 205, 225, 0.26); --accent-2: rgba(187, 185, 209, 0.22); --bubble-bg: rgba(230, 229, 239, 0.06); --bubble-fg: #dbdbe6; }
[data-theme="dark"] .card-slate { --accent-1: rgba(201, 199, 195, 0.22); --accent-2: rgba(181, 179, 174, 0.20); --bubble-bg: rgba(231, 229, 226, 0.05); --bubble-fg: #d6d6d6; }

/* Stats Section */
.stats {
  padding: var(--spacing-8) 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-8);
  padding: var(--spacing-6);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-brand-600);
  margin-bottom: var(--spacing-2);
}

[data-theme="dark"] .stat-value {
  color: var(--color-brand-400);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
