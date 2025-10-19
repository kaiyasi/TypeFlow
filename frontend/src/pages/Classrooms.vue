<template>
  <div class="classrooms-page">
    <Container size="lg">
      <div class="page-header">
        <h1>Classrooms</h1>
        <p class="subtitle">Manage your classes and students</p>
      </div>

      <Card class="create-card">
        <form class="create-form" @submit.prevent="handleCreate">
          <Input v-model="newName" placeholder="Classroom name (e.g., Class A)" />
          <Button type="submit" :disabled="!newName.trim()" variant="primary">Create Classroom</Button>
        </form>
      </Card>

      <div v-if="loading" class="empty-state">Loading...</div>
      <div v-else-if="classrooms.length === 0" class="empty-state">
        <p>No classrooms yet. Create one above.</p>
      </div>
      <div v-else class="grid">
        <Card v-for="c in classrooms" :key="c.id" class="classroom-card" hoverable>
          <div class="feature-accent"></div>
          <h3 class="title">{{ c.name }}</h3>
          <p class="desc">Click Manage to add students and view scores.</p>
          <div class="actions">
            <Button variant="secondary" @click="goDetail(c.id)">Manage</Button>
          </div>
        </Card>
      </div>
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

interface Classroom { id: string; name: string; organization_id: string }

const router = useRouter()
const classrooms = ref<Classroom[]>([])
const loading = ref(false)
const newName = ref('')

const fetchClassrooms = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/classrooms')
    classrooms.value = res.data
  } catch (e) {
    console.error('Failed to load classrooms', e)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!newName.value.trim()) return
  try {
    await api.post('/api/classrooms', { name: newName.value.trim() })
    newName.value = ''
    fetchClassrooms()
  } catch (e) {
    console.error('Failed to create classroom', e)
    alert('Failed to create classroom')
  }
}

const goDetail = (id: string) => {
  router.push(`/classrooms/${id}`)
}

onMounted(() => fetchClassrooms())
</script>

<style scoped>
.classrooms-page { padding: var(--spacing-8) 0; }
.page-header { text-align: center; margin-bottom: var(--spacing-8); }
.subtitle { color: var(--color-text-secondary); }

.create-card { margin-bottom: var(--spacing-6); }
.create-form { display: flex; gap: var(--spacing-3); align-items: center; }

.empty-state { text-align: center; color: var(--color-text-secondary); padding: var(--spacing-8); }

.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: var(--spacing-6); }
.classroom-card { position: relative; padding: var(--spacing-6); }
.classroom-card .feature-accent { position: absolute; top: 0; left: 0; right: 0; height: 6px; background: linear-gradient(90deg, transparent, var(--color-brand-300), var(--color-brand-500), transparent); }
.title { font-size: var(--font-size-xl); margin-bottom: var(--spacing-2); }
.desc { color: var(--color-text-secondary); margin-bottom: var(--spacing-4); }
.actions { display:flex; justify-content:flex-end; }
</style>

