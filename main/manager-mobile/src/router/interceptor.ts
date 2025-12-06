/**
 * by Feige on 2024-03-06
 * Route interceptor, usually also login interceptor
 * Can set route whitelist or blacklist, choose based on business needs
 * Here most pages can be accessed freely, so using blacklist
 */
import { useUserStore } from '@/store'
import { needLoginPages as _needLoginPages, getLastPage, getNeedLoginPages } from '@/utils'

// TODO Check
const loginRoute = import.meta.env.VITE_LOGIN_URL

function isLogined() {
  const userStore = useUserStore()
  return !!userStore.userInfo.username
}

const isDev = import.meta.env.DEV

// Blacklist login interceptor - (suitable for most pages don't need login, few pages need login)
const navigateToInterceptor = {
  // Note: URL here starts with '/', like '/pages/index/index', different from 'path' in 'pages.json'
  // Added relative path handling, BY netizen @ideal
  invoke({ url }: { url: string }) {
    // console.log(url) // /pages/route-interceptor/index?name=feige&age=30
    let path = url.split('?')[0]
    console.log('Page changed')

    // Handle relative path
    if (!path.startsWith('/')) {
      const currentPath = getLastPage().route
      const normalizedCurrentPath = currentPath.startsWith('/') ? currentPath : `/${currentPath}`
      const baseDir = normalizedCurrentPath.substring(0, normalizedCurrentPath.lastIndexOf('/'))
      path = `${baseDir}/${path}`
    }

    let needLoginPages: string[] = []
    // To prevent bugs during development, get it each time here. In production, can move outside function for better performance
    if (isDev) {
      needLoginPages = getNeedLoginPages()
    }
    else {
      needLoginPages = _needLoginPages
    }
    const isNeedLogin = needLoginPages.includes(path)
    if (!isNeedLogin) {
      return true
    }
    const hasLogin = isLogined()
    if (hasLogin) {
      return true
    }
    const redirectRoute = `${loginRoute}?redirect=${encodeURIComponent(url)}`
    uni.navigateTo({ url: redirectRoute })
    return false
  },
}

export const routeInterceptor = {
  install() {
    uni.addInterceptor('navigateTo', navigateToInterceptor)
    uni.addInterceptor('reLaunch', navigateToInterceptor)
    uni.addInterceptor('redirectTo', navigateToInterceptor)
    uni.addInterceptor('switchTab', navigateToInterceptor)
  },
}
