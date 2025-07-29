# Supabase フォールバック統合ガイド

## 概要

REST APIが利用できない場合のフォールバック接続として、Supabaseを使用する実装ガイドです。

## Supabaseフォールバックの利点

### 高可用性
- グローバルに分散されたインフラストラクチャ
- 99.9%以上のアップタイム保証
- 自動スケーリング

### 追加機能
- リアルタイム同期
- 組み込み認証システム
- ファイルストレージ
- Edge Functions

## 実装詳細

### Supabase設定

```javascript
// config/supabase.js
export const supabaseConfig = {
  url: import.meta.env.VITE_SUPABASE_URL,
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
  options: {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true
    },
    realtime: {
      params: {
        eventsPerSecond: 10
      }
    },
    global: {
      headers: {
        'x-app-version': import.meta.env.VITE_APP_VERSION
      }
    }
  }
}
```

### 認証統合

```javascript
// services/auth/supabaseAuthAdapter.js
import { supabaseClient } from '../supabaseClient'

export class SupabaseAuthAdapter {
  async login(credentials) {
    const { email, password } = credentials
    
    const { data, error } = await supabaseClient.client.auth.signInWithPassword({
      email,
      password
    })
    
    if (error) throw error
    
    // JWT形式に変換して互換性を保つ
    return {
      access_token: data.session.access_token,
      refresh_token: data.session.refresh_token,
      user: {
        id: data.user.id,
        email: data.user.email,
        metadata: data.user.user_metadata
      }
    }
  }
  
  async logout() {
    const { error } = await supabaseClient.client.auth.signOut()
    if (error) throw error
  }
  
  async refreshToken() {
    const { data, error } = await supabaseClient.client.auth.refreshSession()
    if (error) throw error
    
    return {
      access_token: data.session.access_token,
      refresh_token: data.session.refresh_token
    }
  }
  
  async getSession() {
    const { data, error } = await supabaseClient.client.auth.getSession()
    if (error) throw error
    
    return data.session
  }
}
```

### リアルタイム機能の活用

```javascript
// services/realtime/supabaseRealtime.js
export class SupabaseRealtimeManager {
  constructor() {
    this.channels = new Map()
  }
  
  subscribeToTable(table, callback) {
    const channelName = `${table}_changes`
    
    if (this.channels.has(channelName)) {
      return this.channels.get(channelName)
    }
    
    const channel = supabaseClient.client
      .channel(channelName)
      .on('postgres_changes', 
        { event: '*', schema: 'public', table },
        (payload) => {
          callback({
            event: payload.eventType,
            old: payload.old,
            new: payload.new
          })
        }
      )
      .subscribe()
    
    this.channels.set(channelName, channel)
    return channel
  }
  
  unsubscribe(channelName) {
    const channel = this.channels.get(channelName)
    if (channel) {
      supabaseClient.client.removeChannel(channel)
      this.channels.delete(channelName)
    }
  }
  
  unsubscribeAll() {
    this.channels.forEach((channel, name) => {
      this.unsubscribe(name)
    })
  }
}
```

### データ変換レイヤー

```javascript
// services/adapters/dataTransformer.js
export class DataTransformer {
  // REST API形式からSupabase形式への変換
  static toSupabaseFormat(apiData, entityType) {
    switch (entityType) {
      case 'user':
        return {
          id: apiData.id,
          email: apiData.email,
          display_name: apiData.displayName,
          avatar_url: apiData.avatarUrl,
          created_at: apiData.createdAt,
          updated_at: apiData.updatedAt
        }
      
      case 'post':
        return {
          id: apiData.id,
          title: apiData.title,
          content: apiData.content,
          user_id: apiData.userId,
          status: apiData.status,
          created_at: apiData.createdAt,
          updated_at: apiData.updatedAt
        }
      
      default:
        return apiData
    }
  }
  
  // Supabase形式からREST API形式への変換
  static fromSupabaseFormat(supabaseData, entityType) {
    switch (entityType) {
      case 'user':
        return {
          id: supabaseData.id,
          email: supabaseData.email,
          displayName: supabaseData.display_name,
          avatarUrl: supabaseData.avatar_url,
          createdAt: supabaseData.created_at,
          updatedAt: supabaseData.updated_at
        }
      
      case 'post':
        return {
          id: supabaseData.id,
          title: supabaseData.title,
          content: supabaseData.content,
          userId: supabaseData.user_id,
          status: supabaseData.status,
          createdAt: supabaseData.created_at,
          updatedAt: supabaseData.updated_at
        }
      
      default:
        return supabaseData
    }
  }
}
```

### RLSポリシー設定

```sql
-- Row Level Security ポリシー設定例

-- Users テーブル
CREATE POLICY "Public users are viewable by everyone"
  ON users FOR SELECT
  USING (true);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

-- Posts テーブル
CREATE POLICY "Public posts are viewable by everyone"
  ON posts FOR SELECT
  USING (status = 'published' OR user_id = auth.uid());

CREATE POLICY "Users can create posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own posts"
  ON posts FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own posts"
  ON posts FOR DELETE
  USING (auth.uid() = user_id);
```

### エラーハンドリング

```javascript
// services/errors/supabaseErrorHandler.js
export class SupabaseErrorHandler {
  static handle(error) {
    // Supabase特有のエラーコードをアプリケーションエラーに変換
    const errorMap = {
      '23505': 'DUPLICATE_ENTRY',
      '23503': 'FOREIGN_KEY_VIOLATION',
      '23502': 'NOT_NULL_VIOLATION',
      'PGRST116': 'NOT_FOUND',
      'PGRST301': 'MULTIPLE_RESULTS',
      '42P01': 'TABLE_NOT_FOUND',
      '42703': 'COLUMN_NOT_FOUND'
    }
    
    const appError = {
      code: errorMap[error.code] || 'UNKNOWN_ERROR',
      message: this.getUserFriendlyMessage(error),
      details: error.details,
      hint: error.hint
    }
    
    return appError
  }
  
  static getUserFriendlyMessage(error) {
    const messageMap = {
      '23505': 'この値は既に使用されています',
      '23503': '関連するデータが存在しません',
      '23502': '必須項目が入力されていません',
      'PGRST116': 'データが見つかりません',
      'PGRST301': '複数の結果が返されました',
      '42P01': 'テーブルが存在しません',
      '42703': 'カラムが存在しません'
    }
    
    return messageMap[error.code] || error.message || '予期しないエラーが発生しました'
  }
}
```

## ストレージ統合

```javascript
// services/storage/supabaseStorage.js
export class SupabaseStorageAdapter {
  constructor() {
    this.bucket = 'user-uploads'
  }
  
  async uploadFile(file, path) {
    const fileName = `${path}/${Date.now()}_${file.name}`
    
    const { data, error } = await supabaseClient.client.storage
      .from(this.bucket)
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      })
    
    if (error) throw error
    
    // 公開URLを取得
    const { data: { publicUrl } } = supabaseClient.client.storage
      .from(this.bucket)
      .getPublicUrl(fileName)
    
    return {
      path: data.path,
      url: publicUrl
    }
  }
  
  async deleteFile(path) {
    const { error } = await supabaseClient.client.storage
      .from(this.bucket)
      .remove([path])
    
    if (error) throw error
  }
  
  async getSignedUrl(path, expiresIn = 3600) {
    const { data, error } = await supabaseClient.client.storage
      .from(this.bucket)
      .createSignedUrl(path, expiresIn)
    
    if (error) throw error
    
    return data.signedUrl
  }
}
```

## 使用例

### コンポーネントでの使用

```vue
<template>
  <div class="user-profile">
    <div class="connection-status">
      <span v-if="isUsingSupabase" class="badge badge-warning">
        Supabase接続中（フォールバック）
      </span>
    </div>
    
    <div v-if="realtimeEnabled" class="realtime-indicator">
      <span class="badge badge-success">リアルタイム更新有効</span>
    </div>
    
    <form @submit.prevent="updateProfile">
      <input
        v-model="profile.displayName"
        placeholder="表示名"
        class="input input-bordered"
      />
      
      <input
        type="file"
        @change="handleFileUpload"
        accept="image/*"
      />
      
      <button type="submit" class="btn btn-primary">
        更新
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { connectionManager } from '@/services/connectionManager'
import { supabaseStorage } from '@/services/storage/supabaseStorage'
import { realtimeManager } from '@/services/realtime/supabaseRealtime'

const profile = ref({
  displayName: '',
  avatarUrl: ''
})

const isUsingSupabase = computed(() => 
  connectionManager.connectionStatus.value === 'fallback'
)

const realtimeEnabled = ref(false)
let realtimeSubscription = null

onMounted(() => {
  // Supabase接続時はリアルタイム更新を有効化
  if (isUsingSupabase.value) {
    realtimeSubscription = realtimeManager.subscribeToTable('users', (change) => {
      if (change.event === 'UPDATE' && change.new.id === currentUserId) {
        profile.value = DataTransformer.fromSupabaseFormat(change.new, 'user')
        realtimeEnabled.value = true
      }
    })
  }
})

onUnmounted(() => {
  if (realtimeSubscription) {
    realtimeManager.unsubscribe('users_changes')
  }
})

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    // Supabase接続時はSupabase Storageを使用
    if (isUsingSupabase.value) {
      const { url } = await supabaseStorage.uploadFile(file, 'avatars')
      profile.value.avatarUrl = url
    }
  } catch (error) {
    console.error('Upload failed:', error)
  }
}
</script>
```

## パフォーマンス最適化

### 接続プーリング

```javascript
// services/optimization/connectionPool.js
export class SupabaseConnectionPool {
  constructor(maxConnections = 5) {
    this.pool = []
    this.maxConnections = maxConnections
    this.activeConnections = 0
  }
  
  async getConnection() {
    if (this.pool.length > 0) {
      return this.pool.pop()
    }
    
    if (this.activeConnections < this.maxConnections) {
      this.activeConnections++
      return createClient(supabaseConfig.url, supabaseConfig.anonKey)
    }
    
    // 接続が利用可能になるまで待機
    await new Promise(resolve => setTimeout(resolve, 100))
    return this.getConnection()
  }
  
  releaseConnection(connection) {
    if (this.pool.length < this.maxConnections) {
      this.pool.push(connection)
    }
  }
}
```

## セキュリティ考慮事項

### APIキーの管理
- Anon Keyはフロントエンドで使用可能（RLSによる保護が前提）
- Service Keyは絶対にフロントエンドに含めない
- 環境変数による管理を徹底

### データ暗号化
- HTTPSによる通信の暗号化
- センシティブデータの追加暗号化を検討
- ローカルストレージへの保存時の暗号化

### 認証トークンの扱い
- Supabase認証トークンとREST API JWTトークンの適切な管理
- トークンのローテーション戦略
- セッション管理の統一