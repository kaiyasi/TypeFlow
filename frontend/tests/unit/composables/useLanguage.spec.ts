import { describe, it, expect, beforeEach } from 'vitest'
import { useLanguage } from '@/composables/useLanguage'

describe('useLanguage', () => {
  beforeEach(() => {
    // 清理 localStorage
    localStorage.clear()
  })

  it('應該初始化為繁體中文', () => {
    const { locale } = useLanguage()
    expect(locale.value).toBe('zh-TW')
  })

  it('應該能切換語言', () => {
    const { locale, setLocale } = useLanguage()
    
    setLocale('en')
    expect(locale.value).toBe('en')
    
    setLocale('zh-TW')
    expect(locale.value).toBe('zh-TW')
  })

  it('應該持久化語言選擇到 localStorage', () => {
    const { setLocale } = useLanguage()
    
    setLocale('en')
    expect(localStorage.getItem('locale')).toBe('en')
  })

  it('應該從 localStorage 恢復語言設定', () => {
    localStorage.setItem('locale', 'en')
    
    const { locale } = useLanguage()
    expect(locale.value).toBe('en')
  })

  it('應該只接受有效的語言代碼', () => {
    const { locale, setLocale } = useLanguage()
    const validLocales = ['en', 'zh-TW']
    
    // 測試有效語言
    setLocale('en')
    expect(validLocales.includes(locale.value)).toBe(true)
    
    // 測試無效語言（應該保持當前語言）
    const currentLocale = locale.value
    setLocale('invalid-locale' as any)
    expect(locale.value).toBe(currentLocale)
  })
})

