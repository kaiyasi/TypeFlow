/**
 * Theme Configuration
 * Controls theme behavior and customization
 */

export type ThemeMode = 'light' | 'dark' | 'system'

export interface ThemeConfig {
  defaultMode: ThemeMode
  storageKey: string
}

export const themeConfig: ThemeConfig = {
  defaultMode: 'system',
  storageKey: 'typeflow-theme'
}

export const getInitialTheme = (): ThemeMode => {
  if (typeof window === 'undefined') return themeConfig.defaultMode

  const stored = localStorage.getItem(themeConfig.storageKey) as ThemeMode | null
  if (stored && ['light', 'dark', 'system'].includes(stored)) {
    return stored
  }

  return themeConfig.defaultMode
}

export const resolveTheme = (mode: ThemeMode): 'light' | 'dark' => {
  if (mode === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return mode
}

export const applyTheme = (mode: ThemeMode) => {
  const resolved = resolveTheme(mode)
  document.documentElement.setAttribute('data-theme', resolved)
  localStorage.setItem(themeConfig.storageKey, mode)
}
