import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/index'

import { useConfigStore } from './config'

export interface User {
  id: string
  display_name: string
  email?: string
  guest_id?: string
  role: 'user' | 'org_admin' | 'super_admin'
  auth_provider: 'google' | 'guest'
}

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => user.value !== null)
  const isAdmin = computed(() => user.value?.role === 'super_admin')
  const isOrgAdmin = computed(() => 
    user.value?.role === 'org_admin' || user.value?.role === 'super_admin'
  )
  const isGuest = computed(() => user.value?.auth_provider === 'guest')

  // Actions
  const checkAuth = async () => {
    try {
      loading.value = true
      const response = await apiClient.get('/api/auth/me', {
        withCredentials: true
      })
      user.value = response.data.user
    } catch (err) {
      // User not authenticated
      user.value = null
    } finally {
      loading.value = false
    }
  }

  const loginAsGuest = async (displayName: string) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiClient.post('/api/auth/guest', {
        display_name: displayName,
        user_agent: navigator.userAgent
      }, {
        withCredentials: true
      })
      
      user.value = response.data.user
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Guest login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      loading.value = true
      await apiClient.post('/api/auth/logout', {}, {
        withCredentials: true
      })
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      loading.value = false
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiClient.patch('/api/auth/profile', data, {
        withCredentials: true
      })
      
      user.value = response.data.user
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Profile update failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const redirectToGoogle = async () => {
    const configStore = useConfigStore()
    
    // Ensure config is loaded
    if (!configStore.config) {
      try {
        console.log('Config not loaded, fetching...')
        await configStore.fetchConfig()
        console.log('Config fetched:', configStore.config)
      } catch (err) {
        console.error('Failed to fetch config:', err)
        alert('Failed to load application configuration. Please try again later.');
        return;
      }
    }
    
    const googleClientId = configStore.config?.google_client_id
    console.log('Google Client ID from config:', googleClientId)

    if (!googleClientId) {
      console.error('No Google Client ID found in config:', configStore.config)
      alert('Google Client ID is not configured in the backend. Please contact the administrator.');
      return;
    }

    const redirectUri = `${window.location.origin}/auth/callback`;
    // Use the full scope URLs that Google expects
    const scope = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid';
    const responseType = 'code';

    // Properly encode the redirect URI and scope
    const encodedRedirectUri = encodeURIComponent(redirectUri);
    const encodedScope = encodeURIComponent(scope);

    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${encodedRedirectUri}&scope=${encodedScope}&response_type=${responseType}&access_type=offline&prompt=consent`;

    console.log('Redirecting to Google OAuth:', authUrl)
    window.location.href = authUrl;
  }

  const handleGoogleCallback = async (code: string) => {
    try {
      loading.value = true;
      error.value = null;

      const response = await apiClient.post('/api/auth/google/callback', {
        code: code,
      }, {
        withCredentials: true
      });

      user.value = response.data.user;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Google authentication failed';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    // State
    user,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    isOrgAdmin,
    isGuest,
    
    // Actions
    checkAuth,
    loginAsGuest,
    logout,
    updateProfile,
    redirectToGoogle,
    handleGoogleCallback
  }
})