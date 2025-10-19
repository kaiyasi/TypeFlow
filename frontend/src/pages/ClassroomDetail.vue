<template>
  <div class="classroom-detail">
    <Container size="lg">
      <div class="page-header">
        <h1>{{ title }}</h1>
        <p class="subtitle">Add members and review scores</p>
      </div>

      <Card class="member-card">
        <h3>Add Member</h3>
        <form class="member-form" @submit.prevent="handleAdd">
          <Input v-model="email" placeholder="Student email" />
          <select v-model="role" class="select">
            <option value="member">member</option>
            <option value="manager">manager</option>
          </select>
          <Button type="submit" :disabled="!email.trim()" variant="primary">Add</Button>
        </form>
      </Card>

      <Card>
        <div class="table-actions">
          <Input v-model="q" placeholder="Search by name/email" />
        </div>
        <div v-if="loading" class="empty-state">Loading...</div>
        <div v-else-if="rows.length === 0" class="empty-state">No data</div>
        <div v-else class="table-container">
          <table class="scores-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Latest</th>
                <th>Best WPM</th>
                <th>Avg WPM</th>
                <th>Avg Acc</th>
                <th>Sessions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in filtered" :key="r.user_id">
                <td>
                  <div class="user-cell">
                    <div class="avatar">{{ r.display_name?.charAt(0).toUpperCase() }}</div>
                    <div class="user-meta">
                      <div class="name">{{ r.display_name }}</div>
                      <div class="mail">{{ r.email }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="pill">{{ r.latest_wpm ?? '-' }} WPM / {{ r.latest_accuracy ?? '-' }}%</div>
                  <div class="date">{{ formatDate(r.latest_at) }}</div>
                </td>
                <td>{{ r.best_wpm ?? '-' }}</td>
                <td>{{ r.avg_wpm ? Math.round(r.avg_wpm) : '-' }}</td>
                <td>{{ r.avg_accuracy ? Math.round(r.avg_accuracy) : '-' }}%</td>
                <td>{{ r.sessions }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </Container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Container from '@/components/layout/Container.vue'
import Card from '@/components/ui/Card.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import api from '@/api'

const route = useRoute()
const id = route.params.id as string
const title = ref('Classroom')
const loading = ref(false)
const rows = ref<any[]>([])

const email = ref('')
const role = ref<'member' | 'manager'>('member')
const q = ref('')

const fetchScores = async () => {
  loading.value = true
  try {
    const res = await api.get(`/api/classrooms/${id}/scores`)
    rows.value = res.data
  } catch (e) {
    console.error('Failed to load scores', e)
  } finally {
    loading.value = false
  }
}

const handleAdd = async () => {
  if (!email.value.trim()) return
  try {
    await api.post(`/api/classrooms/${id}/members`, { email: email.value.trim(), role: role.value })
    email.value = ''
    fetchScores()
  } catch (e) {
    console.error('Failed to add member', e)
    alert('Failed to add member')
  }
}

const filtered = computed(() => {
  if (!q.value.trim()) return rows.value
  const s = q.value.toLowerCase()
  return rows.value.filter((r) =>
    (r.display_name || '').toLowerCase().includes(s) || (r.email || '').toLowerCase().includes(s)
  )
})

const formatDate = (value?: string) => {
  if (!value) return ''
  const d = new Date(value)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(() => fetchScores())
</script>

<style scoped>
.classroom-detail { padding: var(--spacing-8) 0; }
.page-header { text-align: center; margin-bottom: var(--spacing-8); }
.subtitle { color: var(--color-text-secondary); }

.member-card { margin-bottom: var(--spacing-6); }
.member-card h3 { margin-bottom: var(--spacing-3); }
.member-form { display: flex; gap: var(--spacing-3); align-items: center; flex-wrap: wrap; }
.select { padding: var(--spacing-3); border: 1px solid var(--color-border); border-radius: var(--radius-md); }

.empty-state { text-align:center; color: var(--color-text-secondary); padding: var(--spacing-8); }
.table-actions { display:flex; justify-content:flex-end; margin-bottom: var(--spacing-3); }

.table-container { overflow-x: auto; }
.scores-table { width: 100%; border-collapse: collapse; }
.scores-table th { text-align: left; font-size: var(--font-size-sm); color: var(--color-text-tertiary); padding: var(--spacing-3) var(--spacing-4); }
.scores-table td { padding: var(--spacing-3) var(--spacing-4); border-top: 1px solid var(--color-border); vertical-align: top; }

.user-cell { display:flex; gap: var(--spacing-3); align-items: center; }
.avatar { width: 2rem; height:2rem; border-radius: var(--radius-full); background: var(--color-neutral-100); display:flex; align-items:center; justify-content:center; border:1px solid var(--color-border); }
.user-meta .name { font-weight: var(--font-weight-semibold); }
.user-meta .mail { font-size: var(--font-size-sm); color: var(--color-text-tertiary); }
.pill { display:inline-block; padding: 2px 8px; border-radius:999px; background: var(--color-neutral-100); }
.date { font-size: var(--font-size-xs); color: var(--color-text-tertiary); }
</style>

