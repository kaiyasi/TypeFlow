<template>
  <div class="submit-page">
    <Container size="md">
      <!-- Header -->
      <div class="page-header">
        <h1>{{ t('submit.title') }}</h1>
        <p class="subtitle">{{ t('submit.subtitle') }}</p>
      </div>

      <!-- Submit Form -->
      <Card class="submit-form">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <Input
              v-model="form.title"
              :label="t('submit.form.title')"
              :placeholder="t('submit.placeholders.title')"
              required
              :error="errors.title"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">{{ t('submit.form.language') }}</label>
              <select v-model="form.language" class="form-select" required>
                <option value="">{{ t('submit.form.language') }}</option>
                <option value="en">English</option>
                <option value="zh-TW">繁體中文</option>
                <option value="zh-CN">简体中文</option>
                <option value="ja">日本語</option>
                <option value="ko">한국어</option>
                <option value="de">Deutsch</option>
                <option value="ru">Русский</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
                <option value="it">Italiano</option>
                <option value="pt">Português</option>
                <option value="vi">Tiếng Việt</option>
                <option value="code">Code</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">{{ t('submit.form.difficulty') }}</label>
              <select v-model="form.difficulty" class="form-select" required>
                <option value="">{{ t('submit.form.difficulty') }}</option>
                <option value="easy">{{ t('submit.difficulty.easy') }}</option>
                <option value="medium">{{ t('submit.difficulty.medium') }}</option>
                <option value="hard">{{ t('submit.difficulty.hard') }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">
              {{ t('submit.form.content') }}
              <span class="char-count">{{ form.content.length }} / {{ minLength }} {{ t('submit.common.characters') }}</span>
            </label>
            <textarea
              v-model="form.content"
              class="form-textarea"
              :placeholder="t('submit.placeholders.content')"
              rows="12"
              required
              :class="{ 'has-error': errors.content }"
            ></textarea>
            <p v-if="errors.content" class="error-message">{{ errors.content }}</p>
            <p v-else class="hint-text">{{ t('submit.common.minimum') }} {{ minLength }} {{ t('submit.common.characters') }}</p>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.isPublic" class="checkbox" />
              <span>{{ t('submit.common.public') }}</span>
            </label>
          </div>

          <div class="form-actions">
            <Button type="submit" variant="primary" size="lg" :loading="submitting">
              {{ t('submit.buttons.submit') }}
            </Button>
            <Button type="button" variant="ghost" size="lg" @click="resetForm">
              {{ t('common.delete') }}
            </Button>
          </div>
        </form>
      </Card>

      <!-- My Submissions -->
      <Card v-if="mySubmissions.length > 0" class="my-submissions">
        <h2>{{ t('submit.common.mySubmissions') }}</h2>
        <div class="submissions-list">
          <div v-for="submission in mySubmissions" :key="submission.id" class="submission-item">
            <div class="submission-header">
              <h3>{{ submission.title }}</h3>
              <span :class="'status-badge status-' + submission.status">
                {{ submission.status }}
              </span>
            </div>
            <div class="submission-meta">
              <span>{{ submission.language }}</span>
              <span>•</span>
              <span>{{ submission.difficulty }}</span>
              <span>•</span>
              <span>{{ formatDate(submission.created_at) }}</span>
            </div>
            <p class="submission-preview">{{ submission.content?.substring(0, 150) || '' }}{{ submission.content && submission.content.length > 150 ? '...' : '' }}</p>
          </div>
        </div>
      </Card>
    </Container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Container from '@/components/layout/Container.vue'
import Card from '@/components/ui/Card.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import api from '@/api'

interface SubmissionForm {
  title: string
  language: string
  difficulty: string
  content: string
  isPublic: boolean
}

interface Submission {
  id: number
  title: string
  language: string
  difficulty: string
  content: string
  status: string
  created_at: string
}

const router = useRouter()

const minLength = 200

const form = ref<SubmissionForm>({
  title: '',
  language: '',
  difficulty: '',
  content: '',
  isPublic: true
})

const errors = ref({
  title: '',
  content: ''
})

const submitting = ref(false)
const mySubmissions = ref<Submission[]>([])

const validateForm = (): boolean => {
  errors.value = { title: '', content: '' }
  let isValid = true

  if (form.value.title.length < 3) {
    errors.value.title = 'Title must be at least 3 characters'
    isValid = false
  }

  if (form.value.content.length < minLength) {
    errors.value.content = `Content must be at least ${minLength} characters`
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  submitting.value = true
  try {
    await api.post('/api/articles/', {
      title: form.value.title,
      language: form.value.language, // Send as-is: "en", "zh-TW", "code"
      content: form.value.content,
      source: form.value.isPublic ? 'public' : 'private',
      status: 'submitted' // Will be handled by backend based on user role
    })

    alert('Article submitted successfully!')
    resetForm()
    fetchMySubmissions()
  } catch (error: any) {
    console.error('Failed to submit article:', error)
    alert(error.response?.data?.detail || 'Failed to submit article')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  form.value = {
    title: '',
    language: '',
    difficulty: '',
    content: '',
    isPublic: true
  }
  errors.value = { title: '', content: '' }
}

const fetchMySubmissions = async () => {
  try {
    // Fetch without status filter - will get published articles by default
    // For admins, they can see all articles
    const response = await api.get('/api/articles/', {
      params: {
        per_page: 100
      }
    })
    // Note: This will only show published articles for regular users
    // Admins can see all articles through the admin panel
    mySubmissions.value = response.data.articles || []
  } catch (error) {
    console.error('Failed to fetch submissions:', error)
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

onMounted(() => {
  fetchMySubmissions()
})
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<style scoped>
.submit-page {
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

/* Form */
.submit-form {
  margin-bottom: var(--spacing-8);
}

.form-group {
  margin-bottom: var(--spacing-6);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

.form-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.char-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  font-weight: var(--font-weight-normal);
}

.form-select,
.form-textarea {
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background-color: var(--color-background);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: inherit;
  transition: all var(--transition-fast);
}

.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-brand-500);
  box-shadow: 0 0 0 3px var(--color-brand-100);
}

[data-theme="dark"] .form-select:focus,
[data-theme="dark"] .form-textarea:focus {
  box-shadow: 0 0 0 3px var(--color-brand-900);
}

.form-textarea {
  resize: vertical;
  font-family: var(--font-family-mono);
  line-height: var(--line-height-relaxed);
}

.form-textarea.has-error {
  border-color: var(--color-error);
}

.error-message {
  margin-top: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-error);
}

.hint-text {
  margin-top: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-base);
  cursor: pointer;
}

.checkbox {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: var(--spacing-4);
  justify-content: flex-start;
}

/* My Submissions */
.my-submissions h2 {
  margin-bottom: var(--spacing-6);
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.submission-item {
  padding: var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.submission-item:hover {
  border-color: var(--color-brand-400);
  background-color: var(--color-surface);
}

.submission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.submission-header h3 {
  font-size: var(--font-size-lg);
}

.status-badge {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
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

.submission-meta {
  display: flex;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-3);
}

.submission-preview {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}
</style>
