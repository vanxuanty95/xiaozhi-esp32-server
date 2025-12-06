import { ref } from 'vue'
import { defineStore } from 'pinia'

// Supported language types
export type Language = 'zh_CN' | 'en' | 'zh_TW' | 'de' | 'vi'

export interface LangStore {
  currentLang: Language
  changeLang: (lang: Language) => void
}

export const useLangStore = defineStore(
  'lang',
  (): LangStore => {
    // Get language setting from local storage, use default if not found
    const savedLang = uni.getStorageSync('app_language') as Language | null
    const currentLang = ref<Language>(savedLang || 'zh_CN')

    // Change language
    const changeLang = (lang: Language) => {
      currentLang.value = lang
      // Save language setting to local storage
      uni.setStorageSync('app_language', lang)
    }

    return {
      currentLang,
      changeLang,
    }
  },
  {
    persist: {
      key: 'lang',
      serializer: {
        serialize: state => JSON.stringify(state.currentLang),
        deserialize: value => ({ currentLang: JSON.parse(value) }),
      },
    },
  },
)