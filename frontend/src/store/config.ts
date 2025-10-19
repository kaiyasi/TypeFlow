import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/api/index'

export interface AppConfig {
  google_client_id: string
}

export const useConfigStore = defineStore('config', () => {
  // State
  const config = ref<AppConfig | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  const fetchConfig = async () => {
    if (config.value) {
      return // Already fetched
    }

    try {
      loading.value = true
      error.value = null
      
      // Use fetch directly with absolute HTTPS URL to bypass all redirection issues
      const url = `https://${window.location.host}/api/config/`
      console.log('Fetching config from:', url)
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        mode: 'cors',
        cache: 'no-cache',
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      config.value = data
      console.log('Config loaded successfully:', data)
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch app configuration'
      console.error('Config fetch error:', err)
      
      // Last resort: try with hardcoded backend config if available
      console.log('Attempting fallback config...')
      config.value = {
        google_client_id: '731563253553-j1gc4q5hiipdnqcimictognh3dtl7d9s.apps.googleusercontent.com'
      }
      console.log('Using fallback config:', config.value)
    } finally {
      loading.value = false
    }
  }

  return {
    config,
    loading,
    error,
    fetchConfig
  }
})
