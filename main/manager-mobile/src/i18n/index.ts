import { ref } from 'vue'
import { useLangStore } from '@/store/lang'
import type { Language } from '@/store/lang'

// Import translation files for each language
import zh_CN from './zh_CN'
import en from './en'
import zh_TW from './zh_TW'
import de from './de'
import vi from './vi'

// Language pack mapping
const messages = {
  zh_CN: zh_CN,
  en,
  zh_TW: zh_TW,
  de,
  vi,
}

// Currently used language
const currentLang = ref<Language>('zh_CN')

// Initialize language
export function initI18n() {
  const langStore = useLangStore()
  currentLang.value = langStore.currentLang
}

// Change language
export function changeLanguage(lang: Language) {
  currentLang.value = lang
  const langStore = useLangStore()
  langStore.changeLang(lang)
}

// Get translation text
export function t(key: string, params?: Record<string, string | number>): string {
  const langMessages = messages[currentLang.value]

  // Directly search for flat key name
  if (langMessages && typeof langMessages === 'object' && key in langMessages) {
    let value = langMessages[key]
    if (typeof value === 'string') {
      // Handle parameter replacement
      if (params) {
        let result = value
        Object.entries(params).forEach(([paramKey, paramValue]) => {
          const regex = new RegExp(`\{${paramKey}\}`, 'g')
          result = result.replace(regex, String(paramValue))
        })
        return result
      }
      return value
    }
    return key
  }

  return key // If corresponding translation not found, return key itself
}

// Get current language
export function getCurrentLanguage(): Language {
  return currentLang.value
}

// Get supported language list
export function getSupportedLanguages(): { code: Language, name: string }[] {
  return [
    { code: 'zh_CN', name: 'Simplified Chinese' },
    { code: 'en', name: 'English' },
    { code: 'zh_TW', name: 'Traditional Chinese' },
    { code: 'de', name: 'Deutsch' },
    { code: 'vi', name: 'Tiếng Việt' },
  ]
}