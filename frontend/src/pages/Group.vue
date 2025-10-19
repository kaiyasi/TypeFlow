<template>
  <div class="group-page">
    <Container size="lg">
      <div class="page-header">
        <h1>{{ t('group.title') }}</h1>
        <p class="subtitle">{{ t('group.subtitle') }}</p>
      </div>

      <!-- No Group State -->
      <div v-if="!group" class="grid">
        <Card class="feature-card card-rose">
          <div class="feature-accent"></div>
          <h3 class="title">{{ t('group.create.title') }}</h3>
          <p class="desc">{{ t('group.create.desc') }}</p>
          <form class="inline-form" @submit.prevent="createGroup">
            <Input v-model="newName" :placeholder="t('group.create.placeholder')" />
            <Button type="submit" :disabled="!newName.trim()">{{ t('group.create.action') }}</Button>
          </form>
        </Card>
        <Card class="feature-card card-sage">
          <div class="feature-accent"></div>
          <h3 class="title">{{ t('group.join.title') }}</h3>
          <p class="desc">{{ t('group.join.desc') }}</p>
          <form class="inline-form" @submit.prevent="joinGroup">
            <Input v-model="joinId" :placeholder="t('group.join.placeholder')" />
            <Button type="submit" :disabled="!joinId.trim()" variant="secondary">{{ t('group.join.action') }}</Button>
          </form>
        </Card>
      </div>

      <!-- In Group State -->
      <div v-else class="stack">
        <Card class="group-info-card">
          <div class="feature-accent"></div>
          <div class="info-row">
            <div class="info-block">
              <div class="label">{{ t('group.info.group') }}</div>
              <div class="value">{{ group.name }}</div>
            </div>
            <div class="info-block">
              <div class="label">{{ t('group.info.role') }}</div>
              <div class="value">{{ group.role }}</div>
            </div>
            <div class="info-block id-block">
              <div class="label">{{ t('group.info.groupId') }}</div>
              <div class="id-row">
                <code class="id-text">{{ group.id }}</code>
                <Button size="sm" variant="secondary" @click="copyId">{{ t('group.actions.copy') }}</Button>
              </div>
            </div>
            <div class="spacer"></div>
            <div class="info-actions">
              <Button variant="danger" @click="leave">{{ t('group.actions.leave') }}</Button>
            </div>
          </div>
        </Card>

        <Card v-if="group.role === 'manager'" class="invite-card">
          <h3>{{ t('group.invite.title') }}</h3>
          <form class="inline-form" @submit.prevent="invite">
            <Input v-model="inviteEmail" :placeholder="t('group.invite.placeholder')" />
            <Button type="submit" :disabled="!inviteEmail.trim()">{{ t('group.invite.action') }}</Button>
          </form>
        </Card>

        <Card class="leaderboard-card">
          <h3>{{ t('group.leaderboard.title') }}</h3>
          <div class="controls">
            <label class="mode-label">{{ t('group.leaderboard.mode') }}</label>
            <select v-model="mode" class="mode-select" @change="fetchLeaderboard">
              <option value="latest">{{ t('group.leaderboard.modes.latest') }}</option>
              <option value="best">{{ t('group.leaderboard.modes.best') }}</option>
              <option value="average">{{ t('group.leaderboard.modes.average') }}</option>
            </select>
          </div>
          <div v-if="loading" class="empty-state">{{ t('common.loading') }}</div>
          <div v-else-if="rows.length === 0" class="empty-state">{{ t('group.leaderboard.empty') }}</div>
          <div v-else class="table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>{{ t('leaderboard.columns.user') }}</th>
                  <th>{{ t('leaderboard.columns.wpm') }}</th>
                  <th>{{ t('leaderboard.columns.accuracy') }}</th>
                  <th>{{ t('leaderboard.columns.date') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in rows" :key="r.user_id">
                  <td>
                    <div class="user-cell">
                      <img v-if="r.user_picture" :src="r.user_picture" :alt="r.display_name" class="avatar-img" />
                      <div v-else class="avatar">{{ r.display_name?.charAt(0).toUpperCase() }}</div>
                      <span>{{ r.display_name }}</span>
                    </div>
                  </td>
                  <td>{{ r.wpm }}</td>
                  <td>{{ r.accuracy }}%</td>
                  <td>{{ formatDate(r.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </Container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Container from '@/components/layout/Container.vue'
import Card from '@/components/ui/Card.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import api from '@/api'

const group = ref<any | null>(null)
const newName = ref('')
const joinId = ref('')
const rows = ref<any[]>([])
const mode = ref<'latest' | 'best' | 'average'>('latest')
const loading = ref(false)
const inviteEmail = ref('')
const { t } = useI18n()

const fetchMe = async () => {
  const res = await api.get('/api/group/me')
  group.value = res.data
}

const fetchLeaderboard = async () => {
  if (!group.value) return
  loading.value = true
  try {
    const res = await api.get('/api/group/leaderboard', { params: { mode: mode.value } })
    rows.value = res.data
  } catch (e) {
    console.error('Failed to fetch group leaderboard', e)
  } finally {
    loading.value = false
  }
}

const createGroup = async () => {
  try {
    await api.post('/api/group/create', { name: newName.value.trim() })
    newName.value = ''
    await fetchMe()
    await fetchLeaderboard()
  } catch (e: any) {
    alert(e.response?.data?.detail || 'Failed to create group')
  }
}

const joinGroup = async () => {
  try {
    const id = joinId.value.trim()
    const uuidRe = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/
    if (!uuidRe.test(id)) {
      alert('Please enter a valid Group ID (UUID).')
      return
    }
    await api.post('/api/group/join', { group_id: id })
    joinId.value = ''
    await fetchMe()
  } catch (e: any) {
    const msg = e.response?.data?.detail || e.message || 'Failed to join group'
    alert(msg)
  }
}

const formatDate = (value: string) => {
  const d = new Date(value)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(async () => {
  await fetchMe()
  await fetchLeaderboard()
})

const copyId = async () => {
  if (!group.value) return
  try {
    await navigator.clipboard.writeText(group.value.id)
    alert(t('group.messages.copied'))
  } catch (e) {
    console.error('Copy failed', e)
  }
}

const leave = async () => {
  if (!confirm(t('group.confirm.leave'))) return
  try {
    await api.post('/api/group/leave')
    group.value = null
    rows.value = []
  } catch (e: any) {
    alert(e.response?.data?.detail || t('group.errors.leave'))
  }
}

const invite = async () => {
  if (!inviteEmail.value.trim()) return
  try {
    await api.post('/api/group/invite', { email: inviteEmail.value.trim() })
    inviteEmail.value = ''
    alert(t('group.messages.invited'))
    await fetchLeaderboard()
  } catch (e: any) {
    alert(e.response?.data?.detail || t('group.errors.invite'))
  }
}
</script>

<style scoped>
.group-page { padding: var(--spacing-8) 0; }
.page-header { text-align: center; margin-bottom: var(--spacing-8); }
.subtitle { color: var(--color-text-secondary); }

.grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--spacing-6); }
.feature-card { position: relative; padding: var(--spacing-6); }
.feature-accent { position:absolute; top:0; left:0; right:0; height:6px; background: linear-gradient(90deg, transparent, var(--color-brand-300), var(--color-brand-500), transparent); }
.title { font-size: var(--font-size-xl); margin-bottom: var(--spacing-2); }
.desc { color: var(--color-text-secondary); margin-bottom: var(--spacing-3); }
.inline-form { display:flex; gap: var(--spacing-3); align-items:center; }

.stack { display:flex; flex-direction: column; gap: var(--spacing-6); }
.group-info-card { position:relative; padding: var(--spacing-6); }
.info-row { display:flex; gap: var(--spacing-6); align-items: center; flex-wrap: wrap; }
.info-block { min-width: 200px; }
.label { font-size: var(--font-size-sm); color: var(--color-text-tertiary); }
.value { font-weight: var(--font-weight-semibold); }
.id-row { display:flex; align-items:center; gap: var(--spacing-2); }
.id-text { font-family: var(--font-family-mono); background: var(--color-neutral-100); padding: 2px 6px; border-radius: var(--radius-md); }
.id-text { border: 1px solid var(--color-border); }
[data-theme="dark"] .id-text { background: var(--color-neutral-800); color: var(--color-neutral-100); border-color: var(--color-neutral-700); }
.spacer { flex: 1; }
.info-actions { display:flex; gap: var(--spacing-2); }

.invite-card { padding: var(--spacing-6); }

.empty-state { text-align:center; color: var(--color-text-secondary); padding: var(--spacing-6); }
.leaderboard-card h3 { margin-bottom: var(--spacing-3); }
.controls { display:flex; align-items:center; gap: var(--spacing-2); margin: var(--spacing-2) 0 var(--spacing-3); }
.mode-label { font-size: var(--font-size-sm); color: var(--color-text-tertiary); }
.mode-select { height: 2rem; padding: 0 var(--spacing-3); border:1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-background); }
[data-theme="dark"] .mode-select { color: var(--color-text-primary); background: var(--color-background); border-color: var(--color-border); }
.table-container { overflow-x:auto; }
.table { width:100%; border-collapse: collapse; }
.table th { text-align:left; font-size: var(--font-size-sm); color: var(--color-text-tertiary); padding: var(--spacing-3) var(--spacing-4); }
.table td { padding: var(--spacing-3) var(--spacing-4); border-top: 1px solid var(--color-border); }
.user-cell { display:flex; align-items:center; gap: var(--spacing-3); }
.avatar { width: 2rem; height:2rem; border-radius:999px; background: var(--color-neutral-100); display:flex; align-items:center; justify-content:center; border:1px solid var(--color-border); }
.avatar-img { width: 2rem; height:2rem; border-radius:999px; object-fit: cover; border:1px solid var(--color-border); }
</style>
