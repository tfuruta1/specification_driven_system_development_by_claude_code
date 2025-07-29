# Axios 統合ガイド（ハイブリッド接続対応）

## 概要

このドキュメントでは、Vue.js + ハイブリッド接続アプリケーションでのAxios HTTPクライアントの統合方法、設定パターン、FastAPI + SQLAlchemy バックエンドとの完全連携について説明します。

## Axios 基本設定

### インストール

```bash
npm install axios
```

### 基本クライアント設定

```javascript
// lib/api/client.js
import axios from 'axios'

// 基本クライアント作成
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

export default apiClient
```

## 認証統合

### JWT トークン管理

```javascript
// lib/api/auth.js
import apiClient from './client'
import { useAuthStore } from '@/stores/auth'

// リクエストインターセプター（トークン自動付与）
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.accessToken
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター（トークンリフレッシュ）
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401) {
      try {
        await authStore.refreshToken()
        // 元のリクエストを再実行
        return apiClient(error.config)
      } catch (refreshError) {
        authStore.logout()
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export { apiClient }
```

### 認証API

```javascript
// services/authService.js
import apiClient from '@/lib/api/client'

export const authService = {
  /**
   * ログイン
   * @param {Object} credentials - 認証情報
   * @returns {Promise<Object>} 認証結果
   */
  async login(credentials) {
    const response = await apiClient.post('/auth/login', credentials)
    return response.data
  },

  /**
   * トークンリフレッシュ
   * @param {string} refreshToken - リフレッシュトークン
   * @returns {Promise<Object>} 新しいトークン
   */
  async refreshToken(refreshToken) {
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  },

  /**
   * ログアウト
   * @returns {Promise<void>}
   */
  async logout() {
    await apiClient.post('/auth/logout')
  },

  /**
   * ユーザー情報取得
   * @returns {Promise<Object>} ユーザー情報
   */
  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return response.data
  }
}
```

## エラーハンドリング

### エラー処理クラス

```javascript
// lib/api/errors.js

export class ApiError extends Error {
  constructor(message, status, response) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.response = response
  }
}

export class ValidationError extends ApiError {
  constructor(message, errors) {
    super(message, 422)
    this.errors = errors
  }
}

export class NetworkError extends ApiError {
  constructor(message) {
    super(message, 0)
  }
}

/**
 * Axiosエラーを適切なエラークラスに変換
 * @param {Error} error - Axiosエラー
 * @returns {ApiError} 変換されたエラー
 */
export function handleApiError(error) {
  if (!error.response) {
    return new NetworkError('ネットワークエラーが発生しました')
  }

  const { status, data } = error.response

  switch (status) {
    case 422:
      return new ValidationError(
        data.message || 'バリデーションエラー',
        data.errors
      )
    case 401:
      return new ApiError('認証が必要です', status, error.response)
    case 403:
      return new ApiError('アクセス権限がありません', status, error.response)
    case 404:
      return new ApiError('リソースが見つかりません', status, error.response)
    case 500:
      return new ApiError('サーバーエラーが発生しました', status, error.response)
    default:
      return new ApiError(
        data.message || 'APIエラーが発生しました',
        status,
        error.response
      )
  }
}
```

### エラーハンドリングインターセプター

```javascript
// lib/api/client.js (エラーハンドリング追加)
import { handleApiError } from './errors'
import { useNotificationStore } from '@/stores/notification'

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const notificationStore = useNotificationStore()
    const apiError = handleApiError(error)
    
    // 認証エラー以外はユーザーに通知
    if (apiError.status !== 401) {
      notificationStore.showError(apiError.message)
    }
    
    return Promise.reject(apiError)
  }
)
```

## データフェッチング Composables

### useApi

```javascript
// composables/useApi.js
import { ref, computed } from 'vue'
import { handleApiError } from '@/lib/api/errors'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const execute = async (apiCall) => {
    loading.value = true
    error.value = null

    try {
      const result = await apiCall()
      return result
    } catch (err) {
      error.value = handleApiError(err)
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    execute
  }
}
```

### useAsyncData

```javascript
// composables/useAsyncData.js
import { ref, computed, onMounted } from 'vue'
import { useApi } from './useApi'

export function useAsyncData(fetchFunction, options = {}) {
  const { immediate = true } = options
  const { loading, error, execute } = useApi()
  const data = ref(null)

  const refresh = async () => {
    const result = await execute(fetchFunction)
    data.value = result
    return result
  }

  if (immediate) {
    onMounted(refresh)
  }

  return {
    data: computed(() => data.value),
    loading,
    error,
    refresh
  }
}
```

## API サービス例

### ユーザーサービス

```javascript
// services/userService.js
import apiClient from '@/lib/api/client'

export const userService = {
  /**
   * ユーザー一覧取得
   * @param {Object} params - クエリパラメータ
   * @returns {Promise<Object>} ユーザー一覧
   */
  async getUsers(params = {}) {
    const response = await apiClient.get('/users', { params })
    return response.data
  },

  /**
   * ユーザー詳細取得
   * @param {string} id - ユーザーID
   * @returns {Promise<Object>} ユーザー詳細
   */
  async getUser(id) {
    const response = await apiClient.get(`/users/${id}`)
    return response.data
  },

  /**
   * ユーザー作成
   * @param {Object} userData - ユーザーデータ
   * @returns {Promise<Object>} 作成されたユーザー
   */
  async createUser(userData) {
    const response = await apiClient.post('/users', userData)
    return response.data
  },

  /**
   * ユーザー更新
   * @param {string} id - ユーザーID
   * @param {Object} userData - 更新データ
   * @returns {Promise<Object>} 更新されたユーザー
   */
  async updateUser(id, userData) {
    const response = await apiClient.put(`/users/${id}`, userData)
    return response.data
  },

  /**
   * ユーザー削除
   * @param {string} id - ユーザーID
   * @returns {Promise<void>}
   */
  async deleteUser(id) {
    await apiClient.delete(`/users/${id}`)
  }
}
```

## 使用例

### コンポーネントでの使用

```vue
<template>
  <div class="user-list">
    <div v-if="loading" class="loading">
      読み込み中...
    </div>
    
    <div v-else-if="error" class="error">
      エラー: {{ error.message }}
      <button @click="refresh">再試行</button>
    </div>
    
    <div v-else>
      <div v-for="user in users" :key="user.id" class="user-card">
        {{ user.name }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { userService } from '@/services/userService'
import { useAsyncData } from '@/composables/useAsyncData'

const { data: users, loading, error, refresh } = useAsyncData(
  () => userService.getUsers()
)
</script>
```

### ストアでの使用

```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { userService } from '@/services/userService'

export const useUserStore = defineStore('user', () => {
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchUsers = async () => {
    loading.value = true
    error.value = null

    try {
      const result = await userService.getUsers()
      users.value = result.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const createUser = async (userData) => {
    const newUser = await userService.createUser(userData)
    users.value.push(newUser)
    return newUser
  }

  return {
    users: computed(() => users.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    fetchUsers,
    createUser
  }
})
```

## キャッシュ戦略

### メモリキャッシュ

```javascript
// lib/api/cache.js
class ApiCache {
  constructor() {
    this.cache = new Map()
    this.ttl = 5 * 60 * 1000 // 5分
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  get(key) {
    const item = this.cache.get(key)
    if (!item) return null

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  clear() {
    this.cache.clear()
  }
}

export const apiCache = new ApiCache()
```

### キャッシュ統合

```javascript
// composables/useCachedApi.js
import { apiCache } from '@/lib/api/cache'
import { useApi } from './useApi'

export function useCachedApi() {
  const { loading, error, execute } = useApi()

  const executeWithCache = async (cacheKey, apiCall) => {
    // キャッシュをチェック
    const cached = apiCache.get(cacheKey)
    if (cached) {
      return cached
    }

    // キャッシュにない場合はAPIを呼び出し
    const result = await execute(apiCall)
    apiCache.set(cacheKey, result)
    return result
  }

  return {
    loading,
    error,
    executeWithCache
  }
}
```

## ベストプラクティス

### 1. 型安全性

```javascript
/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} name
 * @property {string} email
 * @property {Date} createdAt
 */

/**
 * @typedef {Object} ApiResponse
 * @property {User[]} data
 * @property {Object} meta
 * @property {number} meta.total
 * @property {number} meta.page
 */
```

### 2. リクエスト最適化

```javascript
// 並列リクエスト
const [users, posts] = await Promise.all([
  userService.getUsers(),
  postService.getPosts()
])

// リクエストキャンセル
const controller = new AbortController()
const response = await apiClient.get('/data', {
  signal: controller.signal
})

// タイムアウト時にキャンセル
setTimeout(() => controller.abort(), 5000)
```

### 3. エラー境界

```vue
<!-- ErrorBoundary.vue -->
<template>
  <div v-if="error" class="error-boundary">
    <h3>エラーが発生しました</h3>
    <p>{{ error.message }}</p>
    <button @click="retry">再試行</button>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, provide, onErrorCaptured } from 'vue'

const error = ref(null)

const retry = () => {
  error.value = null
}

onErrorCaptured((err) => {
  error.value = err
  return false
})

provide('retry', retry)
</script>
```

このガイドに従って、Axiosを使用した堅牢で保守性の高いAPI統合を実現してください。