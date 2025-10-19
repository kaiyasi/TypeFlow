/**
 * Navigation Configuration
 * Defines navigation structure for the application
 */

export interface NavItem {
  label: string
  path: string
  icon?: string
  requiresAuth?: boolean
  requiresAdmin?: boolean
  requiresOrgAdmin?: boolean
}

export const mainNav: NavItem[] = [
  {
    label: 'Practice',
    path: '/practice',
    icon: 'keyboard'
  },
  {
    label: 'Leaderboard',
    path: '/leaderboard',
    icon: 'trophy'
  },
  {
    label: 'Submit',
    path: '/submit',
    icon: 'upload',
    requiresAuth: true
  }
]

export const userNav: NavItem[] = [
  {
    label: 'Admin',
    path: '/admin',
    icon: 'shield',
    requiresAdmin: true
  }
]
