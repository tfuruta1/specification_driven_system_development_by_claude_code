# /vue3-hybrid-optimize - Vue3ハイブリッド接続システム最適化

## 概要
Vue3 + ハイブリッド接続（REST API → Supabase → Offline）の3層システムの包括的最適化コマンドです。**システム開発部主導**で部門協調による最適化を実現します。

## 🎯 部門別責任分担

### システム開発部（実装責任）
- Vue3ハイブリッド接続最適化
- 3層データフロー改善
- オフライン同期アルゴリズム
- パフォーマンス実装

### 品質保証部（検証責任）
- 接続パターンテスト
- データ整合性検証
- 3層同期品質保証
- エラーハンドリングテスト

### 経営企画部（戦略責任）
- ハイブリッドアーキテクチャ戦略
- データベース最適化設計
- 監視・可観測性戦略
- ROI効果測定

### 人事部（運用責任）
- 接続状態管理・ユーザビリティ
- ユーザートレーニング・サポート
- 運用マニュアル作成

## 使用方法
```bash
/vue3-hybrid-optimize [feature] [action] [options]

# 使用例
/vue3-hybrid-optimize fallback configure --multi-layer
/vue3-hybrid-optimize offline sync --strategy=eventual
/vue3-hybrid-optimize pwa install --service-worker
/vue3-hybrid-optimize cache optimize --indexeddb
/vue3-hybrid-optimize sync conflict-resolution --auto
```

## ハイブリッド専用最適化機能

### 1. 多層フォールバック戦略
```typescript
// services/hybrid-connection-manager.ts
import axios from 'axios'
import { createClient } from '@supabase/supabase-js'
import localforage from 'localforage'
import { ref, computed } from 'vue'

export class HybridConnectionManager {
  private layers: ConnectionLayer[] = []
  private currentLayer = ref<number>(0)
  private connectionStatus = ref<ConnectionStatus>('online')
  private syncQueue: SyncOperation[] = []
  private retryPolicy: RetryPolicy
  
  constructor() {
    // 接続レイヤーの優先順位設定
    this.layers = [
      {
        name: 'Primary API',
        type: 'rest',
        client: axios.create({
          baseURL: import.meta.env.VITE_PRIMARY_API,
          timeout: 5000
        }),
        priority: 1,
        healthCheck: '/health'
      },
      {
        name: 'Supabase',
        type: 'supabase',
        client: createClient(
          import.meta.env.VITE_SUPABASE_URL,
          import.meta.env.VITE_SUPABASE_KEY
        ),
        priority: 2,
        healthCheck: async () => {
          const { error } = await this.layers[1].client.from('health').select('*').limit(1)
          return !error
        }
      },
      {
        name: 'GraphQL API',
        type: 'graphql',
        client: new GraphQLClient(import.meta.env.VITE_GRAPHQL_ENDPOINT),
        priority: 3,
        healthCheck: '{ __typename }'
      },
      {
        name: 'Local Cache',
        type: 'local',
        client: localforage.createInstance({
          name: 'hybrid-cache',
          storeName: 'data'
        }),
        priority: 4,
        healthCheck: async () => true
      }
    ]
    
    this.initializeConnectionMonitoring()
    this.setupAutoSync()
  }
  
  // インテリジェントリクエストルーティング
  async request(options: RequestOptions): Promise<any> {
    const startTime = Date.now()
    let lastError: Error | null = null
    
    // 現在のレイヤーから順に試行
    for (let i = this.currentLayer.value; i < this.layers.length; i++) {
      const layer = this.layers[i]
      
      try {
        // レイヤー固有の処理
        const result = await this.executeLayerRequest(layer, options)
        
        // 成功時は上位レイヤーを復活チェック
        if (i > 0) {
          this.scheduleLayerRecoveryCheck()
        }
        
        // メトリクス記録
        this.recordMetrics({
          layer: layer.name,
          duration: Date.now() - startTime,
          success: true
        })
        
        return result
        
      } catch (error) {
        lastError = error as Error
        console.warn(`Layer ${layer.name} failed:`, error)
        
        // 次のレイヤーにフォールバック
        if (i < this.layers.length - 1) {
          this.currentLayer.value = i + 1
          continue
        }
      }
    }
    
    // すべてのレイヤーが失敗した場合
    throw new Error(`All layers failed. Last error: ${lastError?.message}`)
  }
  
  // レイヤー固有のリクエスト実行
  private async executeLayerRequest(layer: ConnectionLayer, options: RequestOptions) {
    switch (layer.type) {
      case 'rest':
        return await this.executeRestRequest(layer.client, options)
        
      case 'supabase':
        return await this.executeSupabaseRequest(layer.client, options)
        
      case 'graphql':
        return await this.executeGraphQLRequest(layer.client, options)
        
      case 'local':
        return await this.executeLocalRequest(layer.client, options)
        
      default:
        throw new Error(`Unknown layer type: ${layer.type}`)
    }
  }
  
  // オフライン対応のデータ同期
  async syncOfflineData() {
    if (this.connectionStatus.value === 'offline') {
      return { status: 'offline', synced: 0 }
    }
    
    const results = {
      succeeded: [],
      failed: [],
      conflicts: []
    }
    
    // 同期キューの処理
    while (this.syncQueue.length > 0) {
      const operation = this.syncQueue.shift()!
      
      try {
        // 競合検出
        const conflict = await this.detectConflict(operation)
        
        if (conflict) {
          const resolved = await this.resolveConflict(conflict, operation)
          if (resolved) {
            await this.executeSyncOperation(resolved)
            results.succeeded.push(resolved)
          } else {
            results.conflicts.push({ operation, conflict })
          }
        } else {
          await this.executeSyncOperation(operation)
          results.succeeded.push(operation)
        }
        
      } catch (error) {
        results.failed.push({ operation, error })
        // 失敗した操作は再度キューに戻す
        this.syncQueue.push(operation)
      }
    }
    
    return results
  }
  
  // 競合解決戦略
  private async resolveConflict(conflict: Conflict, operation: SyncOperation) {
    const strategy = this.getConflictResolutionStrategy(operation.type)
    
    switch (strategy) {
      case 'client-wins':
        return operation
        
      case 'server-wins':
        return null
        
      case 'merge':
        return this.mergeConflicts(conflict.serverData, operation.data)
        
      case 'manual':
        return await this.promptUserForResolution(conflict, operation)
        
      default:
        return operation
    }
  }
}

// オフライン対応のVue Composable
export function useHybridData<T>(
  resource: string,
  options: HybridOptions = {}
) {
  const manager = new HybridConnectionManager()
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const syncStatus = ref<SyncStatus>('synced')
  
  // データ取得（キャッシュファースト）
  const fetch = async () => {
    loading.value = true
    error.value = null
    
    try {
      // まずローカルキャッシュから取得
      const cached = await manager.getFromCache(resource)
      if (cached) {
        data.value = cached
        syncStatus.value = 'cached'
      }
      
      // バックグラウンドで最新データ取得
      manager.request({
        method: 'GET',
        resource,
        ...options
      }).then(fresh => {
        data.value = fresh
        syncStatus.value = 'synced'
        manager.updateCache(resource, fresh)
      }).catch(err => {
        // オンライン取得失敗時もキャッシュデータを維持
        if (!cached) {
          error.value = err
        }
      })
      
    } finally {
      loading.value = false
    }
  }
  
  // オプティミスティック更新
  const update = async (updates: Partial<T>) => {
    const previousData = data.value
    
    // 即座にUIを更新
    data.value = { ...data.value, ...updates } as T
    syncStatus.value = 'pending'
    
    try {
      // バックグラウンドで同期
      const result = await manager.request({
        method: 'PATCH',
        resource,
        data: updates
      })
      
      data.value = result
      syncStatus.value = 'synced'
      
    } catch (err) {
      // 失敗時はロールバック
      data.value = previousData
      syncStatus.value = 'error'
      error.value = err as Error
      
      // オフライン時は同期キューに追加
      if (manager.isOffline()) {
        manager.queueSync({
          type: 'update',
          resource,
          data: updates,
          timestamp: Date.now()
        })
        syncStatus.value = 'queued'
      }
    }
  }
  
  return {
    data,
    loading,
    error,
    syncStatus,
    fetch,
    update
  }
}
```

### 2. Progressive Web App (PWA) 最適化
```typescript
// pwa/service-worker.ts
/// <reference lib="webworker" />
declare const self: ServiceWorkerGlobalScope

import { precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { StaleWhileRevalidate, NetworkFirst, CacheFirst } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'
import { BackgroundSyncPlugin } from 'workbox-background-sync'
import { Queue } from 'workbox-background-sync'

// プリキャッシュ設定
precacheAndRoute(self.__WB_MANIFEST)

// APIキャッシュ戦略
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-cache',
    networkTimeoutSeconds: 3,
    plugins: [
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 5 * 60, // 5分
        purgeOnQuotaError: true
      }),
      new BackgroundSyncPlugin('api-queue', {
        maxRetentionTime: 24 * 60 // 24時間
      })
    ]
  })
)

// 静的アセットキャッシュ
registerRoute(
  ({ request }) => 
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'font',
  new CacheFirst({
    cacheName: 'static-assets',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30日
        purgeOnQuotaError: true
      })
    ]
  })
)

// 画像の最適化キャッシュ
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 200,
        maxAgeSeconds: 7 * 24 * 60 * 60, // 7日
        purgeOnQuotaError: true
      })
    ]
  })
)

// バックグラウンド同期
const bgSyncQueue = new Queue('bg-sync-queue', {
  onSync: async ({ queue }) => {
    let entry
    while ((entry = await queue.shiftRequest())) {
      try {
        await fetch(entry.request.clone())
        console.log('Background sync successful:', entry.request.url)
      } catch (error) {
        console.error('Background sync failed:', error)
        await queue.unshiftRequest(entry)
        throw error
      }
    }
  }
})

// オフライン時のフォールバック
self.addEventListener('fetch', (event) => {
  if (event.request.method === 'POST' || event.request.method === 'PUT') {
    const promiseChain = fetch(event.request.clone()).catch(() => {
      // オフライン時はキューに追加
      return bgSyncQueue.pushRequest({ request: event.request })
    })
    
    event.waitUntil(promiseChain)
  }
})

// プッシュ通知
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {}
  const title = data.title || 'New Update'
  const options = {
    body: data.body,
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: data.id
    },
    actions: [
      { action: 'explore', title: 'View' },
      { action: 'close', title: 'Dismiss' }
    ]
  }
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  )
})

// 定期的なバックグラウンド同期
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'content-sync') {
    event.waitUntil(syncContent())
  }
})

async function syncContent() {
  const cache = await caches.open('dynamic-content')
  const requests = await cache.keys()
  
  for (const request of requests) {
    try {
      const response = await fetch(request)
      await cache.put(request, response)
    } catch (error) {
      console.error('Sync failed for:', request.url)
    }
  }
}
```

### 3. IndexedDB最適化とオフラインストレージ
```typescript
// storage/indexed-db-manager.ts
import Dexie, { Table } from 'dexie'
import { compress, decompress } from 'lz-string'

export class OptimizedIndexedDB extends Dexie {
  data!: Table<any>
  metadata!: Table<any>
  syncQueue!: Table<any>
  
  constructor() {
    super('HybridAppDB')
    
    this.version(1).stores({
      data: '++id, resource, timestamp, [resource+timestamp]',
      metadata: 'key, value, expires',
      syncQueue: '++id, operation, resource, data, timestamp, retries'
    })
    
    // データ圧縮フック
    this.data.hook('creating', (primKey, obj) => {
      if (obj.content && obj.content.length > 1000) {
        obj.content = compress(JSON.stringify(obj.content))
        obj.compressed = true
      }
    })
    
    // データ解凍フック
    this.data.hook('reading', (obj) => {
      if (obj.compressed) {
        obj.content = JSON.parse(decompress(obj.content))
        delete obj.compressed
      }
      return obj
    })
  }
  
  // インテリジェントキャッシング
  async smartCache(resource: string, data: any, options: CacheOptions = {}) {
    const {
      ttl = 3600000, // 1時間
      priority = 'normal',
      compress = true
    } = options
    
    // 容量チェック
    const usage = await this.getStorageUsage()
    if (usage.percentage > 80) {
      await this.cleanupOldData(priority)
    }
    
    // データ保存
    await this.data.put({
      resource,
      content: data,
      timestamp: Date.now(),
      expires: Date.now() + ttl,
      priority,
      size: JSON.stringify(data).length
    })
    
    // メタデータ更新
    await this.updateMetadata(resource, {
      lastCached: Date.now(),
      accessCount: 0,
      priority
    })
  }
  
  // 予測的プリフェッチ
  async predictivePrefetch(currentResource: string) {
    // アクセスパターン分析
    const patterns = await this.analyzeAccessPatterns()
    const predictions = this.predictNextResources(currentResource, patterns)
    
    // 予測されたリソースをプリフェッチ
    for (const prediction of predictions) {
      if (prediction.probability > 0.7) {
        this.prefetchResource(prediction.resource)
      }
    }
  }
  
  // ストレージ最適化
  async optimizeStorage() {
    const now = Date.now()
    
    // 期限切れデータ削除
    await this.data.where('expires').below(now).delete()
    
    // アクセス頻度によるデータ整理
    const allData = await this.data.toArray()
    const sorted = allData.sort((a, b) => {
      const scoreA = this.calculateImportanceScore(a)
      const scoreB = this.calculateImportanceScore(b)
      return scoreB - scoreA
    })
    
    // 容量制限に基づく削除
    const maxSize = 50 * 1024 * 1024 // 50MB
    let currentSize = 0
    const toKeep = []
    
    for (const item of sorted) {
      currentSize += item.size || 0
      if (currentSize < maxSize) {
        toKeep.push(item.id)
      }
    }
    
    // 不要なデータを削除
    await this.data.where('id').noneOf(toKeep).delete()
  }
  
  // 同期キュー管理
  async queueForSync(operation: SyncOperation) {
    await this.syncQueue.add({
      ...operation,
      timestamp: Date.now(),
      retries: 0
    })
  }
  
  async processSyncQueue() {
    const queue = await this.syncQueue.toArray()
    const results = []
    
    for (const item of queue) {
      try {
        await this.executeSync(item)
        await this.syncQueue.delete(item.id)
        results.push({ id: item.id, status: 'success' })
        
      } catch (error) {
        item.retries++
        
        if (item.retries >= 3) {
          await this.syncQueue.delete(item.id)
          results.push({ id: item.id, status: 'failed', error })
        } else {
          await this.syncQueue.update(item.id, { retries: item.retries })
          results.push({ id: item.id, status: 'retry' })
        }
      }
    }
    
    return results
  }
}

// オフラインファーストのデータストア
export class OfflineFirstStore {
  private db: OptimizedIndexedDB
  private online = ref(navigator.onLine)
  
  constructor() {
    this.db = new OptimizedIndexedDB()
    
    // オンライン/オフライン検出
    window.addEventListener('online', () => {
      this.online.value = true
      this.syncPendingChanges()
    })
    
    window.addEventListener('offline', () => {
      this.online.value = false
    })
  }
  
  // データ取得（オフラインファースト）
  async get(resource: string) {
    // まずローカルから取得
    const local = await this.db.data
      .where('resource')
      .equals(resource)
      .and(item => item.expires > Date.now())
      .first()
    
    if (local) {
      // バックグラウンドで更新チェック
      if (this.online.value) {
        this.refreshInBackground(resource)
      }
      return local.content
    }
    
    // ローカルになければオンライン取得
    if (this.online.value) {
      const fresh = await this.fetchFromServer(resource)
      await this.db.smartCache(resource, fresh)
      return fresh
    }
    
    throw new Error('Data not available offline')
  }
  
  // 変更の永続化
  async save(resource: string, data: any) {
    // ローカルに即座に保存
    await this.db.smartCache(resource, data, {
      priority: 'high'
    })
    
    if (this.online.value) {
      // オンラインなら即座に同期
      try {
        await this.syncToServer(resource, data)
      } catch (error) {
        // 失敗したら同期キューに追加
        await this.db.queueForSync({
          operation: 'save',
          resource,
          data
        })
      }
    } else {
      // オフラインなら同期キューに追加
      await this.db.queueForSync({
        operation: 'save',
        resource,
        data
      })
    }
  }
}
```

### 4. 接続状態管理とネットワーク最適化
```typescript
// network/connection-optimizer.ts
export class ConnectionOptimizer {
  private connectionType = ref<string>('unknown')
  private bandwidth = ref<number>(0)
  private latency = ref<number>(0)
  private saveDataMode = ref<boolean>(false)
  
  constructor() {
    this.detectNetworkCapabilities()
    this.monitorNetworkChanges()
  }
  
  // ネットワーク能力検出
  private detectNetworkCapabilities() {
    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection
    
    if (connection) {
      this.connectionType.value = connection.effectiveType || 'unknown'
      this.bandwidth.value = connection.downlink || 0
      this.saveDataMode.value = connection.saveData || false
      
      connection.addEventListener('change', () => {
        this.detectNetworkCapabilities()
        this.adjustQualitySettings()
      })
    }
    
    // レイテンシー測定
    this.measureLatency()
  }
  
  // 適応的品質調整
  private adjustQualitySettings() {
    const settings = {
      imageQuality: 'high',
      videoQuality: '1080p',
      prefetchEnabled: true,
      cacheStrategy: 'aggressive'
    }
    
    // 接続タイプに基づく調整
    switch (this.connectionType.value) {
      case 'slow-2g':
      case '2g':
        settings.imageQuality = 'low'
        settings.videoQuality = '360p'
        settings.prefetchEnabled = false
        settings.cacheStrategy = 'minimal'
        break
        
      case '3g':
        settings.imageQuality = 'medium'
        settings.videoQuality = '480p'
        settings.prefetchEnabled = false
        settings.cacheStrategy = 'moderate'
        break
        
      case '4g':
        settings.imageQuality = 'high'
        settings.videoQuality = '720p'
        settings.prefetchEnabled = true
        settings.cacheStrategy = 'aggressive'
        break
        
      case 'wifi':
      case 'ethernet':
        settings.imageQuality = 'original'
        settings.videoQuality = '1080p'
        settings.prefetchEnabled = true
        settings.cacheStrategy = 'aggressive'
        break
    }
    
    // データセーブモード対応
    if (this.saveDataMode.value) {
      settings.imageQuality = 'low'
      settings.prefetchEnabled = false
      settings.cacheStrategy = 'minimal'
    }
    
    return settings
  }
  
  // リクエスト最適化
  optimizeRequest(url: string, options: RequestInit = {}) {
    const optimized = { ...options }
    
    // 低速接続時の最適化
    if (this.connectionType.value === '2g' || this.connectionType.value === '3g') {
      // タイムアウト延長
      optimized.signal = AbortSignal.timeout(30000)
      
      // Accept-Encoding追加
      optimized.headers = {
        ...optimized.headers,
        'Accept-Encoding': 'gzip, deflate, br'
      }
      
      // データセーブヘッダー
      if (this.saveDataMode.value) {
        optimized.headers['Save-Data'] = 'on'
      }
    }
    
    return optimized
  }
}
```

## 出力レポート
```markdown
# Vue3ハイブリッド接続 最適化レポート

## 実施項目
✅ 多層フォールバック: 4層構成実装
✅ オフライン対応: 完全オフライン動作実現
✅ PWA機能: Service Worker最適化
✅ IndexedDB: 50MB容量管理実装
✅ 同期戦略: 競合解決機能実装

## パフォーマンス改善
- オフライン起動時間: 即座（0秒）
- データ同期効率: 85%削減
- キャッシュヒット率: 92%
- ネットワーク使用量: 60%削減

## 信頼性向上
- 可用性: 99.9%（オフライン含む）
- データ整合性: 100%保証
- 自動リカバリー: 実装済み

## 推奨事項
1. WebRTC P2P同期の追加
2. 差分同期アルゴリズム導入
3. 予測的プリフェッチ強化
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: ハイブリッド接続・オフラインファースト開発

---
*このコマンドはVue3ハイブリッド接続アプリケーションに特化しています。*