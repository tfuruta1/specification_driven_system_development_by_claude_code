# /vue3-supabase-optimize - Vue3+Supabase エンタープライズ最適化専用コマンド

## 概要
Vue3 + Supabase を使用したリアルタイムアプリケーションの包括的な最適化コマンドです。Supabase固有の機能（Realtime、RLS、Edge Functions）を最大限活用します。

## 使用方法
```bash
/vue3-supabase-optimize [feature] [action] [options]

# 使用例
/vue3-supabase-optimize realtime optimize --subscriptions
/vue3-supabase-optimize rls generate --policies
/vue3-supabase-optimize edge deploy --functions
/vue3-supabase-optimize auth setup --providers
/vue3-supabase-optimize storage optimize --cdn
```

## Supabase 専用最適化機能

### 1. Realtime購読最適化
```typescript
// services/supabase-realtime-optimizer.ts
import { createClient, RealtimeChannel, SupabaseClient } from '@supabase/supabase-js'
import { ref, reactive, onUnmounted } from 'vue'

class RealtimeOptimizer {
  private client: SupabaseClient
  private channels: Map<string, RealtimeChannel> = new Map()
  private subscriptions: Map<string, Set<Function>> = new Map()
  private messageQueue: any[] = []
  private batchTimer: NodeJS.Timeout | null = null
  
  constructor() {
    this.client = createClient(
      import.meta.env.VITE_SUPABASE_URL,
      import.meta.env.VITE_SUPABASE_ANON_KEY,
      {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true
        },
        realtime: {
          params: {
            eventsPerSecond: 10, // レート制限
            // カスタムトランスポート設定
            transport: WebSocket,
            // 再接続戦略
            reconnectAfterMs: (attempts: number) => {
              return Math.min(1000 * 2 ** attempts, 30000)
            }
          }
        }
      }
    )
    
    this.setupConnectionMonitoring()
  }
  
  // 最適化された購読管理
  subscribeToTable(
    tableName: string,
    filter?: { column: string; operator: string; value: any }
  ) {
    const channelName = `${tableName}_${filter ? JSON.stringify(filter) : 'all'}`
    
    // 既存チャンネルの再利用
    if (this.channels.has(channelName)) {
      return this.channels.get(channelName)!
    }
    
    // Presence対応チャンネル作成
    const channel = this.client
      .channel(channelName, {
        config: {
          broadcast: { self: true },
          presence: { key: 'user_id' }
        }
      })
    
    // PostgreSQL変更の購読
    const subscription = channel
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: tableName,
          filter: filter ? `${filter.column}=${filter.operator}.${filter.value}` : undefined
        },
        (payload) => {
          this.handleChange(tableName, payload)
        }
      )
      .on('presence', { event: 'sync' }, () => {
        const state = channel.presenceState()
        this.handlePresenceSync(channelName, state)
      })
      .on('broadcast', { event: 'cursor' }, (payload) => {
        this.handleCursorUpdate(payload)
      })
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Subscribed to ${channelName}`)
          this.trackSubscription(channelName)
        }
      })
    
    this.channels.set(channelName, channel)
    return channel
  }
  
  // バッチ処理で更新を最適化
  private handleChange(tableName: string, payload: any) {
    this.messageQueue.push({ tableName, payload, timestamp: Date.now() })
    
    if (!this.batchTimer) {
      this.batchTimer = setTimeout(() => {
        this.processBatch()
        this.batchTimer = null
      }, 100) // 100ms でバッチ処理
    }
  }
  
  private processBatch() {
    if (this.messageQueue.length === 0) return
    
    // 重複排除
    const uniqueMessages = this.deduplicateMessages(this.messageQueue)
    
    // テーブルごとにグループ化
    const grouped = this.groupByTable(uniqueMessages)
    
    // バッチ更新通知
    Object.entries(grouped).forEach(([table, messages]) => {
      this.notifySubscribers(table, messages)
    })
    
    this.messageQueue = []
  }
  
  // 購読解除の最適化
  async unsubscribeAll() {
    const unsubscribePromises = Array.from(this.channels.values()).map(
      channel => channel.unsubscribe()
    )
    
    await Promise.all(unsubscribePromises)
    this.channels.clear()
    this.subscriptions.clear()
  }
}

// Vue3 Composable
export function useRealtimeData(tableName: string, filter?: any) {
  const data = ref<any[]>([])
  const loading = ref(true)
  const error = ref<Error | null>(null)
  const optimizer = new RealtimeOptimizer()
  
  // 初期データ取得
  const fetchInitialData = async () => {
    try {
      let query = optimizer.client.from(tableName).select('*')
      
      if (filter) {
        Object.entries(filter).forEach(([key, value]) => {
          query = query.eq(key, value)
        })
      }
      
      const { data: initialData, error: fetchError } = await query
      
      if (fetchError) throw fetchError
      
      data.value = initialData || []
      loading.value = false
    } catch (err) {
      error.value = err as Error
      loading.value = false
    }
  }
  
  // リアルタイム購読
  const channel = optimizer.subscribeToTable(tableName, filter)
  
  // データ更新ハンドラー
  channel.on('postgres_changes', { event: 'INSERT' }, (payload) => {
    data.value.push(payload.new)
  })
  
  channel.on('postgres_changes', { event: 'UPDATE' }, (payload) => {
    const index = data.value.findIndex(item => item.id === payload.new.id)
    if (index !== -1) {
      data.value[index] = payload.new
    }
  })
  
  channel.on('postgres_changes', { event: 'DELETE' }, (payload) => {
    data.value = data.value.filter(item => item.id !== payload.old.id)
  })
  
  // 初期化
  fetchInitialData()
  
  // クリーンアップ
  onUnmounted(() => {
    channel.unsubscribe()
  })
  
  return {
    data,
    loading,
    error,
    refetch: fetchInitialData
  }
}
```

### 2. Row Level Security (RLS) 自動生成
```sql
-- RLS ポリシー自動生成
CREATE OR REPLACE FUNCTION generate_rls_policies(
  p_table_name text,
  p_auth_column text DEFAULT 'user_id'
)
RETURNS void AS $$
DECLARE
  v_policy_name text;
BEGIN
  -- 既存ポリシー削除
  EXECUTE format('DROP POLICY IF EXISTS %I ON %I', 
    p_table_name || '_select_policy', p_table_name);
  EXECUTE format('DROP POLICY IF EXISTS %I ON %I', 
    p_table_name || '_insert_policy', p_table_name);
  EXECUTE format('DROP POLICY IF EXISTS %I ON %I', 
    p_table_name || '_update_policy', p_table_name);
  EXECUTE format('DROP POLICY IF EXISTS %I ON %I', 
    p_table_name || '_delete_policy', p_table_name);
  
  -- RLS有効化
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', p_table_name);
  
  -- SELECT ポリシー（自分のデータ + 公開データ）
  EXECUTE format('
    CREATE POLICY %I ON %I FOR SELECT
    USING (
      %I = auth.uid()
      OR EXISTS (
        SELECT 1 FROM public.data_permissions
        WHERE table_name = %L
        AND user_id = auth.uid()
        AND permission_type = ''read''
      )
      OR is_public = true
    )',
    p_table_name || '_select_policy',
    p_table_name,
    p_auth_column,
    p_table_name
  );
  
  -- INSERT ポリシー
  EXECUTE format('
    CREATE POLICY %I ON %I FOR INSERT
    WITH CHECK (
      %I = auth.uid()
      OR EXISTS (
        SELECT 1 FROM public.user_roles
        WHERE user_id = auth.uid()
        AND role_name IN (''admin'', ''moderator'')
      )
    )',
    p_table_name || '_insert_policy',
    p_table_name,
    p_auth_column
  );
  
  -- UPDATE ポリシー
  EXECUTE format('
    CREATE POLICY %I ON %I FOR UPDATE
    USING (%I = auth.uid())
    WITH CHECK (
      %I = auth.uid()
      AND (
        updated_at > created_at
        OR updated_at IS NULL
      )
    )',
    p_table_name || '_update_policy',
    p_table_name,
    p_auth_column,
    p_auth_column
  );
  
  -- DELETE ポリシー
  EXECUTE format('
    CREATE POLICY %I ON %I FOR DELETE
    USING (
      %I = auth.uid()
      OR EXISTS (
        SELECT 1 FROM public.user_roles
        WHERE user_id = auth.uid()
        AND role_name = ''admin''
      )
    )',
    p_table_name || '_delete_policy',
    p_table_name,
    p_auth_column
  );
  
  -- 監査ログ
  INSERT INTO public.rls_audit_log (
    table_name,
    action,
    performed_by,
    performed_at
  ) VALUES (
    p_table_name,
    'RLS_POLICIES_GENERATED',
    auth.uid(),
    NOW()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 階層的権限管理
CREATE TABLE IF NOT EXISTS public.hierarchical_permissions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  resource_type TEXT NOT NULL,
  resource_id UUID,
  permission_level INT NOT NULL, -- 1: Read, 2: Write, 3: Admin
  inherited_from UUID REFERENCES public.hierarchical_permissions(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  
  CONSTRAINT unique_user_resource UNIQUE(user_id, resource_type, resource_id)
);

-- 権限チェック関数
CREATE OR REPLACE FUNCTION check_permission(
  p_user_id UUID,
  p_resource_type TEXT,
  p_resource_id UUID,
  p_required_level INT
)
RETURNS BOOLEAN AS $$
DECLARE
  v_permission_level INT;
BEGIN
  SELECT MAX(permission_level) INTO v_permission_level
  FROM public.hierarchical_permissions
  WHERE user_id = p_user_id
    AND resource_type = p_resource_type
    AND (resource_id = p_resource_id OR resource_id IS NULL)
    AND (expires_at IS NULL OR expires_at > NOW());
  
  RETURN COALESCE(v_permission_level, 0) >= p_required_level;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3. Edge Functions最適化
```typescript
// supabase/functions/optimized-edge-function/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// グローバルキャッシュ
const cache = new Map<string, { data: any; expires: number }>()

// コネクションプール
const supabasePool = new Map<string, any>()

function getSupabaseClient(token?: string) {
  const key = token || 'anon'
  
  if (!supabasePool.has(key)) {
    supabasePool.set(key, createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      token || Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    ))
  }
  
  return supabasePool.get(key)
}

// メイン処理
serve(async (req) => {
  try {
    // CORS設定
    if (req.method === 'OPTIONS') {
      return new Response('ok', {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
          'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        },
      })
    }
    
    // リクエスト解析
    const { pathname, searchParams } = new URL(req.url)
    const cacheKey = `${pathname}:${searchParams.toString()}`
    
    // キャッシュチェック
    const cached = cache.get(cacheKey)
    if (cached && cached.expires > Date.now()) {
      return new Response(JSON.stringify(cached.data), {
        headers: { 
          'Content-Type': 'application/json',
          'X-Cache': 'HIT'
        },
      })
    }
    
    // 認証トークン取得
    const authHeader = req.headers.get('Authorization')
    const token = authHeader?.replace('Bearer ', '')
    const supabase = getSupabaseClient(token)
    
    // ルーティング
    switch (pathname) {
      case '/api/aggregate':
        return await handleAggregation(supabase, req)
        
      case '/api/batch':
        return await handleBatchOperation(supabase, req)
        
      case '/api/stream':
        return await handleStreamResponse(supabase, req)
        
      case '/api/webhook':
        return await handleWebhook(supabase, req)
        
      default:
        return new Response('Not Found', { status: 404 })
    }
    
  } catch (error) {
    console.error('Edge Function Error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
})

// 集計処理の最適化
async function handleAggregation(supabase: any, req: Request) {
  const { table, groupBy, aggregate } = await req.json()
  
  // 複雑な集計をEdge側で処理
  const { data, error } = await supabase
    .from(table)
    .select('*')
  
  if (error) throw error
  
  // グループ化と集計
  const result = data.reduce((acc: any, row: any) => {
    const key = groupBy.map((field: string) => row[field]).join(':')
    
    if (!acc[key]) {
      acc[key] = {
        count: 0,
        sum: {},
        avg: {},
        min: {},
        max: {},
        values: []
      }
    }
    
    acc[key].count++
    acc[key].values.push(row)
    
    // 集計計算
    aggregate.forEach((agg: any) => {
      const value = row[agg.field]
      
      switch (agg.type) {
        case 'sum':
          acc[key].sum[agg.field] = (acc[key].sum[agg.field] || 0) + value
          break
        case 'avg':
          acc[key].avg[agg.field] = acc[key].sum[agg.field] / acc[key].count
          break
        case 'min':
          acc[key].min[agg.field] = Math.min(acc[key].min[agg.field] || Infinity, value)
          break
        case 'max':
          acc[key].max[agg.field] = Math.max(acc[key].max[agg.field] || -Infinity, value)
          break
      }
    })
    
    return acc
  }, {})
  
  // キャッシュ保存（5分間）
  cache.set(req.url, {
    data: result,
    expires: Date.now() + 300000
  })
  
  return new Response(JSON.stringify(result), {
    headers: { 
      'Content-Type': 'application/json',
      'X-Cache': 'MISS'
    }
  })
}

// バッチ操作の最適化
async function handleBatchOperation(supabase: any, req: Request) {
  const { operations } = await req.json()
  
  // トランザクション風の実行
  const results = []
  const rollbackOperations = []
  
  try {
    for (const op of operations) {
      let result
      
      switch (op.type) {
        case 'insert':
          result = await supabase.from(op.table).insert(op.data)
          rollbackOperations.push({
            type: 'delete',
            table: op.table,
            ids: result.data?.map((r: any) => r.id)
          })
          break
          
        case 'update':
          result = await supabase.from(op.table)
            .update(op.data)
            .match(op.match)
          break
          
        case 'delete':
          result = await supabase.from(op.table)
            .delete()
            .match(op.match)
          break
      }
      
      if (result.error) {
        throw result.error
      }
      
      results.push(result.data)
    }
    
    return new Response(JSON.stringify({ success: true, results }), {
      headers: { 'Content-Type': 'application/json' }
    })
    
  } catch (error) {
    // ロールバック処理
    for (const rollback of rollbackOperations.reverse()) {
      try {
        await executeRollback(supabase, rollback)
      } catch (rollbackError) {
        console.error('Rollback failed:', rollbackError)
      }
    }
    
    throw error
  }
}

// ストリーミングレスポンス
async function handleStreamResponse(supabase: any, req: Request) {
  const { table, pageSize = 100 } = await req.json()
  
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      let page = 0
      let hasMore = true
      
      while (hasMore) {
        const { data, error } = await supabase
          .from(table)
          .select('*')
          .range(page * pageSize, (page + 1) * pageSize - 1)
        
        if (error) {
          controller.error(error)
          break
        }
        
        if (data.length === 0) {
          hasMore = false
        } else {
          // NDJSON形式でストリーミング
          for (const row of data) {
            controller.enqueue(encoder.encode(JSON.stringify(row) + '\n'))
          }
          page++
        }
        
        // バックプレッシャー対応
        await new Promise(resolve => setTimeout(resolve, 10))
      }
      
      controller.close()
    }
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'application/x-ndjson',
      'Transfer-Encoding': 'chunked'
    }
  })
}
```

### 4. 認証・セキュリティ最適化
```typescript
// auth/supabase-auth-optimizer.ts
import { createClient } from '@supabase/supabase-js'
import { ref, computed } from 'vue'

export class AuthOptimizer {
  private supabase: any
  private sessionRefreshTimer: NodeJS.Timeout | null = null
  private user = ref(null)
  private session = ref(null)
  
  constructor() {
    this.supabase = createClient(
      import.meta.env.VITE_SUPABASE_URL,
      import.meta.env.VITE_SUPABASE_ANON_KEY
    )
    
    this.initializeAuth()
  }
  
  // 認証初期化
  private async initializeAuth() {
    // セッション復元
    const { data: { session } } = await this.supabase.auth.getSession()
    
    if (session) {
      this.session.value = session
      this.user.value = session.user
      this.setupSessionRefresh(session)
    }
    
    // 認証状態監視
    this.supabase.auth.onAuthStateChange((event: string, session: any) => {
      this.handleAuthChange(event, session)
    })
  }
  
  // マルチファクタ認証
  async enableMFA() {
    const { data: { id: factorId }, error } = await this.supabase.auth.mfa.enroll({
      factorType: 'totp'
    })
    
    if (error) throw error
    
    return {
      factorId,
      qrCode: await this.generateQRCode(factorId)
    }
  }
  
  // ソーシャルログイン最適化
  async signInWithProvider(provider: string) {
    const { data, error } = await this.supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        scopes: this.getProviderScopes(provider),
        queryParams: {
          access_type: 'offline',
          prompt: 'consent'
        }
      }
    })
    
    if (error) throw error
    
    return data
  }
  
  // セッション自動更新
  private setupSessionRefresh(session: any) {
    if (this.sessionRefreshTimer) {
      clearTimeout(this.sessionRefreshTimer)
    }
    
    // 有効期限の5分前に更新
    const expiresIn = session.expires_in * 1000
    const refreshTime = expiresIn - 300000 // 5分前
    
    this.sessionRefreshTimer = setTimeout(async () => {
      const { data, error } = await this.supabase.auth.refreshSession()
      
      if (!error && data.session) {
        this.session.value = data.session
        this.setupSessionRefresh(data.session)
      }
    }, refreshTime)
  }
  
  // 権限チェック最適化
  async checkPermission(resource: string, action: string) {
    // キャッシュチェック
    const cacheKey = `perm:${this.user.value?.id}:${resource}:${action}`
    const cached = this.permissionCache.get(cacheKey)
    
    if (cached && cached.expires > Date.now()) {
      return cached.allowed
    }
    
    // データベースチェック
    const { data, error } = await this.supabase
      .rpc('check_permission', {
        p_user_id: this.user.value?.id,
        p_resource_type: resource,
        p_required_level: this.getActionLevel(action)
      })
    
    if (error) throw error
    
    // キャッシュ保存
    this.permissionCache.set(cacheKey, {
      allowed: data,
      expires: Date.now() + 60000 // 1分間
    })
    
    return data
  }
}

// Vue3 Composable
export function useSupabaseAuth() {
  const optimizer = new AuthOptimizer()
  
  const isAuthenticated = computed(() => !!optimizer.user.value)
  const currentUser = computed(() => optimizer.user.value)
  
  const signIn = async (email: string, password: string) => {
    return await optimizer.signIn(email, password)
  }
  
  const signUp = async (email: string, password: string, metadata?: any) => {
    return await optimizer.signUp(email, password, metadata)
  }
  
  const signOut = async () => {
    return await optimizer.signOut()
  }
  
  const can = async (resource: string, action: string) => {
    return await optimizer.checkPermission(resource, action)
  }
  
  return {
    isAuthenticated,
    currentUser,
    signIn,
    signUp,
    signOut,
    can
  }
}
```

### 5. ストレージ最適化
```typescript
// storage/supabase-storage-optimizer.ts
export class StorageOptimizer {
  private supabase: any
  private uploadQueue: Map<string, any> = new Map()
  private cdnCache: Map<string, string> = new Map()
  
  // 画像最適化アップロード
  async uploadOptimizedImage(
    file: File,
    bucket: string,
    options: {
      maxWidth?: number
      maxHeight?: number
      quality?: number
      format?: 'webp' | 'avif' | 'jpeg'
    } = {}
  ) {
    // 画像圧縮
    const optimized = await this.optimizeImage(file, options)
    
    // サムネイル生成
    const thumbnail = await this.generateThumbnail(optimized, {
      width: 200,
      height: 200
    })
    
    // 並列アップロード
    const [mainUpload, thumbUpload] = await Promise.all([
      this.supabase.storage
        .from(bucket)
        .upload(`images/${Date.now()}_${file.name}`, optimized, {
          cacheControl: '3600',
          upsert: false,
          contentType: `image/${options.format || 'webp'}`
        }),
      this.supabase.storage
        .from(bucket)
        .upload(`thumbnails/${Date.now()}_${file.name}`, thumbnail, {
          cacheControl: '3600',
          upsert: false
        })
    ])
    
    if (mainUpload.error) throw mainUpload.error
    
    // CDN URL生成
    const cdnUrl = this.getCDNUrl(bucket, mainUpload.data.path)
    
    return {
      url: cdnUrl,
      thumbnailUrl: this.getCDNUrl(bucket, thumbUpload.data.path),
      size: optimized.size,
      format: options.format || 'webp'
    }
  }
  
  // チャンクアップロード
  async uploadLargeFile(
    file: File,
    bucket: string,
    onProgress?: (progress: number) => void
  ) {
    const chunkSize = 5 * 1024 * 1024 // 5MB
    const chunks = Math.ceil(file.size / chunkSize)
    const uploadId = crypto.randomUUID()
    
    for (let i = 0; i < chunks; i++) {
      const start = i * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const chunk = file.slice(start, end)
      
      const { error } = await this.supabase.storage
        .from(bucket)
        .upload(
          `chunks/${uploadId}/${i}`,
          chunk,
          {
            cacheControl: '3600',
            upsert: false
          }
        )
      
      if (error) throw error
      
      if (onProgress) {
        onProgress(((i + 1) / chunks) * 100)
      }
    }
    
    // チャンク結合（Edge Function経由）
    const { data, error } = await this.supabase.functions.invoke('merge-chunks', {
      body: { uploadId, chunks, fileName: file.name }
    })
    
    if (error) throw error
    
    return data
  }
  
  // CDN最適化
  private getCDNUrl(bucket: string, path: string): string {
    const baseUrl = this.supabase.storage.from(bucket).getPublicUrl(path).data.publicUrl
    
    // CloudFlare/Fastly CDN URL変換
    const cdnUrl = baseUrl.replace(
      'supabase.co',
      'cdn.yourapp.com'
    )
    
    // クエリパラメータで画像変換
    return `${cdnUrl}?w=auto&q=80&f=auto`
  }
  
  // プリフェッチ戦略
  async prefetchImages(urls: string[]) {
    const link = document.createElement('link')
    
    urls.forEach(url => {
      if (!this.cdnCache.has(url)) {
        link.rel = 'prefetch'
        link.as = 'image'
        link.href = url
        document.head.appendChild(link)
        
        this.cdnCache.set(url, url)
      }
    })
  }
}
```

## 出力レポート
```markdown
# Vue3+Supabase 最適化レポート

## 実施項目
✅ Realtime購読: バッチ処理で80%効率化
✅ RLS自動生成: 全テーブル適用完了
✅ Edge Functions: 5つのFunction最適化
✅ 認証フロー: MFA対応、セッション自動更新
✅ ストレージ: CDN統合、画像最適化

## パフォーマンス改善
- Realtime遅延: 500ms → 50ms (90%改善)
- API応答時間: Edge Functions で 70%高速化
- 画像ロード: WebP/AVIF で 60%サイズ削減
- 認証処理: セッション管理で 80%高速化

## セキュリティ強化
- RLS: 全テーブル有効化
- MFA: TOTP実装
- 権限: 階層的権限管理
- 監査: 全操作ログ記録

## 推奨事項
1. Realtime購読の更なる最適化
2. Edge Functionsの地域展開
3. Vector Embeddingsの活用
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: Vue3 + Supabase リアルタイム開発

---
*このコマンドはVue3+Supabaseのリアルタイムアプリケーション開発に特化しています。*