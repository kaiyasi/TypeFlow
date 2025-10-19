import { ref, computed } from 'vue'

export type LanguageCode = 'en' | 'zh-TW' | 'code'

export interface LanguageOption {
  code: LanguageCode
  name: string
  nativeName: string
  flag: string
  description: string
}

const currentLanguage = ref<LanguageCode>('en')

const languages: Record<LanguageCode, LanguageOption> = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸',
    description: 'English Article Practice'
  },
  'zh-TW': {
    code: 'zh-TW',
    name: 'Traditional Chinese',
    nativeName: '繁體中文',
    flag: '🇹🇼',
    description: 'Traditional Chinese Practice'
  },
  code: {
    code: 'code',
    name: 'Programming',
    nativeName: 'Programming',
    flag: '💻',
    description: 'Programming Practice'
  }
}

const translations = {
  en: {
    // Common
    'common.loading': 'Loading...',
    'common.start': 'Start',
    'common.back': 'Back',
    'common.home': 'Home',
    'common.language': 'Language',
    'common.duration': 'Duration',
    
    // Home page
    'home.title': 'TypeFlow',
    'home.subtitle': 'Advanced Multi-Language Typing Practice',
    'home.description': 'Real-time typing experience with WebSocket-driven instant feedback and comprehensive analytics',
    'home.startPractice': 'Start Practice',
    'home.features': 'Features',
    'home.languages': 'Languages',
    
    // Practice page
    'practice.title': 'Start Your Typing Practice',
    'practice.subtitle': 'Choose language and practice duration to improve your typing skills',
    'practice.chooseLanguage': 'Choose Practice Language',
    'practice.chooseDuration': 'Practice Duration',
    'practice.startButton': 'Start Practice',
    'practice.backHome': 'Return Home',
    'practice.restart': 'Restart',
    'practice.end': 'End Practice',
    
    // Stats
    'stats.time': 'Time',
    'stats.wpm': 'WPM',
    'stats.accuracy': 'Accuracy',
    'stats.errors': 'Errors',
    'stats.words': 'Words',
    'stats.characters': 'Characters',
    
    // Durations
    'duration.quick': 'Quick Practice',
    'duration.standard': 'Standard Practice',
    'duration.medium': 'Medium Practice',
    'duration.long': 'Long Practice'
  },
  'zh-TW': {
    // Common
    'common.loading': '載入中...',
    'common.start': '開始',
    'common.back': '返回',
    'common.home': '首頁',
    'common.language': '語言',
    'common.duration': '時長',
    
    // Home page
    'home.title': 'TypeFlow',
    'home.subtitle': '進階多語言打字練習',
    'home.description': '即時打字體驗，具備 WebSocket 驅動的即時反饋和全面分析',
    'home.startPractice': '開始練習',
    'home.features': '功能特色',
    'home.languages': '支援語言',
    
    // Practice page
    'practice.title': '開始你的打字練習',
    'practice.subtitle': '選擇語言和練習時間，提升你的打字技能',
    'practice.chooseLanguage': '選擇練習語言',
    'practice.chooseDuration': '練習時長',
    'practice.startButton': '開始練習',
    'practice.backHome': '返回首頁',
    'practice.restart': '重新開始',
    'practice.end': '結束練習',
    
    // Stats
    'stats.time': '時間',
    'stats.wpm': '速度',
    'stats.accuracy': '準確率',
    'stats.errors': '錯誤數',
    'stats.words': '單詞',
    'stats.characters': '字符',
    
    // Durations
    'duration.quick': '快速練習',
    'duration.standard': '標準練習',
    'duration.medium': '中等練習',
    'duration.long': '長時間練習'
  },
  code: {
    // Common
    'common.loading': 'Loading...',
    'common.start': 'Start',
    'common.back': 'Back',
    'common.home': 'Home',
    'common.language': 'Language',
    'common.duration': 'Duration',
    
    // Home page
    'home.title': 'TypeFlow',
    'home.subtitle': 'Advanced Programming Practice',
    'home.description': 'Real-time coding experience with syntax highlighting and comprehensive analytics',
    'home.startPractice': 'Start Coding',
    'home.features': 'Features',
    'home.languages': 'Languages',
    
    // Practice page
    'practice.title': 'Start Your Coding Practice',
    'practice.subtitle': 'Choose programming language and practice duration',
    'practice.chooseLanguage': 'Choose Programming Language',
    'practice.chooseDuration': 'Practice Duration',
    'practice.startButton': 'Start Coding',
    'practice.backHome': 'Return Home',
    'practice.restart': 'Restart',
    'practice.end': 'End Session',
    
    // Stats
    'stats.time': 'Time',
    'stats.wpm': 'CPM',
    'stats.accuracy': 'Accuracy',
    'stats.errors': 'Errors',
    'stats.words': 'Lines',
    'stats.characters': 'Characters',
    
    // Durations
    'duration.quick': 'Quick Session',
    'duration.standard': 'Standard Session',
    'duration.medium': 'Medium Session',
    'duration.long': 'Long Session'
  }
}

export function useLanguage() {
  const setLanguage = (lang: LanguageCode) => {
    currentLanguage.value = lang
    localStorage.setItem('typeflow-language', lang)
  }

  const t = (key: string): string => {
    const keys = key.split('.')
    let value: any = translations[currentLanguage.value]
    
    for (const k of keys) {
      value = value?.[k]
    }
    
    return value || key
  }

  const availableLanguages = computed(() => Object.values(languages))
  const currentLang = computed(() => languages[currentLanguage.value])

  // Initialize from localStorage
  const savedLang = localStorage.getItem('typeflow-language') as LanguageCode
  if (savedLang && languages[savedLang]) {
    currentLanguage.value = savedLang
  }

  return {
    currentLanguage: currentLanguage,
    currentLang,
    availableLanguages,
    setLanguage,
    t
  }
}