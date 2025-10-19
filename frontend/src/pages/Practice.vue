<template>
  <div class="practice-page">
    <Container size="full">
      <!-- Header Section -->
      <div class="practice-header">
        <div class="header-content">
          <h1>{{ t('practice.title') }}</h1>
          <p class="subtitle">{{ t('practice.subtitle') }}</p>
        </div>

        <!-- Quick Stats Overview -->
        <div v-if="practiceHistory.length > 0 && gameState === 'language-selection'" class="quick-stats">
          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <span class="stat-value">{{ averageWpm }}</span>
              <span class="stat-label">{{ t('practice.quickStats.avgWpm') }}</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <span class="stat-value">{{ averageAccuracy }}%</span>
              <span class="stat-label">{{ t('practice.quickStats.avgAccuracy') }}</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <span class="stat-value">{{ practiceHistory.length }}</span>
              <span class="stat-label">{{ t('practice.quickStats.sessions') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Language Selection -->
      <div v-if="gameState === 'language-selection'" class="selection-section">
        <Card class="language-selection-card">
          <h2>{{ t('practice.selection.title') }}</h2>
          <p class="selection-subtitle">{{ t('practice.selection.subtitle') }}</p>

          <!-- Time Duration Selection -->
          <div class="duration-section">
            <label class="duration-label">{{ t('practice.selection.practiceDuration') }}</label>
            <div class="duration-buttons">
              <button
                v-for="duration in durations"
                :key="duration.value"
                :class="['duration-btn', { active: selectedDuration === duration.value }]"
                @click="selectedDuration = duration.value"
              >
                {{ duration.label }}
              </button>
            </div>
          </div>

          <!-- Language Grid -->
          <div class="language-section">
            <label class="language-section-label">{{ t('practice.selectLanguage') }}</label>
            <div class="language-grid">
              <button
                v-for="lang in availableLanguages"
                :key="lang.value"
                :class="['language-option', { 'has-articles': lang.count > 0 }]"
                @click="selectLanguage(lang.value)"
                :disabled="lang.count === 0"
              >
                <div class="language-name">{{ lang.label }}</div>
                <div class="language-count">{{ lang.count }} {{ t('practice.common.articles') }}</div>
              </button>
            </div>
          </div>
        </Card>
      </div>

      <!-- Countdown -->
      <div v-else-if="gameState === 'countdown'" class="countdown-section">
        <Card class="countdown-card">
          <h2>{{ t('practice.countdown.title') }}</h2>
          <p class="countdown-lang">{{ selectedLanguageLabel }}</p>
          <div class="countdown-number">{{ countdown }}</div>
          <p class="countdown-hint">{{ t('practice.countdown.hint') }}</p>
        </Card>
      </div>

      <!-- Practice Area -->
      <div v-else-if="gameState === 'practicing'" class="practice-area">
        <!-- Top Bar with Stats and Controls -->
        <div class="practice-controls">
          <Button variant="ghost" size="sm" @click="exitPractice" class="back-btn">
            ← {{ t('practice.actions.exit') }}
          </Button>

          <div class="live-stats">
            <div class="stat-pill">
              <span class="stat-pill-label">{{ t('practice.stats.wpm') }}</span>
              <span class="stat-pill-value">{{ wpm }}</span>
            </div>
            <div class="stat-pill">
              <span class="stat-pill-label">{{ t('practice.stats.accuracy') }}</span>
              <span class="stat-pill-value">{{ accuracy }}%</span>
            </div>
            <div class="stat-pill">
              <span class="stat-pill-label">{{ t('practice.stats.time') }}</span>
              <span class="stat-pill-value">{{ formatTime(timeElapsed) }}</span>
            </div>
            <div class="stat-pill">
              <span class="stat-pill-label">{{ t('practice.stats.errors') }}</span>
              <span class="stat-pill-value error">{{ errorCount }}</span>
            </div>
          </div>

          <Button variant="secondary" size="sm" @click="resetPractice">
            {{ t('practice.actions.reset') }}
          </Button>
        </div>

        <!-- Typing Area -->
        <Card class="typing-card">
          <div class="typing-header">
            <h2>{{ selectedArticle?.title || 'Loading...' }}</h2>
            <div class="progress-info">
              <span class="progress-text">{{ userInput.length }} / {{ displayText.length }}</span>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: `${progress}%` }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Text Display -->
          <div
            class="text-display"
            ref="textDisplayRef"
            tabindex="0"
            @click="focusInput"
            @keydown="handleKeydown"
            @keypress="handleKeypress"
          >
            <template v-for="(char, index) in displayText" :key="index">
              <span
                :class="getCharClass(index)"
                :ref="index === userInput.length ? 'currentChar' : undefined"
              >{{ char === '\n' ? '' : char }}</span><wbr v-if="char === ' ' || char === '\n'" /><br v-if="char === '\n'" />
            </template>
          </div>
          <p class="typing-hint">Start typing to begin</p>

          <!-- Hidden Input Area -->
          <div class="input-area hidden-input">
            <Input
              v-model="userInput"
              placeholder="Start typing..."
              @input="handleInput"
              @keydown="handleKeydown"
              :disabled="isFinished"
              size="lg"
              ref="inputRef"
              class="practice-input"
            />
          </div>
        </Card>

        <!-- Practice History Sidebar -->
        <Card v-if="practiceHistory.length > 0 && !isFinished" class="history-card">
          <h3>Recent Sessions</h3>
          <div class="history-list">
            <div v-for="(session, index) in recentSessions" :key="index" class="history-item">
              <div class="history-header">
                <span class="history-title">Session {{ practiceHistory.length - index }}</span>
                <span class="history-time">{{ formatDate(session.date) }}</span>
              </div>
              <div class="history-stats">
                <span class="history-stat">{{ session.wpm }} WPM</span>
                <span class="history-stat">{{ session.accuracy }}%</span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <!-- Results Modal -->
      <div v-if="isFinished" class="results-overlay" @click.self="closeResults">
        <Card class="results-modal">
          <div class="results-header">
            <h2>Practice Complete</h2>
          </div>

          <div class="results-stats">
            <div class="result-card primary">
              <div class="result-value">{{ finalWpm }}</div>
              <div class="result-label">Words Per Minute</div>
            </div>
            <div class="result-card">
              <div class="result-value">{{ finalAccuracy }}%</div>
              <div class="result-label">Accuracy</div>
            </div>
            <div class="result-card">
              <div class="result-value">{{ formatTime(finalTime) }}</div>
              <div class="result-label">Time Taken</div>
            </div>
            <div class="result-card">
              <div class="result-value">{{ finalErrors }}</div>
              <div class="result-label">Total Errors</div>
            </div>
          </div>

          <div class="results-actions">
            <Button @click="restartPractice" variant="primary" size="lg">
              Restart
            </Button>
            <Button @click="backToHome" variant="secondary" size="lg">
              Back to Home
            </Button>
          </div>
        </Card>
      </div>
    </Container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import Container from '@/components/layout/Container.vue'
import Card from '@/components/ui/Card.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import api from '@/api'

interface Article {
  id: number | string
  title: string
  content: string
  language: string
  version?: number
}

interface PracticeSession {
  date: Date
  wpm: number
  accuracy: number
  time: number
  errors: number
}

type GameState = 'language-selection' | 'countdown' | 'practicing'

// State
const gameState = ref<GameState>('language-selection')
const articles = ref<Article[]>([])
const selectedArticle = ref<Article | null>(null)
const selectedLanguage = ref<string | null>(null)
const selectedDuration = ref(60) // Default 60 seconds
const userInput = ref('')
const startTime = ref<number | null>(null)
const timeElapsed = ref(0)
const { t } = useI18n()
const isFinished = ref(false)
const inputRef = ref()
const textDisplayRef = ref()
const currentChar = ref()
const loading = ref(true)
const errorCount = ref(0)
const maxInputLength = ref(0) // Track maximum characters typed (cannot decrease)
const countdown = ref(3)

// Final stats
const finalWpm = ref(0)
const finalAccuracy = ref(0)
const finalTime = ref(0)
const finalErrors = ref(0)

// Practice History
const practiceHistory = ref<PracticeSession[]>([])
const route = useRoute()
const autoStartRequested = ref(false)

let timer: number | null = null
let countdownTimer: number | null = null

// Duration options
const durations = [
  { value: 30, label: '30s' },
  { value: 60, label: '1m' },
  { value: 120, label: '2m' },
  { value: 180, label: '3m' },
  { value: 300, label: '5m' },
]

// Language options
const languageOptions = [
  { value: 'en', label: 'English' },
  { value: 'zh-TW', label: '繁體中文' },
  { value: 'zh-CN', label: '简体中文' },
  { value: 'ja', label: '日本語' },
  { value: 'ko', label: '한국어' },
  { value: 'de', label: 'Deutsch' },
  { value: 'ru', label: 'Русский' },
  { value: 'code', label: 'Code' },
]

const tryAutoStart = () => {
  const start = route.query.start === '1' || route.query.start === 1
  const duration = parseInt((route.query.duration as string) || '60', 10)
  const lang = (route.query.lang as string) || 'en'
  if (!start) return
  autoStartRequested.value = true
  if ([30,60,120,180,300].includes(duration)) {
    selectedDuration.value = duration
  }
  // prefer requested language if available, otherwise first available
  const hasLang = articles.value.some(a => a.language === lang)
  const chosen = hasLang ? lang : (availableLanguages.value.find(l => l.count > 0)?.value || null)
  if (chosen) {
    selectedLanguage.value = chosen
    gameState.value = 'countdown'
    startCountdown()
  }
}

// Computed
const displayText = computed(() => selectedArticle.value?.content || '')

const progress = computed(() => {
  if (!displayText.value.length) return 0
  return Math.round((userInput.value.length / displayText.value.length) * 100)
})

const availableLanguages = computed(() => {
  return languageOptions.map(lang => {
    const count = articles.value.filter(a => a.language === lang.value).length
    return { ...lang, count }
  })
})

const selectedLanguageLabel = computed(() => {
  return languageOptions.find(l => l.value === selectedLanguage.value)?.label || ''
})

const wpm = computed(() => {
  if (!startTime.value || maxInputLength.value === 0) return 0
  // Calculate actual elapsed time (selected duration minus remaining time)
  const actualElapsed = selectedDuration.value - timeElapsed.value
  if (actualElapsed <= 0) return 0
  const minutes = actualElapsed / 60
  const words = maxInputLength.value / 5 // Use max length, not current length
  return Math.round(words / minutes) || 0
})

const accuracy = computed(() => {
  if (maxInputLength.value === 0) return 100
  // Calculate accuracy based on max characters typed (not current after backspace)
  const correctChars = maxInputLength.value - errorCount.value
  return Math.round((correctChars / maxInputLength.value) * 100)
})

const recentSessions = computed(() => {
  return practiceHistory.value.slice(-5).reverse()
})

const averageWpm = computed(() => {
  if (practiceHistory.value.length === 0) return 0
  const total = practiceHistory.value.reduce((sum, s) => sum + s.wpm, 0)
  return Math.round(total / practiceHistory.value.length)
})

const averageAccuracy = computed(() => {
  if (practiceHistory.value.length === 0) return 0
  const total = practiceHistory.value.reduce((sum, s) => sum + s.accuracy, 0)
  return Math.round(total / practiceHistory.value.length)
})

// Methods
const getCharClass = (index: number) => {
  if (index >= userInput.value.length) {
    return index === userInput.value.length ? 'char-current' : 'char-pending'
  }
  if (userInput.value[index] === displayText.value[index]) {
    return 'char-correct'
  }
  return 'char-incorrect'
}

const selectLanguage = (lang: string) => {
  selectedLanguage.value = lang
  gameState.value = 'countdown'
  startCountdown()
}

const startCountdown = () => {
  countdown.value = 3
  countdownTimer = window.setInterval(() => {
    countdown.value--
    if (countdown.value === 0) {
      stopCountdown()
      startPractice()
    }
  }, 1000)
}

const stopCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

const startPractice = async () => {
  // Get random article for selected language
  const languageArticles = articles.value.filter(a => a.language === selectedLanguage.value)
  if (languageArticles.length === 0) {
    alert('No articles available for this language')
    gameState.value = 'language-selection'
    return
  }

  const randomArticle = languageArticles[Math.floor(Math.random() * languageArticles.length)]
  selectedArticle.value = randomArticle

  gameState.value = 'practicing'
  resetPracticeData()

  // Auto-focus the text display area after DOM updates
  await nextTick()
  // Use setTimeout to ensure DOM is fully rendered
  setTimeout(() => {
    if (textDisplayRef.value) {
      textDisplayRef.value.focus()
    }
  }, 100)
}

const focusInput = () => {
  textDisplayRef.value?.focus()
}

const handleKeypress = (event: KeyboardEvent) => {
  if (isFinished.value) return

  event.preventDefault()

  const char = event.key

  // Ignore special keys
  if (char.length > 1 && char !== 'Enter') return

  // Stop-loss logic: If the last character typed was wrong, only accept the correct next character
  const lastIndex = userInput.value.length - 1
  if (lastIndex >= 0 && userInput.value[lastIndex] !== displayText.value[lastIndex]) {
    // There's an error in the last position - user must type the correct next character
    const nextCorrectChar = displayText.value[userInput.value.length]
    const inputChar = char === 'Enter' ? '\n' : char

    // Only accept the correct next character to continue
    if (inputChar !== nextCorrectChar) {
      // Block: wrong character while there's an existing error
      return
    }
  }

  // Handle input
  if (char === 'Enter') {
    userInput.value += '\n'
  } else {
    userInput.value += char
  }

  handleInput()
}

const handleKeydown = (event: KeyboardEvent) => {
  if (isFinished.value) return

  if (event.key === 'Backspace') {
    event.preventDefault()
    if (userInput.value.length > 0) {
      // Allow deletion for visual correction, but don't reduce error count
      userInput.value = userInput.value.slice(0, -1)
    }
  }
}

const handleInput = () => {
  if (!startTime.value && userInput.value.length > 0) {
    startTime.value = Date.now()
    startTimer()
  }

  // Only count errors when typing new characters (not when backspacing)
  if (userInput.value.length > maxInputLength.value) {
    const lastIndex = userInput.value.length - 1
    if (lastIndex >= 0 && userInput.value[lastIndex] !== displayText.value[lastIndex]) {
      errorCount.value++
    }
    // Update max length when typing forward
    maxInputLength.value = userInput.value.length
  }

  nextTick(() => {
    if (currentChar.value) {
      currentChar.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })

  if (userInput.value.length >= displayText.value.length) {
    finishPractice()
  }
}

const startTimer = () => {
  timer = window.setInterval(() => {
    if (startTime.value) {
      const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
      timeElapsed.value = selectedDuration.value - elapsed

      // Check if time limit reached
      if (timeElapsed.value <= 0) {
        timeElapsed.value = 0
        finishPractice()
      }
    }
  }, 1000)
}

const stopTimer = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const finishPractice = () => {
  isFinished.value = true
  stopTimer()
  finalWpm.value = wpm.value
  finalAccuracy.value = accuracy.value
  // Calculate actual time used (selected duration minus remaining time)
  finalTime.value = selectedDuration.value - timeElapsed.value
  finalErrors.value = errorCount.value

  practiceHistory.value.push({
    date: new Date(),
    wpm: finalWpm.value,
    accuracy: finalAccuracy.value,
    time: finalTime.value,
    errors: finalErrors.value
  })

  savePracticeHistory()

  // Persist to backend (best-effort)
  try {
    if (selectedArticle.value) {
      const started = startTime.value ? new Date(startTime.value) : new Date()
      const ended = new Date()
      const correct = Math.max(maxInputLength.value - errorCount.value, 0)
      const payload = {
        article_id: selectedArticle.value.id,
        article_version: (selectedArticle.value as any).version || 1,
        mode_seconds: selectedDuration.value,
        started_at: started.toISOString(),
        ended_at: ended.toISOString(),
        language: selectedLanguage.value || selectedArticle.value.language || 'en',
        wpm: finalWpm.value,
        accuracy: finalAccuracy.value,
        gross_wpm: finalWpm.value,
        net_wpm: finalWpm.value,
        correct_keystrokes: correct,
        error_keystrokes: errorCount.value,
      }
      api.post('/api/sessions/submit', payload).catch((e:any)=>{
        console.error('Failed to record session', e)
      })
    }
  } catch (e) {
    console.error('Failed to persist score', e)
  }
}

const resetPracticeData = () => {
  userInput.value = ''
  startTime.value = null
  timeElapsed.value = selectedDuration.value
  isFinished.value = false
  errorCount.value = 0
  maxInputLength.value = 0
  stopTimer()
  finalWpm.value = 0
  finalAccuracy.value = 0
  finalTime.value = 0
  finalErrors.value = 0
}

const resetPractice = () => {
  // Pick a new random article for current language
  if (selectedLanguage.value) {
    const languageArticles = articles.value.filter(a => a.language === selectedLanguage.value)
    if (languageArticles.length > 0) {
      const randomArticle = languageArticles[Math.floor(Math.random() * languageArticles.length)]
      selectedArticle.value = randomArticle
    }
  }
  resetPracticeData()
  nextTick(() => {
    inputRef.value?.$el?.querySelector('input')?.focus()
  })
}

const exitPractice = () => {
  stopTimer()
  stopCountdown()
  gameState.value = 'language-selection'
  selectedArticle.value = null
  selectedLanguage.value = null
  resetPracticeData()
}

const closeResults = () => {
  isFinished.value = false
}

const continueWithSameLanguage = () => {
  isFinished.value = false
  gameState.value = 'countdown'
  startCountdown()
}

const exitToLanguageSelection = () => {
  isFinished.value = false
  exitPractice()
}

const backToHome = () => {
  window.location.href = '/'
}

const restartPractice = () => {
  isFinished.value = false
  // Restart with same language and duration; startCountdown will pick a fresh article in startPractice
  gameState.value = 'countdown'
  startCountdown()
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return date.toLocaleDateString()
}

const fetchArticles = async () => {
  try {
    loading.value = true
    const response = await api.get('/api/articles/')
    articles.value = response.data.articles || []
  } catch (error) {
    console.error('Failed to fetch articles:', error)
    articles.value = []
  } finally {
    loading.value = false
  }
}

const loadPracticeHistory = () => {
  const saved = localStorage.getItem('typeflow_practice_history')
  if (saved) {
    const parsed = JSON.parse(saved)
    practiceHistory.value = parsed.map((s: any) => ({
      ...s,
      date: new Date(s.date)
    }))
  }
}

const savePracticeHistory = () => {
  localStorage.setItem('typeflow_practice_history', JSON.stringify(practiceHistory.value))
}

onMounted(() => {
  fetchArticles()
  loadPracticeHistory()
})

onUnmounted(() => {
  stopTimer()
  stopCountdown()
})

// Run auto-start once articles are loaded
watch(articles, () => {
  if (!autoStartRequested.value) {
    tryAutoStart()
  }
})
</script>

<style scoped>
.practice-page {
  min-height: calc(100vh - var(--header-height));
  background: linear-gradient(180deg, var(--color-background) 0%, var(--color-background-secondary) 100%);
  padding: var(--spacing-8) 0;
}

/* Header Section */
.practice-header {
  margin-bottom: var(--spacing-8);
}

.header-content {
  text-align: center;
  margin-bottom: var(--spacing-6);
}

.practice-header h1 {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-2);
  background: linear-gradient(135deg, var(--color-brand-600), var(--color-brand-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-6);
  max-width: 1000px;
  margin: 0 auto;
}

/* Redesigned stat card in feature-card style (no scale/hover animation) */
.stat-card {
  position: relative;
  background: linear-gradient(180deg, var(--color-surface) 0%, rgba(255,255,255,0.5) 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  box-shadow: var(--shadow-xs) inset, var(--shadow-sm);
}

/* Dark theme tuning for stat cards */
[data-theme="dark"] .stat-card {
  background: var(--color-surface);
  box-shadow: var(--shadow-xs);
  border-color: var(--color-border);
}

[data-theme="dark"] .stat-card::before {
  background: linear-gradient(90deg, transparent, var(--color-brand-700), var(--color-brand-500), transparent);
}

[data-theme="dark"] .stat-icon {
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-text-secondary);
  border-color: rgba(255, 255, 255, 0.08);
}

[data-theme="dark"] .stat-value {
  color: var(--color-brand-400);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 6px;
  background: linear-gradient(90deg, transparent, var(--color-brand-300), var(--color-brand-500), transparent);
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--color-neutral-100);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xs);
  font-size: var(--font-size-xl);
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-brand-600);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Language Selection */
.selection-section {
  max-width: 900px;
  margin: 0 auto;
}

.language-selection-card {
  text-align: center;
  padding: var(--spacing-8);
}

.language-selection-card h2 {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-2);
}

.selection-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-8);
}

/* Duration Selection */
.duration-section {
  margin-bottom: var(--spacing-8);
  padding-bottom: var(--spacing-8);
  border-bottom: 1px solid var(--color-border);
}

.duration-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.duration-buttons {
  display: flex;
  gap: var(--spacing-6);
  flex-wrap: wrap;
  justify-content: center;
}

/* Pure-text buttons with center-out underline animation */
.duration-btn {
  position: relative;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  padding: var(--spacing-2) var(--spacing-3);
}

.duration-btn::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 0;
  width: 100%;
  height: 2px;
  background: currentColor;
  transform: translateX(-50%) scaleX(0);
  transform-origin: center;
  transition: transform 220ms var(--transition-fast);
  opacity: 0.9;
}

.duration-btn::before {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -2px;
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  transform: translateX(-50%) scale(0);
  transition: transform 180ms var(--transition-fast);
}

.duration-btn:hover::before,
.duration-btn.active::before {
  transform: translateX(-50%) scale(1);
}

.duration-btn:hover::after,
.duration-btn.active::after {
  transform: translateX(-50%) scaleX(1);
}

.duration-btn.active {
  color: var(--color-brand-600);
}

.language-section {
  margin-top: var(--spacing-4);
}

.language-section-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.language-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.language-option {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  padding: var(--spacing-4);
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  text-align: left;
  /* Ensure button text color follows theme tokens (UA styles on button may force black) */
  color: var(--color-text-primary);
}

.language-option.has-articles:hover {
  border-color: var(--color-brand-600);
  background: var(--color-surface);
}

.language-option:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.language-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-1);
  /* Explicitly set to avoid inheriting black from button UA styles in dark mode */
  color: var(--color-text-primary);
}

.language-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

/* Countdown */
.countdown-section {
  max-width: 600px;
  margin: 0 auto;
}

.countdown-card {
  text-align: center;
  padding: var(--spacing-12);
}

.countdown-card h2 {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-4);
}

.countdown-lang {
  font-size: var(--font-size-xl);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-8);
}

.countdown-number {
  font-size: 96px;
  font-weight: var(--font-weight-bold);
  color: var(--color-brand-600);
  line-height: 1;
  margin-bottom: var(--spacing-8);
}

.countdown-hint {
  font-size: var(--font-size-base);
  color: var(--color-text-tertiary);
}

/* Practice Area */
.practice-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
  position: relative;
  margin: 0 auto;
  width: 100%;
  overflow: hidden;
}

.practice-area > * {
  max-width: 100%;
  min-width: 0;
}

@media (min-width: 1200px) {
  .practice-area {
    display: flex;
  }
}

.practice-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
}

.back-btn {
  flex-shrink: 0;
}

.live-stats {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
  flex: 1;
  justify-content: center;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  background: var(--color-background-secondary);
  border-radius: var(--radius-full);
}

.stat-pill-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-pill-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-brand-600);
}

.stat-pill-value.error {
  color: var(--color-error);
}

/* Typing Card */
.typing-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
  min-width: 0;
}

.typing-card > * {
  max-width: 100%;
  box-sizing: border-box;
}

.typing-header {
  margin-bottom: var(--spacing-6);
}

.typing-header h2 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-4);
}

.progress-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.progress-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  min-width: 80px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--color-background-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand-600), var(--color-brand-400));
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.text-display {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xl);
  line-height: var(--line-height-relaxed);
  padding: var(--spacing-8);
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-3);
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  user-select: none;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  overflow-wrap: anywhere;
  cursor: text;
  outline: none;
  transition: all var(--transition-base);
  width: 100%;
  box-sizing: border-box;
}

.text-display:focus {
  border-color: var(--color-brand-600);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.text-display span {
  display: inline;
  white-space: normal;
  word-break: normal;
}

.typing-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  text-align: center;
  margin-bottom: var(--spacing-6);
}

.char-pending {
  color: var(--color-text-tertiary);
}

.char-current {
  color: var(--color-text-primary);
  background: var(--color-brand-100);
  border-bottom: 3px solid var(--color-brand-600);
  animation: blink 1s infinite;
}

[data-theme="dark"] .char-current {
  background: rgba(99, 102, 241, 0.2);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.5; }
}

.char-correct {
  color: var(--color-success);
}

.char-incorrect {
  color: var(--color-error);
  background-color: rgba(239, 68, 68, 0.15);
  border-radius: var(--radius-sm);
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.hidden-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  height: 0;
  overflow: hidden;
}

.practice-input {
  font-size: var(--font-size-lg);
}

.input-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  text-align: center;
}

/* Results Overlay */
.results-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-4);
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.results-modal {
  max-width: 700px;
  width: 100%;
  background: var(--color-surface);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.results-header {
  text-align: center;
  margin-bottom: var(--spacing-6);
}

.results-header h2 {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-2);
}

.celebration-icon {
  font-size: 64px;
}

.results-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-8);
}

.result-card {
  text-align: center;
  padding: var(--spacing-6);
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.result-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.result-card.primary {
  border-color: var(--color-brand-600);
  background: var(--color-brand-50);
}

[data-theme="dark"] .result-card.primary {
  background: rgba(99, 102, 241, 0.1);
}

.result-icon {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-2);
}

.result-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-brand-600);
  margin-bottom: var(--spacing-1);
}

.result-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.results-actions {
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
  flex-wrap: wrap;
}

/* History Card */
.history-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  position: sticky;
  top: var(--spacing-6);
  max-height: calc(100vh - var(--spacing-12));
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.history-card h3 {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-4);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  overflow-y: auto;
}

.history-item {
  position: relative;
  padding: var(--spacing-4);
  background: linear-gradient(180deg, var(--color-surface) 0%, rgba(255,255,255,0.5) 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xs) inset, var(--shadow-sm);
}

.history-item::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, transparent, var(--color-brand-300), var(--color-brand-500), transparent);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.history-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.history-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.history-stats {
  display: flex;
  gap: var(--spacing-3);
}

.history-stat {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .practice-header h1 {
    font-size: var(--font-size-3xl);
  }

  .language-grid {
    grid-template-columns: 1fr;
  }

  .practice-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .live-stats {
    justify-content: space-between;
  }

  .stat-pill {
    flex: 1;
    justify-content: center;
  }

  .text-display {
    font-size: var(--font-size-base);
  }

  .results-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .results-actions {
    flex-direction: column;
  }

  .countdown-number {
    font-size: 80px;
  }
}
</style>
