<template>
  <div class="leaderboard-page">
    <Container size="lg">
      <!-- Header -->
      <div class="page-header">
        <h1>{{ t('leaderboard.title') }}</h1>
        <p class="subtitle">{{ t('leaderboard.subtitle') }}</p>
      </div>

      <!-- Filters -->
      <Card class="filters">
        <div class="filter-row">
          <div class="filter-group">
            <label>{{ t('leaderboard.scopes.title') }}</label>
            <select v-model="timePeriod" class="filter-select">
              <option value="all">{{ t('leaderboard.scopes.alltime') }}</option>
              <option value="month">{{ t('leaderboard.scopes.monthly') }}</option>
              <option value="week">{{ t('leaderboard.scopes.weekly') }}</option>
              <option value="today">{{ t('leaderboard.scopes.daily') }}</option>
            </select>
          </div>
          <div class="filter-group">
            <label>{{ t('leaderboard.categories.title') }}</label>
            <select v-model="language" class="filter-select">
              <option value="all">{{ t('leaderboard.categories.overall') }}</option>
              <option value="en">{{ t('leaderboard.categories.en') }}</option>
              <option value="zh-TW">{{ t('leaderboard.categories.zh-TW') }}</option>
            </select>
          </div>
          <Button @click="fetchLeaderboard" size="md">{{ t('common.save') }}</Button>
        </div>
      </Card>

      <!-- Leaderboard Table -->
      <Card class="leaderboard-card">
        <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
        <div v-else-if="entries.length === 0" class="empty-state">
          <p>{{ t('common.results') }}: 0</p>
        </div>
        <div v-else class="table-container">
          <table class="leaderboard-table">
            <thead>
              <tr>
                <th>{{ t('leaderboard.columns.rank') }}</th>
                <th>{{ t('leaderboard.columns.user') }}</th>
                <th>{{ t('leaderboard.columns.wpm') }}</th>
                <th>{{ t('leaderboard.columns.accuracy') }}</th>
                <th>{{ t('leaderboard.columns.date') }}</th>
            </tr>
          </thead>
            <tbody>
              <tr
                v-for="(entry, index) in displayEntries"
                :key="entry.user_id + '-' + entry.rank"
                :class="{ 'highlight-row': isCurrentUser(entry.user_id) }"
              >
                <td class="rank-cell">
                  <span class="rank" :class="getRankClass(index + 1)">
                    {{ getRankDisplay(index + 1) }}
                  </span>
                </td>
                <td class="user-cell">
                  <div class="user-info">
                    <img v-if="entry.picture" :src="entry.picture" alt="avatar" class="user-avatar" />
                    <div v-else class="user-avatar-placeholder">
                      {{ entry.display_name?.charAt(0).toUpperCase() }}
                    </div>
                    <span class="user-name">{{ entry.display_name }}</span>
                  </div>
                </td>
                <td class="wpm-cell">
                  <span class="wpm-value">{{ entry.wpm }}</span>
                </td>
                <td class="accuracy-cell">
                  <div class="accuracy-bar">
                    <div class="accuracy-fill" :style="{ width: entry.accuracy + '%' }"></div>
                    <span class="accuracy-text">{{ entry.accuracy }}%</span>
                  </div>
                </td>
                <td class="date-cell">{{ formatDate(entry.date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </Container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Container from '@/components/layout/Container.vue'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import { useUserStore } from '@/store/user'
import api from '@/api'

interface LeaderboardEntry {
  rank: number
  user_id: string
  display_name: string
  picture?: string | null
  wpm: number
  accuracy: number
  date: string
}

const userStore = useUserStore()

const timePeriod = ref('all')
const language = ref('all')
const loading = ref(false)
const entries = ref<LeaderboardEntry[]>([])

const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return ''
}

const getRankDisplay = (rank: number) => {
  if (rank === 1) return '🥇'
  if (rank === 2) return '🥈'
  if (rank === 3) return '🥉'
  return rank
}

const isCurrentUser = (userId: string) => {
  return userStore.user?.id === userId
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const scopeMap: Record<string, string> = {
  today: 'daily',
  week: 'weekly',
  month: 'monthly',
  all: 'alltime'
}

const displayEntries = computed(() => {
  // Keep only best entry per user (by WPM, then Accuracy, then most recent)
  const best = new Map<string, LeaderboardEntry>()
  for (const e of entries.value) {
    const prev = best.get(e.user_id)
    if (!prev) {
      best.set(e.user_id, e)
      continue
    }
    const prevDate = new Date(prev.date).getTime()
    const currDate = new Date(e.date).getTime()
    const isBetter = e.wpm > prev.wpm || (e.wpm === prev.wpm && (e.accuracy > prev.accuracy || (e.accuracy === prev.accuracy && currDate > prevDate)))
    if (isBetter) best.set(e.user_id, e)
  }
  // Return sorted by WPM desc, accuracy desc, date desc
  return Array.from(best.values()).sort((a, b) => {
    if (b.wpm !== a.wpm) return b.wpm - a.wpm
    if (b.accuracy !== a.accuracy) return b.accuracy - a.accuracy
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  }).map((e, idx) => ({ ...e, rank: idx + 1 }))
})
const { t } = useI18n()

const fetchLeaderboard = async () => {
  loading.value = true
  try {
    // Use trailing slash to avoid FastAPI 308 redirect (which may downgrade scheme if proxy headers not honored)
    const response = await api.get('/api/leaderboard/', {
      params: {
        scope: scopeMap[timePeriod.value] || 'alltime',
        category: language.value === 'all' ? 'overall' : language.value,
        limit: 50,
      }
    })
    const data = response.data
    entries.value = (data?.entries || []).map((e: any) => ({
      rank: e.rank,
      user_id: e.user_id,
      display_name: e.display_name,
      picture: e.picture || null,
      wpm: Math.round((e.wpm || 0) as number),
      accuracy: Math.round((e.accuracy || 0) as number),
      date: e.date,
    }))
  } catch (error) {
    console.error('Failed to fetch leaderboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLeaderboard()
})
</script>

<style scoped>
.leaderboard-page {
  padding: var(--spacing-8) 0;
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
}

.page-header h1 {
  font-size: var(--font-size-4xl);
  margin-bottom: var(--spacing-2);
}

.subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

/* Filters */
.filters {
  margin-bottom: var(--spacing-6);
}

.filter-row {
  display: flex;
  gap: var(--spacing-4);
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  flex: 1;
  min-width: 150px;
}

.filter-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.filter-select {
  height: 2.5rem; /* align with .button-md height */
  padding: 0 var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background-color: var(--color-background);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: all var(--transition-fast);
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-brand-500);
  box-shadow: 0 0 0 3px var(--color-brand-100);
}

[data-theme="dark"] .filter-select:focus {
  box-shadow: 0 0 0 3px var(--color-brand-900);
}

/* Leaderboard */
.leaderboard-card {
  padding: 0;
  overflow: hidden;
}

.loading,
.empty-state {
  padding: var(--spacing-12);
  text-align: center;
  color: var(--color-text-secondary);
}

.table-container {
  overflow-x: auto;
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
}

.leaderboard-table thead {
  background-color: var(--color-surface);
  border-bottom: 2px solid var(--color-border);
}

.leaderboard-table th {
  padding: var(--spacing-4) var(--spacing-6);
  text-align: left;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.leaderboard-table tbody tr {
  border-bottom: 1px solid var(--color-border);
  transition: background-color var(--transition-fast);
}

.leaderboard-table tbody tr:hover {
  background-color: var(--color-surface);
}

.highlight-row {
  background-color: var(--color-brand-50) !important;
}

[data-theme="dark"] .highlight-row {
  background-color: var(--color-brand-900) !important;
}

.leaderboard-table td {
  padding: var(--spacing-4) var(--spacing-6);
}

/* Rank */
.rank-cell {
  width: 80px;
}

.rank {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

.rank-gold,
.rank-silver,
.rank-bronze {
  font-size: var(--font-size-2xl);
}

/* User */
.user-cell {
  min-width: 200px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius-full);
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius-full);
  background-color: var(--color-brand-600);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-semibold);
}

.user-name {
  font-weight: var(--font-weight-medium);
}

/* WPM */
.wpm-cell {
  width: 100px;
}

.wpm-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-brand-600);
}

[data-theme="dark"] .wpm-value {
  color: var(--color-brand-400);
}

/* Accuracy */
.accuracy-cell {
  width: 150px;
}

.accuracy-bar {
  position: relative;
  height: 2rem;
  background-color: var(--color-neutral-100);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

[data-theme="dark"] .accuracy-bar {
  background-color: var(--color-neutral-800);
}

.accuracy-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand-600), var(--color-brand-400));
  transition: width var(--transition-slow);
}

.accuracy-text {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  z-index: 1;
}

/* Date */
.date-cell {
  width: 120px;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

@media (max-width: 768px) {
  .leaderboard-table th,
  .leaderboard-table td {
    padding: var(--spacing-3) var(--spacing-4);
  }

  .user-avatar,
  .user-avatar-placeholder {
    width: 2rem;
    height: 2rem;
  }
}
</style>
