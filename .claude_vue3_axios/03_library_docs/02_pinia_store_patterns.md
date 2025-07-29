# Pinia状態管理パターン集

Vue 3アプリケーションにおけるPiniaを使った状態管理の必須パターンとSupabase連携方法を解説します。

## 📚 目次

1. [ストア設定と構成](#ストア設定と構成)
2. [基本的なストアパターン](#基本的なストアパターン)
3. [エラーハンドリング付き非同期アクション](#エラーハンドリング付き非同期アクション)
4. [ストア合成パターン](#ストア合成パターン)
5. [計算プロパティとゲッター](#計算プロパティとゲッター)
6. [永続化パターン](#永続化パターン)
7. [リアルタイム状態管理](#リアルタイム状態管理)
8. [パフォーマンス最適化](#パフォーマンス最適化)

## ストア設定と構成

### Pinia設定

```javascript
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'
import App from './App.vue'

const pinia = createPinia()

// 永続化プラグインを追加
pinia.use(createPersistedState({
  key: id => `${id}-store`,
  storage: localStorage,
  beforeRestore: (context) => {
    console.log('ストア復元中:', context.store.$id)
  },
  afterRestore: (context) => {
    console.log('ストア復元完了:', context.store.$id)
  }
}))

const app = createApp(App)
app.use(pinia)
app.mount('#app')
```

### ベースストアパターン

```javascript
// stores/base.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 共通パターンを持つベースストアファクトリー
 * @param {string} id - ストア識別子
 * @param {Object} options - ストア設定
 * @returns {Function} ストア定義
 */
export function defineBaseStore(id, options = {}) {
  return defineStore(id, () => {
    // 共通状態
    const loading = ref(false)
    const error = ref(null)
    const lastUpdated = ref(null)
    
    // 改善：リトライ機能付きAPI呼び出し
    const executeWithRetry = async (apiFn, maxRetries = 3, delay = 1000) => {
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          loading.value = true
          const result = await apiFn()
          error.value = null
          lastUpdated.value = Date.now()
          return result
        } catch (err) {
          if (attempt === maxRetries) {
            error.value = {
              message: err.message,
              code: err.code || 'UNKNOWN',
              attempt,
              timestamp: new Date().toISOString(),
              retryable: shouldRetry(err)
            }
            throw err
          }
          
          // 指数バックオフでリトライ
          if (shouldRetry(err)) {
            const backoffDelay = delay * Math.pow(2, attempt - 1)
            console.log(`${id}: リトライ ${attempt}/${maxRetries} (${backoffDelay}ms後)`)
            await new Promise(resolve => setTimeout(resolve, backoffDelay))
          } else {
            // リトライしないエラーは即座に失敗
            error.value = {
              message: err.message,
              code: err.code || 'UNKNOWN',
              attempt,
              timestamp: new Date().toISOString(),
              retryable: false
            }
            throw err
          }
        } finally {
          if (attempt === maxRetries) {
            loading.value = false
          }
        }
      }
    }
    
    /**
     * エラーがリトライ可能かチェック
     * @param {Error} error - チェックするエラー
     * @returns {boolean} リトライ可能かどうか
     */
    const shouldRetry = (error) => {
      // ネットワークエラー
      if (error.name === 'NetworkError') return true
      
      // タイムアウトエラー
      if (error.message.includes('timeout')) return true
      
      // 5xxサーバーエラー
      if (error.status >= 500 && error.status < 600) return true
      
      // レート制限
      if (error.status === 429) return true
      
      // Supabase固有のエラー
      if (error.code === 'PGRST301') return true // 接続エラー
      
      return false
    }
    
    // 共通ゲッター
    const isReady = computed(() => !loading.value && error.value === null)
    const hasError = computed(() => error.value !== null)
    const isStale = computed(() => {
      if (!lastUpdated.value) return true
      const staleTime = options.staleTime || 300000 // 5分
      return Date.now() - lastUpdated.value > staleTime
    })
    
    /**
     * ローディング状態を設定
     * @param {boolean} value - ローディング状態
     */
    const setLoading = (value) => {
      loading.value = value
    }
    
    /**
     * エラー状態を設定
     * @param {Error|string|null} value - エラー値
     */
    const setError = (value) => {
      if (typeof value === 'string') {
        error.value = {
          message: value,
          code: 'MANUAL_ERROR',
          timestamp: new Date().toISOString()
        }
      } else if (value instanceof Error) {
        error.value = {
          message: value.message,
          code: value.code || 'ERROR',
          timestamp: new Date().toISOString()
        }
      } else {
        error.value = value
      }
    }
    
    /**
     * エラー状態をクリア
     */
    const clearError = () => {
      error.value = null
    }
    
    /**
     * 最終更新時刻を更新
     */
    const touch = () => {
      lastUpdated.value = Date.now()
    }
    
    /**
     * ストアを初期状態にリセット
     */
    const $reset = () => {
      loading.value = false
      error.value = null
      lastUpdated.value = null
      // カスタムリセットが提供されている場合実行
      if (options.reset) {
        options.reset()
      }
    }
    
    return {
      // 状態
      loading: readonly(loading),
      error: readonly(error),
      lastUpdated: readonly(lastUpdated),
      // ゲッター
      isReady,
      hasError,
      isStale,
      // アクション
      executeWithRetry,
      setLoading,
      setError,
      clearError,
      touch,
      $reset
    }
  })
}
```

## 基本的なストアパターン

### ユーザーストア

```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

/**
 * ユーザー認証とプロフィールストア
 */
export const useUserStore = defineStore('user', () => {
  const { supabase } = useAuth()
  
  // 状態
  const user = ref(null)
  const profile = ref(null)
  const session = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // ゲッター
  const isAuthenticated = computed(() => !!session.value)
  const isAdmin = computed(() => profile.value?.role === 'admin')
  const fullName = computed(() => {
    if (!profile.value) return ''
    return `${profile.value.first_name} ${profile.value.last_name}`.trim()
  })
  const avatar = computed(() => {
    return profile.value?.avatar_url || '/default-avatar.png'
  })
  
  /**
   * 認証状態を初期化
   */
  const initialize = async () => {
    try {
      loading.value = true
      error.value = null
      
      // 現在のセッションを取得
      const { data: { session: currentSession } } = await supabase.auth.getSession()
      
      if (currentSession) {
        session.value = currentSession
        user.value = currentSession.user
        await fetchProfile()
      }
      
      // 認証状態の変更を監視
      supabase.auth.onAuthStateChange((event, newSession) => {
        session.value = newSession
        user.value = newSession?.user || null
        
        if (event === 'SIGNED_IN' && newSession) {
          fetchProfile()
        } else if (event === 'SIGNED_OUT') {
          clearUserData()
        }
      })
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  /**
   * ユーザーサインイン
   * @param {string} email - ユーザーメール
   * @param {string} password - ユーザーパスワード
   */
  const signIn = async (email, password) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      })
      
      if (signInError) throw signInError
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 新規ユーザー登録
   * @param {Object} userData - ユーザー登録データ
   */
  const signUp = async (userData) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: signUpError } = await supabase.auth.signUp({
        email: userData.email,
        password: userData.password,
        options: {
          data: {
            first_name: userData.firstName,
            last_name: userData.lastName
          }
        }
      })
      
      if (signUpError) throw signUpError
      
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * ユーザーサインアウト
   */
  const signOut = async () => {
    try {
      loading.value = true
      await supabase.auth.signOut()
      clearUserData()
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  /**
   * ユーザープロフィールを取得
   */
  const fetchProfile = async () => {
    if (!user.value) return
    
    try {
      const { data, error: profileError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.value.id)
        .single()
      
      if (profileError) throw profileError
      
      profile.value = data
    } catch (err) {
      console.error('プロフィール取得に失敗しました:', err)
    }
  }
  
  /**
   * ユーザープロフィールを更新
   * @param {Object} updates - プロフィール更新
   */
  const updateProfile = async (updates) => {
    if (!user.value) return
    
    try {
      loading.value = true
      error.value = null
      
      const { data, error: updateError } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', user.value.id)
        .select()
        .single()
      
      if (updateError) throw updateError
      
      profile.value = data
      return { success: true, data }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * ユーザーデータをクリア
   */
  const clearUserData = () => {
    user.value = null
    profile.value = null
    session.value = null
    error.value = null
  }
  
  /**
   * ストアをリセット
   */
  const $reset = () => {
    clearUserData()
    loading.value = false
  }
  
  return {
    // 状態
    user: readonly(user),
    profile: readonly(profile),
    session: readonly(session),
    loading: readonly(loading),
    error: readonly(error),
    
    // ゲッター
    isAuthenticated,
    isAdmin,
    fullName,
    avatar,
    
    // アクション
    initialize,
    signIn,
    signUp,
    signOut,
    fetchProfile,
    updateProfile,
    clearUserData,
    $reset
  }
}, {
  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['profile'] // プロフィールのみ永続化、セッションは除外
  }
})
```

### 投稿ストア

```javascript
// stores/posts.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSupabase } from '@/composables/useSupabase'
import { useUserStore } from './user'

/**
 * 投稿管理ストア
 */
export const usePostsStore = defineStore('posts', () => {
  const { supabase } = useSupabase()
  const userStore = useUserStore()
  
  // 状態
  const posts = ref([])
  const currentPost = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const filters = ref({
    search: '',
    category: '',
    author: '',
    status: 'published'
  })
  const pagination = ref({
    page: 1,
    limit: 10,
    total: 0
  })
  
  // ゲッター
  const filteredPosts = computed(() => {
    let filtered = posts.value
    
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      filtered = filtered.filter(post => 
        post.title.toLowerCase().includes(search) ||
        post.excerpt.toLowerCase().includes(search)
      )
    }
    
    if (filters.value.category) {
      filtered = filtered.filter(post => post.category === filters.value.category)
    }
    
    if (filters.value.author) {
      filtered = filtered.filter(post => post.author_id === filters.value.author)
    }
    
    if (filters.value.status) {
      filtered = filtered.filter(post => post.status === filters.value.status)
    }
    
    return filtered
  })
  
  const myPosts = computed(() => {
    if (!userStore.isAuthenticated) return []
    return posts.value.filter(post => post.author_id === userStore.user.id)
  })
  
  const publishedPosts = computed(() => {
    return posts.value.filter(post => post.status === 'published')
  })
  
  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.limit)
  })
  
  /**
   * ページネーションとフィルター付きで投稿を取得
   * @param {Object} options - 取得オプション
   */
  const fetchPosts = async (options = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const {
        page = pagination.value.page,
        limit = pagination.value.limit,
        reset = false
      } = options
      
      const from = (page - 1) * limit
      const to = from + limit - 1
      
      let query = supabase
        .from('posts')
        .select(`
          *,
          profiles:author_id (
            first_name,
            last_name,
            avatar_url
          ),
          categories (
            name,
            slug
          )
        `, { count: 'exact' })
        .range(from, to)
        .order('created_at', { ascending: false })
      
      // フィルターを適用
      if (filters.value.category) {
        query = query.eq('category', filters.value.category)
      }
      
      if (filters.value.status) {
        query = query.eq('status', filters.value.status)
      }
      
      if (filters.value.author) {
        query = query.eq('author_id', filters.value.author)
      }
      
      const { data, error: fetchError, count } = await query
      
      if (fetchError) throw fetchError
      
      if (reset || page === 1) {
        posts.value = data
      } else {
        posts.value.push(...data)
      }
      
      pagination.value = {
        page,
        limit,
        total: count
      }
      
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * IDで単一投稿を取得
   * @param {string} id - 投稿ID
   */
  const fetchPost = async (id) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: fetchError } = await supabase
        .from('posts')
        .select(`
          *,
          profiles:author_id (
            first_name,
            last_name,
            avatar_url
          ),
          categories (
            name,
            slug
          )
        `)
        .eq('id', id)
        .single()
      
      if (fetchError) throw fetchError
      
      currentPost.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 新しい投稿を作成
   * @param {Object} postData - 投稿データ
   */
  const createPost = async (postData) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: createError } = await supabase
        .from('posts')
        .insert({
          ...postData,
          author_id: userStore.user.id
        })
        .select()
        .single()
      
      if (createError) throw createError
      
      posts.value.unshift(data)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 既存投稿を更新
   * @param {string} id - 投稿ID
   * @param {Object} updates - 投稿更新データ
   */
  const updatePost = async (id, updates) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: updateError } = await supabase
        .from('posts')
        .update(updates)
        .eq('id', id)
        .select()
        .single()
      
      if (updateError) throw updateError
      
      const index = posts.value.findIndex(post => post.id === id)
      if (index !== -1) {
        posts.value[index] = data
      }
      
      if (currentPost.value && currentPost.value.id === id) {
        currentPost.value = data
      }
      
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 投稿を削除
   * @param {string} id - 投稿ID
   */
  const deletePost = async (id) => {
    try {
      loading.value = true
      error.value = null
      
      const { error: deleteError } = await supabase
        .from('posts')
        .delete()
        .eq('id', id)
      
      if (deleteError) throw deleteError
      
      posts.value = posts.value.filter(post => post.id !== id)
      
      if (currentPost.value && currentPost.value.id === id) {
        currentPost.value = null
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * フィルターを更新
   * @param {Object} newFilters - 新しいフィルター値
   */
  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.page = 1 // 最初のページにリセット
  }
  
  /**
   * より多くの投稿を読み込み（無限スクロール）
   */
  const loadMore = async () => {
    if (pagination.value.page < totalPages.value) {
      await fetchPosts({
        page: pagination.value.page + 1,
        reset: false
      })
    }
  }
  
  /**
   * ストアをリセット
   */
  const $reset = () => {
    posts.value = []
    currentPost.value = null
    loading.value = false
    error.value = null
    filters.value = {
      search: '',
      category: '',
      author: '',
      status: 'published'
    }
    pagination.value = {
      page: 1,
      limit: 10,
      total: 0
    }
  }
  
  return {
    // 状態
    posts: readonly(posts),
    currentPost: readonly(currentPost),
    loading: readonly(loading),
    error: readonly(error),
    filters: readonly(filters),
    pagination: readonly(pagination),
    
    // ゲッター
    filteredPosts,
    myPosts,
    publishedPosts,
    totalPages,
    
    // アクション
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    updateFilters,
    loadMore,
    $reset
  }
})
```

## エラーハンドリング付き非同期アクション

### 高度なエラーハンドリングパターン

```javascript
// stores/api.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * APIエラーハンドリングとリクエスト管理ストア
 */
export const useApiStore = defineStore('api', () => {
  const requests = ref(new Map())
  const errors = ref([])
  const retryAttempts = ref(new Map())
  
  /**
   * エラーハンドリングとリトライロジック付きAPIリクエスト実行
   * @param {string} key - リクエスト識別子
   * @param {Function} requestFn - リクエスト関数
   * @param {Object} options - リクエストオプション
   */
  const executeRequest = async (key, requestFn, options = {}) => {
    const {
      retries = 3,
      retryDelay = 1000,
      timeout = 10000,
      onSuccess,
      onError,
      silent = false
    } = options
    
    // 重複リクエストを防止
    if (requests.value.has(key)) {
      throw new Error(`リクエスト "${key}" は既に実行中です`)
    }
    
    requests.value.set(key, {
      startTime: Date.now(),
      status: 'pending'
    })
    
    let lastError = null
    const maxRetries = retries
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // タイムアウトラッパーを追加
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('リクエストタイムアウト')), timeout)
        })
        
        const result = await Promise.race([requestFn(), timeoutPromise])
        
        // 成功
        requests.value.delete(key)
        retryAttempts.value.delete(key)
        
        if (onSuccess) {
          onSuccess(result)
        }
        
        return result
      } catch (error) {
        lastError = error
        
        // リトライ回数を更新
        retryAttempts.value.set(key, attempt + 1)
        
        // リトライするかチェック
        if (attempt < maxRetries && shouldRetry(error)) {
          await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, attempt)))
          continue
        }
        
        // 全ての試行が失敗
        break
      }
    }
    
    // リクエスト失敗
    requests.value.delete(key)
    
    const errorInfo = {
      id: Date.now(),
      key,
      error: lastError,
      attempts: retryAttempts.value.get(key) || 1,
      timestamp: new Date(),
      silent
    }
    
    if (!silent) {
      errors.value.push(errorInfo)
    }
    
    if (onError) {
      onError(errorInfo)
    }
    
    throw lastError
  }
  
  /**
   * エラーがリトライすべきかどうかを判定
   * @param {Error} error - チェックするエラー
   * @returns {boolean} リトライすべきかどうか
   */
  const shouldRetry = (error) => {
    // ネットワークエラー
    if (error.name === 'NetworkError') return true
    
    // タイムアウトエラー
    if (error.message.includes('timeout')) return true
    
    // 5xxサーバーエラー
    if (error.status >= 500 && error.status < 600) return true
    
    // レート制限
    if (error.status === 429) return true
    
    return false
  }
  
  /**
   * IDでエラーをクリア
   * @param {number} id - エラーID
   */
  const clearError = (id) => {
    errors.value = errors.value.filter(error => error.id !== id)
  }
  
  /**
   * 全エラーをクリア
   */
  const clearAllErrors = () => {
    errors.value = []
  }
  
  /**
   * リクエストをキャンセル
   * @param {string} key - リクエストキー
   */
  const cancelRequest = (key) => {
    requests.value.delete(key)
    retryAttempts.value.delete(key)
  }
  
  return {
    requests: readonly(requests),
    errors: readonly(errors),
    retryAttempts: readonly(retryAttempts),
    executeRequest,
    clearError,
    clearAllErrors,
    cancelRequest
  }
})
```

## ストア合成パターン

### 依存関係を持つストア合成

```javascript
// stores/dashboard.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'
import { usePostsStore } from './posts'
import { useNotificationsStore } from './notifications'

/**
 * 複数のストアを合成するダッシュボードストア
 */
export const useDashboardStore = defineStore('dashboard', () => {
  const userStore = useUserStore()
  const postsStore = usePostsStore()
  const notificationsStore = useNotificationsStore()
  
  // 状態
  const widgets = ref([
    { id: 'posts', enabled: true, order: 1 },
    { id: 'notifications', enabled: true, order: 2 },
    { id: 'profile', enabled: true, order: 3 }
  ])
  const layout = ref('grid')
  const refreshInterval = ref(300000) // 5分
  
  // ゲッター
  const dashboardData = computed(() => {
    return {
      user: {
        profile: userStore.profile,
        fullName: userStore.fullName,
        avatar: userStore.avatar
      },
      posts: {
        total: postsStore.myPosts.length,
        published: postsStore.myPosts.filter(p => p.status === 'published').length,
        drafts: postsStore.myPosts.filter(p => p.status === 'draft').length,
        recent: postsStore.myPosts.slice(0, 5)
      },
      notifications: {
        unread: notificationsStore.unreadCount,
        recent: notificationsStore.recentNotifications
      }
    }
  })
  
  const enabledWidgets = computed(() => {
    return widgets.value
      .filter(widget => widget.enabled)
      .sort((a, b) => a.order - b.order)
  })
  
  const isLoading = computed(() => {
    return userStore.loading || postsStore.loading || notificationsStore.loading
  })
  
  /**
   * ダッシュボードデータを初期化
   */
  const initialize = async () => {
    try {
      await Promise.all([
        userStore.fetchProfile(),
        postsStore.fetchPosts({ limit: 10 }),
        notificationsStore.fetchNotifications({ limit: 20 })
      ])
    } catch (error) {
      console.error('ダッシュボードの初期化に失敗しました:', error)
    }
  }
  
  /**
   * 全ダッシュボードデータを更新
   */
  const refresh = async () => {
    await initialize()
  }
  
  /**
   * ウィジェット設定を更新
   * @param {string} widgetId - ウィジェットID
   * @param {Object} updates - ウィジェット更新
   */
  const updateWidget = (widgetId, updates) => {
    const widget = widgets.value.find(w => w.id === widgetId)
    if (widget) {
      Object.assign(widget, updates)
    }
  }
  
  /**
   * ウィジェットの順序を変更
   * @param {Array} newOrder - 新しいウィジェット順序
   */
  const reorderWidgets = (newOrder) => {
    newOrder.forEach((widgetId, index) => {
      const widget = widgets.value.find(w => w.id === widgetId)
      if (widget) {
        widget.order = index + 1
      }
    })
  }
  
  return {
    // 状態
    widgets: readonly(widgets),
    layout: readonly(layout),
    refreshInterval: readonly(refreshInterval),
    
    // ゲッター
    dashboardData,
    enabledWidgets,
    isLoading,
    
    // アクション
    initialize,
    refresh,
    updateWidget,
    reorderWidgets
  }
}, {
  persist: {
    key: 'dashboard-store',
    paths: ['widgets', 'layout', 'refreshInterval']
  }
})
```

### プラグインストアパターン

```javascript
// stores/plugins.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 動的ローディング付きプラグイン管理ストア
 */
export const usePluginsStore = defineStore('plugins', () => {
  const plugins = ref(new Map())
  const loadedPlugins = ref(new Set())
  const enabledPlugins = ref(new Set())
  const loading = ref(false)
  const error = ref(null)
  
  const availablePlugins = computed(() => Array.from(plugins.value.values()))
  const activePlugins = computed(() => {
    return availablePlugins.value.filter(plugin => 
      enabledPlugins.value.has(plugin.id) && loadedPlugins.value.has(plugin.id)
    )
  })
  
  /**
   * プラグイン定義を登録
   * @param {Object} plugin - プラグイン定義
   */
  const registerPlugin = (plugin) => {
    if (!plugin.id || !plugin.name) {
      throw new Error('プラグインにはidとnameが必要です')
    }
    
    plugins.value.set(plugin.id, {
      ...plugin,
      registered: Date.now()
    })
  }
  
  /**
   * プラグインを動的にロード
   * @param {string} pluginId - プラグインID
   */
  const loadPlugin = async (pluginId) => {
    const plugin = plugins.value.get(pluginId)
    if (!plugin) {
      throw new Error(`プラグイン "${pluginId}" が見つかりません`)
    }
    
    if (loadedPlugins.value.has(pluginId)) {
      return plugin
    }
    
    try {
      loading.value = true
      error.value = null
      
      // 動的インポート
      const pluginModule = await import(plugin.path)
      
      // プラグインを初期化
      if (pluginModule.default && typeof pluginModule.default.install === 'function') {
        await pluginModule.default.install()
      }
      
      loadedPlugins.value.add(pluginId)
      
      // ロードされたモジュールでプラグインを更新
      plugin.module = pluginModule.default
      plugin.loaded = Date.now()
      
      return plugin
    } catch (err) {
      error.value = `プラグイン "${pluginId}" のロードに失敗しました: ${err.message}`
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * プラグインを有効化
   * @param {string} pluginId - プラグインID
   */
  const enablePlugin = async (pluginId) => {
    if (!loadedPlugins.value.has(pluginId)) {
      await loadPlugin(pluginId)
    }
    
    enabledPlugins.value.add(pluginId)
    
    const plugin = plugins.value.get(pluginId)
    if (plugin.module && typeof plugin.module.enable === 'function') {
      await plugin.module.enable()
    }
  }
  
  /**
   * プラグインを無効化
   * @param {string} pluginId - プラグインID
   */
  const disablePlugin = async (pluginId) => {
    enabledPlugins.value.delete(pluginId)
    
    const plugin = plugins.value.get(pluginId)
    if (plugin.module && typeof plugin.module.disable === 'function') {
      await plugin.module.disable()
    }
  }
  
  /**
   * IDでプラグインを取得
   * @param {string} pluginId - プラグインID
   * @returns {Object} プラグイン定義
   */
  const getPlugin = (pluginId) => {
    return plugins.value.get(pluginId)
  }
  
  /**
   * プラグインが有効かチェック
   * @param {string} pluginId - プラグインID
   * @returns {boolean} プラグイン有効状態
   */
  const isPluginEnabled = (pluginId) => {
    return enabledPlugins.value.has(pluginId)
  }
  
  return {
    plugins: readonly(plugins),
    loadedPlugins: readonly(loadedPlugins),
    enabledPlugins: readonly(enabledPlugins),
    loading: readonly(loading),
    error: readonly(error),
    availablePlugins,
    activePlugins,
    registerPlugin,
    loadPlugin,
    enablePlugin,
    disablePlugin,
    getPlugin,
    isPluginEnabled
  }
}, {
  persist: {
    key: 'plugins-store',
    paths: ['enabledPlugins']
  }
})
```

## 計算プロパティとゲッター

### 高度な計算プロパティパターン

```javascript
// stores/analytics.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 高度な計算プロパティを持つ分析ストア
 */
export const useAnalyticsStore = defineStore('analytics', () => {
  const rawData = ref([])
  const dateRange = ref({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30日前
    end: new Date()
  })
  
  // 日付範囲に基づくフィルタリングされたデータ
  const filteredData = computed(() => {
    return rawData.value.filter(item => {
      const itemDate = new Date(item.date)
      return itemDate >= dateRange.value.start && itemDate <= dateRange.value.end
    })
  })
  
  // 時間ベースの集計
  const dailyStats = computed(() => {
    const stats = new Map()
    
    filteredData.value.forEach(item => {
      const date = item.date.split('T')[0] // 日付部分のみ取得
      
      if (!stats.has(date)) {
        stats.set(date, {
          date,
          views: 0,
          visitors: new Set(),
          revenue: 0,
          conversions: 0
        })
      }
      
      const dayStats = stats.get(date)
      dayStats.views += item.views || 0
      dayStats.visitors.add(item.visitor_id)
      dayStats.revenue += item.revenue || 0
      dayStats.conversions += item.conversions || 0
    })
    
    // VisitorのSetを数値に変換
    return Array.from(stats.values()).map(stat => ({
      ...stat,
      uniqueVisitors: stat.visitors.size
    })).sort((a, b) => new Date(a.date) - new Date(b.date))
  })
  
  // 成長指標の計算
  const growthMetrics = computed(() => {
    const current = dailyStats.value.slice(-7) // 直近7日間
    const previous = dailyStats.value.slice(-14, -7) // 前の7日間
    
    const currentTotal = current.reduce((sum, day) => sum + day.views, 0)
    const previousTotal = previous.reduce((sum, day) => sum + day.views, 0)
    
    const growth = previousTotal > 0 
      ? ((currentTotal - previousTotal) / previousTotal) * 100 
      : 0
    
    return {
      current: currentTotal,
      previous: previousTotal,
      growth: Math.round(growth * 100) / 100,
      trend: growth > 0 ? 'up' : growth < 0 ? 'down' : 'stable'
    }
  })
  
  // トップパフォーマー
  const topPages = computed(() => {
    const pageStats = new Map()
    
    filteredData.value.forEach(item => {
      if (!pageStats.has(item.page)) {
        pageStats.set(item.page, {
          page: item.page,
          views: 0,
          uniqueVisitors: new Set()
        })
      }
      
      const stats = pageStats.get(item.page)
      stats.views += item.views || 0
      stats.uniqueVisitors.add(item.visitor_id)
    })
    
    return Array.from(pageStats.values())
      .map(stat => ({
        ...stat,
        uniqueVisitors: stat.uniqueVisitors.size
      }))
      .sort((a, b) => b.views - a.views)
      .slice(0, 10)
  })
  
  // サマリー統計
  const summary = computed(() => {
    const total = filteredData.value.reduce((acc, item) => {
      acc.views += item.views || 0
      acc.revenue += item.revenue || 0
      acc.conversions += item.conversions || 0
      acc.visitors.add(item.visitor_id)
      return acc
    }, {
      views: 0,
      revenue: 0,
      conversions: 0,
      visitors: new Set()
    })
    
    return {
      totalViews: total.views,
      totalRevenue: total.revenue,
      totalConversions: total.conversions,
      uniqueVisitors: total.visitors.size,
      conversionRate: total.views > 0 ? (total.conversions / total.views) * 100 : 0,
      revenuePerVisitor: total.visitors.size > 0 ? total.revenue / total.visitors.size : 0
    }
  })
  
  return {
    rawData: readonly(rawData),
    dateRange: readonly(dateRange),
    filteredData,
    dailyStats,
    growthMetrics,
    topPages,
    summary
  }
})
```

## 永続化パターン

### カスタム永続化戦略

```javascript
// stores/settings.js
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

/**
 * カスタム永続化機能付き設定ストア
 */
export const useSettingsStore = defineStore('settings', () => {
  const theme = ref('light')
  const language = ref('ja')
  const notifications = ref({
    email: true,
    push: false,
    desktop: true
  })
  const layout = ref({
    sidebar: 'expanded',
    density: 'comfortable',
    animations: true
  })
  
  /**
   * 設定を複数のストレージに保存
   */
  const saveSettings = async () => {
    const settings = {
      theme: theme.value,
      language: language.value,
      notifications: notifications.value,
      layout: layout.value
    }
    
    // localStorageに保存
    localStorage.setItem('app-settings', JSON.stringify(settings))
    
    // ユーザーが認証されている場合はサーバーに保存
    const userStore = useUserStore()
    if (userStore.isAuthenticated) {
      try {
        await supabase
          .from('user_settings')
          .upsert({
            user_id: userStore.user.id,
            settings: settings
          })
      } catch (error) {
        console.warn('サーバーへの設定同期に失敗しました:', error)
      }
    }
  }
  
  /**
   * ストレージから設定を読み込み
   */
  const loadSettings = async () => {
    try {
      // まずサーバーから読み込みを試行
      const userStore = useUserStore()
      if (userStore.isAuthenticated) {
        const { data } = await supabase
          .from('user_settings')
          .select('settings')
          .eq('user_id', userStore.user.id)
          .single()
        
        if (data?.settings) {
          applySettings(data.settings)
          return
        }
      }
      
      // localStorageにフォールバック
      const stored = localStorage.getItem('app-settings')
      if (stored) {
        const settings = JSON.parse(stored)
        applySettings(settings)
      }
    } catch (error) {
      console.warn('設定の読み込みに失敗しました:', error)
    }
  }
  
  /**
   * 設定をストアに適用
   * @param {Object} settings - 設定オブジェクト
   */
  const applySettings = (settings) => {
    if (settings.theme) theme.value = settings.theme
    if (settings.language) language.value = settings.language
    if (settings.notifications) {
      notifications.value = { ...notifications.value, ...settings.notifications }
    }
    if (settings.layout) {
      layout.value = { ...layout.value, ...settings.layout }
    }
  }
  
  // 変更を監視して自動保存
  watch([theme, language, notifications, layout], saveSettings, { deep: true })
  
  return {
    theme,
    language,
    notifications,
    layout,
    saveSettings,
    loadSettings,
    applySettings
  }
})
```

## リアルタイム状態管理

### リアルタイム購読付きストア

```javascript
// stores/realtime.js
import { defineStore } from 'pinia'
import { ref, onUnmounted } from 'vue'
import { useSupabase } from '@/composables/useSupabase'

/**
 * リアルタイムデータ管理ストア
 */
export const useRealtimeStore = defineStore('realtime', () => {
  const { supabase } = useSupabase()
  
  const subscriptions = ref(new Map())
  const channels = ref(new Map())
  const connectionStatus = ref('disconnected')
  
  /**
   * テーブル変更を購読
   * @param {string} table - テーブル名
   * @param {Object} options - 購読オプション
   */
  const subscribeToTable = (table, options = {}) => {
    const {
      event = '*',
      filter,
      onInsert,
      onUpdate,
      onDelete,
      onError
    } = options
    
    if (subscriptions.value.has(table)) {
      console.warn(`既にテーブル ${table} を購読しています`)
      return
    }
    
    const channel = supabase
      .channel(`${table}_changes`)
      .on('postgres_changes', {
        event,
        schema: 'public',
        table,
        ...(filter && { filter })
      }, (payload) => {
        handleTableChange(payload, { onInsert, onUpdate, onDelete })
      })
      .subscribe((status) => {
        connectionStatus.value = status
        if (status === 'SUBSCRIBED') {
          console.log(`${table} の変更購読を開始しました`)
        } else if (status === 'CLOSED') {
          console.log(`${table} の変更購読を終了しました`)
        }
      })
    
    subscriptions.value.set(table, {
      channel,
      options,
      createdAt: Date.now()
    })
    
    channels.value.set(`${table}_changes`, channel)
  }
  
  /**
   * テーブル変更イベントを処理
   * @param {Object} payload - 変更ペイロード
   * @param {Object} handlers - イベントハンドラー
   */
  const handleTableChange = (payload, handlers) => {
    const { eventType, new: newRecord, old: oldRecord, table } = payload
    
    try {
      switch (eventType) {
        case 'INSERT':
          if (handlers.onInsert) {
            handlers.onInsert(newRecord, table)
          }
          break
          
        case 'UPDATE':
          if (handlers.onUpdate) {
            handlers.onUpdate(newRecord, oldRecord, table)
          }
          break
          
        case 'DELETE':
          if (handlers.onDelete) {
            handlers.onDelete(oldRecord, table)
          }
          break
      }
    } catch (error) {
      console.error(`${table} の ${eventType} 処理でエラーが発生しました:`, error)
      if (handlers.onError) {
        handlers.onError(error, payload)
      }
    }
  }
  
  /**
   * テーブル変更の購読を停止
   * @param {string} table - テーブル名
   */
  const unsubscribeFromTable = (table) => {
    const subscription = subscriptions.value.get(table)
    if (subscription) {
      supabase.removeChannel(subscription.channel)
      subscriptions.value.delete(table)
      channels.value.delete(`${table}_changes`)
    }
  }
  
  /**
   * ルーム内のプレゼンスを購読
   * @param {string} room - ルーム名
   * @param {Object} userState - ユーザープレゼンス状態
   */
  const joinPresence = (room, userState = {}) => {
    const channel = supabase.channel(room, {
      config: {
        presence: {
          key: userState.id || 'anonymous'
        }
      }
    })
    
    channel
      .on('presence', { event: 'sync' }, () => {
        const state = channel.presenceState()
        // プレゼンス同期を処理
      })
      .on('presence', { event: 'join' }, ({ key, newPresences }) => {
        // ユーザー参加を処理
      })
      .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
        // ユーザー退出を処理
      })
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          await channel.track(userState)
        }
      })
    
    channels.value.set(room, channel)
    return channel
  }
  
  /**
   * プレゼンスルームから退出
   * @param {string} room - ルーム名
   */
  const leavePresence = (room) => {
    const channel = channels.value.get(room)
    if (channel) {
      supabase.removeChannel(channel)
      channels.value.delete(room)
    }
  }
  
  /**
   * 全購読をクリーンアップ
   */
  const cleanup = () => {
    channels.value.forEach(channel => {
      supabase.removeChannel(channel)
    })
    subscriptions.value.clear()
    channels.value.clear()
    connectionStatus.value = 'disconnected'
  }
  
  // アンマウント時のクリーンアップ
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    subscriptions: readonly(subscriptions),
    channels: readonly(channels),
    connectionStatus: readonly(connectionStatus),
    subscribeToTable,
    unsubscribeFromTable,
    joinPresence,
    leavePresence,
    cleanup
  }
})
```

## パフォーマンス最適化

### ストアパフォーマンスパターン

```javascript
// stores/performance.js
import { defineStore } from 'pinia'
import { ref, computed, shallowRef } from 'vue'

/**
 * パフォーマンス最適化されたストアパターン
 */
export const usePerformanceStore = defineStore('performance', () => {
  // 大きなデータセットには深いリアクティビティが不要な場合shallowRefを使用
  const largeDataset = shallowRef([])
  
  // 頻繁にアクセスされる小さなデータには通常のrefを使用
  const metadata = ref({})
  
  // メモ化キャッシュ
  const computeCache = ref(new Map())
  
  /**
   * メモ化された重い計算
   */
  const expensiveComputation = computed(() => {
    const cacheKey = JSON.stringify(metadata.value)
    
    if (computeCache.value.has(cacheKey)) {
      return computeCache.value.get(cacheKey)
    }
    
    // 重い計算をシミュレート
    const result = largeDataset.value.reduce((acc, item) => {
      // 複雑な計算をここで実行
      return acc + item.value * metadata.value.multiplier
    }, 0)
    
    computeCache.value.set(cacheKey, result)
    return result
  })
  
  /**
   * 複数のリアクティビティトリガーを防ぐバッチ更新
   * @param {Array} updates - 更新オブジェクトの配列
   */
  const batchUpdate = (updates) => {
    // nextTickを使用してDOM更新をバッチ化
    nextTick(() => {
      updates.forEach(update => {
        if (update.type === 'metadata') {
          Object.assign(metadata.value, update.data)
        } else if (update.type === 'dataset') {
          largeDataset.value = update.data
        }
      })
    })
  }
  
  /**
   * 計算キャッシュをクリア
   */
  const clearCache = () => {
    computeCache.value.clear()
  }
  
  /**
   * 大きなリスト用の仮想スクロールヘルパー
   * @param {number} startIndex - 開始インデックス
   * @param {number} count - アイテム数
   */
  const getVirtualItems = (startIndex, count) => {
    return largeDataset.value.slice(startIndex, startIndex + count)
  }
  
  return {
    largeDataset: readonly(largeDataset),
    metadata: readonly(metadata),
    expensiveComputation,
    batchUpdate,
    clearCache,
    getVirtualItems
  }
})
```

## 📊 実用的なビジネスロジック例

### 通知システム

```javascript
// stores/notifications.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSupabase } from '@/composables/useSupabase'
import { useUserStore } from './user'

export const useNotificationsStore = defineStore('notifications', () => {
  const { supabase } = useSupabase()
  const userStore = useUserStore()
  
  // 状態
  const notifications = ref([])
  const loading = ref(false)
  const error = ref(null)
  const settings = ref({
    email: true,
    push: true,
    desktop: true,
    sound: false
  })
  
  // 計算プロパティ
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.read)
  )
  
  const unreadCount = computed(() => unreadNotifications.value.length)
  
  const recentNotifications = computed(() => 
    notifications.value
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 10)
  )
  
  const notificationsByType = computed(() => {
    const grouped = {}
    notifications.value.forEach(notification => {
      const type = notification.type
      if (!grouped[type]) {
        grouped[type] = []
      }
      grouped[type].push(notification)
    })
    return grouped
  })
  
  /**
   * 通知を取得
   */
  const fetchNotifications = async (options = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const { limit = 50, offset = 0 } = options
      
      const { data, error: fetchError } = await supabase
        .from('notifications')
        .select('*')
        .eq('user_id', userStore.user.id)
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1)
      
      if (fetchError) throw fetchError
      
      notifications.value = data || []
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 通知を既読にマーク
   */
  const markAsRead = async (notificationId) => {
    try {
      const { error: updateError } = await supabase
        .from('notifications')
        .update({ read: true, read_at: new Date().toISOString() })
        .eq('id', notificationId)
        .eq('user_id', userStore.user.id)
      
      if (updateError) throw updateError
      
      // ローカル状態を更新
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.read = true
        notification.read_at = new Date().toISOString()
      }
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  /**
   * 全通知を既読にマーク
   */
  const markAllAsRead = async () => {
    try {
      loading.value = true
      
      const unreadIds = unreadNotifications.value.map(n => n.id)
      
      const { error: updateError } = await supabase
        .from('notifications')
        .update({ read: true, read_at: new Date().toISOString() })
        .in('id', unreadIds)
        .eq('user_id', userStore.user.id)
      
      if (updateError) throw updateError
      
      // ローカル状態を更新
      notifications.value.forEach(notification => {
        if (!notification.read) {
          notification.read = true
          notification.read_at = new Date().toISOString()
        }
      })
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 通知を削除
   */
  const deleteNotification = async (notificationId) => {
    try {
      const { error: deleteError } = await supabase
        .from('notifications')
        .delete()
        .eq('id', notificationId)
        .eq('user_id', userStore.user.id)
      
      if (deleteError) throw deleteError
      
      // ローカル状態から削除
      notifications.value = notifications.value.filter(n => n.id !== notificationId)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  /**
   * 通知設定を更新
   */
  const updateSettings = async (newSettings) => {
    try {
      settings.value = { ...settings.value, ...newSettings }
      
      // サーバーに保存
      const { error: updateError } = await supabase
        .from('user_notification_settings')
        .upsert({
          user_id: userStore.user.id,
          settings: settings.value
        })
      
      if (updateError) throw updateError
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  /**
   * リアルタイム通知を初期化
   */
  const initializeRealtime = () => {
    if (!userStore.isAuthenticated) return
    
    const channel = supabase
      .channel('notifications')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'notifications',
        filter: `user_id=eq.${userStore.user.id}`
      }, (payload) => {
        // 新しい通知を追加
        notifications.value.unshift(payload.new)
        
        // デスクトップ通知を表示
        if (settings.value.desktop && 'Notification' in window) {
          new Notification(payload.new.title, {
            body: payload.new.message,
            icon: '/notification-icon.png'
          })
        }
        
        // サウンド再生
        if (settings.value.sound) {
          const audio = new Audio('/notification-sound.mp3')
          audio.play().catch(console.error)
        }
      })
      .subscribe()
    
    return channel
  }
  
  return {
    // 状態
    notifications: readonly(notifications),
    loading: readonly(loading),
    error: readonly(error),
    settings: readonly(settings),
    
    // 計算プロパティ
    unreadNotifications,
    unreadCount,
    recentNotifications,
    notificationsByType,
    
    // アクション
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    updateSettings,
    initializeRealtime
  }
}, {
  persist: {
    key: 'notifications-store',
    paths: ['settings']
  }
})
```

## ✅ 開発品質チェックリスト

### Piniaストア設計
- [ ] **単一責任**: 各ストアは明確な責任を持つ
- [ ] **状態の正規化**: データの重複を避ける
- [ ] **JSDoc**: 関数とデータ構造の適切なドキュメント化
- [ ] **エラーハンドリング**: 一貫したエラー処理パターン
- [ ] **ローディング状態**: 非同期操作の適切な状態管理

### パフォーマンス
- [ ] **適切なリアクティビティ**: 必要に応じてshallowRefを使用
- [ ] **メモ化**: 重い計算をキャッシュ
- [ ] **バッチ更新**: 複数の状態変更をまとめる
- [ ] **購読管理**: リアルタイム購読の適切なクリーンアップ
- [ ] **永続化**: 必要なデータのみ永続化

### セキュリティ
- [ ] **データ検証**: サーバーからのデータを検証
- [ ] **権限チェック**: ユーザー権限に基づくアクセス制御
- [ ] **機密データ**: 機密情報をストアに保存しない
- [ ] **入力サニタイズ**: ユーザー入力の適切な処理
- [ ] **セッション管理**: 認証状態の安全な管理

### テスト
- [ ] **ストアテスト**: アクションとゲッターのテスト
- [ ] **モッキング**: 外部依存関係のモック
- [ ] **エッジケース**: エラー状態とエッジケースのテスト
- [ ] **統合テスト**: ストア間の相互作用テスト
- [ ] **カバレッジ**: 十分なテストカバレッジ

## 🎯 ベストプラクティス

### 1. ストア設計原則

```javascript
// ✅ 良い例: 明確な責任分離
export const useUserStore = defineStore('user', () => {
  // ユーザー関連の状態とロジックのみ
  // 認証、プロフィール、設定に焦点
})

export const usePostsStore = defineStore('posts', () => {
  // 投稿関連の状態とロジックのみ
  // CRUD操作、フィルタリング、ページネーション
})

// ❌ 悪い例: 責任が混在
export const useAppStore = defineStore('app', () => {
  // ユーザー、投稿、通知、設定など全てを含む
  // テストが困難で保守性が低い
})
```

### 2. 状態管理パターン

```javascript
// ✅ 良い例: 正規化された状態
export const usePostsStore = defineStore('posts', () => {
  const posts = ref({})          // ID -> Post のマップ
  const postIds = ref([])        // 順序付きIDリスト
  const categories = ref({})     // ID -> Category のマップ
  
  const postsArray = computed(() => 
    postIds.value.map(id => posts.value[id])
  )
})

// ❌ 悪い例: 非正規化された状態
export const usePostsStore = defineStore('posts', () => {
  const posts = ref([])  // 重複したカテゴリ情報を含む
})
```

### 3. エラーハンドリング

```javascript
// ✅ 良い例: 構造化されたエラーハンドリング
export const useApiStore = defineStore('api', () => {
  const handleError = (error, context) => {
    const errorInfo = {
      message: error.message,
      code: error.code,
      timestamp: Date.now(),
      context
    }
    
    // エラー分類とユーザーフレンドリーなメッセージ
    if (error.code === 'NETWORK_ERROR') {
      errorInfo.userMessage = 'ネットワーク接続を確認してください'
    }
    
    return errorInfo
  }
})
```

### 4. リアルタイム管理

```javascript
// ✅ 良い例: クリーンアップ付きリアルタイム
export const useRealtimeStore = defineStore('realtime', () => {
  const subscriptions = ref(new Map())
  
  const subscribe = (table, handlers) => {
    // 購読を作成し、subscriptionsに保存
    // 適切なクリーンアップ機能を提供
  }
  
  onUnmounted(() => {
    // 全購読をクリーンアップ
    subscriptions.value.forEach(sub => sub.unsubscribe())
  })
})
```

## 📚 関連ドキュメント

- **[Vue Compositionパターン](./01_vue_composition_patterns.md)** - Composableとの統合
- **[Supabase連携パターン](./03_supabase_integration.md)** - データベース操作との連携
- **[Vite設定ガイド](./04_vite_configuration.md)** - ビルド設定とパフォーマンス最適化

## ベストプラクティス

1. **ストア命名**: `use`プレフィックスと明確な名前を使用
2. **状態構造**: フラットで正規化された状態を保持
3. **アクション**: 非同期でエラーハンドリングを適切に実装
4. **ゲッター**: 計算プロパティで派生状態を管理
5. **永続化**: 必要なデータのみ永続化
6. **パフォーマンス**: 大きなデータセットにはshallowRefを使用
7. **クリーンアップ**: リアルタイムチャンネルの購読解除
8. **TypeScript**: より良い開発体験と型安全性のために型を追加