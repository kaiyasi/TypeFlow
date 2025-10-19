<template>
  <header class="header">
    <div class="container header-container">
      <!-- Logo -->
      <router-link to="/" class="logo">
        <img v-if="siteConfig.logo" :src="siteConfig.logo + '?v=' + Date.now()" alt="Logo" class="logo-image" @error="function(e){ e && e.target && (e.target.src = '/logo.svg?v=' + Date.now()) }" />
        <span class="logo-text">{{ siteConfig.name }}</span>
      </router-link>

      <!-- Desktop Navigation -->
      <nav class="nav-desktop">
        <router-link
          v-for="item in visibleNavItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          active-class="nav-link-active"
        >
          {{ t(`nav.${item.label.toLowerCase()}`) }}
        </router-link>
      </nav>

      <!-- Actions -->
      <div class="header-actions">
        <!-- Theme Toggle -->
        <button class="icon-button" @click="toggleTheme" aria-label="Toggle theme">
          <svg
            v-if="theme === 'light'"
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
        </button>

        <!-- Language Selector -->
        <div class="language-selector">
          <button class="icon-button" @click="toggleLanguageMenu" aria-label="Change language">
            {{ currentLocaleLabel }}
          </button>
          <div v-if="showLanguageMenu" class="dropdown-menu">
            <button @click="changeLanguage('en')" class="dropdown-item">English</button>
            <button @click="changeLanguage('zh-TW')" class="dropdown-item">繁體中文</button>
          </div>
        </div>

        <!-- User Menu -->
        <div v-if="userStore.isAuthenticated" class="user-menu">
          <button class="user-avatar" @click="toggleUserMenu" aria-label="User menu">
            <img
              v-if="userStore.user?.picture"
              :src="userStore.user.picture"
              :alt="userStore.user.display_name"
            />
            <span v-else>{{ userStore.user?.display_name?.charAt(0).toUpperCase() }}</span>
          </button>
          <div v-if="showUserMenu" class="dropdown-menu">
            <div class="user-info">
              <div class="user-name">{{ userStore.user?.display_name }}</div>
              <div class="user-email">{{ userStore.user?.email }}</div>
            </div>
            <div class="dropdown-divider"></div>
            <router-link to="/group" class="dropdown-item">{{ t('nav.group') }}</router-link>
            <router-link v-if="userStore.isAdmin" to="/admin" class="dropdown-item">
              {{ t('nav.admin') }}
            </router-link>
            <button @click="handleLogout" class="dropdown-item logout">
              {{ t('nav.logout') }}
            </button>
          </div>
        </div>
        <Button v-else @click="handleLogin" variant="primary" size="sm">
          {{ t('nav.login') }}
        </Button>

        <!-- Mobile Menu Toggle -->
        <button class="mobile-menu-toggle" @click="toggleMobileMenu" aria-label="Toggle menu">
          <svg
            v-if="!showMobileMenu"
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div v-if="showMobileMenu" class="nav-mobile">
      <router-link
        v-for="item in visibleNavItems"
        :key="item.path"
        :to="item.path"
        class="nav-mobile-link"
        @click="showMobileMenu = false"
      >
        {{ t(`nav.${item.label.toLowerCase()}`) }}
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { mainNav } from '@/config/nav.config'
import { siteConfig } from '@/config/site.config'
import { applyTheme, getInitialTheme, resolveTheme, type ThemeMode } from '@/config/theme.config'
import { useUserStore } from '@/store/user'
import Button from '@/components/ui/Button.vue'

const { t, locale } = useI18n()
const userStore = useUserStore()

const theme = ref<'light' | 'dark'>('light')
const showLanguageMenu = ref(false)
const showUserMenu = ref(false)
const showMobileMenu = ref(false)

const currentLocale = computed(() => locale.value)
const currentLocaleLabel = computed(() => {
  if (locale.value === 'zh-TW') return '繁體中文'
  if (locale.value === 'en') return 'English'
  return locale.value
})

const visibleNavItems = computed(() => {
  return mainNav.filter(item => {
    if (item.requiresAuth && !userStore.isAuthenticated) return false
    if (item.requiresAdmin && !userStore.isAdmin) return false
    if (item.requiresOrgAdmin && !userStore.isOrgAdmin) return false
    return true
  })
})

const toggleTheme = () => {
  const newTheme: ThemeMode = theme.value === 'light' ? 'dark' : 'light'
  applyTheme(newTheme)
  theme.value = resolveTheme(newTheme)
}

const toggleLanguageMenu = () => {
  showLanguageMenu.value = !showLanguageMenu.value
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showLanguageMenu.value = false
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const changeLanguage = (lang: string) => {
  locale.value = lang
  localStorage.setItem('typeflow-locale', lang)
  showLanguageMenu.value = false
}

const handleLogin = () => {
  userStore.redirectToGoogle()
}

const handleLogout = () => {
  userStore.logout()
  showUserMenu.value = false
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.language-selector')) {
    showLanguageMenu.value = false
  }
  if (!target.closest('.user-menu')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  const initialTheme = getInitialTheme()
  theme.value = resolveTheme(initialTheme)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: var(--z-index-sticky);
  background-color: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  gap: var(--spacing-4);
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  text-decoration: none;
  color: var(--color-text-primary);
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-xl);
  transition: opacity var(--transition-fast);
}

.logo:hover {
  opacity: 0.8;
}

.logo-image {
  height: 2rem;
  width: auto;
}

.logo-text {
  background: linear-gradient(135deg, var(--color-brand-600), var(--color-brand-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Desktop Navigation */
.nav-desktop {
  display: none;
  align-items: center;
  gap: var(--spacing-2);
}

@media (min-width: 768px) {
  .nav-desktop {
    display: flex;
  }
}

.nav-link {
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-text-primary);
  background-color: var(--color-surface);
}

.nav-link-active {
  color: var(--color-brand-600);
  background-color: var(--color-brand-50);
}

[data-theme="dark"] .nav-link-active {
  color: var(--color-brand-400);
  background-color: var(--color-brand-900);
}

/* Header Actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  border-radius: var(--radius-lg);
  background-color: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-button:hover {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
}

/* Language Selector */
.language-selector {
  position: relative;
}

.language-selector .icon-button {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  width: auto;               /* allow text width */
  padding: 0 var(--spacing-3);
  white-space: nowrap;       /* prevent wrap */
}

/* User Menu */
.user-menu {
  position: relative;
}

.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius-full);
  border: 2px solid var(--color-border);
  background-color: var(--color-brand-600);
  color: white;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-avatar:hover {
  border-color: var(--color-brand-500);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + var(--spacing-2));
  right: 0;
  min-width: 12rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-2);
  z-index: var(--z-index-dropdown);
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  border: none;
  border-radius: var(--radius-lg);
  background-color: transparent;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dropdown-item:hover {
  background-color: var(--color-neutral-100);
}

[data-theme="dark"] .dropdown-item:hover {
  background-color: var(--color-neutral-800);
}

.dropdown-item.logout {
  color: var(--color-error);
}

.dropdown-item.logout:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--color-border);
  margin: var(--spacing-2) 0;
}

.user-info {
  padding: var(--spacing-3) var(--spacing-4);
}

.user-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.user-email {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-1);
}

/* Mobile Menu */
.mobile-menu-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  border-radius: var(--radius-lg);
  background-color: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
}

@media (min-width: 768px) {
  .mobile-menu-toggle {
    display: none;
  }
}

.nav-mobile {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  padding: var(--spacing-4);
  border-top: 1px solid var(--color-border);
}

.nav-mobile-link {
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.nav-mobile-link:hover {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
}
</style>
