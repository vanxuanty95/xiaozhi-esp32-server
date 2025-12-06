import { VueQueryPlugin } from '@tanstack/vue-query'
import { createSSRApp } from 'vue'
import App from './App.vue'
import { routeInterceptor } from './router/interceptor'

import store from './store'
import '@/style/index.scss'
import 'virtual:uno.css'

// Import internationalization related functionality
import { initI18n } from './i18n'
import { useLangStore } from './store/lang'

export function createApp() {
  const app = createSSRApp(App)
  app.use(store)
  app.use(routeInterceptor)
  app.use(VueQueryPlugin)

  // Initialize internationalization
  initI18n()

  return {
    app,
  }
}
