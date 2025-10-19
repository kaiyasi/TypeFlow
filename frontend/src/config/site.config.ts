/**
 * Site Configuration
 * Centralized configuration for the TypeFlow application
 */

export interface SiteConfig {
  name: string
  tagline: string
  description: string
  url: string
  logo: string
  favicon?: string
  author: {
    name: string
    email: string
  }
  social: {
    github?: string
    twitter?: string
  }
  features: {
    practice: boolean
    leaderboard: boolean
    submit: boolean
    admin: boolean
  }
}

export const siteConfig: SiteConfig = {
  name: 'TypeFlow',
  tagline: 'Master Your Typing Skills',
  description: 'A modern typing practice platform for improving your typing speed and accuracy',
  url: process.env.VITE_APP_URL || 'http://localhost:5173',
  // Primary logo - new design with mountain background
  logo: '/logo.png',
  // Favicon shown in browser tab
  favicon: '/logo.png',
  author: {
    name: 'TypeFlow',
    email: 'hello@typeflow.dev'
  },
  social: {
    github: 'https://github.com/kaiyasi/TypeFlow'
  },
  features: {
    practice: true,
    leaderboard: true,
    submit: true,
    admin: true
  }
}
