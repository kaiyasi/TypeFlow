import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/store/user'

describe('User Store', () => {
  beforeEach(() => {
    // 建立新的 Pinia 實例
    setActivePinia(createPinia())
    // 清理 localStorage
    localStorage.clear()
  })

  describe('初始狀態', () => {
    it('應該未登入', () => {
      const store = useUserStore()
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
    })

    it('應該不是管理員', () => {
      const store = useUserStore()
      expect(store.isAdmin).toBe(false)
    })
  })

  describe('用戶登入', () => {
    it('登入後應更新用戶狀態', () => {
      const store = useUserStore()
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        display_name: 'Test User',
        role: 'user'
      }
      
      store.setUser(mockUser)
      
      expect(store.isAuthenticated).toBe(true)
      expect(store.user).toEqual(mockUser)
    })

    it('應該保存 token', () => {
      const store = useUserStore()
      const token = 'test-jwt-token'
      
      store.setToken(token)
      
      expect(store.token).toBe(token)
      expect(localStorage.getItem('token')).toBe(token)
    })

    it('管理員用戶應該被識別', () => {
      const store = useUserStore()
      const adminUser = {
        id: '456',
        email: 'admin@example.com',
        display_name: 'Admin User',
        role: 'super_admin'
      }
      
      store.setUser(adminUser)
      
      expect(store.isAdmin).toBe(true)
    })
  })

  describe('用戶登出', () => {
    it('登出應清除用戶狀態', () => {
      const store = useUserStore()
      
      // 先登入
      store.setUser({
        id: '123',
        email: 'test@example.com',
        display_name: 'Test User',
        role: 'user'
      })
      store.setToken('test-token')
      
      // 登出
      store.logout()
      
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(localStorage.getItem('token')).toBeNull()
    })
  })

  describe('狀態持久化', () => {
    it('應該從 localStorage 恢復用戶狀態', () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        display_name: 'Test User',
        role: 'user'
      }
      
      localStorage.setItem('user', JSON.stringify(mockUser))
      localStorage.setItem('token', 'test-token')
      
      const store = useUserStore()
      store.loadFromStorage()
      
      expect(store.isAuthenticated).toBe(true)
      expect(store.user).toEqual(mockUser)
      expect(store.token).toBe('test-token')
    })
  })
})

