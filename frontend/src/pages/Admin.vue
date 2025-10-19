<template>
  <div class="admin-page">
    <Container size="lg">
      <!-- Header -->
      <div class="page-header">
        <h1>{{ t('admin.title') }}</h1>
        <p class="subtitle">{{ t('admin.subtitle') }}</p>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <Card class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-value">{{ stats.pendingArticles }}</div>
          <div class="stat-label">{{ t('admin.stats.pending') }}</div>
        </Card>
        <Card class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-value">{{ stats.approvedArticles }}</div>
          <div class="stat-label">{{ t('admin.stats.approved') }}</div>
        </Card>
        <Card class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-label">{{ t('admin.stats.users') }}</div>
        </Card>
        <Card class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-value">{{ stats.totalRecords }}</div>
          <div class="stat-label">{{ t('admin.stats.records') }}</div>
        </Card>
      </div>

      <!-- Tabs -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['tab', { 'tab-active': activeTab === tab.id }]"
        >
          {{ t(tab.i18n) }}
        </button>
      </div>

      <!-- Pending Articles -->
      <Card v-if="activeTab === 'pending'" class="content-card">
        <h2>{{ t('admin.sections.pending') }}</h2>
        <div v-if="pendingArticles.length === 0" class="empty-state">
          <p>{{ t('common.results') }}: 0</p>
        </div>
        <div v-else class="articles-list">
          <div v-for="article in pendingArticles" :key="article.id" class="article-item">
            <div class="article-header">
              <h3>{{ article.title }}</h3>
              <div class="article-meta">
                <span>{{ article.language }}</span>
                <template v-if="article.difficulty">
                  <span>•</span>
                  <span>{{ article.difficulty }}</span>
                </template>
                <span>•</span>
                <span>{{ t('admin.common.by') }} {{ article.author_name }}</span>
              </div>
            </div>
            <p class="article-preview">{{ article.content?.substring(0, 200) || '' }}{{ article.content && article.content.length > 200 ? '...' : '' }}</p>
            <div class="article-actions">
              <Button @click="approveArticle(article.id)" variant="primary" size="sm">
                {{ t('common.success') }}
              </Button>
              <Button @click="rejectArticle(article.id)" variant="danger" size="sm">
                {{ t('common.delete') }}
              </Button>
              <Button @click="viewArticle(article)" variant="ghost" size="sm">
                {{ t('admin.actions.viewFull') }}
              </Button>
            </div>
          </div>
        </div>
      </Card>

      <!-- All Articles -->
      <Card v-if="activeTab === 'all'" class="content-card">
        <div class="card-header">
          <h2>{{ t('admin.sections.allArticles') }}</h2>
          <Input
            v-model="searchQuery"
            :placeholder="t('admin.search.articles')"
            size="sm"
          />
        </div>
        <div v-if="filteredArticles.length === 0" class="empty-state">
          <p>{{ t('admin.empty.noArticles') }}</p>
        </div>
        <div v-else class="table-container">
          <table class="admin-table">
            <thead>
              <tr>
                <th>{{ t('submit.form.title') }}</th>
                <th>{{ t('submit.form.language') }}</th>
                <th>{{ t('submit.form.difficulty') }}</th>
                <th>{{ t('leaderboard.columns.date') }}</th>
                <th>{{ t('leaderboard.columns.user') }}</th>
                <th>{{ t('leaderboard.columns.date') }}</th>
                <th>{{ t('admin.common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="article in filteredArticles" :key="article.id">
                <td>{{ article.title }}</td>
                <td>{{ article.language }}</td>
                <td>{{ article.difficulty }}</td>
                <td>
                  <span :class="'status-badge status-' + article.status">
                    {{ article.status }}
                  </span>
                </td>
                <td>{{ article.author_name }}</td>
                <td>{{ formatDate(article.created_at) }}</td>
                <td>
                  <div class="table-actions">
                    <button @click="openEdit(article)" class="icon-btn" :title="t('admin.actions.edit')">✏️</button>
                    <button @click="deleteArticle(article.id)" class="icon-btn" :title="t('common.delete')">🗑️</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

  <!-- Users -->
  <Card v-if="activeTab === 'users'" class="content-card">
        <h2>{{ t('admin.users.title') }}</h2>
        <div class="user-role-controls">
          <Input v-model="roleEmail" :placeholder="t('admin.users.emailPlaceholder')" />
          <select v-model="roleToSet" class="select">
            <option value="user">{{ t('admin.users.roles.user') }}</option>
            <option value="org_admin">{{ t('admin.users.roles.orgAdmin') }}</option>
            <option value="super_admin">{{ t('admin.users.roles.superAdmin') }}</option>
          </select>
          <Button @click="setRoleByEmail" size="sm">{{ t('admin.users.setRole') }}</Button>
        </div>
        <div v-if="users.length === 0" class="empty-state">
          <p>{{ t('admin.empty.noUsers') }}</p>
        </div>
        <div v-else class="table-container">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>{{ t('leaderboard.columns.user') }}</th>
                <th>Email</th>
                <th>{{ t('admin.users.role') }}</th>
                <th>{{ t('leaderboard.columns.date') }}</th>
                <th>{{ t('admin.users.records') }}</th>
                <th>{{ t('admin.common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td><code>{{ user.id }}</code></td>
                <td>
                  <div class="user-cell">
                    <img
                      v-if="user.picture"
                      :src="user.picture"
                      :alt="user.display_name"
                      class="user-avatar"
                    />
                    <div v-else class="user-avatar-placeholder">
                      {{ user.display_name?.charAt(0).toUpperCase() }}
                    </div>
                    <span>{{ user.display_name }}</span>
                  </div>
                </td>
                <td>{{ user.email }}</td>
                <td>{{ roleLabel(user.role) }}</td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>{{ user.record_count || 0 }}</td>
                <td>
                  <div class="user-actions">
                    <select v-model="userRoleUpdates[user.id]" class="select">
                      <option value="user">{{ t('admin.users.roles.user') }}</option>
                      <option value="org_admin">{{ t('admin.users.roles.orgAdmin') }}</option>
                      <option value="super_admin">{{ t('admin.users.roles.superAdmin') }}</option>
                    </select>
                    <Button size="sm" @click="applyUserRole(user)">{{ t('common.save') }}</Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
  </Card>

  <!-- Scores (Admin edit) -->
  <Card v-if="activeTab === 'scores'" class="content-card">
    <h2>{{ t('admin.scores.title') }}</h2>
    <div class="score-controls">
      <Input v-model="scoreUserId" :placeholder="t('admin.scores.userIdPlaceholder')" />
      <Button @click="fetchUserScores">{{ t('admin.actions.load') }}</Button>
    </div>
    <div v-if="userScores.length === 0" class="empty-state">
      <p>{{ t('admin.empty.noScores') }}</p>
    </div>
    <div v-else class="table-container">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>{{ t('leaderboard.columns.wpm') }}</th>
            <th>{{ t('leaderboard.columns.accuracy') }}</th>
            <th>{{ t('leaderboard.categories.title') }}</th>
            <th>{{ t('leaderboard.columns.date') }}</th>
            <th>{{ t('admin.common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in userScores" :key="row.id">
            <td><code>{{ row.id }}</code></td>
            <td><input class="inline-number" type="number" v-model.number="row.wpm" min="0" max="1000" step="0.1" /></td>
            <td><input class="inline-number" type="number" v-model.number="row.accuracy" min="0" max="100" step="0.1" /></td>
            <td>{{ row.language }}</td>
            <td>{{ row.created_at ? formatDate(row.created_at) : '-' }}</td>
            <td>
              <Button :disabled="savingScoreId === row.id" size="sm" @click="saveScore(row)">
                {{ savingScoreId === row.id ? t('common.loading') : t('common.save') }}
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </Card>
    </Container>

    <!-- View Article Modal (simplified) -->
    <div v-if="viewingArticle" class="modal-overlay" @click="viewingArticle = null">
      <Card class="modal-content" @click.stop>
        <h2>{{ viewingArticle.title }}</h2>
        <div class="modal-meta">
          <span>{{ viewingArticle.language }}</span>
          <template v-if="viewingArticle.difficulty">
            <span>•</span>
            <span>{{ viewingArticle.difficulty }}</span>
          </template>
          <span>•</span>
          <span>{{ t('admin.common.by') }} {{ viewingArticle.author_name }}</span>
          <template v-if="viewingArticle.created_at">
            <span>•</span>
            <span>{{ formatDate(viewingArticle.created_at) }}</span>
          </template>
        </div>
        <div class="modal-content-text">{{ viewingArticle.content }}</div>
        <div class="modal-actions">
          <Button @click="viewingArticle = null" variant="secondary">{{ t('common.cancel') }}</Button>
        </div>
      </Card>
    </div>

    <!-- Edit Article Modal -->
    <div v-if="editingArticle" class="modal-overlay" @click="cancelEdit">
      <Card class="modal-content" @click.stop>
        <h2>{{ t('admin.actions.edit') }}</h2>
        <div class="modal-meta">
          <span>ID: {{ editingArticle.id }}</span>
        </div>
        <form class="edit-form" @submit.prevent="saveEdit">
          <label>
            <span>{{ t('submit.form.title') }}</span>
            <Input v-model="editForm.title" />
          </label>
          <label>
            <span>{{ t('submit.form.language') }}</span>
            <select v-model="editForm.language" class="select">
              <option value="en">en</option>
              <option value="zh-TW">zh-TW</option>
              <option value="zh-CN">zh-CN</option>
              <option value="ja">ja</option>
              <option value="ko">ko</option>
              <option value="de">de</option>
              <option value="ru">ru</option>
              <option value="es">es</option>
              <option value="fr">fr</option>
              <option value="it">it</option>
              <option value="pt">pt</option>
              <option value="vi">vi</option>
              <option value="code">code</option>
            </select>
          </label>
          <label>
            <span>Status</span>
            <select v-model="editForm.status" class="select">
              <option value="draft">draft</option>
              <option value="submitted">submitted</option>
              <option value="approved">approved</option>
              <option value="rejected">rejected</option>
              <option value="published">published</option>
            </select>
          </label>
          <label>
            <span>{{ t('submit.form.content') }}</span>
            <textarea v-model="editForm.content" class="textarea"></textarea>
          </label>
          <div class="modal-actions">
            <Button type="button" variant="secondary" @click="cancelEdit">{{ t('common.cancel') }}</Button>
            <Button type="submit" variant="primary">{{ t('common.save') }}</Button>
          </div>
        </form>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Container from '@/components/layout/Container.vue'
import Card from '@/components/ui/Card.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import { useUserStore } from '@/store/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

// Check admin access
if (!userStore.isAdmin) {
  router.push('/')
}

interface Article {
  id: number
  title: string
  content: string
  language: string
  difficulty: string
  status: string
  author_name: string
  created_at: string
}

interface User {
  id: number
  email: string
  display_name: string
  picture?: string
  role: string
  created_at: string
  record_count?: number
}

const activeTab = ref('pending')
const searchQuery = ref('')
const viewingArticle = ref<Article | null>(null)
const editingArticle = ref<Article | null>(null)
const editForm = ref({
  title: '',
  language: 'en',
  status: 'draft',
  content: ''
})

const tabs = [
  { id: 'pending', i18n: 'admin.tabs.pending' },
  { id: 'all', i18n: 'admin.tabs.allArticles' },
  { id: 'users', i18n: 'admin.tabs.users' },
  { id: 'scores', i18n: 'admin.tabs.scores' },
]

const stats = ref({
  pendingArticles: 0,
  approvedArticles: 0,
  totalUsers: 0,
  totalRecords: 0
})

const pendingArticles = ref<Article[]>([])
const allArticles = ref<Article[]>([])
const users = ref<User[]>([])
const userRoleUpdates = ref<Record<string, string>>({})
const roleEmail = ref('')
const roleToSet = ref<'user' | 'org_admin' | 'super_admin'>('super_admin')
const { t } = useI18n()

const roleLabel = (role: string) => {
  if (role === 'super_admin') return t('admin.users.roles.superAdmin')
  if (role === 'org_admin') return t('admin.users.roles.orgAdmin')
  return t('admin.users.roles.user')
}
const scoreUserId = ref('')
const userScores = ref<any[]>([])
const savingScoreId = ref<string | null>(null)

const filteredArticles = computed(() => {
  if (!searchQuery.value) return allArticles.value
  const query = searchQuery.value.toLowerCase()
  return allArticles.value.filter(article =>
    article.title.toLowerCase().includes(query) ||
    article.author_name.toLowerCase().includes(query)
  )
})

const fetchStats = async () => {
  try {
    const response = await api.get('/api/admin/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchPendingArticles = async () => {
  try {
    const response = await api.get('/api/admin/articles/pending')
    pendingArticles.value = response.data
  } catch (error) {
    console.error('Failed to fetch pending articles:', error)
  }
}

const fetchAllArticles = async () => {
  try {
    const response = await api.get('/api/admin/articles')
    allArticles.value = response.data
  } catch (error) {
    console.error('Failed to fetch all articles:', error)
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/api/admin/users')
    users.value = response.data
    // initialize selections
    const init: Record<string, string> = {}
    for (const u of users.value as any[]) init[u.id] = u.role
    userRoleUpdates.value = init
  } catch (error) {
    console.error('Failed to fetch users:', error)
  }
}

const applyUserRole = async (user: any) => {
  try {
    const newRole = userRoleUpdates.value[user.id]
    await api.post(`/api/admin/users/${user.id}/role`, { role: newRole })
    await fetchUsers()
    alert(t('admin.users.roleUpdated'))
  } catch (e) {
    console.error('Failed to update role', e)
    alert(t('admin.users.roleUpdateFailed'))
  }
}

const setRoleByEmail = async () => {
  if (!roleEmail.value.trim()) return
  try {
    await api.post('/api/admin/users/by-email/role', { email: roleEmail.value.trim(), role: roleToSet.value })
    roleEmail.value = ''
    await fetchUsers()
    alert(t('admin.users.roleUpdated'))
  } catch (e) {
    console.error('Failed to set role by email', e)
    alert(t('admin.users.roleUpdateFailed'))
  }
}

const approveArticle = async (id: number) => {
  try {
    await api.post(`/api/admin/articles/${id}/approve`)
    await fetchPendingArticles()
    await fetchStats()
    alert('Article approved successfully')
  } catch (error) {
    console.error('Failed to approve article:', error)
    alert('Failed to approve article')
  }
}

const rejectArticle = async (id: number) => {
  if (!confirm('Are you sure you want to reject this article?')) return

  try {
    await api.post(`/api/admin/articles/${id}/reject`)
    await fetchPendingArticles()
    await fetchStats()
    alert('Article rejected')
  } catch (error) {
    console.error('Failed to reject article:', error)
    alert('Failed to reject article')
  }
}

const deleteArticle = async (id: number) => {
  if (!confirm('Are you sure you want to delete this article? This action cannot be undone.')) return

  try {
    await api.delete(`/api/admin/articles/${id}`)
    await fetchAllArticles()
    await fetchStats()
    alert('Article deleted successfully')
  } catch (error) {
    console.error('Failed to delete article:', error)
    alert('Failed to delete article')
  }
}

const viewArticle = (article: Article) => {
  viewingArticle.value = article
}

const openEdit = (article: Article) => {
  editingArticle.value = article
  editForm.value = {
    title: article.title,
    language: article.language,
    status: article.status,
    content: article.content
  }
}

const cancelEdit = () => {
  editingArticle.value = null
}

const saveEdit = async () => {
  if (!editingArticle.value) return
  try {
    await api.put(`/api/admin/articles/${editingArticle.value.id}`, {
      title: editForm.value.title,
      language: editForm.value.language,
      status: editForm.value.status,
      content: editForm.value.content
    })
    // Refresh lists to reflect changes
    await fetchAllArticles()
    await fetchPendingArticles()
    editingArticle.value = null
    alert('Article updated successfully')
  } catch (error) {
    console.error('Failed to update article:', error)
    alert('Failed to update article')
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

onMounted(() => {
  fetchStats()
  fetchPendingArticles()
  fetchAllArticles()
  fetchUsers()
})

const fetchUserScores = async () => {
  if (!scoreUserId.value.trim()) {
    alert('Enter a User ID (UUID)')
    return
  }
  try {
    const res = await api.get(`/api/scores/user/${scoreUserId.value.trim()}`)
    userScores.value = res.data
  } catch (e) {
    console.error('Failed to fetch user scores', e)
    alert('Failed to fetch user scores')
  }
}

const saveScore = async (row: any) => {
  try {
    savingScoreId.value = row.id
    await api.patch(`/api/scores/${row.id}`, {
      wpm: Number(row.wpm),
      accuracy: Number(row.accuracy)
    })
    alert('Score updated')
  } catch (e: any) {
    console.error('Failed to update score', e)
    alert(e.response?.data?.detail || 'Failed to update score')
  } finally {
    savingScoreId.value = null
  }
}
</script>

<style scoped>
.user-role-controls { display:flex; gap: var(--spacing-3); align-items:center; margin-bottom: var(--spacing-3); }
.admin-page {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-8);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-6);
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-3);
}

.stat-value {
  font-size: var(--font-size-3xl);
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
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Tabs */
.tabs {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-6);
  border-bottom: 2px solid var(--color-border);
}

.tab {
  padding: var(--spacing-3) var(--spacing-6);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.tab:hover {
  color: var(--color-text-primary);
}

.tab-active {
  color: var(--color-brand-600);
  border-bottom-color: var(--color-brand-600);
}

[data-theme="dark"] .tab-active {
  color: var(--color-brand-400);
  border-bottom-color: var(--color-brand-400);
}

/* Content Card */
.content-card h2 {
  margin-bottom: var(--spacing-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
  gap: var(--spacing-4);
}

.card-header h2 {
  margin: 0;
}

.empty-state {
  padding: var(--spacing-12);
  text-align: center;
  color: var(--color-text-secondary);
}

/* Articles List */
.articles-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.article-item {
  padding: var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.article-header h3 {
  margin-bottom: var(--spacing-2);
}

.article-meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-3);
  display: flex;
  gap: var(--spacing-2);
}

.article-preview {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-4);
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

.article-actions {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

/* Table */
.table-container {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table thead {
  background-color: var(--color-surface);
  border-bottom: 2px solid var(--color-border);
}

.admin-table th {
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.admin-table tbody tr {
  border-bottom: 1px solid var(--color-border);
}

.admin-table tbody tr:hover {
  background-color: var(--color-surface);
}

.admin-table td {
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--font-size-sm);
}
.inline-number { width: 6.5rem; padding: 6px 8px; border:1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-background); color: var(--color-text-primary); }
.score-controls { display:flex; gap: var(--spacing-3); align-items:center; margin-bottom: var(--spacing-4); }

.status-badge {
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
}

.status-pending {
  background-color: var(--color-warning);
  color: white;
}

.status-approved {
  background-color: var(--color-success);
  color: white;
}

.status-rejected {
  background-color: var(--color-error);
  color: white;
}

.role-badge {
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
}

.role-admin {
  background-color: var(--color-brand-600);
  color: white;
}

.role-user {
  background-color: var(--color-neutral-200);
  color: var(--color-neutral-800);
}

.table-actions {
  display: flex;
  gap: var(--spacing-2);
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-lg);
  padding: var(--spacing-1);
  transition: transform var(--transition-fast);
}

.icon-btn:hover {
  transform: scale(1.2);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.user-actions { display:flex; align-items:center; gap: var(--spacing-2); }

.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-full);
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-full);
  background-color: var(--color-brand-600);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal);
  padding: var(--spacing-4);
}

.modal-content {
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.modal-meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-4);
  display: flex;
  gap: var(--spacing-2);
}

.modal-content-text {
  padding: var(--spacing-4);
  background-color: var(--color-background);
  border-radius: var(--radius-lg);
  font-family: var(--font-family-mono);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-4);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
  max-height: 60vh;
  overflow: auto;
}

.modal-actions {
  display: flex;
  gap: var(--spacing-2);
  justify-content: flex-end;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.edit-form label {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.select {
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
}

.textarea {
  min-height: 200px;
  padding: var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-family: var(--font-family-mono);
  line-height: var(--line-height-relaxed);
}
</style>
