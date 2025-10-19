import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import { siteConfig } from './config/site.config'

// Import language files
import enMessages from './i18n/en.json'
import zhTWMessages from './i18n/zh-TW.json'

// Create Vue I18n instance
const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('typeflow-locale') || 'en',
  fallbackLocale: 'en',
  messages: {
    en: enMessages,
    'zh-TW': zhTWMessages,
  },
})

// Create Pinia instance
const pinia = createPinia()

// Create and mount Vue app
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(i18n)

app.mount('#app')

// Dynamically set favicon and app icons after app mounts
const applyIcons = () => {
  const version = Date.now().toString() // cache buster to avoid stale icons
  const iconHref = (siteConfig.favicon || siteConfig.logo || '/logo.png') + `?v=${version}`

  const ensureLink = (rel: string, sizes?: string, type?: string) => {
    let link = document.querySelector(`link[rel='${rel}']${sizes ? `[sizes='${sizes}']` : ''}`) as HTMLLinkElement | null
    if (!link) {
      link = document.createElement('link')
      link.rel = rel
      if (sizes) link.sizes = sizes
      if (type) link.type = type
      document.head.appendChild(link)
    }
    return link
  }

  // Standard favicon (SVG or PNG)
  const favicon = ensureLink('icon')
  favicon.href = iconHref

  // 32x32 PNG fallback
  const favicon32 = ensureLink('icon', '32x32', 'image/png')
  favicon32.href = '/favicon-32x32.png?v=' + version

  // 16x16 PNG fallback
  const favicon16 = ensureLink('icon', '16x16', 'image/png')
  favicon16.href = '/favicon-16x16.png?v=' + version

  // Apple touch icon
  const appleTouch = ensureLink('apple-touch-icon')
  appleTouch.href = '/apple-touch-icon.png?v=' + version
}

applyIcons()
