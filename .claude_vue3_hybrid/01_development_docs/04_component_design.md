# 状態管理設計

Vue 3 Composition APIとSupabase統合によるPiniaを使用した状態管理アーキテクチャの包括的なガイド。

## 目次

1. [状態アーキテクチャ概要](#1-状態アーキテクチャ概要)
2. [ストア設計パターン](#2-ストア設計パターン)
3. [データフロー管理](#3-データフロー管理)
4. [状態の正規化](#4-状態の正規化)
5. [非同期状態処理](#5-非同期状態処理)
6. [キャッシュ戦略](#6-キャッシュ戦略)
7. [楽観的更新](#7-楽観的更新)
8. [エラー状態管理](#8-エラー状態管理)

## 1. 状態アーキテクチャ概要

### 1.1 アプリケーション状態構造

```javascript
// stores/index.js
/**
 * 中央ストアレジストリと設定
 */

import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'

// ストアのインポート
import { useAppStore } from './app'
import { useUserStore } from './user'
import { usePostsStore } from './posts'
import { useNotificationsStore } from './notifications'
import { useUIStore } from './ui'

/**
 * アプリケーション状態構造
 * 
 * app/
 * ├── meta/           # アプリメタデータ（バージョン、設定など）
 * ├── auth/           # 認証状態
 * └── settings/       # グローバルアプリ設定
 * 
 * domain/
 * ├── users/          # ユーザー関連状態
 * ├── posts/          # 投稿とコンテンツ
 * ├── comments/       # コメント状態
 * ├── categories/     # カテゴリ管理
 * └── notifications/  # 通知システム
 * 
 * ui/
 * ├── layout/         # レイアウト状態（サイドバー、モーダルなど）
 * ├── forms/          # フォーム状態管理
 * ├── loading/        # ローディング状態
 * └── errors/         # エラー状態
 * 
 * cache/
 * ├── entities/       # 正規化されたエンティティキャッシュ
 * ├── queries/        # クエリ結果キャッシュ
 * └── metadata/       # キャッシュメタデータ（タイムスタンプなど）
 */

// Piniaの設定
export const pinia = createPinia()

// 永続化プラグインの追加
pinia.use(createPersistedState({
  storage: localStorage,
  beforeRestore: (context) => {
    // 復元前の永続化データの検証
    if (context.store.$id === 'auth' && !isValidAuthState(context.pinia.state.value)) {
      return false // 無効な認証状態の場合は復元をスキップ
    }
    return true
  }
}))

// 共通パターンを持つストアファクトリー
export function createStoreRegistry() {
  const stores = {
    app: useAppStore,
    user: useUserStore,
    posts: usePostsStore,
    notifications: useNotificationsStore,
    ui: useUIStore
  }
  
  /**
   * ストアインスタンスを取得
   * @param {string} name - ストア名
   * @returns {Object} ストアインスタンス
   */
  const getStore = (name) => {
    if (!stores[name]) {
      throw new Error(`ストア "${name}" が見つかりません`)
    }
    return stores[name]()
  }
  
  /**
   * 全ストアを初期化
   */
  const initializeStores = async () => {
    const initPromises = Object.values(stores).map(storeFactory => {
      const store = storeFactory()
      return store.initialize?.() || Promise.resolve()
    })
    
    await Promise.all(initPromises)
  }
  
  /**
   * 全ストアをリセット
   */
  const resetAllStores = () => {
    Object.values(stores).forEach(storeFactory => {
      const store = storeFactory()
      store.$reset?.()
    })
  }
  
  return {
    getStore,
    initializeStores,
    resetAllStores,
    stores
  }
}
```

### 1.2 レイヤー分離

```javascript
// stores/layers/index.js
/**
 * クリーンアーキテクチャのための状態レイヤー分離
 */

/**
 * プレゼンテーション層 - UI状態とビューロジック
 */
export const usePresentationLayer = defineStore('presentation', () => {
  const activeModal = ref(null)
  const sidebarOpen = ref(false)
  const theme = ref('light')
  const loading = ref(new Set())
  
  const isLoading = computed(() => loading.value.size > 0)
  
  const setLoading = (key, state) => {
    if (state) {
      loading.value.add(key)
    } else {
      loading.value.delete(key)
    }
  }
  
  return {
    activeModal,
    sidebarOpen,
    theme,
    loading: readonly(loading),
    isLoading,
    setLoading
  }
})

/**
 * ドメイン層 - ビジネスロジックとルール
 */
export const useDomainLayer = defineStore('domain', () => {
  const entities = ref(new Map())
  const relationships = ref(new Map())
  const businessRules = ref(new Map())
  
  /**
   * エンティティにビジネスルールを適用
   * @param {string} entityType - エンティティタイプ
   * @param {string} ruleKey - ビジネスルールキー
   * @param {Object} entity - エンティティデータ
   * @returns {Object} 検証済みエンティティ
   */
  const applyBusinessRule = (entityType, ruleKey, entity) => {
    const rule = businessRules.value.get(`${entityType}.${ruleKey}`)
    
    if (!rule) {
      throw new Error(`ビジネスルール "${ruleKey}" が ${entityType} に見つかりません`)
    }
    
    return rule.validate(entity)
  }
  
  /**
   * ビジネスルールを登録
   * @param {string} entityType - エンティティタイプ
   * @param {string} ruleKey - ルールキー
   * @param {Object} rule - ルール定義
   */
  const registerBusinessRule = (entityType, ruleKey, rule) => {
    businessRules.value.set(`${entityType}.${ruleKey}`, rule)
  }
  
  return {
    entities: readonly(entities),
    relationships: readonly(relationships),
    applyBusinessRule,
    registerBusinessRule
  }
})

/**
 * インフラストラクチャ層 - 外部サービスとデータアクセス
 */
export const useInfrastructureLayer = defineStore('infrastructure', () => {
  const apiClients = ref(new Map())
  const cache = ref(new Map())
  const syncQueue = ref([])
  
  /**
   * APIクライアントを登録
   * @param {string} name - クライアント名
   * @param {Object} client - APIクライアントインスタンス
   */
  const registerApiClient = (name, client) => {
    apiClients.value.set(name, client)
  }
  
  /**
   * APIクライアントを取得
   * @param {string} name - クライアント名
   * @returns {Object} APIクライアント
   */
  const getApiClient = (name) => {
    return apiClients.value.get(name)
  }
  
  /**
   * 同期操作をキューに追加
   * @param {Object} operation - 同期操作
   */
  const queueSync = (operation) => {
    syncQueue.value.push({
      ...operation,
      id: crypto.randomUUID(),
      timestamp: Date.now()
    })
  }
  
  /**
   * 同期キューを処理
   */
  const processSyncQueue = async () => {
    const operations = [...syncQueue.value]
    syncQueue.value = []
    
    for (const operation of operations) {
      try {
        await operation.execute()
      } catch (error) {
        // 失敗した操作を再キューに追加
        queueSync(operation)
        console.error('同期操作が失敗しました:', error)
      }
    }
  }
  
  return {
    apiClients: readonly(apiClients),
    cache: readonly(cache),
    syncQueue: readonly(syncQueue),
    registerApiClient,
    getApiClient,
    queueSync,
    processSyncQueue
  }
})
```

## 4. 状態の正規化

### 4.1 エンティティ正規化

```javascript
// stores/normalization.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 状態正規化ストア
 */
export const useNormalizationStore = defineStore('normalization', () => {
  const entities = ref({})
  const schemas = ref(new Map())
  
  /**
   * エンティティスキーマを登録
   * @param {string} entityType - エンティティタイプ
   * @param {Object} schema - エンティティスキーマ
   */
  const registerSchema = (entityType, schema) => {
    schemas.value.set(entityType, {
      ...schema,
      entityType
    })
  }
  
  /**
   * エンティティまたはエンティティ配列を正規化
   * @param {Object|Array} data - 正規化するデータ
   * @param {string} schemaType - スキーマタイプ
   * @returns {Object} 正規化されたデータ
   */
  const normalize = (data, schemaType) => {
    const schema = schemas.value.get(schemaType)
    if (!schema) {
      throw new Error(`スキーマ "${schemaType}" が見つかりません`)
    }
    
    const result = {
      entities: {},
      result: null
    }
    
    if (Array.isArray(data)) {
      result.result = data.map(item => normalizeEntity(item, schema, result.entities))
    } else {
      result.result = normalizeEntity(data, schema, result.entities)
    }
    
    return result
  }
  
  /**
   * 単一エンティティを正規化
   * @param {Object} entity - 正規化するエンティティ
   * @param {Object} schema - エンティティスキーマ
   * @param {Object} entities - エンティティアキュムレータ
   * @returns {string} エンティティID
   */
  const normalizeEntity = (entity, schema, entities) => {
    const { entityType, idAttribute = 'id' } = schema
    const entityId = entity[idAttribute]
    
    if (!entityId) {
      throw new Error(`エンティティに ${idAttribute} がありません`)
    }
    
    // エンティティタイプをエンティティに初期化
    if (!entities[entityType]) {
      entities[entityType] = {}
    }
    
    // 正規化されたエンティティを作成
    const normalizedEntity = { ...entity }
    
    // リレーションシップを処理
    if (schema.relationships) {
      Object.entries(schema.relationships).forEach(([key, relationSchema]) => {
        if (entity[key]) {
          if (relationSchema.type === 'array') {
            normalizedEntity[key] = entity[key].map(relatedEntity => 
              normalizeEntity(relatedEntity, relationSchema.schema, entities)
            )
          } else {
            normalizedEntity[key] = normalizeEntity(
              entity[key], 
              relationSchema.schema, 
              entities
            )
          }
        }
      })
    }
    
    // 正規化されたエンティティを保存
    entities[entityType][entityId] = normalizedEntity
    
    return entityId
  }
  
  /**
   * エンティティを非正規化
   * @param {string|Array} ids - エンティティID（複数可）
   * @param {string} schemaType - スキーマタイプ
   * @returns {Object|Array} 非正規化されたデータ
   */
  const denormalize = (ids, schemaType) => {
    const schema = schemas.value.get(schemaType)
    if (!schema) {
      throw new Error(`スキーマ "${schemaType}" が見つかりません`)
    }
    
    if (Array.isArray(ids)) {
      return ids.map(id => denormalizeEntity(id, schema))
    } else {
      return denormalizeEntity(ids, schema)
    }
  }
  
  /**
   * 単一エンティティを非正規化
   * @param {string} id - エンティティID
   * @param {Object} schema - エンティティスキーマ
   * @returns {Object} 非正規化されたエンティティ
   */
  const denormalizeEntity = (id, schema) => {
    const { entityType } = schema
    const entityState = entities.value[entityType]
    
    if (!entityState || !entityState[id]) {
      return null
    }
    
    const entity = { ...entityState[id] }
    
    // リレーションシップを処理
    if (schema.relationships) {
      Object.entries(schema.relationships).forEach(([key, relationSchema]) => {
        if (entity[key]) {
          if (relationSchema.type === 'array') {
            entity[key] = entity[key]
              .map(relatedId => denormalizeEntity(relatedId, relationSchema.schema))
              .filter(Boolean)
          } else {
            entity[key] = denormalizeEntity(entity[key], relationSchema.schema)
          }
        }
      })
    }
    
    return entity
  }
  
  /**
   * 正規化されたエンティティを更新
   * @param {string} entityType - エンティティタイプ
   * @param {string} id - エンティティID
   * @param {Object} updates - エンティティ更新
   */
  const updateEntity = (entityType, id, updates) => {
    if (!entities.value[entityType]) {
      entities.value[entityType] = {}
    }
    
    const currentEntity = entities.value[entityType][id] || {}
    entities.value[entityType][id] = {
      ...currentEntity,
      ...updates,
      _updatedAt: Date.now()
    }
  }
  
  /**
   * 正規化されたエンティティを削除
   * @param {string} entityType - エンティティタイプ
   * @param {string} id - エンティティID
   */
  const removeEntity = (entityType, id) => {
    if (entities.value[entityType]) {
      delete entities.value[entityType][id]
    }
  }
  
  /**
   * タイプとIDでエンティティを取得
   * @param {string} entityType - エンティティタイプ
   * @param {string} id - エンティティID
   * @returns {Object} エンティティ
   */
  const getEntity = (entityType, id) => {
    return entities.value[entityType]?.[id] || null
  }
  
  /**
   * タイプの全エンティティを取得
   * @param {string} entityType - エンティティタイプ
   * @returns {Array} エンティティ
   */
  const getEntitiesByType = (entityType) => {
    return Object.values(entities.value[entityType] || {})
  }
  
  return {
    entities: readonly(entities),
    schemas: readonly(schemas),
    registerSchema,
    normalize,
    denormalize,
    updateEntity,
    removeEntity,
    getEntity,
    getEntitiesByType
  }
})

// スキーマの例
export const userSchema = {
  entityType: 'users',
  idAttribute: 'id'
}

export const postSchema = {
  entityType: 'posts',
  idAttribute: 'id',
  relationships: {
    author: {
      type: 'single',
      schema: userSchema
    },
    comments: {
      type: 'array',
      schema: commentSchema
    }
  }
}

export const commentSchema = {
  entityType: 'comments',
  idAttribute: 'id',
  relationships: {
    author: {
      type: 'single',
      schema: userSchema
    }
  }
}
```

## 5. 非同期状態処理

### 5.1 ローディング状態管理

```javascript
// stores/loading.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * グローバルローディング状態管理
 */
export const useLoadingStore = defineStore('loading', () => {
  const loadingStates = ref(new Map())
  const loadingCounts = ref(new Map())
  
  const isLoading = computed(() => loadingStates.value.size > 0)
  const loadingKeys = computed(() => Array.from(loadingStates.value.keys()))
  
  /**
   * ローディング状態を設定
   * @param {string} key - ローディングキー
   * @param {boolean} loading - ローディング状態
   * @param {Object} metadata - ローディングメタデータ
   */
  const setLoading = (key, loading, metadata = {}) => {
    if (loading) {
      loadingStates.value.set(key, {
        startTime: Date.now(),
        ...metadata
      })
      
      // このキーのカウントを増加
      const currentCount = loadingCounts.value.get(key) || 0
      loadingCounts.value.set(key, currentCount + 1)
    } else {
      loadingStates.value.delete(key)
    }
  }
  
  /**
   * 特定のキーがローディング中かチェック
   * @param {string} key - ローディングキー
   * @returns {boolean} ローディング状態
   */
  const isLoadingKey = (key) => {
    return loadingStates.value.has(key)
  }
  
  /**
   * ローディングメタデータを取得
   * @param {string} key - ローディングキー
   * @returns {Object} ローディングメタデータ
   */
  const getLoadingMetadata = (key) => {
    return loadingStates.value.get(key) || null
  }
  
  /**
   * ローディング継続時間を取得
   * @param {string} key - ローディングキー
   * @returns {number} ミリ秒単位の継続時間
   */
  const getLoadingDuration = (key) => {
    const metadata = loadingStates.value.get(key)
    return metadata ? Date.now() - metadata.startTime : 0
  }
  
  /**
   * 非同期操作用のローディングラッパーを作成
   * @param {string} key - ローディングキー
   * @returns {Function} ローディングラッパー
   */
  const withLoading = (key) => {
    return async (asyncOperation) => {
      try {
        setLoading(key, true)
        const result = await asyncOperation()
        return result
      } finally {
        setLoading(key, false)
      }
    }
  }
  
  /**
   * 全ローディング状態をクリア
   */
  const clearAll = () => {
    loadingStates.value.clear()
  }
  
  return {
    loadingStates: readonly(loadingStates),
    loadingCounts: readonly(loadingCounts),
    isLoading,
    loadingKeys,
    setLoading,
    isLoadingKey,
    getLoadingMetadata,
    getLoadingDuration,
    withLoading,
    clearAll
  }
})
```

## 6. キャッシュ戦略

### 6.1 スマートキャッシュ管理

```javascript
// stores/cache.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 複数戦略を持つ高度なキャッシュストア
 */
export const useCacheStore = defineStore('cache', () => {
  const cache = ref(new Map())
  const metadata = ref(new Map())
  const strategies = ref(new Map())
  
  const cacheSize = computed(() => cache.value.size)
  const totalMemoryUsage = computed(() => {
    let total = 0
    for (const [key, data] of cache.value) {
      const meta = metadata.value.get(key)
      total += meta?.size || JSON.stringify(data).length
    }
    return total
  })
  
  /**
   * キャッシュ戦略を登録
   * @param {string} name - 戦略名
   * @param {Object} strategy - 戦略実装
   */
  const registerStrategy = (name, strategy) => {
    strategies.value.set(name, strategy)
  }
  
  /**
   * 戦略付きでキャッシュアイテムを設定
   * @param {string} key - キャッシュキー
   * @param {any} data - キャッシュするデータ
   * @param {Object} options - キャッシュオプション
   */
  const set = (key, data, options = {}) => {
    const {
      ttl = 300000, // デフォルト5分
      strategy = 'lru',
      tags = [],
      priority = 1,
      compress = false
    } = options
    
    let processedData = data
    
    // 要求があればデータを圧縮
    if (compress && typeof data === 'object') {
      processedData = compressData(data)
    }
    
    // データを保存
    cache.value.set(key, processedData)
    
    // メタデータを保存
    metadata.value.set(key, {
      createdAt: Date.now(),
      accessedAt: Date.now(),
      accessCount: 0,
      ttl,
      strategy,
      tags,
      priority,
      compressed: compress,
      size: JSON.stringify(data).length
    })
    
    // キャッシュ戦略を適用
    applyCacheStrategy(strategy)
  }
  
  /**
   * キャッシュアイテムを取得
   * @param {string} key - キャッシュキー
   * @returns {any} キャッシュされたデータまたは null
   */
  const get = (key) => {
    if (!cache.value.has(key)) {
      return null
    }
    
    const meta = metadata.value.get(key)
    
    // TTLをチェック
    if (meta && Date.now() - meta.createdAt > meta.ttl) {
      remove(key)
      return null
    }
    
    // アクセスメタデータを更新
    if (meta) {
      meta.accessedAt = Date.now()
      meta.accessCount++
    }
    
    let data = cache.value.get(key)
    
    // 必要に応じてデータを展開
    if (meta?.compressed) {
      data = decompressData(data)
    }
    
    return data
  }
  
  /**
   * キャッシュアイテムを削除
   * @param {string} key - キャッシュキー
   */
  const remove = (key) => {
    cache.value.delete(key)
    metadata.value.delete(key)
  }
  
  /**
   * タグでキャッシュをクリア
   * @param {Array} tags - クリアするタグ
   */
  const clearByTags = (tags) => {
    const keysToRemove = []
    
    for (const [key, meta] of metadata.value) {
      if (meta.tags.some(tag => tags.includes(tag))) {
        keysToRemove.push(key)
      }
    }
    
    keysToRemove.forEach(key => remove(key))
  }
  
  /**
   * キャッシュ戦略を適用
   * @param {string} strategyName - 戦略名
   */
  const applyCacheStrategy = (strategyName) => {
    const strategy = strategies.value.get(strategyName)
    if (strategy) {
      strategy.apply(cache.value, metadata.value)
    }
  }
  
  /**
   * キャッシュ統計を取得
   * @returns {Object} キャッシュ統計
   */
  const getStats = () => {
    let hits = 0
    let misses = 0
    let totalSize = 0
    
    for (const meta of metadata.value.values()) {
      hits += meta.accessCount
      totalSize += meta.size
    }
    
    return {
      size: cacheSize.value,
      hits,
      misses,
      hitRate: hits / (hits + misses) || 0,
      totalSize,
      averageItemSize: totalSize / cacheSize.value || 0
    }
  }
  
  /**
   * データを圧縮
   * @param {any} data - 圧縮するデータ
   * @returns {string} 圧縮されたデータ
   */
  const compressData = (data) => {
    // シンプルな圧縮実装
    // 本番環境では適切な圧縮ライブラリを使用
    return JSON.stringify(data)
  }
  
  /**
   * データを展開
   * @param {string} compressedData - 圧縮されたデータ
   * @returns {any} 展開されたデータ
   */
  const decompressData = (compressedData) => {
    return JSON.parse(compressedData)
  }
  
  /**
   * 期限切れアイテムをクリア
   */
  const clearExpired = () => {
    const now = Date.now()
    const expiredKeys = []
    
    for (const [key, meta] of metadata.value) {
      if (now - meta.createdAt > meta.ttl) {
        expiredKeys.push(key)
      }
    }
    
    expiredKeys.forEach(key => remove(key))
    
    return expiredKeys.length
  }
  
  /**
   * 全キャッシュをクリア
   */
  const clear = () => {
    cache.value.clear()
    metadata.value.clear()
  }
  
  return {
    cache: readonly(cache),
    metadata: readonly(metadata),
    cacheSize,
    totalMemoryUsage,
    registerStrategy,
    set,
    get,
    remove,
    clearByTags,
    getStats,
    clearExpired,
    clear
  }
})

// 組み込みキャッシュ戦略
export const cacheStrategies = {
  lru: {
    apply: (cache, metadata) => {
      const maxSize = 100 // 設定可能
      
      if (cache.size > maxSize) {
        // 最も使用頻度の低いアイテムを探す
        let lruKey = null
        let lruTime = Date.now()
        
        for (const [key, meta] of metadata) {
          if (meta.accessedAt < lruTime) {
            lruTime = meta.accessedAt
            lruKey = key
          }
        }
        
        if (lruKey) {
          cache.delete(lruKey)
          metadata.delete(lruKey)
        }
      }
    }
  },
  
  lfu: {
    apply: (cache, metadata) => {
      const maxSize = 100 // 設定可能
      
      if (cache.size > maxSize) {
        // 最も使用頻度の低いアイテムを探す
        let lfuKey = null
        let lfuCount = Infinity
        
        for (const [key, meta] of metadata) {
          if (meta.accessCount < lfuCount) {
            lfuCount = meta.accessCount
            lfuKey = key
          }
        }
        
        if (lfuKey) {
          cache.delete(lfuKey)
          metadata.delete(lfuKey)
        }
      }
    }
  },
  
  priority: {
    apply: (cache, metadata) => {
      const maxSize = 100 // 設定可能
      
      if (cache.size > maxSize) {
        // 最も優先度の低いアイテムを探す
        let lowPriorityKey = null
        let lowPriority = Infinity
        
        for (const [key, meta] of metadata) {
          if (meta.priority < lowPriority) {
            lowPriority = meta.priority
            lowPriorityKey = key
          }
        }
        
        if (lowPriorityKey) {
          cache.delete(lowPriorityKey)
          metadata.delete(lowPriorityKey)
        }
      }
    }
  }
}
```

## 7. 楽観的更新

### 7.1 楽観的更新マネージャー

```javascript
// stores/optimisticUpdates.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 楽観的更新管理ストア
 */
export const useOptimisticUpdatesStore = defineStore('optimisticUpdates', () => {
  const pendingUpdates = ref(new Map())
  const updateHistory = ref([])
  const rollbackQueue = ref([])
  
  const hasPendingUpdates = computed(() => pendingUpdates.value.size > 0)
  const pendingCount = computed(() => pendingUpdates.value.size)
  
  /**
   * 楽観的更新を適用
   * @param {string} key - 更新キー
   * @param {Object} update - 更新設定
   */
  const applyOptimisticUpdate = (key, update) => {
    const {
      entity,
      operation, // 'create', 'update', 'delete'
      changes,
      rollbackData,
      storeName,
      storeAction
    } = update
    
    const updateRecord = {
      id: crypto.randomUUID(),
      key,
      entity,
      operation,
      changes,
      rollbackData,
      storeName,
      storeAction,
      appliedAt: Date.now(),
      status: 'pending'
    }
    
    // 保留中の更新を保存
    pendingUpdates.value.set(key, updateRecord)
    
    // 楽観的変更を即座に適用
    if (storeName && storeAction) {
      const store = getStore(storeName)
      if (store && store[storeAction]) {
        try {
          store[storeAction](changes)
          updateRecord.status = 'applied'
        } catch (error) {
          updateRecord.status = 'failed'
          updateRecord.error = error.message
        }
      }
    }
    
    return updateRecord
  }
  
  /**
   * 楽観的更新を確認
   * @param {string} key - 更新キー
   * @param {any} serverResponse - サーバーレスポンス
   */
  const confirmUpdate = (key, serverResponse = null) => {
    const update = pendingUpdates.value.get(key)
    
    if (update) {
      update.status = 'confirmed'
      update.confirmedAt = Date.now()
      update.serverResponse = serverResponse
      
      // 履歴に移動
      updateHistory.value.push(update)
      pendingUpdates.value.delete(key)
      
      // サーバーレスポンスが楽観的更新と異なる場合は調整
      if (serverResponse && update.entity) {
        reconcileWithServerResponse(update, serverResponse)
      }
    }
  }
  
  /**
   * 楽観的更新をロールバック
   * @param {string} key - 更新キー
   * @param {string} reason - ロールバック理由
   */
  const rollbackUpdate = (key, reason = '不明なエラー') => {
    const update = pendingUpdates.value.get(key)
    
    if (update) {
      update.status = 'rolledback'
      update.rolledbackAt = Date.now()
      update.rollbackReason = reason
      
      // ロールバックを適用
      if (update.rollbackData && update.storeName && update.storeAction) {
        const store = getStore(update.storeName)
        const rollbackAction = getRollbackAction(update.operation)
        
        if (store && store[rollbackAction]) {
          try {
            store[rollbackAction](update.rollbackData)
          } catch (error) {
            console.error('ロールバックが失敗しました:', error)
            
            // 手動ロールバック用にキューに追加
            rollbackQueue.value.push({
              ...update,
              rollbackError: error.message
            })
          }
        }
      }
      
      // 履歴に移動
      updateHistory.value.push(update)
      pendingUpdates.value.delete(key)
    }
  }
  
  /**
   * 楽観的更新をサーバーレスポンスと調整
   * @param {Object} update - 更新レコード
   * @param {any} serverResponse - サーバーレスポンス
   */
  const reconcileWithServerResponse = (update, serverResponse) => {
    // 楽観的変更とサーバーレスポンスを比較
    const differences = findDifferences(update.changes, serverResponse)
    
    if (differences.length > 0) {
      // サーバー修正を適用
      if (update.storeName && update.storeAction) {
        const store = getStore(update.storeName)
        if (store && store[update.storeAction]) {
          try {
            store[update.storeAction](serverResponse)
            
            // 調整をログ
            console.warn('楽観的更新がサーバーと調整されました:', {
              key: update.key,
              differences,
              serverResponse
            })
          } catch (error) {
            console.error('調整が失敗しました:', error)
          }
        }
      }
    }
  }
  
  /**
   * 操作のロールバックアクションを取得
   * @param {string} operation - 操作タイプ
   * @returns {string} ロールバックアクション名
   */
  const getRollbackAction = (operation) => {
    const rollbackActions = {
      create: 'deleteEntity',
      update: 'updateEntity',
      delete: 'createEntity'
    }
    
    return rollbackActions[operation] || 'updateEntity'
  }
  
  /**
   * オブジェクト間の差分を見つける
   * @param {Object} obj1 - 最初のオブジェクト
   * @param {Object} obj2 - 2番目のオブジェクト
   * @returns {Array} 差分の配列
   */
  const findDifferences = (obj1, obj2) => {
    const differences = []
    
    const allKeys = new Set([...Object.keys(obj1), ...Object.keys(obj2)])
    
    for (const key of allKeys) {
      if (obj1[key] !== obj2[key]) {
        differences.push({
          key,
          optimistic: obj1[key],
          server: obj2[key]
        })
      }
    }
    
    return differences
  }
  
  /**
   * 失敗した楽観的更新を再試行
   * @param {string} key - 更新キー
   */
  const retryUpdate = async (key) => {
    const update = pendingUpdates.value.get(key)
    
    if (update && update.status === 'failed') {
      update.status = 'retrying'
      update.retriedAt = Date.now()
      
      // 楽観的変更を再適用
      try {
        if (update.storeName && update.storeAction) {
          const store = getStore(update.storeName)
          if (store && store[update.storeAction]) {
            await store[update.storeAction](update.changes)
            update.status = 'applied'
          }
        }
      } catch (error) {
        update.status = 'failed'
        update.error = error.message
        throw error
      }
    }
  }
  
  /**
   * 更新履歴をクリア
   * @param {number} olderThan - この日時より古い更新をクリア
   */
  const clearHistory = (olderThan = Date.now() - 24 * 60 * 60 * 1000) => {
    updateHistory.value = updateHistory.value.filter(
      update => update.appliedAt > olderThan
    )
  }
  
  /**
   * エンティティの保留中更新を取得
   * @param {string} entityId - エンティティID
   * @returns {Array} 保留中更新
   */
  const getPendingUpdatesForEntity = (entityId) => {
    return Array.from(pendingUpdates.value.values())
      .filter(update => update.entity?.id === entityId)
  }
  
  return {
    pendingUpdates: readonly(pendingUpdates),
    updateHistory: readonly(updateHistory),
    rollbackQueue: readonly(rollbackQueue),
    hasPendingUpdates,
    pendingCount,
    applyOptimisticUpdate,
    confirmUpdate,
    rollbackUpdate,
    retryUpdate,
    clearHistory,
    getPendingUpdatesForEntity
  }
})
```

## 8. エラー状態管理

### 8.1 包括的エラーハンドリング

```javascript
// stores/errors.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 集中エラー管理ストア
 */
export const useErrorStore = defineStore('errors', () => {
  const errors = ref([])
  const errorTypes = ref(new Map())
  const errorHandlers = ref(new Map())
  const globalErrorHandler = ref(null)
  
  const activeErrors = computed(() => 
    errors.value.filter(error => !error.dismissed)
  )

### 2.1 エンティティストアパターン

```javascript
// stores/patterns/entityStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 汎用エンティティストアファクトリー
 * @param {string} entityName - エンティティ名
 * @param {Object} config - エンティティ設定
 * @returns {Function} ストア定義
 */
export function createEntityStore(entityName, config = {}) {
  const {
    idField = 'id',
    relationships = {},
    validators = {},
    defaultState = {},
    cacheTimeout = 300000
  } = config
  
  return defineStore(`${entityName}Entity`, () => {
    // 状態
    const entities = ref(new Map())
    const selectedIds = ref(new Set())
    const loading = ref(new Map())
    const errors = ref(new Map())
    const metadata = ref({
      total: 0,
      lastFetch: null,
      filters: {},
      sorting: { field: 'created_at', direction: 'desc' }
    })
    
    // ゲッター
    const allEntities = computed(() => Array.from(entities.value.values()))
    
    const selectedEntities = computed(() => {
      return allEntities.value.filter(entity => 
        selectedIds.value.has(entity[idField])
      )
    })
    
    const entitiesByStatus = computed(() => {
      const grouped = new Map()
      
      allEntities.value.forEach(entity => {
        const status = entity.status || 'active'
        if (!grouped.has(status)) {
          grouped.set(status, [])
        }
        grouped.get(status).push(entity)
      })
      
      return grouped
    })
    
    const isLoading = computed(() => loading.value.size > 0)
    const hasErrors = computed(() => errors.value.size > 0)
    
    // アクション
    /**
     * APIからエンティティを取得
     * @param {Object} options - 取得オプション
     */
    const fetchEntities = async (options = {}) => {
      const fetchKey = JSON.stringify(options)
      
      try {
        loading.value.set(fetchKey, true)
        errors.value.delete(fetchKey)
        
        const response = await api.get(`/${entityName}`, {
          params: {
            ...metadata.value.filters,
            ...options.filters,
            sort: `${metadata.value.sorting.field}:${metadata.value.sorting.direction}`,
            ...options.params
          }
        })
        
        // エンティティを正規化して保存
        response.data.forEach(entityData => {
          const normalizedEntity = normalizeEntity(entityData)
          entities.value.set(normalizedEntity[idField], normalizedEntity)
        })
        
        // メタデータを更新
        metadata.value = {
          ...metadata.value,
          total: response.meta?.total || response.data.length,
          lastFetch: Date.now(),
          ...options.updateMetadata
        }
        
        return response.data
      } catch (error) {
        errors.value.set(fetchKey, error)
        throw error
      } finally {
        loading.value.delete(fetchKey)
      }
    }
    
    /**
     * IDで単一エンティティを取得
     * @param {string} id - エンティティID
     * @param {Object} options - 取得オプション
     */
    const fetchEntity = async (id, options = {}) => {
      const loadingKey = `entity-${id}`
      
      // 最初にキャッシュを確認
      if (!options.forceRefresh && entities.value.has(id)) {
        const cached = entities.value.get(id)
        const cacheAge = Date.now() - (cached._fetchedAt || 0)
        
        if (cacheAge < cacheTimeout) {
          return cached
        }
      }
      
      try {
        loading.value.set(loadingKey, true)
        errors.value.delete(loadingKey)
        
        const response = await api.get(`/${entityName}/${id}`, {
          params: options.params
        })
        
        const normalizedEntity = normalizeEntity(response.data)
        entities.value.set(id, normalizedEntity)
        
        return normalizedEntity
      } catch (error) {
        errors.value.set(loadingKey, error)
        throw error
      } finally {
        loading.value.delete(loadingKey)
      }
    }
    
    /**
     * 新しいエンティティを作成
     * @param {Object} entityData - エンティティデータ
     */
    const createEntity = async (entityData) => {
      const loadingKey = 'create'
      
      try {
        loading.value.set(loadingKey, true)
        errors.value.delete(loadingKey)
        
        // エンティティデータを検証
        const validatedData = await validateEntity(entityData, 'create')
        
        const response = await api.post(`/${entityName}`, validatedData)
        
        const normalizedEntity = normalizeEntity(response.data)
        entities.value.set(normalizedEntity[idField], normalizedEntity)
        
        // メタデータを更新
        metadata.value.total += 1
        
        return normalizedEntity
      } catch (error) {
        errors.value.set(loadingKey, error)
        throw error
      } finally {
        loading.value.delete(loadingKey)
      }
    }
    
    /**
     * 既存エンティティを更新
     * @param {string} id - エンティティID
     * @param {Object} updates - エンティティ更新
     */
    const updateEntity = async (id, updates) => {
      const loadingKey = `update-${id}`
      const currentEntity = entities.value.get(id)
      
      try {
        loading.value.set(loadingKey, true)
        errors.value.delete(loadingKey)
        
        // 楽観的更新
        if (currentEntity) {
          entities.value.set(id, { ...currentEntity, ...updates })
        }
        
        // 更新を検証
        const validatedUpdates = await validateEntity(updates, 'update')
        
        const response = await api.patch(`/${entityName}/${id}`, validatedUpdates)
        
        const normalizedEntity = normalizeEntity(response.data)
        entities.value.set(id, normalizedEntity)
        
        return normalizedEntity
      } catch (error) {
        // エラー時は楽観的更新を戻す
        if (currentEntity) {
          entities.value.set(id, currentEntity)
        }
        
        errors.value.set(loadingKey, error)
        throw error
      } finally {
        loading.value.delete(loadingKey)
      }
    }
    
    /**
     * エンティティを削除
     * @param {string} id - エンティティID
     */
    const deleteEntity = async (id) => {
      const loadingKey = `delete-${id}`
      const deletedEntity = entities.value.get(id)
      
      try {
        loading.value.set(loadingKey, true)
        errors.value.delete(loadingKey)
        
        // 楽観的削除
        entities.value.delete(id)
        selectedIds.value.delete(id)
        
        await api.delete(`/${entityName}/${id}`)
        
        // メタデータを更新
        metadata.value.total = Math.max(0, metadata.value.total - 1)
        
        return deletedEntity
      } catch (error) {
        // エラー時は楽観的削除を戻す
        if (deletedEntity) {
          entities.value.set(id, deletedEntity)
        }
        
        errors.value.set(loadingKey, error)
        throw error
      } finally {
        loading.value.delete(loadingKey)
      }
    }
    
    /**
     * エンティティを選択/選択解除
     * @param {string|Array} ids - エンティティID（複数可）
     * @param {boolean} selected - 選択状態
     */
    const setSelection = (ids, selected = true) => {
      const idArray = Array.isArray(ids) ? ids : [ids]
      
      idArray.forEach(id => {
        if (selected) {
          selectedIds.value.add(id)
        } else {
          selectedIds.value.delete(id)
        }
      })
    }
    
    /**
     * 全選択をクリア
     */
    const clearSelection = () => {
      selectedIds.value.clear()
    }
    
    /**
     * フィルターを適用
     * @param {Object} filters - フィルターオブジェクト
     */
    const setFilters = (filters) => {
      metadata.value.filters = { ...metadata.value.filters, ...filters }
    }
    
    /**
     * ソートを適用
     * @param {string} field - ソートフィールド
     * @param {string} direction - ソート方向
     */
    const setSorting = (field, direction = 'asc') => {
      metadata.value.sorting = { field, direction }
    }
    
    /**
     * エンティティデータを正規化
     * @param {Object} entityData - 生エンティティデータ
     * @returns {Object} 正規化されたエンティティ
     */
    const normalizeEntity = (entityData) => {
      const normalized = {
        ...defaultState,
        ...entityData,
        _fetchedAt: Date.now(),
        _normalized: true
      }
      
      // リレーションシップを処理
      Object.entries(relationships).forEach(([key, config]) => {
        if (normalized[key]) {
          normalized[key] = normalizeRelationship(normalized[key], config)
        }
      })
      
      return normalized
    }
    
    /**
     * リレーションシップデータを正規化
     * @param {any} relationData - リレーションシップデータ
     * @param {Object} config - リレーションシップ設定
     * @returns {any} 正規化されたリレーションシップ
     */
    const normalizeRelationship = (relationData, config) => {
      if (config.type === 'hasMany') {
        return Array.isArray(relationData) 
          ? relationData.map(item => item[config.idField || 'id'])
          : []
      } else if (config.type === 'belongsTo') {
        return typeof relationData === 'object' 
          ? relationData[config.idField || 'id']
          : relationData
      }
      
      return relationData
    }
    
    /**
     * エンティティデータを検証
     * @param {Object} entityData - 検証するエンティティデータ
     * @param {string} operation - 操作タイプ（create、update）
     * @returns {Object} 検証済みデータ
     */
    const validateEntity = async (entityData, operation) => {
      const relevantValidators = Object.entries(validators)
        .filter(([field, validator]) => {
          if (!validator.operations) return true
          return validator.operations.includes(operation)
        })
      
      const validatedData = { ...entityData }
      const validationErrors = []
      
      for (const [field, validator] of relevantValidators) {
        try {
          const value = validatedData[field]
          
          if (validator.required && (value === undefined || value === null || value === '')) {
            validationErrors.push(`${field} は必須です`)
            continue
          }
          
          if (value !== undefined && validator.validate) {
            const result = await validator.validate(value, validatedData)
            if (result !== true) {
              validationErrors.push(result || `${field} が無効です`)
            }
          }
          
          if (validator.transform) {
            validatedData[field] = validator.transform(value, validatedData)
          }
        } catch (error) {
          validationErrors.push(`${field}: ${error.message}`)
        }
      }
      
      if (validationErrors.length > 0) {
        throw new Error(`検証失敗: ${validationErrors.join(', ')}`)
      }
      
      return validatedData
    }
    
    /**
     * ストア状態をリセット
     */
    const $reset = () => {
      entities.value.clear()
      selectedIds.value.clear()
      loading.value.clear()
      errors.value.clear()
      metadata.value = {
        total: 0,
        lastFetch: null,
        filters: {},
        sorting: { field: 'created_at', direction: 'desc' }
      }
    }
    
    return {
      // 状態
      entities: readonly(entities),
      selectedIds: readonly(selectedIds),
      loading: readonly(loading),
      errors: readonly(errors),
      metadata: readonly(metadata),
      
      // ゲッター
      allEntities,
      selectedEntities,
      entitiesByStatus,
      isLoading,
      hasErrors,
      
      // アクション
      fetchEntities,
      fetchEntity,
      createEntity,
      updateEntity,
      deleteEntity,
      setSelection,
      clearSelection,
      setFilters,
      setSorting,
      $reset
    }
  })
}
```

### 2.2 コマンドパターンストア

```javascript
// stores/patterns/commandStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 複雑な操作を処理するためのコマンドパターンストア
 */
export const useCommandStore = defineStore('commands', () => {
  const commands = ref(new Map())
  const executionHistory = ref([])
  const undoStack = ref([])
  const redoStack = ref([])
  
  const canUndo = computed(() => undoStack.value.length > 0)
  const canRedo = computed(() => redoStack.value.length > 0)
  
  /**
   * コマンドを登録
   * @param {string} name - コマンド名
   * @param {Object} command - コマンド定義
   */
  const registerCommand = (name, command) => {
    if (!command.execute || typeof command.execute !== 'function') {
      throw new Error('コマンドには execute メソッドが必要です')
    }
    
    commands.value.set(name, {
      ...command,
      name,
      registered: Date.now()
    })
  }
  
  /**
   * コマンドを実行
   * @param {string} commandName - コマンド名
   * @param {Object} params - コマンドパラメータ
   * @param {Object} options - 実行オプション
   */
  const executeCommand = async (commandName, params = {}, options = {}) => {
    const command = commands.value.get(commandName)
    if (!command) {
      throw new Error(`コマンド "${commandName}" が見つかりません`)
    }
    
    const execution = {
      id: crypto.randomUUID(),
      commandName,
      params,
      timestamp: Date.now(),
      status: 'pending'
    }
    
    try {
      // 履歴に追加
      executionHistory.value.push(execution)
      
      // コマンドを実行
      const result = await command.execute(params, options)
      
      execution.status = 'completed'
      execution.result = result
      execution.completedAt = Date.now()
      
      // コマンドが元に戻せる場合は、undo スタックに追加
      if (command.undo && !options.skipUndo) {
        undoStack.value.push({
          ...execution,
          undoParams: command.getUndoParams ? 
            command.getUndoParams(params, result) : 
            params
        })
        
        // redo スタックをクリア
        redoStack.value = []
      }
      
      return result
    } catch (error) {
      execution.status = 'failed'
      execution.error = error.message
      execution.failedAt = Date.now()
      
      throw error
    }
  }
  
  /**
   * 最後のコマンドを元に戻す
   */
  const undo = async () => {
    if (!canUndo.value) {
      throw new Error('元に戻すものがありません')
    }
    
    const lastExecution = undoStack.value.pop()
    const command = commands.value.get(lastExecution.commandName)
    
    if (!command.undo) {
      throw new Error(`コマンド "${lastExecution.commandName}" は元に戻せません`)
    }
    
    try {
      await command.undo(lastExecution.undoParams, lastExecution.result)
      
      // redo スタックに追加
      redoStack.value.push(lastExecution)
      
      // 履歴に undo を追加
      executionHistory.value.push({
        id: crypto.randomUUID(),
        commandName: `undo_${lastExecution.commandName}`,
        params: lastExecution.undoParams,
        timestamp: Date.now(),
        status: 'completed',
        isUndo: true
      })
    } catch (error) {
      // undo が失敗した場合は undo スタックに戻す
      undoStack.value.push(lastExecution)
      throw error
    }
  }
  
  /**
   * 最後に元に戻したコマンドをやり直す
   */
  const redo = async () => {
    if (!canRedo.value) {
      throw new Error('やり直すものがありません')
    }
    
    const lastUndone = redoStack.value.pop()
    
    try {
      await executeCommand(
        lastUndone.commandName, 
        lastUndone.params, 
        { skipUndo: false }
      )
    } catch (error) {
      // redo が失敗した場合は redo スタックに戻す
      redoStack.value.push(lastUndone)
      throw error
    }
  }
  
  /**
   * コマンドのバッチを実行
   * @param {Array} commandBatch - コマンド定義の配列
   * @param {Object} options - バッチオプション
   */
  const executeBatch = async (commandBatch, options = {}) => {
    const { atomic = false } = options
    const results = []
    const executed = []
    
    try {
      for (const { name, params } of commandBatch) {
        const result = await executeCommand(name, params, { skipUndo: true })
        results.push(result)
        executed.push({ name, params, result })
      }
      
      // atomic の場合はバッチを undo スタックに追加
      if (atomic) {
        undoStack.value.push({
          id: crypto.randomUUID(),
          isBatch: true,
          commands: executed,
          timestamp: Date.now()
        })
      }
      
      return results
    } catch (error) {
      // atomic の場合は実行されたコマンドをロールバック
      if (atomic) {
        for (let i = executed.length - 1; i >= 0; i--) {
          const { name, params } = executed[i]
          const command = commands.value.get(name)
          
          if (command.undo) {
            try {
              await command.undo(params, executed[i].result)
            } catch (undoError) {
              console.error(`コマンド "${name}" のロールバックに失敗:`, undoError)
            }
          }
        }
      }
      
      throw error
    }
  }
  
  /**
   * コマンド履歴をクリア
   */
  const clearHistory = () => {
    executionHistory.value = []
    undoStack.value = []
    redoStack.value = []
  }
  
  return {
    commands: readonly(commands),
    executionHistory: readonly(executionHistory),
    undoStack: readonly(undoStack),
    redoStack: readonly(redoStack),
    canUndo,
    canRedo,
    registerCommand,
    executeCommand,
    undo,
    redo,
    executeBatch,
    clearHistory
  }
})

// コマンド定義の例
export const postCommands = {
  createPost: {
    execute: async (params) => {
      const response = await api.post('/posts', params)
      return response.data
    },
    undo: async (params, result) => {
      await api.delete(`/posts/${result.id}`)
    },
    getUndoParams: (params, result) => ({ id: result.id })
  },
  
  updatePost: {
    execute: async (params) => {
      const response = await api.patch(`/posts/${params.id}`, params.updates)
      return response.data
    },
    undo: async (undoParams) => {
      await api.patch(`/posts/${undoParams.id}`, undoParams.previousData)
    },
    getUndoParams: (params, result) => ({
      id: params.id,
      previousData: params.previousData
    })
  },
  
  deletePost: {
    execute: async (params) => {
      const response = await api.get(`/posts/${params.id}`)
      const post = response.data
      await api.delete(`/posts/${params.id}`)
      return post
    },
    undo: async (params, deletedPost) => {
      await api.post('/posts', deletedPost)
    }
  }
}
```

## 3. データフロー管理

### 3.1 単方向データフロー

```javascript
// stores/dataFlow.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * データフロー管理ストア
 */
export const useDataFlowStore = defineStore('dataFlow', () => {
  const actions = ref([])
  const middlewares = ref([])
  const subscribers = ref([])
  
  /**
   * ミドルウェアを登録
   * @param {Function} middleware - ミドルウェア関数
   */
  const use = (middleware) => {
    middlewares.value.push(middleware)
  }
  
  /**
   * アクションを購読
   * @param {Function} subscriber - 購読者関数
   * @returns {Function} 購読解除関数
   */
  const subscribe = (subscriber) => {
    subscribers.value.push(subscriber)
    
    return () => {
      const index = subscribers.value.indexOf(subscriber)
      if (index > -1) {
        subscribers.value.splice(index, 1)
      }
    }
  }
  
  /**
   * ミドルウェアチェーンを通してアクションをディスパッチ
   * @param {Object} action - アクションオブジェクト
   */
  const dispatch = async (action) => {
    const enrichedAction = {
      ...action,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      meta: {
        ...action.meta,
        source: action.meta?.source || 'unknown'
      }
    }
    
    // アクション履歴に追加
    actions.value.push(enrichedAction)
    
    // ミドルウェアチェーンを実行
    let currentAction = enrichedAction
    
    for (const middleware of middlewares.value) {
      try {
        const result = await middleware(currentAction, {
          dispatch,
          getState: () => getCurrentState()
        })
        
        if (result) {
          currentAction = result
        }
      } catch (error) {
        console.error('ミドルウェアエラー:', error)
        
        // エラーアクションをディスパッチ
        const errorAction = {
          type: 'MIDDLEWARE_ERROR',
          payload: { error, originalAction: currentAction },
          timestamp: Date.now()
        }
        
        // 購読者にエラーを通知
        notifySubscribers(errorAction)
        throw error
      }
    }
    
    // 購読者に通知
    notifySubscribers(currentAction)
    
    return currentAction
  }
  
  /**
   * 全購読者に通知
   * @param {Object} action - アクションオブジェクト
   */
  const notifySubscribers = (action) => {
    subscribers.value.forEach(subscriber => {
      try {
        subscriber(action)
      } catch (error) {
        console.error('購読者エラー:', error)
      }
    })
  }
  
  /**
   * 現在のアプリケーション状態を取得
   * @returns {Object} 現在の状態
   */
  const getCurrentState = () => {
    // 全ストアから状態を収集
    const state = {}
    
    // 登録されたストアを反復処理して状態を収集する
    // 実装はストア構造に基づく
    
    return state
  }
  
  return {
    actions: readonly(actions),
    use,
    subscribe,
    dispatch
  }
})

// ミドルウェアの例
export const loggingMiddleware = (action, { getState }) => {
  console.group(`アクション: ${action.type}`)
  console.log('ペイロード:', action.payload)
  console.log('事前状態:', getState())
  
  // アクションをそのまま通す
  return action
}

export const analyticsMiddleware = async (action, { getState }) => {
  // アナリティクス用にユーザーアクションを追跡
  if (action.meta?.trackable) {
    try {
      await analytics.track(action.type, {
        payload: action.payload,
        timestamp: action.timestamp,
        userId: getState().user?.id
      })
    } catch (error) {
      console.warn('アナリティクス追跡が失敗しました:', error)
    }
  }
  
  return action
}

export const validationMiddleware = (action, { getState }) => {
  // アクションペイロードを検証
  if (action.meta?.validate) {
    const validator = action.meta.validate
    const isValid = validator(action.payload, getState())
    
    if (!isValid) {
      throw new Error(`${action.type} のアクションペイロードが無効です`)
    }
  }
  
  return action
}