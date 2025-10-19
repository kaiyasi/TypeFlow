import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/pages/Home.vue'),
      meta: { title: 'TypeFlow - Advanced Multi-Language Typing Practice' }
    },
    {
      path: '/group',
      name: 'Group',
      component: () => import('@/pages/Group.vue'),
      meta: { title: 'Group - TypeFlow', requiresAuth: true }
    },
    {
      path: '/classrooms',
      name: 'Classrooms',
      component: () => import('@/pages/Classrooms.vue'),
      meta: {
        title: 'Classrooms - TypeFlow',
        requiresAuth: true,
        requiresOrgAdmin: true
      }
    },
    {
      path: '/classrooms/:id',
      name: 'ClassroomDetail',
      component: () => import('@/pages/ClassroomDetail.vue'),
      meta: {
        title: 'Classroom - TypeFlow',
        requiresAuth: true,
        requiresOrgAdmin: true
      }
    },
    {
      path: '/practice',
      name: 'Practice',
      component: () => import('@/pages/Practice.vue'),
      meta: { title: 'Practice - TypeFlow' }
    },
    {
      path: '/leaderboard',
      name: 'Leaderboard',
      component: () => import('@/pages/Leaderboard.vue'),
      meta: { title: 'Leaderboard - TypeFlow' }
    },
    {
      path: '/submit',
      name: 'Submit',
      component: () => import('@/pages/Submit.vue'),
      meta: {
        title: 'Submit Article - TypeFlow',
        requiresAuth: true
      }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('@/pages/Admin.vue'),
      meta: { 
        title: 'Admin - TypeFlow',
        requiresAuth: true,
        requiresAdmin: true
      }
    },
    {
      path: '/auth/callback',
      name: 'AuthCallback',
      component: () => import('@/pages/AuthCallback.vue'),
      meta: { title: 'Authenticating... - TypeFlow' }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/pages/NotFound.vue'),
      meta: { title: 'Page Not Found - TypeFlow' }
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // Set page title
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  
  // Check authentication requirements
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      // Redirect to home with login prompt
      next({ name: 'Home', query: { login: 'required' } })
      return
    }
  }
  
  // Check admin requirements
  if (to.meta.requiresAdmin) {
    if (!userStore.isAdmin) {
      // Redirect to home
      next({ name: 'Home' })
      return
    }
  }

  // Check org admin (teacher) requirements
  if ((to.meta as any).requiresOrgAdmin) {
    if (!userStore.isOrgAdmin) {
      next({ name: 'Home' })
      return
    }
  }
  
  next()
})

export default router
