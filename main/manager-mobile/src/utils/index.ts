import { pages, subPackages } from '@/pages.json'
import { isMpWeixin } from './platform'

/**
 * Runtime server address override storage key
 */
export const SERVER_BASE_URL_OVERRIDE_KEY = 'server_base_url_override'

/**
 * Set/clear/get runtime override server address
 */
export function setServerBaseUrlOverride(url: string) {
  uni.setStorageSync(SERVER_BASE_URL_OVERRIDE_KEY, url)
}

export function clearServerBaseUrlOverride() {
  uni.removeStorageSync(SERVER_BASE_URL_OVERRIDE_KEY)
}

export function getServerBaseUrlOverride(): string | null {
  const value = uni.getStorageSync(SERVER_BASE_URL_OVERRIDE_KEY)
  return value || null
}

export function getLastPage() {
  // getCurrentPages() has at least 1 element, so no additional check needed
  // const lastPage = getCurrentPages().at(-1)
  // The above one will cause errors when packaging on low-version Android, so use the one below instead [Even though I added src/interceptions/prototype.ts, it still errors]
  const pages = getCurrentPages()
  return pages[pages.length - 1]
}

/**
 * Get current page route's path and redirectPath
 * path e.g. '/pages/login/index'
 * redirectPath e.g. '/pages/demo/base/route-interceptor'
 */
export function currRoute() {
  const lastPage = getLastPage()
  const currRoute = (lastPage as any).$page
  // console.log('lastPage.$page:', currRoute)
  // console.log('lastPage.$page.fullpath:', currRoute.fullPath)
  // console.log('lastPage.$page.options:', currRoute.options)
  // console.log('lastPage.options:', (lastPage as any).options)
  // After multi-platform testing, only fullPath is reliable, others are not
  const { fullPath } = currRoute as { fullPath: string }
  // console.log(fullPath)
  // eg: /pages/login/index?redirect=%2Fpages%2Fdemo%2Fbase%2Froute-interceptor (mini program)
  // eg: /pages/login/index?redirect=%2Fpages%2Froute-interceptor%2Findex%3Fname%3Dfeige%26age%3D30(h5)
  return getUrlObj(fullPath)
}

function ensureDecodeURIComponent(url: string) {
  if (url.startsWith('%')) {
    return ensureDecodeURIComponent(decodeURIComponent(url))
  }
  return url
}
/**
 * Parse url to get path and query
 * e.g. input url: /pages/login/index?redirect=%2Fpages%2Fdemo%2Fbase%2Froute-interceptor
 * output: {path: /pages/login/index, query: {redirect: /pages/demo/base/route-interceptor}}
 */
export function getUrlObj(url: string) {
  const [path, queryStr] = url.split('?')
  // console.log(path, queryStr)

  if (!queryStr) {
    return {
      path,
      query: {},
    }
  }
  const query: Record<string, string> = {}
  queryStr.split('&').forEach((item) => {
    const [key, value] = item.split('=')
    // console.log(key, value)
    query[key] = ensureDecodeURIComponent(value) // Need to uniformly decodeURIComponent here to be compatible with h5 and WeChat
  })
  return { path, query }
}
/**
 * Get all pages that need login, including main package and sub-packages
 * Designed to be more generic, can pass key as judgment basis, default is needLogin, used together with route-block
 * If no key is passed, it means all pages, if key is passed, it means filter by key
 */
export function getAllPages(key = 'needLogin') {
  // Handle main package here
  const mainPages = pages
    .filter(page => !key || page[key])
    .map(page => ({
      ...page,
      path: `/${page.path}`,
    }))

  // Handle sub-packages here
  const subPages: any[] = []
  subPackages.forEach((subPageObj) => {
    // console.log(subPageObj)
    const { root } = subPageObj

    subPageObj.pages
      .filter(page => !key || page[key])
      .forEach((page: { path: string } & Record<string, any>) => {
        subPages.push({
          ...page,
          path: `/${root}/${page.path}`,
        })
      })
  })
  const result = [...mainPages, ...subPages]
  // console.log(`getAllPages by ${key} result: `, result)
  return result
}

/**
 * Get all pages that need login, including main package and sub-packages
 * Only get path array
 */
export const getNeedLoginPages = (): string[] => getAllPages('needLogin').map(page => page.path)

/**
 * Get all pages that need login, including main package and sub-packages
 * Only get path array
 */
export const needLoginPages: string[] = getAllPages('needLogin').map(page => page.path)

/**
 * Determine the baseUrl to get based on WeChat mini program current environment
 */
export function getEnvBaseUrl() {
  // If user-set override address exists, return it first
  const override = getServerBaseUrlOverride()
  if (override)
    return override

  // Request base address (default from env)
  let baseUrl = import.meta.env.VITE_SERVER_BASEURL

  // # Some may need to set upload addresses separately for develop, trial, release in WeChat mini program, reference code as follows.
  const VITE_SERVER_BASEURL__WEIXIN_DEVELOP = 'https://ukw0y1.laf.run'
  const VITE_SERVER_BASEURL__WEIXIN_TRIAL = 'https://ukw0y1.laf.run'
  const VITE_SERVER_BASEURL__WEIXIN_RELEASE = 'https://ukw0y1.laf.run'

  // WeChat mini program environment distinction
  if (isMpWeixin) {
    const {
      miniProgram: { envVersion },
    } = uni.getAccountInfoSync()

    switch (envVersion) {
      case 'develop':
        baseUrl = VITE_SERVER_BASEURL__WEIXIN_DEVELOP || baseUrl
        break
      case 'trial':
        baseUrl = VITE_SERVER_BASEURL__WEIXIN_TRIAL || baseUrl
        break
      case 'release':
        baseUrl = VITE_SERVER_BASEURL__WEIXIN_RELEASE || baseUrl
        break
    }
  }

  return baseUrl
}

/**
 * Determine the UPLOAD_BASEURL to get based on WeChat mini program current environment
 */
export function getEnvBaseUploadUrl() {
  // Request base address
  let baseUploadUrl = import.meta.env.VITE_UPLOAD_BASEURL

  const VITE_UPLOAD_BASEURL__WEIXIN_DEVELOP = 'https://ukw0y1.laf.run/upload'
  const VITE_UPLOAD_BASEURL__WEIXIN_TRIAL = 'https://ukw0y1.laf.run/upload'
  const VITE_UPLOAD_BASEURL__WEIXIN_RELEASE = 'https://ukw0y1.laf.run/upload'

  // WeChat mini program environment distinction
  if (isMpWeixin) {
    const {
      miniProgram: { envVersion },
    } = uni.getAccountInfoSync()

    switch (envVersion) {
      case 'develop':
        baseUploadUrl = VITE_UPLOAD_BASEURL__WEIXIN_DEVELOP || baseUploadUrl
        break
      case 'trial':
        baseUploadUrl = VITE_UPLOAD_BASEURL__WEIXIN_TRIAL || baseUploadUrl
        break
      case 'release':
        baseUploadUrl = VITE_UPLOAD_BASEURL__WEIXIN_RELEASE || baseUploadUrl
        break
    }
  }

  return baseUploadUrl
}

import smCrypto from 'sm-crypto'

/**
 * Generate SM2 key pair (hexadecimal format)
 * @returns {Object} Object containing public key and private key
 */
export function generateSm2KeyPairHex() {
    // Use sm-crypto library to generate SM2 key pair
    const sm2 = smCrypto.sm2;
    const keypair = sm2.generateKeyPairHex();
    
    return {
        publicKey: keypair.publicKey,
        privateKey: keypair.privateKey,
        clientPublicKey: keypair.publicKey, // Client public key
        clientPrivateKey: keypair.privateKey // Client private key
    };
}

/**
 * SM2 public key encryption
 * @param {string} publicKey Public key (hexadecimal format)
 * @param {string} plainText Plaintext
 * @returns {string} Encrypted ciphertext (hexadecimal format)
 */
export function sm2Encrypt(publicKey: string, plainText: string): string {
    if (!publicKey) {
        throw new Error('Public key cannot be null or undefined');
    }
    
    if (!plainText) {
        throw new Error('Plaintext cannot be empty');
    }
    
    const sm2 = smCrypto.sm2;
    // SM2 encryption, add 04 prefix to indicate uncompressed public key
    const encrypted = sm2.doEncrypt(plainText, publicKey, 1);
    // Convert to hexadecimal format (consistent with backend, add 04 prefix)
    const result = "04" + encrypted;
    
    return result;
}

/**
 * SM2 private key decryption
 * @param {string} privateKey Private key (hexadecimal format)
 * @param {string} cipherText Ciphertext (hexadecimal format)
 * @returns {string} Decrypted plaintext
 */
export function sm2Decrypt(privateKey: string, cipherText: string): string {
    const sm2 = smCrypto.sm2;
    // Remove 04 prefix (consistent with backend)
    const dataWithoutPrefix = cipherText.startsWith("04") ? cipherText.substring(2) : cipherText;
    // SM2 decryption
    return sm2.doDecrypt(dataWithoutPrefix, privateKey, 1);
}
