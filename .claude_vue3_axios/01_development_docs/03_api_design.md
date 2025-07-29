# REST API設計パターン

## 1. REST API アーキテクチャ概要

### HTTP クライアント設定
```javascript
// lib/api/client.js
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

export const apiClient = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// リクエストインターセプター（認証トークン自動付与）
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// レスポンスインターセプター（エラーハンドリング）
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // トークンリフレッシュ処理
      await refreshToken()
      return apiClient(error.config)
    }
    return Promise.reject(error)
  }
)
```

### API 層の設計原則
1. **単一責任**: 各API関数は一つの責任を持つ
2. **一貫性**: 統一されたレスポンス形式
3. **エラーハンドリング**: 予測可能なエラー処理
4. **型安全性**: JSDoc による型定義
5. **キャッシュ戦略**: 効率的なデータ取得

## 2. CRUD 操作パターン

### 2.1 基本的なCRUD API
```javascript
// lib/api/posts.js
import { apiClient } from './client'

/**
 * @typedef {Object} Post
 * @property {string} id
 * @property {string} title
 * @property {string} content
 * @property {string} user_id
 * @property {'draft'|'published'|'archived'} status
 * @property {string[]} tags
 * @property {string} created_at
 * @property {string} updated_at
 */

/**
 * @typedef {Object} ApiResponse
 * @property {boolean} success
 * @property {*} data
 * @property {string|null} error
 * @property {Object|null} meta
 */

export const postsApi = {
  /**
   * 投稿一覧を取得
   * @param {Object} options
   * @param {number} options.page - ページ番号
   * @param {number} options.limit - 取得件数
   * @param {string} options.status - ステータスフィルター
   * @param {string[]} options.tags - タグフィルター
   * @returns {Promise<ApiResponse>}
   */
  async getAll(options = {}) {
    try {
      const { page = 1, limit = 10, status, tags } = options
      
      const params = {
        page,
        limit,
        ...(status && { status }),
        ...(tags && tags.length > 0 && { tags: tags.join(',') })
      }

      const response = await apiClient.get('/posts', { params })

      return {
        success: true,
        data: response.data.data,
        error: null,
        meta: response.data.meta
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.response?.data?.message || error.message,
        meta: null
      }
    }
  },

  /**
   * 投稿詳細を取得
   * @param {string} id - 投稿ID
   * @returns {Promise<ApiResponse>}
   */
  async getById(id) {
    try {
      const { data, error } = await supabase
        .from('posts')
        .select(`
          id,
          title,
          content,
          excerpt,
          slug,
          status,
          tags,
          metadata,
          view_count,
          like_count,
          comment_count,
          published_at,
          created_at,
          updated_at,
          users:user_id (
            id,
            name,
            avatar_url,
            bio
          )
        `)
        .eq('id', id)
        .single()

      if (error) throw error

      // 閲覧数をインクリメント
      await this.incrementViewCount(id)

      return {
        success: true,
        data,
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * 投稿を作成
   * @param {Partial<Post>} postData - 投稿データ
   * @returns {Promise<ApiResponse>}
   */
  async create(postData) {
    try {
      const { data: { user }, error: authError } = await supabase.auth.getUser()
      if (authError) throw authError
      if (!user) throw new Error('認証が必要です')

      // スラッグの自動生成
      const slug = postData.slug || generateSlug(postData.title)

      const { data, error } = await supabase
        .from('posts')
        .insert({
          user_id: user.id,
          title: postData.title,
          content: postData.content,
          excerpt: postData.excerpt || generateExcerpt(postData.content),
          slug,
          status: postData.status || 'draft',
          tags: postData.tags || [],
          metadata: postData.metadata || {},
          published_at: postData.status === 'published' ? new Date().toISOString() : null
        })
        .select()
        .single()

      if (error) throw error

      return {
        success: true,
        data,
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * 投稿を更新
   * @param {string} id - 投稿ID
   * @param {Partial<Post>} updates - 更新データ
   * @returns {Promise<ApiResponse>}
   */
  async update(id, updates) {
    try {
      const updateData = { ...updates }

      // 公開ステータスが変更された場合
      if (updates.status === 'published' && !updates.published_at) {
        updateData.published_at = new Date().toISOString()
      }

      const { data, error } = await supabase
        .from('posts')
        .update(updateData)
        .eq('id', id)
        .select()
        .single()

      if (error) throw error

      return {
        success: true,
        data,
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * 投稿を削除
   * @param {string} id - 投稿ID
   * @returns {Promise<ApiResponse>}
   */
  async delete(id) {
    try {
      const { error } = await supabase
        .from('posts')
        .delete()
        .eq('id', id)

      if (error) throw error

      return {
        success: true,
        data: { id },
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * 閲覧数をインクリメント
   * @param {string} id - 投稿ID
   * @returns {Promise<void>}
   */
  async incrementViewCount(id) {
    try {
      await supabase.rpc('increment_view_count', { post_id: id })
    } catch (error) {
      console.error('閲覧数の更新に失敗:', error)
    }
  }
}

/**
 * スラッグを生成
 * @param {string} title - タイトル
 * @returns {string}
 */
function generateSlug(title) {
  return title
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

/**
 * 抜粋を生成
 * @param {string} content - 本文
 * @param {number} length - 抜粋の長さ
 * @returns {string}
 */
function generateExcerpt(content, length = 150) {
  if (!content) return ''
  return content.length > length 
    ? content.substring(0, length) + '...'
    : content
}
```

### 2.2 検索API
```javascript
// lib/supabase/search.js

export const searchApi = {
  /**
   * 全文検索
   * @param {string} query - 検索クエリ
   * @param {Object} options - 検索オプション
   * @returns {Promise<ApiResponse>}
   */
  async searchPosts(query, options = {}) {
    try {
      const { limit = 20, offset = 0 } = options

      const { data, error } = await supabase
        .from('posts')
        .select(`
          id,
          title,
          excerpt,
          slug,
          tags,
          published_at,
          users:user_id (name, avatar_url)
        `)
        .textSearch('title_content', query, {
          type: 'websearch',
          config: 'japanese'
        })
        .eq('status', 'published')
        .order('published_at', { ascending: false })
        .range(offset, offset + limit - 1)

      if (error) throw error

      return {
        success: true,
        data,
        error: null,
        meta: { query, count: data.length }
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * タグ検索
   * @param {string[]} tags - タグ配列
   * @returns {Promise<ApiResponse>}
   */
  async searchByTags(tags) {
    try {
      const { data, error } = await supabase
        .from('posts')
        .select(`
          id,
          title,
          excerpt,
          slug,
          tags,
          published_at,
          users:user_id (name, avatar_url)
        `)
        .overlaps('tags', tags)
        .eq('status', 'published')
        .order('published_at', { ascending: false })

      if (error) throw error

      return {
        success: true,
        data,
        error: null,
        meta: { tags, count: data.length }
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  }
}
```

## 3. リアルタイム API パターン

### 3.1 リアルタイム購読
```javascript
// lib/supabase/realtime.js

export class RealtimeManager {
  constructor() {
    this.subscriptions = new Map()
  }

  /**
   * 投稿の変更を購読
   * @param {Function} callback - コールバック関数
   * @returns {Function} unsubscribe function
   */
  subscribeToPostChanges(callback) {
    const channel = supabase
      .channel('posts-changes')
      .on(
        'postgres_changes',
        { 
          event: '*', 
          schema: 'public', 
          table: 'posts',
          filter: "status=eq.published"
        },
        (payload) => {
          callback({
            type: payload.eventType,
            record: payload.new || payload.old,
            timestamp: new Date().toISOString()
          })
        }
      )
      .subscribe()

    this.subscriptions.set('posts', channel)

    return () => this.unsubscribe('posts')
  }

  /**
   * ユーザーのオンライン状態を購読
   * @param {string} userId - ユーザーID
   * @param {Function} callback - コールバック関数
   */
  subscribeToUserPresence(userId, callback) {
    const channel = supabase
      .channel('user-presence')
      .on('presence', { event: 'sync' }, () => {
        const state = channel.presenceState()
        callback(state)
      })
      .on('presence', { event: 'join' }, ({ key, newPresences }) => {
        callback({ event: 'join', userId: key, data: newPresences })
      })
      .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
        callback({ event: 'leave', userId: key, data: leftPresences })
      })
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          // ユーザーの存在を追跡
          await channel.track({
            user_id: userId,
            online_at: new Date().toISOString(),
          })
        }
      })

    this.subscriptions.set(`presence-${userId}`, channel)
  }

  /**
   * 購読を解除
   * @param {string} key - 購読キー
   */
  unsubscribe(key) {
    const channel = this.subscriptions.get(key)
    if (channel) {
      supabase.removeChannel(channel)
      this.subscriptions.delete(key)
    }
  }

  /**
   * 全ての購読を解除
   */
  unsubscribeAll() {
    for (const [key] of this.subscriptions) {
      this.unsubscribe(key)
    }
  }
}

export const realtimeManager = new RealtimeManager()
```

### 3.2 リアルタイム通知システム
```javascript
// lib/supabase/notifications.js

export const notificationsApi = {
  /**
   * 通知を作成
   * @param {Object} notification - 通知データ
   * @returns {Promise<ApiResponse>}
   */
  async create(notification) {
    try {
      const { data, error } = await supabase
        .from('notifications')
        .insert({
          user_id: notification.userId,
          type: notification.type,
          title: notification.title,
          message: notification.message,
          data: notification.data || {},
          read: false
        })
        .select()
        .single()

      if (error) throw error

      // リアルタイム通知の送信
      await this.sendRealtimeNotification(notification.userId, data)

      return {
        success: true,
        data,
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * ユーザーの通知一覧を取得
   * @param {string} userId - ユーザーID
   * @param {Object} options - オプション
   * @returns {Promise<ApiResponse>}
   */
  async getByUserId(userId, options = {}) {
    try {
      const { limit = 50, unreadOnly = false } = options

      let query = supabase
        .from('notifications')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(limit)

      if (unreadOnly) {
        query = query.eq('read', false)
      }

      const { data, error } = await query

      if (error) throw error

      return {
        success: true,
        data,
        error: null,
        meta: { userId, unreadCount: data.filter(n => !n.read).length }
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * 通知を既読にする
   * @param {string} notificationId - 通知ID
   * @returns {Promise<ApiResponse>}
   */
  async markAsRead(notificationId) {
    try {
      const { data, error } = await supabase
        .from('notifications')
        .update({ read: true, read_at: new Date().toISOString() })
        .eq('id', notificationId)
        .select()
        .single()

      if (error) throw error

      return {
        success: true,
        data,
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * リアルタイム通知を送信
   * @param {string} userId - ユーザーID
   * @param {Object} notification - 通知データ
   */
  async sendRealtimeNotification(userId, notification) {
    const channel = supabase.channel(`notifications-${userId}`)
    await channel.send({
      type: 'broadcast',
      event: 'notification',
      payload: notification
    })
  }
}
```

## 4. ファイルストレージ API

### 4.1 ファイルアップロード
```javascript
// lib/supabase/storage.js

export const storageApi = {
  /**
   * ファイルをアップロード
   * @param {File} file - アップロードするファイル
   * @param {Object} options - オプション
   * @returns {Promise<ApiResponse>}
   */
  async uploadFile(file, options = {}) {
    try {
      const { bucket = 'uploads', folder = 'general' } = options
      
      // ファイル名の生成（重複を避けるためタイムスタンプを付与）
      const fileExt = file.name.split('.').pop()
      const fileName = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}.${fileExt}`
      const filePath = `${folder}/${fileName}`

      // ファイルサイズチェック（10MB制限）
      const maxSize = 10 * 1024 * 1024
      if (file.size > maxSize) {
        throw new Error('ファイルサイズが大きすぎます（10MB以下にしてください）')
      }

      // ファイルタイプチェック
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        throw new Error('サポートされていないファイル形式です')
      }

      const { data, error } = await supabase.storage
        .from(bucket)
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        })

      if (error) throw error

      // 公開URLを取得
      const { data: { publicUrl } } = supabase.storage
        .from(bucket)
        .getPublicUrl(filePath)

      return {
        success: true,
        data: {
          path: data.path,
          fullPath: data.fullPath,
          publicUrl,
          fileName: file.name,
          fileSize: file.size,
          fileType: file.type
        },
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * ファイルを削除
   * @param {string} filePath - ファイルパス
   * @param {string} bucket - バケット名
   * @returns {Promise<ApiResponse>}
   */
  async deleteFile(filePath, bucket = 'uploads') {
    try {
      const { error } = await supabase.storage
        .from(bucket)
        .remove([filePath])

      if (error) throw error

      return {
        success: true,
        data: { filePath },
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * ファイル一覧を取得
   * @param {string} folder - フォルダパス
   * @param {string} bucket - バケット名
   * @returns {Promise<ApiResponse>}
   */
  async listFiles(folder = '', bucket = 'uploads') {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .list(folder, {
          limit: 100,
          offset: 0,
          sortBy: { column: 'created_at', order: 'desc' }
        })

      if (error) throw error

      // 公開URLを付与
      const filesWithUrl = data.map(file => ({
        ...file,
        publicUrl: supabase.storage
          .from(bucket)
          .getPublicUrl(`${folder}/${file.name}`).data.publicUrl
      }))

      return {
        success: true,
        data: filesWithUrl,
        error: null,
        meta: { folder, bucket, count: data.length }
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  }
}
```

## 5. エラーハンドリングとロギング

### 5.1 統一エラーハンドラー
```javascript
// lib/supabase/errorHandler.js

export class SupabaseErrorHandler {
  /**
   * Supabaseエラーを処理
   * @param {Error} error - エラーオブジェクト
   * @returns {Object} 処理済みエラー
   */
  static handleError(error) {
    const handledError = {
      message: 'エラーが発生しました',
      code: 'UNKNOWN_ERROR',
      statusCode: 500,
      originalError: error
    }

    // PostgreSQLエラー
    if (error.code) {
      switch (error.code) {
        case '23505': // unique_violation
          handledError.message = 'データが既に存在します'
          handledError.code = 'DUPLICATE_ERROR'
          handledError.statusCode = 409
          break
        case '23503': // foreign_key_violation
          handledError.message = '関連するデータが見つかりません'
          handledError.code = 'FOREIGN_KEY_ERROR'
          handledError.statusCode = 400
          break
        case '23514': // check_violation
          handledError.message = 'データの制約に違反しています'
          handledError.code = 'CONSTRAINT_ERROR'
          handledError.statusCode = 400
          break
      }
    }

    // Supabase Auth エラー
    if (error.message) {
      if (error.message.includes('Invalid login credentials')) {
        handledError.message = 'ログイン情報が正しくありません'
        handledError.code = 'INVALID_CREDENTIALS'
        handledError.statusCode = 401
      } else if (error.message.includes('User not found')) {
        handledError.message = 'ユーザーが見つかりません'
        handledError.code = 'USER_NOT_FOUND'
        handledError.statusCode = 404
      } else if (error.message.includes('Email not confirmed')) {
        handledError.message = 'メールアドレスが確認されていません'
        handledError.code = 'EMAIL_NOT_CONFIRMED'
        handledError.statusCode = 401
      }
    }

    return handledError
  }

  /**
   * エラーログを送信
   * @param {Error} error - エラーオブジェクト
   * @param {Object} context - コンテキスト情報
   */
  static async logError(error, context = {}) {
    if (import.meta.env.PROD) {
      try {
        await supabase
          .from('error_logs')
          .insert({
            error_message: error.message,
            error_stack: error.stack,
            error_code: error.code,
            context: JSON.stringify(context),
            user_agent: navigator.userAgent,
            url: window.location.href,
            timestamp: new Date().toISOString()
          })
      } catch (logError) {
        console.error('エラーログの送信に失敗:', logError)
      }
    } else {
      console.error('Error:', error, 'Context:', context)
    }
  }
}
```

## 6. API レスポンスキャッシュ

### 6.1 クエリキャッシュ
```javascript
// lib/supabase/cache.js

export class SupabaseCache {
  constructor() {
    this.cache = new Map()
    this.ttl = new Map()
  }

  /**
   * キャッシュされたクエリを実行
   * @param {string} key - キャッシュキー
   * @param {Function} queryFn - クエリ関数
   * @param {number} ttlMs - TTL（ミリ秒）
   * @returns {Promise<*>}
   */
  async cachedQuery(key, queryFn, ttlMs = 5 * 60 * 1000) {
    // キャッシュから取得を試行
    if (this.cache.has(key)) {
      const expiry = this.ttl.get(key)
      if (Date.now() < expiry) {
        return this.cache.get(key)
      } else {
        // 期限切れのキャッシュを削除
        this.cache.delete(key)
        this.ttl.delete(key)
      }
    }

    // クエリを実行してキャッシュに保存
    try {
      const result = await queryFn()
      this.cache.set(key, result)
      this.ttl.set(key, Date.now() + ttlMs)
      return result
    } catch (error) {
      throw error
    }
  }

  /**
   * キャッシュを無効化
   * @param {string|RegExp} pattern - 無効化パターン
   */
  invalidate(pattern) {
    if (typeof pattern === 'string') {
      this.cache.delete(pattern)
      this.ttl.delete(pattern)
    } else if (pattern instanceof RegExp) {
      for (const key of this.cache.keys()) {
        if (pattern.test(key)) {
          this.cache.delete(key)
          this.ttl.delete(key)
        }
      }
    }
  }

  /**
   * 全キャッシュをクリア
   */
  clear() {
    this.cache.clear()
    this.ttl.clear()
  }
}

export const apiCache = new SupabaseCache()
```

## 7. パフォーマンス最適化

### 7.1 バッチクエリ
```javascript
// lib/supabase/batch.js

export const batchApi = {
  /**
   * 複数の投稿を一括取得
   * @param {string[]} postIds - 投稿ID配列
   * @returns {Promise<ApiResponse>}
   */
  async getPostsByIds(postIds) {
    try {
      if (!postIds.length) {
        return { success: true, data: [], error: null, meta: null }
      }

      const { data, error } = await supabase
        .from('posts')
        .select(`
          id,
          title,
          excerpt,
          slug,
          status,
          published_at,
          users:user_id (name, avatar_url)
        `)
        .in('id', postIds)
        .eq('status', 'published')

      if (error) throw error

      // 元の順序を保持
      const orderedData = postIds
        .map(id => data.find(post => post.id === id))
        .filter(Boolean)

      return {
        success: true,
        data: orderedData,
        error: null,
        meta: { requestedIds: postIds, foundCount: orderedData.length }
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  },

  /**
   * 関連データを一括取得
   * @param {string} postId - 投稿ID
   * @returns {Promise<ApiResponse>}
   */
  async getPostWithRelatedData(postId) {
    try {
      // 並列でクエリを実行
      const [postResult, commentsResult, likesResult] = await Promise.all([
        // 投稿データ
        supabase
          .from('posts')
          .select(`
            id, title, content, excerpt, slug, status,
            published_at, created_at,
            users:user_id (id, name, avatar_url)
          `)
          .eq('id', postId)
          .single(),

        // コメントデータ
        supabase
          .from('comments')
          .select(`
            id, content, created_at,
            users:user_id (id, name, avatar_url)
          `)
          .eq('post_id', postId)
          .eq('is_approved', true)
          .order('created_at', { ascending: true }),

        // いいねデータ
        supabase.rpc('get_post_likes_count', { post_id: postId })
      ])

      if (postResult.error) throw postResult.error

      return {
        success: true,
        data: {
          post: postResult.data,
          comments: commentsResult.data || [],
          likesCount: likesResult.data || 0
        },
        error: null,
        meta: null
      }
    } catch (error) {
      return {
        success: false,
        data: null,
        error: error.message,
        meta: null
      }
    }
  }
}
```

## 8. まとめ

このAPI設計の特徴：

1. **一貫性**: 統一されたレスポンス形式とエラーハンドリング
2. **型安全性**: JSDoc による詳細な型定義
3. **パフォーマンス**: 効率的なクエリとキャッシュ戦略
4. **リアルタイム**: WebSocket による即座のデータ同期
5. **セキュリティ**: RLS とバリデーションによる保護

### 関連ドキュメント
- [データベース設計](./02_database_design.md)
- [Supabase統合ガイド](../03_library_docs/03_supabase_integration.md)
- [エラーハンドリング設計](./07_error_handling_design.md)