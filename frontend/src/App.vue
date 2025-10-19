<template>
  <div class="app">
    <Header />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import { useUserStore } from '@/store/user'
import { useConfigStore } from '@/store/config'
import { applyTheme, getInitialTheme } from '@/config/theme.config'
import { setAppMeta, setHtmlLang } from '@/utils/meta'

const userStore = useUserStore()
const configStore = useConfigStore()

onMounted(async () => {
  // Initialize theme
  const initialTheme = getInitialTheme()
  applyTheme(initialTheme)

  // Initialize locale
  const savedLocale = localStorage.getItem('typeflow-locale')
  if (savedLocale) {
    // The locale will be handled by i18n plugin
  }

  // Load app data
  await Promise.all([
    configStore.fetchConfig(),
    userStore.checkAuth()
  ])

  // Set dynamic meta and html lang based on current locale
  const { t, locale } = useI18n()
  setAppMeta(t('meta.title'), t('meta.description'))
  setHtmlLang(locale.value)

  // Watch locale changes to update meta and lang
  watch(() => locale.value, (val) => {
    setAppMeta(t('meta.title'), t('meta.description'))
    setHtmlLang(val)
  })
})
</script>

<style>
@import './styles/global.css';

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base), transform var(--transition-base);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
