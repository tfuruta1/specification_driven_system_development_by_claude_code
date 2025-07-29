# Supabase連携パターン集

Vue 3 Composition APIアプリケーションにSupabaseを統合するための重要パターンを解説します。

## 📚 目次

1. [マルチAI協調最適化機能](#マルチai協調最適化機能)
2. [Supabaseクライアント設定](#supabaseクライアント設定)
3. [認証パターン](#認証パターン)
4. [データベースクエリパターン](#データベースクエリパターン)
5. [リアルタイム購読パターン](#リアルタイム購読パターン)
6. [ファイルストレージパターン](#ファイルストレージパターン)
7. [Edge Functions統合](#edge-functions統合)
8. [エラーハンドリング](#エラーハンドリング)
9. [パフォーマンス最適化](#パフォーマンス最適化)
10. [型安全性](#型安全性)

## マルチAI協調最適化機能

### AI協調パフォーマンス監視
```javascript
// services/monitoring/aiCollaborativeMonitoring.js
export class AICollaborativeMonitoring {
  constructor() {
    this.geminiCLI = new GeminiDataAnalyst()
    this.o3MCP = new O3DatabaseSpecialist()
    this.performanceMetrics = new Map()
  }
  
  async analyzePerformancePatterns() {
    // Gemini CLI によるデータパターン分析
    const dataInsights = await this.geminiCLI.analyzeSupabasePatterns({
      timeRange: '24h',
      includeUserBehavior: true,
      focusAreas: ['realtime', 'rls', 'queries']
    })
    
    // o3 MCP による技術検証
    const techValidation = await this.o3MCP.validateArchitecture({
      performanceTargets: dataInsights.recommendations,
      optimizationFocus: ['postgresql', 'edge_functions', 'storage']
    })
    
    return this.synthesizeOptimizations(dataInsights, techValidation)
  }
  
  synthesizeOptimizations(dataInsights, techValidation) {
    return {
      queryOptimizations: this.mergeQueryRecommendations(dataInsights, techValidation),
      realtimeOptimizations: this.optimizeRealtimeChannels(dataInsights),
      rlsOptimizations: this.optimizeRLSPolicies(techValidation),
      edgeFunctionRecommendations: this.identifyEdgeFunctionOpportunities(dataInsights)
    }
  }
}
```

### o3 MCP データベーススペシャリスト統合
```javascript
// services/database/o3MCPIntegration.js
export class O3MCPDatabaseIntegration {
  constructor(supabaseClient) {
    this.supabase = supabaseClient
    this.o3MCP = new O3DatabaseSpecialist()
  }
  
  async optimizeQuery(query, params) {
    // o3 MCP による実時間クエリ最適化
    const optimizationPlan = await this.o3MCP.analyzeQuery({
      query,
      params,
      executionContext: 'supabase_postgresql'
    })
    
    if (optimizationPlan.suggestAlternative) {
      return await this.executeOptimizedQuery(optimizationPlan.optimizedQuery, params)
    }
    
    return await this.supabase.rpc(query, params)
  }
  
  async monitorPerformance() {
    // リアルタイムパフォーマンス監視
    const metrics = await this.o3MCP.getPerformanceMetrics()
    
    if (metrics.slowQueries.length > 0) {
      await this.handleSlowQueries(metrics.slowQueries)
    }
    
    return metrics
  }
}
```

## Supabaseクライアント設定

### 基本的なクライアント設定

```javascript
// lib/supabase.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

/**
 * Supabaseクライアントインスタンス
 * @type {import('@supabase/supabase-js').SupabaseClient}
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  db: {
    schema: 'public'
  },
  global: {
    headers: { 'x-my-custom-header': 'my-app-name' }
  }
})
```

### 環境設定

```bash
# .env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### SupabaseクライアントのComposable

```javascript
// composables/useSupabase.js
import { supabase } from '@/lib/supabase'

/**
 * Supabaseクライアントへのアクセスを提供
 * @returns {Object} Supabaseユーティリティ
 */
export function useSupabase() {
  return {
    supabase,
    auth: supabase.auth,
    storage: supabase.storage,
    from: (table) => supabase.from(table),
    rpc: (fn, params) => supabase.rpc(fn, params)
  }
}
```

## 認証パターン

### 認証Composable

```javascript
// composables/useAuth.js
import { ref, computed, onMounted } from 'vue'
import { useSupabase } from './useSupabase'
import { useRouter } from 'vue-router'

/**
 * 認証状態とメソッド
 * @returns {Object} 認証ユーティリティ
 */
export function useAuth() {
  const { supabase } = useSupabase()
  const router = useRouter()
  
  const user = ref(null)
  const session = ref(null)
  const loading = ref(true)
  const error = ref(null)
  
  const isAuthenticated = computed(() => !!session.value)
  const isAnonymous = computed(() => !!session.value && !session.value.user.email)
  
  /**
   * メールとパスワードでサインアップ
   * @param {string} email - ユーザーメール
   * @param {string} password - ユーザーパスワード
   * @param {Object} metadata - 追加のユーザーメタデータ
   * @returns {Promise<Object>} サインアップ結果
   */
  const signUp = async (email, password, metadata = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata
        }
      })
      
      if (signUpError) throw signUpError
      
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * メールとパスワードでサインイン
   * @param {string} email - ユーザーメール
   * @param {string} password - ユーザーパスワード
   * @returns {Promise<Object>} サインイン結果
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
      
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * OAuthプロバイダーでサインイン
   * @param {string} provider - OAuth プロバイダー（google, github等）
   * @param {Object} options - 追加オプション
   * @returns {Promise<Object>} OAuth サインイン結果
   */
  const signInWithOAuth = async (provider, options = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: oauthError } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          ...options
        }
      })
      
      if (oauthError) throw oauthError
      
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 現在のユーザーをサインアウト
   * @returns {Promise<void>}
   */
  const signOut = async () => {
    try {
      loading.value = true
      await supabase.auth.signOut()
      router.push('/login')
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  /**
   * メール用パスワードリセット
   * @param {string} email - ユーザーメール
   * @returns {Promise<Object>} リセット結果
   */
  const resetPassword = async (email) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: resetError } = await supabase.auth.resetPasswordForEmail(
        email,
        {
          redirectTo: `${window.location.origin}/auth/reset-password`
        }
      )
      
      if (resetError) throw resetError
      
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * ユーザーパスワードを更新
   * @param {string} password - 新しいパスワード
   * @returns {Promise<Object>} 更新結果
   */
  const updatePassword = async (password) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: updateError } = await supabase.auth.updateUser({
        password
      })
      
      if (updateError) throw updateError
      
      return { data, error: null }
    } catch (err) {
      error.value = err.message
      return { data: null, error: err }
    } finally {
      loading.value = false
    }
  }
  
  // 認証状態の初期化
  onMounted(() => {
    // 初期セッションを取得
    supabase.auth.getSession().then(({ data: { session } }) => {
      session.value = session
      user.value = session?.user ?? null
      loading.value = false
    })
    
    // 認証状態の変更を監視
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        session.value = session
        user.value = session?.user ?? null
        loading.value = false
        
        // 認証イベントを処理
        if (event === 'SIGNED_IN') {
          router.push('/dashboard')
        } else if (event === 'SIGNED_OUT') {
          router.push('/login')
        }
      }
    )
    
    // 購読をクリーンアップ
    return () => subscription.unsubscribe()
  })
  
  return {
    user: readonly(user),
    session: readonly(session),
    loading: readonly(loading),
    error: readonly(error),
    isAuthenticated,
    isAnonymous,
    signUp,
    signIn,
    signInWithOAuth,
    signOut,
    resetPassword,
    updatePassword
  }
}
```

### ルートガード

```javascript
// router/guards.js
import { useAuth } from '@/composables/useAuth'

/**
 * 保護されたルート用の認証ガード
 * @param {Object} to - 対象ルート
 * @param {Object} from - 元ルート
 * @param {Function} next - ナビゲーションコールバック
 */
export function authGuard(to, from, next) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading.value) {
    // 認証状態の読み込みを待機
    return
  }
  
  if (!isAuthenticated.value) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
}

/**
 * パブリックルート用のゲストガード
 * @param {Object} to - 対象ルート
 * @param {Object} from - 元ルート
 * @param {Function} next - ナビゲーションコールバック
 */
export function guestGuard(to, from, next) {
  const { isAuthenticated } = useAuth()
  
  if (isAuthenticated.value) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
}
```

## データベースクエリパターン

### CRUD操作Composable

```javascript
// composables/useDatabase.js
import { ref, computed } from 'vue'
import { useSupabase } from './useSupabase'

/**
 * 特定テーブルのデータベース操作
 * @param {string} tableName - データベーステーブル名
 * @returns {Object} データベースユーティリティ
 */
export function useDatabase(tableName) {
  const { supabase } = useSupabase()
  
  const data = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const isEmpty = computed(() => data.value.length === 0)
  const count = computed(() => data.value.length)
  
  /**
   * オプションのフィルタリング付きで全レコードを取得
   * @param {Object} options - クエリオプション
   * @returns {Promise<Array>} レコード配列
   */
  const fetchAll = async (options = {}) => {
    try {
      loading.value = true
      error.value = null
      
      let query = supabase.from(tableName).select(options.select || '*')
      
      // フィルターを適用
      if (options.filters) {
        options.filters.forEach(filter => {
          query = query[filter.method](...filter.args)
        })
      }
      
      // 順序を適用
      if (options.orderBy) {
        query = query.order(options.orderBy.column, {
          ascending: options.orderBy.ascending ?? true
        })
      }
      
      // ページネーションを適用
      if (options.range) {
        query = query.range(options.range.from, options.range.to)
      }
      
      const { data: records, error: fetchError } = await query
      
      if (fetchError) throw fetchError
      
      data.value = records || []
      return records
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * IDで単一レコードを取得
   * @param {string|number} id - レコードID
   * @param {string} select - 選択するフィールド
   * @returns {Promise<Object>} 単一レコード
   */
  const fetchById = async (id, select = '*') => {
    try {
      loading.value = true
      error.value = null
      
      const { data: record, error: fetchError } = await supabase
        .from(tableName)
        .select(select)
        .eq('id', id)
        .single()
      
      if (fetchError) throw fetchError
      
      return record
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 新しいレコードを作成
   * @param {Object} record - レコードデータ
   * @returns {Promise<Object>} 作成されたレコード
   */
  const create = async (record) => {
    try {
      loading.value = true
      error.value = null
      
      const { data: created, error: createError } = await supabase
        .from(tableName)
        .insert(record)
        .select()
        .single()
      
      if (createError) throw createError
      
      data.value.push(created)
      return created
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 既存レコードを更新
   * @param {string|number} id - レコードID
   * @param {Object} updates - 更新データ
   * @returns {Promise<Object>} 更新されたレコード
   */
  const update = async (id, updates) => {
    try {
      loading.value = true
      error.value = null
      
      const { data: updated, error: updateError } = await supabase
        .from(tableName)
        .update(updates)
        .eq('id', id)
        .select()
        .single()
      
      if (updateError) throw updateError
      
      // ローカルデータを更新
      const index = data.value.findIndex(item => item.id === id)
      if (index !== -1) {
        data.value[index] = updated
      }
      
      return updated
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * IDでレコードを削除
   * @param {string|number} id - レコードID
   * @returns {Promise<void>}
   */
  const remove = async (id) => {
    try {
      loading.value = true
      error.value = null
      
      const { error: deleteError } = await supabase
        .from(tableName)
        .delete()
        .eq('id', id)
      
      if (deleteError) throw deleteError
      
      // ローカルデータから削除
      data.value = data.value.filter(item => item.id !== id)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * レコードをアップサート（挿入または更新）
   * @param {Object} record - レコードデータ
   * @param {Object} options - アップサートオプション
   * @returns {Promise<Object>} アップサートされたレコード
   */
  const upsert = async (record, options = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const { data: upserted, error: upsertError } = await supabase
        .from(tableName)
        .upsert(record, {
          onConflict: options.onConflict || 'id',
          ignoreDuplicates: options.ignoreDuplicates || false
        })
        .select()
        .single()
      
      if (upsertError) throw upsertError
      
      // ローカルデータを更新
      const index = data.value.findIndex(item => item.id === upserted.id)
      if (index !== -1) {
        data.value[index] = upserted
      } else {
        data.value.push(upserted)
      }
      
      return upserted
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    isEmpty,
    count,
    fetchAll,
    fetchById,
    create,
    update,
    remove,
    upsert
  }
}
```

### 高度なクエリパターン

```javascript
// composables/useAdvancedQueries.js
import { useSupabase } from './useSupabase'

/**
 * 高度なクエリパターンとユーティリティ
 * @returns {Object} 高度なクエリユーティリティ
 */
export function useAdvancedQueries() {
  const { supabase } = useSupabase()
  
  /**
   * 複数カラムでの全文検索
   * @param {string} table - テーブル名
   * @param {string} query - 検索クエリ
   * @param {Array} columns - 検索対象カラム
   * @returns {Promise<Array>} 検索結果
   */
  const fullTextSearch = async (table, query, columns = []) => {
    let searchQuery = supabase.from(table).select('*')
    
    if (columns.length > 0) {
      // 特定カラムを検索
      const orConditions = columns.map(col => `${col}.ilike.%${query}%`).join(',')
      searchQuery = searchQuery.or(orConditions)
    } else {
      // Supabaseの全文検索を使用（利用可能な場合）
      searchQuery = searchQuery.textSearch('fts', query)
    }
    
    const { data, error } = await searchQuery
    if (error) throw error
    
    return data
  }
  
  /**
   * メタデータ付きページネーションクエリ
   * @param {string} table - テーブル名
   * @param {Object} options - ページネーションオプション
   * @returns {Promise<Object>} メタデータ付きページネーション結果
   */
  const paginatedQuery = async (table, options = {}) => {
    const {
      page = 1,
      limit = 10,
      orderBy = 'created_at',
      ascending = false,
      filters = []
    } = options
    
    const from = (page - 1) * limit
    const to = from + limit - 1
    
    // クエリを構築
    let query = supabase.from(table).select('*', { count: 'exact' })
    
    // フィルターを適用
    filters.forEach(filter => {
      query = query[filter.method](...filter.args)
    })
    
    // 順序と範囲を適用
    query = query.order(orderBy, { ascending }).range(from, to)
    
    const { data, error, count } = await query
    if (error) throw error
    
    return {
      data,
      pagination: {
        page,
        limit,
        total: count,
        totalPages: Math.ceil(count / limit),
        hasNext: to < count - 1,
        hasPrev: page > 1
      }
    }
  }
  
  /**
   * 集計クエリ
   * @param {string} table - テーブル名
   * @param {Object} options - 集計オプション
   * @returns {Promise<Object>} 集計結果
   */
  const aggregate = async (table, options = {}) => {
    const { groupBy, aggregates, filters = [] } = options
    
    let query = supabase.from(table)
    
    // 集計付きでselectを構築
    const selectFields = []
    if (groupBy) selectFields.push(groupBy)
    
    aggregates.forEach(agg => {
      selectFields.push(`${agg.function}(${agg.column})`)
    })
    
    query = query.select(selectFields.join(','))
    
    // フィルターを適用
    filters.forEach(filter => {
      query = query[filter.method](...filter.args)
    })
    
    // 指定されている場合はグループ化
    if (groupBy) {
      query = query.order(groupBy)
    }
    
    const { data, error } = await query
    if (error) throw error
    
    return data
  }
  
  return {
    fullTextSearch,
    paginatedQuery,
    aggregate
  }
}
```

## リアルタイム購読パターン

### リアルタイムComposable

```javascript
// composables/useRealtime.js
import { ref, onUnmounted } from 'vue'
import { useSupabase } from './useSupabase'

/**
 * 堅牢なリアルタイム接続管理
 * @returns {Object} リアルタイム接続ユーティリティ
 */
export function useRealtimeConnection() {
  const { supabase } = useSupabase()
  
  const connections = ref(new Map())
  const reconnectAttempts = ref(new Map())
  const connectionStatus = ref(new Map())
  const maxReconnectAttempts = 5
  const baseReconnectDelay = 1000
  
  /**
   * 自動再接続機能付きチャンネル接続
   * @param {string} channelName - チャンネル名
   * @param {Object} config - チャンネル設定
   * @returns {Object} チャンネルと制御関数
   */
  const connectWithReconnect = (channelName, config = {}) => {
    const connect = () => {
      const channel = supabase.channel(channelName, config.options)
      
      // イベントリスナーを設定
      if (config.events) {
        config.events.forEach(({ event, callback }) => {
          channel.on(event.type, event.filter || {}, callback)
        })
      }
      
      channel.subscribe((status) => {
        connectionStatus.value.set(channelName, status)
        
        if (status === 'SUBSCRIBED') {
          console.log(`${channelName}: 接続成功`)
          reconnectAttempts.value.set(channelName, 0) // リセット
          
          if (config.onConnect) {
            config.onConnect(channel)
          }
        } else if (status === 'CLOSED') {
          const attempts = reconnectAttempts.value.get(channelName) || 0
          
          if (attempts < maxReconnectAttempts) {
            const delay = baseReconnectDelay * Math.pow(2, attempts)
            console.log(`${channelName}: 再接続試行 ${attempts + 1}/${maxReconnectAttempts} (${delay}ms後)`)
            
            reconnectAttempts.value.set(channelName, attempts + 1)
            
            setTimeout(() => {
              // 既存の接続をクリーンアップ
              if (connections.value.has(channelName)) {
                supabase.removeChannel(connections.value.get(channelName))
              }
              
              // 再接続
              connect()
            }, delay)
          } else {
            console.error(`${channelName}: 最大再接続試行回数に達しました`)
            
            if (config.onMaxReconnectReached) {
              config.onMaxReconnectReached(channelName)
            }
          }
        } else if (status === 'CHANNEL_ERROR') {
          console.error(`${channelName}: チャンネルエラー`)
          
          if (config.onError) {
            config.onError(new Error(`チャンネル接続エラー: ${channelName}`))
          }
        }
      })
      
      connections.value.set(channelName, channel)
      return channel
    }
    
    return connect()
  }
  
  /**
   * 接続を手動で切断
   * @param {string} channelName - チャンネル名
   */
  const disconnect = (channelName) => {
    const channel = connections.value.get(channelName)
    if (channel) {
      supabase.removeChannel(channel)
      connections.value.delete(channelName)
      connectionStatus.value.delete(channelName)
      reconnectAttempts.value.delete(channelName)
      console.log(`${channelName}: 手動切断`)
    }
  }
  
  /**
   * 全接続を切断
   */
  const disconnectAll = () => {
    connections.value.forEach((channel, channelName) => {
      supabase.removeChannel(channel)
      console.log(`${channelName}: 切断`)
    })
    
    connections.value.clear()
    connectionStatus.value.clear()
    reconnectAttempts.value.clear()
  }
  
  /**
   * 接続状態を取得
   * @param {string} channelName - チャンネル名
   * @returns {string} 接続状態
   */
  const getConnectionStatus = (channelName) => {
    return connectionStatus.value.get(channelName) || 'disconnected'
  }
  
  /**
   * 接続が有効かチェック
   * @param {string} channelName - チャンネル名
   * @returns {boolean} 接続状態
   */
  const isConnected = (channelName) => {
    return getConnectionStatus(channelName) === 'SUBSCRIBED'
  }
  
  /**
   * 接続統計を取得
   * @returns {Object} 接続統計情報
   */
  const getConnectionStats = () => {
    const stats = {
      total: connections.value.size,
      connected: 0,
      connecting: 0,
      failed: 0,
      channels: []
    }
    
    connectionStatus.value.forEach((status, channelName) => {
      const attempts = reconnectAttempts.value.get(channelName) || 0
      
      stats.channels.push({
        name: channelName,
        status,
        attempts
      })
      
      if (status === 'SUBSCRIBED') {
        stats.connected++
      } else if (status === 'JOINING') {
        stats.connecting++
      } else {
        stats.failed++
      }
    })
    
    return stats
  }
  
  // クリーンアップ
  onUnmounted(() => {
    disconnectAll()
  })
  
  return {
    connections: readonly(connections),
    connectionStatus: readonly(connectionStatus),
    connectWithReconnect,
    disconnect,
    disconnectAll,
    getConnectionStatus,
    isConnected,
    getConnectionStats
  }
}
```

### プレゼンス追跡

```javascript
// composables/usePresence.js
import { ref, onUnmounted } from 'vue'
import { useSupabase } from './useSupabase'
import { useAuth } from './useAuth'

/**
 * リアルタイムプレゼンス追跡
 * @param {string} channelName - プレゼンスチャンネル名
 * @returns {Object} プレゼンスユーティリティ
 */
export function usePresence(channelName) {
  const { supabase } = useSupabase()
  const { user } = useAuth()
  
  const presenceState = ref({})
  const onlineUsers = ref([])
  const channel = ref(null)
  
  /**
   * プレゼンスチャンネルに参加
   * @param {Object} metadata - ユーザーメタデータ
   * @returns {void}
   */
  const join = (metadata = {}) => {
    if (!user.value) return
    
    const userPresence = {
      user_id: user.value.id,
      email: user.value.email,
      online_at: new Date().toISOString(),
      ...metadata
    }
    
    channel.value = supabase.channel(channelName, {
      config: {
        presence: {
          key: user.value.id
        }
      }
    })
    
    channel.value
      .on('presence', { event: 'sync' }, () => {
        const state = channel.value.presenceState()
        presenceState.value = state
        onlineUsers.value = Object.values(state).flat()
      })
      .on('presence', { event: 'join' }, ({ key, newPresences }) => {
        // ユーザー参加を処理
      })
      .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
        // ユーザー退出を処理
      })
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          await channel.value.track(userPresence)
        }
      })
  }
  
  /**
   * プレゼンスチャンネルから退出
   * @returns {void}
   */
  const leave = () => {
    if (channel.value) {
      supabase.removeChannel(channel.value)
      channel.value = null
      presenceState.value = {}
      onlineUsers.value = []
    }
  }
  
  /**
   * プレゼンスメタデータを更新
   * @param {Object} metadata - 更新されたメタデータ
   * @returns {void}
   */
  const updatePresence = (metadata) => {
    if (channel.value && user.value) {
      const userPresence = {
        user_id: user.value.id,
        email: user.value.email,
        online_at: new Date().toISOString(),
        ...metadata
      }
      
      channel.value.track(userPresence)
    }
  }
  
  // アンマウント時のクリーンアップ
  onUnmounted(() => {
    leave()
  })
  
  return {
    presenceState: readonly(presenceState),
    onlineUsers: readonly(onlineUsers),
    join,
    leave,
    updatePresence
  }
}
```

## ファイルストレージパターン

### ファイルアップロードComposable

```javascript
// composables/useStorage.js
import { ref } from 'vue'
import { useSupabase } from './useSupabase'
import { useAuth } from './useAuth'

/**
 * ファイルストレージ操作
 * @param {string} bucket - ストレージバケット名
 * @returns {Object} ストレージユーティリティ
 */
export function useStorage(bucket) {
  const { supabase } = useSupabase()
  const { user } = useAuth()
  
  const uploading = ref(false)
  const downloading = ref(false)
  const error = ref(null)
  
  /**
   * ファイルをストレージにアップロード
   * @param {File} file - アップロードするファイル
   * @param {Object} options - アップロードオプション
   * @returns {Promise<Object>} アップロード結果
   */
  const uploadFile = async (file, options = {}) => {
    try {
      uploading.value = true
      error.value = null
      
      const {
        path,
        fileName = file.name,
        upsert = false,
        metadata = {}
      } = options
      
      // ファイルパスを生成
      const filePath = path || `${user.value.id}/${Date.now()}-${fileName}`
      
      // ファイルをアップロード
      const { data, error: uploadError } = await supabase.storage
        .from(bucket)
        .upload(filePath, file, {
          upsert,
          metadata: {
            ...metadata,
            originalName: file.name,
            contentType: file.type,
            size: file.size
          }
        })
      
      if (uploadError) throw uploadError
      
      // パブリックURLを取得
      const { data: { publicUrl } } = supabase.storage
        .from(bucket)
        .getPublicUrl(filePath)
      
      return {
        path: data.path,
        fullPath: data.fullPath,
        publicUrl,
        metadata: data.metadata
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      uploading.value = false
    }
  }
  
  /**
   * 複数ファイルをアップロード
   * @param {FileList} files - アップロードするファイル
   * @param {Object} options - アップロードオプション
   * @returns {Promise<Array>} アップロード結果
   */
  const uploadMultiple = async (files, options = {}) => {
    const results = []
    
    for (const file of files) {
      try {
        const result = await uploadFile(file, {
          ...options,
          path: options.path ? `${options.path}/${file.name}` : undefined
        })
        results.push({ success: true, file: file.name, data: result })
      } catch (err) {
        results.push({ success: false, file: file.name, error: err.message })
      }
    }
    
    return results
  }
  
  /**
   * ストレージからファイルをダウンロード
   * @param {string} path - ファイルパス
   * @returns {Promise<Blob>} ファイルBlob
   */
  const downloadFile = async (path) => {
    try {
      downloading.value = true
      error.value = null
      
      const { data, error: downloadError } = await supabase.storage
        .from(bucket)
        .download(path)
      
      if (downloadError) throw downloadError
      
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      downloading.value = false
    }
  }
  
  /**
   * ストレージからファイルを削除
   * @param {string} path - ファイルパス
   * @returns {Promise<void>}
   */
  const deleteFile = async (path) => {
    try {
      error.value = null
      
      const { error: deleteError } = await supabase.storage
        .from(bucket)
        .remove([path])
      
      if (deleteError) throw deleteError
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  /**
   * プライベートファイル用の署名付きURLを取得
   * @param {string} path - ファイルパス
   * @param {number} expiresIn - URL有効期限（秒）
   * @returns {Promise<string>} 署名付きURL
   */
  const getSignedUrl = async (path, expiresIn = 3600) => {
    try {
      error.value = null
      
      const { data, error: urlError } = await supabase.storage
        .from(bucket)
        .createSignedUrl(path, expiresIn)
      
      if (urlError) throw urlError
      
      return data.signedUrl
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  /**
   * ディレクトリ内のファイルをリスト
   * @param {string} folder - フォルダーパス
   * @param {Object} options - リストオプション
   * @returns {Promise<Array>} ファイルリスト
   */
  const listFiles = async (folder = '', options = {}) => {
    try {
      error.value = null
      
      const { data, error: listError } = await supabase.storage
        .from(bucket)
        .list(folder, {
          limit: options.limit || 100,
          offset: options.offset || 0,
          sortBy: options.sortBy || { column: 'name', order: 'asc' }
        })
      
      if (listError) throw listError
      
      return data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  return {
    uploading: readonly(uploading),
    downloading: readonly(downloading),
    error: readonly(error),
    uploadFile,
    uploadMultiple,
    downloadFile,
    deleteFile,
    getSignedUrl,
    listFiles
  }
}
```

## エラーハンドリング

### グローバルエラーハンドラー

```javascript
// composables/useErrorHandler.js
import { ref } from 'vue'

const globalErrors = ref([])

/**
 * グローバルエラーハンドリングユーティリティ
 * @returns {Object} エラーハンドリングユーティリティ
 */
export function useErrorHandler() {
  /**
   * Supabaseエラーを処理
   * @param {Error} error - Supabaseエラー
   * @returns {Object} フォーマットされたエラー
   */
  const handleSupabaseError = (error) => {
    const formattedError = {
      id: Date.now(),
      timestamp: new Date(),
      type: 'supabase',
      code: error.code || 'UNKNOWN',
      message: error.message || '不明なエラーが発生しました',
      details: error.details,
      hint: error.hint
    }
    
    // 一般的なエラーを分類
    if (error.code === 'PGRST116') {
      formattedError.category = 'not_found'
      formattedError.userMessage = '要求されたリソースが見つかりませんでした'
    } else if (error.code === '23505') {
      formattedError.category = 'duplicate'
      formattedError.userMessage = 'このレコードは既に存在します'
    } else if (error.code === '42501') {
      formattedError.category = 'permission'
      formattedError.userMessage = 'この操作を実行する権限がありません'
    } else if (error.message.includes('JWT')) {
      formattedError.category = 'auth'
      formattedError.userMessage = 'セッションが期限切れです。再度ログインしてください'
    } else {
      formattedError.category = 'unknown'
      formattedError.userMessage = '予期しないエラーが発生しました'
    }
    
    globalErrors.value.push(formattedError)
    return formattedError
  }
  
  /**
   * 全エラーをクリア
   * @returns {void}
   */
  const clearErrors = () => {
    globalErrors.value = []
  }
  
  /**
   * 特定エラーをクリア
   * @param {number} id - エラーID
   * @returns {void}
   */
  const clearError = (id) => {
    globalErrors.value = globalErrors.value.filter(error => error.id !== id)
  }
  
  return {
    errors: readonly(globalErrors),
    handleSupabaseError,
    clearErrors,
    clearError
  }
}
```

## パフォーマンス最適化

### クエリ最適化パターン

```javascript
// composables/useOptimizedQueries.js
import { ref, computed } from 'vue'
import { useSupabase } from './useSupabase'

/**
 * キャッシュ付き最適化クエリパターン
 * @returns {Object} 最適化クエリユーティリティ
 */
export function useOptimizedQueries() {
  const { supabase } = useSupabase()
  
  const cache = ref(new Map())
  const loading = ref(new Set())
  
  /**
   * TTL付きキャッシュクエリ
   * @param {string} key - キャッシュキー
   * @param {Function} queryFn - クエリ関数
   * @param {number} ttl - 生存時間（ミリ秒）
   * @returns {Promise<any>} クエリ結果
   */
  const cachedQuery = async (key, queryFn, ttl = 300000) => {
    // キャッシュをチェック
    const cached = cache.value.get(key)
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.data
    }
    
    // 重複クエリを防止
    if (loading.value.has(key)) {
      return new Promise((resolve) => {
        const checkLoading = () => {
          if (!loading.value.has(key)) {
            const result = cache.value.get(key)
            resolve(result ? result.data : null)
          } else {
            setTimeout(checkLoading, 100)
          }
        }
        checkLoading()
      })
    }
    
    try {
      loading.value.add(key)
      const data = await queryFn()
      
      cache.value.set(key, {
        data,
        timestamp: Date.now()
      })
      
      return data
    } finally {
      loading.value.delete(key)
    }
  }
  
  /**
   * 複数クエリをバッチ処理
   * @param {Array} queries - クエリオブジェクトの配列
   * @returns {Promise<Array>} クエリ結果
   */
  const batchQueries = async (queries) => {
    const promises = queries.map(async ({ key, query, ttl }) => {
      try {
        const result = await cachedQuery(key, query, ttl)
        return { success: true, key, data: result }
      } catch (error) {
        return { success: false, key, error: error.message }
      }
    })
    
    return Promise.all(promises)
  }
  
  /**
   * キャッシュエントリを無効化
   * @param {string} key - 無効化するキャッシュキー
   * @returns {void}
   */
  const invalidateCache = (key) => {
    cache.value.delete(key)
  }
  
  /**
   * 全キャッシュをクリア
   * @returns {void}
   */
  const clearCache = () => {
    cache.value.clear()
  }
  
  const cacheSize = computed(() => cache.value.size)
  const isLoading = (key) => loading.value.has(key)
  
  return {
    cacheSize,
    cachedQuery,
    batchQueries,
    invalidateCache,
    clearCache,
    isLoading
  }
}
```

## JSDocによる型定義

### JavaScript用の型定義

```javascript
// types/supabase.js
/**
 * データベーステーブルの行データ
 * @typedef {Object} Tables
 */

/**
 * ユーザーテーブルの行データ
 * @typedef {Object} UserRow
 * @property {string} id - ユーザーID
 * @property {string} email - メールアドレス
 * @property {string} created_at - 作成日時
 * @property {string} [first_name] - 名前
 * @property {string} [last_name] - 姓
 * @property {string} [avatar_url] - アバター画像URL
 */

/**
 * 投稿テーブルの行データ
 * @typedef {Object} PostRow
 * @property {string} id - 投稿ID
 * @property {string} title - タイトル
 * @property {string} content - 内容
 * @property {string} user_id - 作成者ID
 * @property {string} created_at - 作成日時
 * @property {boolean} published - 公開状態
 */

/**
 * Supabaseレスポンス
 * @template T
 * @typedef {Object} SupabaseResponse
 * @property {T|null} data - レスポンスデータ
 * @property {Error|null} error - エラー情報
 */

/**
 * ページネーション付きレスポンス
 * @template T
 * @typedef {Object} PaginatedResponse
 * @property {T[]} data - データ配列
 * @property {Object} pagination - ページネーション情報
 * @property {number} pagination.page - 現在のページ
 * @property {number} pagination.limit - 1ページあたりの件数
 * @property {number} pagination.total - 総件数
 * @property {number} pagination.totalPages - 総ページ数
 * @property {boolean} pagination.hasNext - 次のページの有無
 * @property {boolean} pagination.hasPrev - 前のページの有無
 */

/**
 * リアルタイムペイロード
 * @template T
 * @typedef {Object} RealtimePayload
 * @property {'INSERT'|'UPDATE'|'DELETE'} eventType - イベントタイプ
 * @property {T} new - 新しいレコード
 * @property {T} old - 古いレコード
 */

/**
 * 認証ユーザー情報
 * @typedef {Object} AuthUser
 * @property {string} id - ユーザーID
 * @property {string} email - メールアドレス
 * @property {Object} user_metadata - ユーザーメタデータ
 * @property {string} created_at - 作成日時
 */

/**
 * 認証セッション情報
 * @typedef {Object} AuthSession
 * @property {string} access_token - アクセストークン
 * @property {string} refresh_token - リフレッシュトークン
 * @property {number} expires_in - 有効期限（秒）
 * @property {AuthUser} user - ユーザー情報
 */

// エクスポート（JSDocでの型定義用）
export {}
```

## 🎯 実用的なビジネスロジック例

### プロジェクト管理システム

```javascript
// composables/useProjectManagement.js
import { ref, computed } from 'vue'
import { useSupabase } from './useSupabase'
import { useAuth } from './useAuth'

export function useProjectManagement() {
  const { supabase } = useSupabase()
  const { user } = useAuth()
  
  // 状態
  const projects = ref([])
  const tasks = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 計算プロパティ
  const activeProjects = computed(() => 
    projects.value.filter(p => p.status === 'active')
  )
  
  const myTasks = computed(() => 
    tasks.value.filter(t => t.assigned_to === user.value?.id)
  )
  
  const overdueTasks = computed(() => {
    const today = new Date()
    return tasks.value.filter(t => 
      new Date(t.due_date) < today && t.status !== 'completed'
    )
  })
  
  const projectProgress = computed(() => {
    return projects.value.map(project => {
      const projectTasks = tasks.value.filter(t => t.project_id === project.id)
      const completedTasks = projectTasks.filter(t => t.status === 'completed')
      
      return {
        ...project,
        totalTasks: projectTasks.length,
        completedTasks: completedTasks.length,
        progress: projectTasks.length > 0 
          ? Math.round((completedTasks.length / projectTasks.length) * 100)
          : 0
      }
    })
  })
  
  /**
   * プロジェクトを取得
   */
  const fetchProjects = async () => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: fetchError } = await supabase
        .from('projects')
        .select(`
          *,
          project_members!inner (
            user_id,
            role,
            profiles (
              first_name,
              last_name,
              avatar_url
            )
          )
        `)
        .eq('project_members.user_id', user.value.id)
        .order('created_at', { ascending: false })
      
      if (fetchError) throw fetchError
      
      projects.value = data || []
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * タスクを取得
   */
  const fetchTasks = async (projectId = null) => {
    try {
      loading.value = true
      error.value = null
      
      let query = supabase
        .from('tasks')
        .select(`
          *,
          projects (
            name,
            color
          ),
          assigned_user:profiles!tasks_assigned_to_fkey (
            first_name,
            last_name,
            avatar_url
          ),
          created_by_user:profiles!tasks_created_by_fkey (
            first_name,
            last_name
          )
        `)
        .order('created_at', { ascending: false })
      
      if (projectId) {
        query = query.eq('project_id', projectId)
      }
      
      const { data, error: fetchError } = await query
      
      if (fetchError) throw fetchError
      
      tasks.value = data || []
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 新しいプロジェクトを作成
   */
  const createProject = async (projectData) => {
    try {
      loading.value = true
      error.value = null
      
      const { data: project, error: projectError } = await supabase
        .from('projects')
        .insert({
          ...projectData,
          created_by: user.value.id
        })
        .select()
        .single()
      
      if (projectError) throw projectError
      
      // 作成者をプロジェクトメンバーとして追加
      const { error: memberError } = await supabase
        .from('project_members')
        .insert({
          project_id: project.id,
          user_id: user.value.id,
          role: 'owner'
        })
      
      if (memberError) throw memberError
      
      projects.value.unshift(project)
      return project
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 新しいタスクを作成
   */
  const createTask = async (taskData) => {
    try {
      loading.value = true
      error.value = null
      
      const { data, error: createError } = await supabase
        .from('tasks')
        .insert({
          ...taskData,
          created_by: user.value.id
        })
        .select(`
          *,
          projects (
            name,
            color
          ),
          assigned_user:profiles!tasks_assigned_to_fkey (
            first_name,
            last_name,
            avatar_url
          )
        `)
        .single()
      
      if (createError) throw createError
      
      tasks.value.unshift(data)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * タスクステータスを更新
   */
  const updateTaskStatus = async (taskId, status) => {
    try {
      const updates = { 
        status,
        ...(status === 'completed' && { completed_at: new Date().toISOString() })
      }
      
      const { data, error: updateError } = await supabase
        .from('tasks')
        .update(updates)
        .eq('id', taskId)
        .select()
        .single()
      
      if (updateError) throw updateError
      
      // ローカル状態を更新
      const taskIndex = tasks.value.findIndex(t => t.id === taskId)
      if (taskIndex !== -1) {
        tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...data }
      }
      
      return data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  /**
   * プロジェクトメンバーを招待
   */
  const inviteMember = async (projectId, email, role = 'member') => {
    try {
      loading.value = true
      error.value = null
      
      // ユーザーを検索
      const { data: profiles, error: searchError } = await supabase
        .from('profiles')
        .select('id, email')
        .eq('email', email)
        .single()
      
      if (searchError) throw new Error('ユーザーが見つかりません')
      
      // プロジェクトメンバーとして追加
      const { data, error: inviteError } = await supabase
        .from('project_members')
        .insert({
          project_id: projectId,
          user_id: profiles.id,
          role,
          invited_by: user.value.id
        })
        .select()
        .single()
      
      if (inviteError) throw inviteError
      
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * リアルタイム更新を初期化
   */
  const initializeRealtime = () => {
    // プロジェクト変更を購読
    const projectsChannel = supabase
      .channel('projects_changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'projects'
      }, (payload) => {
        handleRealtimeUpdate('projects', payload)
      })
      .subscribe()
    
    // タスク変更を購読
    const tasksChannel = supabase
      .channel('tasks_changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'tasks'
      }, (payload) => {
        handleRealtimeUpdate('tasks', payload)
      })
      .subscribe()
    
    return { projectsChannel, tasksChannel }
  }
  
  /**
   * リアルタイム更新を処理
   */
  const handleRealtimeUpdate = (table, payload) => {
    const { eventType, new: newRecord, old: oldRecord } = payload
    
    if (table === 'projects') {
      switch (eventType) {
        case 'INSERT':
          projects.value.unshift(newRecord)
          break
        case 'UPDATE':
          const projectIndex = projects.value.findIndex(p => p.id === newRecord.id)
          if (projectIndex !== -1) {
            projects.value[projectIndex] = newRecord
          }
          break
        case 'DELETE':
          projects.value = projects.value.filter(p => p.id !== oldRecord.id)
          break
      }
    } else if (table === 'tasks') {
      switch (eventType) {
        case 'INSERT':
          tasks.value.unshift(newRecord)
          break
        case 'UPDATE':
          const taskIndex = tasks.value.findIndex(t => t.id === newRecord.id)
          if (taskIndex !== -1) {
            tasks.value[taskIndex] = newRecord
          }
          break
        case 'DELETE':
          tasks.value = tasks.value.filter(t => t.id !== oldRecord.id)
          break
      }
    }
  }
  
  return {
    // 状態
    projects: readonly(projects),
    tasks: readonly(tasks),
    loading: readonly(loading),
    error: readonly(error),
    
    // 計算プロパティ
    activeProjects,
    myTasks,
    overdueTasks,
    projectProgress,
    
    // メソッド
    fetchProjects,
    fetchTasks,
    createProject,
    createTask,
    updateTaskStatus,
    inviteMember,
    initializeRealtime
  }
}
```

## ✅ 開発品質チェックリスト

### Supabase統合
- [ ] **クライアント設定**: 適切な設定でクライアントを初期化
- [ ] **環境変数**: セキュアな環境変数管理
- [ ] **エラーハンドリング**: Supabaseエラーの適切な処理
- [ ] **JSDoc**: 関数とデータ構造の適切なドキュメント化
- [ ] **セキュリティ**: RLSポリシーの適切な設定

### パフォーマンス
- [ ] **クエリ最適化**: 必要なフィールドのみ選択
- [ ] **キャッシュ**: 適切なクエリキャッシュ実装
- [ ] **ページネーション**: 大量データの効率的な処理
- [ ] **インデックス**: データベースインデックスの最適化
- [ ] **接続管理**: リアルタイム接続の適切な管理

### 認証とセキュリティ
- [ ] **RLS**: Row Level Securityの適切な実装
- [ ] **権限**: ユーザー権限の適切なチェック
- [ ] **セッション**: セッション管理の適切な実装
- [ ] **入力検証**: ユーザー入力の適切な検証
- [ ] **機密データ**: 機密情報の適切な保護

### リアルタイム機能
- [ ] **購読管理**: チャンネル購読の適切なクリーンアップ
- [ ] **エラー処理**: 接続エラーの適切な処理
- [ ] **パフォーマンス**: 不要な購読の削除
- [ ] **同期**: データ同期の一貫性保証
- [ ] **スケーラビリティ**: 大量接続への対応

### ファイルストレージ
- [ ] **権限**: ストレージアクセス権限の適切な設定
- [ ] **サイズ制限**: ファイルサイズ制限の実装
- [ ] **ファイル形式**: 許可されたファイル形式の検証
- [ ] **メタデータ**: ファイルメタデータの適切な管理
- [ ] **クリーンアップ**: 不要ファイルの自動削除

## 🎯 ベストプラクティス

### 1. クライアント設定

```javascript
// ✅ 良い例: 環境別設定
const supabaseConfig = {
  development: {
    realtime: { params: { eventsPerSecond: 2 } }
  },
  production: {
    realtime: { params: { eventsPerSecond: 10 } }
  }
}

export const supabase = createClient(url, key, {
  ...supabaseConfig[process.env.NODE_ENV],
  auth: {
    autoRefreshToken: true,
    persistSession: true
  }
})

// ❌ 悪い例: ハードコーディング
export const supabase = createClient(
  'https://your-project.supabase.co',
  'your-anon-key'
)
```

### 2. エラーハンドリング

```javascript
// ✅ 良い例: 構造化されたエラー処理
const handleDatabaseError = (error) => {
  switch (error.code) {
    case 'PGRST116':
      return { message: 'データが見つかりません', retryable: false }
    case '23505':
      return { message: '重複したデータです', retryable: false }
    case 'PGRST301':
      return { message: 'ネットワークエラー', retryable: true }
    default:
      return { message: 'システムエラー', retryable: true }
  }
}

// ❌ 悪い例: 汎用エラー処理
const handleError = (error) => {
  console.error(error)
  alert('エラーが発生しました')
}
```

### 3. クエリ最適化

```javascript
// ✅ 良い例: 必要なフィールドのみ選択
const { data } = await supabase
  .from('posts')
  .select('id, title, excerpt, created_at, author:profiles(name)')
  .eq('published', true)
  .range(0, 9)

// ❌ 悪い例: 全フィールド選択
const { data } = await supabase
  .from('posts')
  .select('*')
```

### 4. リアルタイム管理

```javascript
// ✅ 良い例: 適切なクリーンアップ
export function useRealtimeSubscription() {
  const channels = ref([])
  
  const subscribe = (table, callback) => {
    const channel = supabase.channel(table)
      .on('postgres_changes', { event: '*', schema: 'public', table }, callback)
      .subscribe()
    
    channels.value.push(channel)
    return channel
  }
  
  onUnmounted(() => {
    channels.value.forEach(channel => {
      supabase.removeChannel(channel)
    })
  })
  
  return { subscribe }
}

// ❌ 悪い例: クリーンアップなし
const channel = supabase.channel('posts')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'posts' }, callback)
  .subscribe()
```

## トラブルシューティング

### よくある問題

1. **認証エラー**
   - 環境変数を確認
   - RLSポリシーを検証
   - 適切なセッション処理を確保

2. **クエリパフォーマンス**
   - 適切なインデックスを使用
   - クエリキャッシュを実装
   - select文を最適化

3. **リアルタイム購読**
   - RLSポリシーでリアルタイム対応を確認
   - チャンネル購読を検証
   - 接続切断を適切に処理

4. **ファイルアップロード問題**
   - バケットポリシーを確認
   - ファイルサイズ制限を検証
   - ネットワークエラーを適切に処理

## 📚 関連ドキュメント

- **[Vue Compositionパターン](./01_vue_composition_patterns.md)** - Vue 3 Composition APIパターン
- **[Pinia状態管理パターン](./02_pinia_store_patterns.md)** - Piniaとの状態管理
- **[Vite設定ガイド](./04_vite_configuration.md)** - ビルド設定とパフォーマンス最適化

## リソース

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [Realtime](https://supabase.com/docs/guides/realtime)
- [Storage](https://supabase.com/docs/guides/storage)