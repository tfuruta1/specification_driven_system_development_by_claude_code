# パフォーマンス最適化設計書

## 概要

このドキュメントでは、Vue.js + Supabaseアプリケーションにおけるパフォーマンス最適化の戦略と実装方法を定義します。初期表示の高速化、バンドルサイズの最適化、リアルタイム機能の効率化など、ユーザー体験向上に直結する最適化手法を体系的に解説します。

## 1. パフォーマンス最適化戦略

### 1.1 最適化対象の分類
```javascript
// パフォーマンス最適化対象の体系化
const optimizationTargets = {
  loadTime: {
    firstContentfulPaint: "初回コンテンツ描画時間",
    largestContentfulPaint: "最大コンテンツ描画時間", 
    timeToInteractive: "操作可能になるまでの時間",
    firstInputDelay: "初回入力遅延"
  },
  
  runtime: {
    reactivity: "リアクティビティの効率化",
    rendering: "レンダリングパフォーマンス",
    memory: "メモリ使用量最適化",
    networkRequests: "ネットワークリクエスト最適化"
  },
  
  bundleSize: {
    treeShaking: "不要コードの除去",
    codesplitting: "コード分割",
    compression: "圧縮最適化",
    staticAssets: "静的アセット最適化"
  },
  
  database: {
    queryOptimization: "クエリ最適化",
    indexing: "インデックス戦略",
    caching: "キャッシュ戦略",
    connectionPooling: "コネクションプール"
  }
}
```

### 1.2 パフォーマンス目標設定
```javascript
// パフォーマンス目標値（Core Web Vitals準拠）
const performanceTargets = {
  loading: {
    lcp: "2.5秒以下", // Largest Contentful Paint
    fcp: "1.8秒以下", // First Contentful Paint
    ttfb: "600ms以下", // Time To First Byte
    speedIndex: "3.4秒以下"
  },
  
  interactivity: {
    fid: "100ms以下", // First Input Delay
    cls: "0.1以下", // Cumulative Layout Shift
    inp: "200ms以下", // Interaction to Next Paint
    tbt: "200ms以下" // Total Blocking Time
  },
  
  resources: {
    jsBundle: "250KB以下（gzip圧縮後）",
    cssBundle: "50KB以下（gzip圧縮後）",
    imageOptimization: "WebP形式、適切なサイズ",
    fontLoading: "FOUT/FOIT最小化"
  }
}
```

## 2. フロントエンド最適化

### 2.1 Vue.js パフォーマンス最適化
```vue
<!-- components/optimized/LazyComponent.vue -->
<template>
  <div class="lazy-component">
    <!-- 計算プロパティの活用 -->
    <div class="expensive-calculation">
      {{ expensiveComputation }}
    </div>
    
    <!-- 仮想スクロール -->
    <VirtualList
      v-if="items.length > 100"
      :items="items"
      :item-height="60"
      :container-height="400"
    >
      <template #default="{ item }">
        <ListItem :item="item" />
      </template>
    </VirtualList>
    
    <!-- 通常のリスト（少数要素） -->
    <div v-else class="regular-list">
      <ListItem
        v-for="item in items"
        :key="item.id"
        :item="item"
      />
    </div>
    
    <!-- 遅延ローディング画像 -->
    <LazyImage
      :src="imageUrl"
      :placeholder="placeholderUrl"
      loading="lazy"
    />
  </div>
</template>

<script setup>
import { ref, computed, shallowRef, defineAsyncComponent } from 'vue'
import { useDebounceFn, useThrottleFn } from '@vueuse/core'

// 遅延読み込みコンポーネント
const VirtualList = defineAsyncComponent({
  loader: () => import('./VirtualList.vue'),
  delay: 200,
  timeout: 3000,
  suspensible: false
})

const LazyImage = defineAsyncComponent(() => import('./LazyImage.vue'))

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  imageUrl: {
    type: String,
    required: true
  }
})

// shallowRefを使用してネストしたリアクティビティを制限
const items = shallowRef(props.data)

// 重い計算処理のメモ化
const expensiveComputation = computed(() => {
  // 複雑な計算処理
  return props.data
    .filter(item => item.active)
    .reduce((sum, item) => sum + item.value, 0)
})

// デバウンス処理
const debouncedSearch = useDebounceFn((query) => {
  // 検索処理
  console.log('検索:', query)
}, 300)

// スロットル処理
const throttledScroll = useThrottleFn((event) => {
  // スクロール処理
  console.log('スクロール:', event.target.scrollTop)
}, 16) // 60fps相当
</script>
```

### 2.2 リアクティビティ最適化
```javascript
// composables/useOptimizedStore.js
import { ref, shallowRef, triggerRef, readonly } from 'vue'

/**
 * 最適化されたストア管理
 */
export function useOptimizedStore() {
  // 大きなオブジェクトはshallowRefを使用
  const largeDataset = shallowRef([])
  
  // 読み取り専用データ
  const readonlyData = readonly(ref({}))
  
  // 頻繁に更新されるデータ
  const frequentUpdates = ref(0)
  
  /**
   * 大量データの効率的な更新
   * @param {Array} newData
   */
  const updateLargeDataset = (newData) => {
    // 参照を直接置き換えて再レンダリングを最小化
    largeDataset.value = newData
    // 手動でリアクティビティをトリガー
    triggerRef(largeDataset)
  }
  
  /**
   * バッチ更新
   * @param {Array} updates
   */
  const batchUpdate = (updates) => {
    // 複数の更新を一度に実行
    updates.forEach(update => {
      if (update.type === 'increment') {
        frequentUpdates.value += update.value
      }
    })
  }
  
  /**
   * 効率的なフィルタリング
   * @param {Function} predicate
   */
  const filterData = (predicate) => {
    // 新しい配列を作成せず、インデックスのみ管理
    const filteredIndices = []
    largeDataset.value.forEach((item, index) => {
      if (predicate(item)) {
        filteredIndices.push(index)
      }
    })
    return filteredIndices.map(i => largeDataset.value[i])
  }
  
  return {
    largeDataset: readonly(largeDataset),
    readonlyData,
    frequentUpdates: readonly(frequentUpdates),
    updateLargeDataset,
    batchUpdate,
    filterData
  }
}
```

### 2.3 コンポーネント分割戦略
```javascript
// utils/performance/componentSplitting.js

/**
 * 動的コンポーネント読み込み戦略
 */
export const componentSplittingStrategy = {
  // 即座に必要なコンポーネント
  critical: [
    'AppHeader',
    'Navigation',
    'MainContent'
  ],
  
  // ユーザー操作後に読み込み
  interactive: [
    'Modal',
    'Dropdown',
    'Tooltip'
  ],
  
  // ビューポートに入ったら読み込み
  viewport: [
    'Footer',
    'AdditionalContent',
    'RelatedItems'
  ],
  
  // ルート変更時に読み込み
  route: [
    'AdminPanel',
    'UserProfile',
    'Settings'
  ]
}

/**
 * スマートコンポーネントローダー
 */
export class SmartComponentLoader {
  constructor() {
    this.loadedComponents = new Set()
    this.loadingPromises = new Map()
  }
  
  /**
   * コンポーネントの遅延読み込み
   * @param {string} componentName
   * @param {Function} importer
   * @returns {Promise}
   */
  async loadComponent(componentName, importer) {
    if (this.loadedComponents.has(componentName)) {
      return null // 既に読み込み済み
    }
    
    if (this.loadingPromises.has(componentName)) {
      return this.loadingPromises.get(componentName)
    }
    
    const loadingPromise = importer()
    this.loadingPromises.set(componentName, loadingPromise)
    
    try {
      const component = await loadingPromise
      this.loadedComponents.add(componentName)
      return component
    } catch (error) {
      this.loadingPromises.delete(componentName)
      throw error
    }
  }
  
  /**
   * 複数コンポーネントの並列読み込み
   * @param {Object} components
   */
  async loadMultipleComponents(components) {
    const loadPromises = Object.entries(components).map(
      ([name, importer]) => this.loadComponent(name, importer)
    )
    
    return Promise.allSettled(loadPromises)
  }
  
  /**
   * プリロード（低優先度）
   * @param {string} componentName
   * @param {Function} importer
   */
  preloadComponent(componentName, importer) {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        this.loadComponent(componentName, importer)
      })
    } else {
      // フォールバック
      setTimeout(() => {
        this.loadComponent(componentName, importer)
      }, 0)
    }
  }
}
```

## 3. バンドル最適化

### 3.1 Vite最適化設定
```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue({
      // テンプレート最適化
      template: {
        compilerOptions: {
          // プロダクションビルドでdev-onlyブロックを除去
          isCustomElement: tag => tag.startsWith('custom-')
        }
      }
    })
  ],
  
  build: {
    // チャンク分割戦略
    rollupOptions: {
      output: {
        manualChunks: {
          // ベンダーライブラリ
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['@headlessui/vue', '@heroicons/vue'],
          'vendor-utils': ['lodash-es', 'date-fns'],
          
          // 機能別チャンク
          'feature-auth': [
            './src/stores/auth.js',
            './src/components/auth'
          ],
          'feature-dashboard': [
            './src/views/Dashboard.vue',
            './src/components/dashboard'
          ]
        },
        
        // ファイル命名規則
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId
          if (facadeModuleId) {
            const fileName = facadeModuleId.split('/').pop().replace('.vue', '')
            return `chunks/${fileName}-[hash].js`
          }
          return 'chunks/[name]-[hash].js'
        },
        
        // アセット命名
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          
          if (/\.(png|jpe?g|gif|svg)$/.test(assetInfo.name)) {
            return `images/[name]-[hash].${ext}`
          }
          if (/\.(woff2?|eot|ttf|otf)$/.test(assetInfo.name)) {
            return `fonts/[name]-[hash].${ext}`
          }
          return `assets/[name]-[hash].${ext}`
        }
      }
    },
    
    // 圧縮設定
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // console.logを除去
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.warn'] // 特定の関数を除去
      },
      mangle: {
        safari10: true // Safari 10対応
      }
    },
    
    // チャンクサイズ警告の閾値
    chunkSizeWarningLimit: 500,
    
    // ソースマップ（開発時のみ）
    sourcemap: process.env.NODE_ENV === 'development'
  },
  
  // 依存関係の最適化
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      '@supabase/supabase-js'
    ],
    exclude: [
      '@vueuse/core' // 部分的にインポートするため除外
    ]
  },
  
  // アセット処理
  assetsInclude: ['**/*.md'], // Markdownファイルをアセットとして扱う
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@composables': resolve(__dirname, 'src/composables'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@utils': resolve(__dirname, 'src/utils')
    }
  }
})
```

### 3.2 Tree Shakingの最適化
```javascript
// utils/performance/treeShaking.js

/**
 * Tree Shaking最適化ガイド
 */

// ❌ 悪い例：ライブラリ全体をインポート
import _ from 'lodash'
import * as dateUtils from 'date-fns'

// ✅ 良い例：必要な関数のみインポート
import { debounce, throttle } from 'lodash-es'
import { format, parseISO } from 'date-fns'

// ❌ 悪い例：デフォルトエクスポートの濫用
export default {
  utils: {
    formatDate: () => {},
    validateEmail: () => {},
    // ...多数の関数
  }
}

// ✅ 良い例：名前付きエクスポート
export const formatDate = (date) => {
  return format(date, 'yyyy-MM-dd')
}

export const validateEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * 条件付きインポートの最適化
 */
export const conditionalImports = {
  // 開発時のみのインポート
  async loadDevTools() {
    if (process.env.NODE_ENV === 'development') {
      const { setupDevtools } = await import('@vue/devtools')
      return setupDevtools
    }
    return null
  },
  
  // 機能フラグによる条件付きインポート
  async loadFeature(featureFlag) {
    if (featureFlag.enabled) {
      const feature = await import(`@/features/${featureFlag.name}`)
      return feature.default
    }
    return null
  },
  
  // ブラウザ機能による条件付きインポート
  async loadPolyfill() {
    if (!('IntersectionObserver' in window)) {
      await import('intersection-observer')
    }
  }
}

/**
 * 動的インポート最適化
 */
export class DynamicImportOptimizer {
  constructor() {
    this.importCache = new Map()
    this.preloadPromises = new Map()
  }
  
  /**
   * キャッシュ付き動的インポート
   * @param {string} modulePath
   * @returns {Promise}
   */
  async importWithCache(modulePath) {
    if (this.importCache.has(modulePath)) {
      return this.importCache.get(modulePath)
    }
    
    const module = await import(modulePath)
    this.importCache.set(modulePath, module)
    return module
  }
  
  /**
   * プリフェッチ
   * @param {string} modulePath
   */
  prefetch(modulePath) {
    if (!this.preloadPromises.has(modulePath)) {
      const link = document.createElement('link')
      link.rel = 'prefetch'
      link.href = modulePath
      document.head.appendChild(link)
      
      this.preloadPromises.set(modulePath, true)
    }
  }
  
  /**
   * プリロード（高優先度）
   * @param {string} modulePath
   */
  preload(modulePath) {
    if (!this.preloadPromises.has(modulePath)) {
      const link = document.createElement('link')
      link.rel = 'preload'
      link.as = 'script'
      link.href = modulePath
      document.head.appendChild(link)
      
      this.preloadPromises.set(modulePath, true)
    }
  }
}
```

## 4. データベース最適化

### 4.1 Supabaseクエリ最適化
```javascript
// services/database/optimizedQueries.js
import { supabase } from '@/lib/supabase'

/**
 * 最適化されたデータベースクエリ
 */
export class OptimizedQueries {
  /**
   * ページネーション付きクエリ
   * @param {string} table
   * @param {Object} options
   */
  static async getPaginatedData(table, options = {}) {
    const {
      page = 1,
      limit = 20,
      orderBy = 'created_at',
      orderDirection = 'desc',
      filters = {},
      select = '*'
    } = options
    
    let query = supabase
      .from(table)
      .select(select, { count: 'exact' })
      .order(orderBy, { ascending: orderDirection === 'asc' })
    
    // フィルター適用
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        query = query.in(key, value)
      } else if (typeof value === 'object' && value.operator) {
        query = query.filter(key, value.operator, value.value)
      } else {
        query = query.eq(key, value)
      }
    })
    
    // ページネーション
    const from = (page - 1) * limit
    const to = from + limit - 1
    
    const { data, error, count } = await query.range(from, to)
    
    if (error) throw error
    
    return {
      data,
      pagination: {
        page,
        limit,
        total: count,
        totalPages: Math.ceil(count / limit),
        hasNextPage: to < count - 1,
        hasPreviousPage: page > 1
      }
    }
  }
  
  /**
   * 関連データの効率的な取得
   * @param {string} userId
   */
  static async getUserWithRelations(userId) {
    const { data, error } = await supabase
      .from('users')
      .select(`
        id,
        email,
        display_name,
        avatar_url,
        profiles (
          bio,
          website,
          location
        ),
        posts (
          id,
          title,
          created_at,
          comments (
            id,
            content,
            created_at
          )
        )
      `)
      .eq('id', userId)
      .limit(10, { foreignTable: 'posts' })
      .limit(5, { foreignTable: 'posts.comments' })
      .order('created_at', { 
        foreignTable: 'posts', 
        ascending: false 
      })
      .single()
    
    if (error) throw error
    return data
  }
  
  /**
   * 検索最適化（全文検索）
   * @param {string} table
   * @param {string} query
   * @param {Array} columns
   */
  static async searchWithFullText(table, query, columns = ['title', 'content']) {
    // PostgreSQLの全文検索を活用
    const { data, error } = await supabase
      .from(table)
      .select('*')
      .textSearch('fts', query, {
        type: 'websearch',
        config: 'japanese' // 日本語検索設定
      })
      .limit(50)
    
    if (error) throw error
    return data
  }
  
  /**
   * バッチ更新
   * @param {string} table
   * @param {Array} updates
   */
  static async batchUpdate(table, updates) {
    const batchSize = 100
    const results = []
    
    for (let i = 0; i < updates.length; i += batchSize) {
      const batch = updates.slice(i, i + batchSize)
      
      const { data, error } = await supabase
        .from(table)
        .upsert(batch)
        .select()
      
      if (error) throw error
      results.push(...data)
    }
    
    return results
  }
  
  /**
   * 集計クエリの最適化
   * @param {string} table
   * @param {Object} options
   */
  static async getAggregatedData(table, options = {}) {
    const { groupBy, aggregations, filters = {} } = options
    
    let query = supabase
      .from(table)
      .select(`
        ${groupBy},
        ${aggregations.map(agg => `${agg.column}.${agg.function}()`).join(', ')}
      `)
    
    // フィルター適用
    Object.entries(filters).forEach(([key, value]) => {
      query = query.eq(key, value)
    })
    
    const { data, error } = await query
    
    if (error) throw error
    return data
  }
}
```

### 4.2 キャッシュ戦略
```javascript
// services/cache/cacheManager.js
import { ref, computed } from 'vue'

/**
 * 多層キャッシュマネージャー
 */
export class CacheManager {
  constructor() {
    this.memoryCache = new Map()
    this.indexedDBCache = null
    this.cacheStats = ref({
      hits: 0,
      misses: 0,
      evictions: 0
    })
    
    this.initIndexedDB()
  }
  
  /**
   * IndexedDBの初期化
   */
  async initIndexedDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('AppCache', 1)
      
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.indexedDBCache = request.result
        resolve()
      }
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        
        // キャッシュストア
        const cacheStore = db.createObjectStore('cache', { keyPath: 'key' })
        cacheStore.createIndex('expiry', 'expiry')
        cacheStore.createIndex('lastAccessed', 'lastAccessed')
      }
    })
  }
  
  /**
   * メモリキャッシュの取得
   * @param {string} key
   * @returns {*}
   */
  getFromMemory(key) {
    const item = this.memoryCache.get(key)
    if (!item) return null
    
    if (Date.now() > item.expiry) {
      this.memoryCache.delete(key)
      this.cacheStats.value.evictions++
      return null
    }
    
    item.lastAccessed = Date.now()
    this.cacheStats.value.hits++
    return item.data
  }
  
  /**
   * メモリキャッシュの設定
   * @param {string} key
   * @param {*} data
   * @param {number} ttl
   */
  setInMemory(key, data, ttl = 300000) { // デフォルト5分
    // メモリ使用量制限（100件まで）
    if (this.memoryCache.size >= 100) {
      const oldestKey = this.findOldestKey()
      this.memoryCache.delete(oldestKey)
      this.cacheStats.value.evictions++
    }
    
    this.memoryCache.set(key, {
      data,
      expiry: Date.now() + ttl,
      lastAccessed: Date.now()
    })
  }
  
  /**
   * IndexedDBからの取得
   * @param {string} key
   * @returns {Promise<*>}
   */
  async getFromIndexedDB(key) {
    if (!this.indexedDBCache) await this.initIndexedDB()
    
    return new Promise((resolve) => {
      const transaction = this.indexedDBCache.transaction(['cache'], 'readonly')
      const store = transaction.objectStore('cache')
      const request = store.get(key)
      
      request.onsuccess = () => {
        const item = request.result
        if (!item || Date.now() > item.expiry) {
          resolve(null)
          return
        }
        
        // メモリキャッシュにも設定
        this.setInMemory(key, item.data, item.expiry - Date.now())
        this.cacheStats.value.hits++
        resolve(item.data)
      }
      
      request.onerror = () => resolve(null)
    })
  }
  
  /**
   * IndexedDBへの保存
   * @param {string} key
   * @param {*} data
   * @param {number} ttl
   */
  async setInIndexedDB(key, data, ttl = 3600000) { // デフォルト1時間
    if (!this.indexedDBCache) await this.initIndexedDB()
    
    const item = {
      key,
      data,
      expiry: Date.now() + ttl,
      lastAccessed: Date.now()
    }
    
    const transaction = this.indexedDBCache.transaction(['cache'], 'readwrite')
    const store = transaction.objectStore('cache')
    store.put(item)
  }
  
  /**
   * 統合キャッシュ取得
   * @param {string} key
   * @param {Function} fetchFunction
   * @param {Object} options
   */
  async get(key, fetchFunction, options = {}) {
    const { 
      memoryTTL = 300000,
      persistentTTL = 3600000,
      useMemory = true,
      usePersistent = true 
    } = options
    
    // メモリキャッシュから取得
    if (useMemory) {
      const memoryResult = this.getFromMemory(key)
      if (memoryResult !== null) return memoryResult
    }
    
    // IndexedDBから取得
    if (usePersistent) {
      const persistentResult = await this.getFromIndexedDB(key)
      if (persistentResult !== null) return persistentResult
    }
    
    // キャッシュミス：データをフェッチ
    this.cacheStats.value.misses++
    try {
      const data = await fetchFunction()
      
      // キャッシュに保存
      if (useMemory) {
        this.setInMemory(key, data, memoryTTL)
      }
      if (usePersistent) {
        await this.setInIndexedDB(key, data, persistentTTL)
      }
      
      return data
    } catch (error) {
      console.error('データフェッチエラー:', error)
      throw error
    }
  }
  
  /**
   * キャッシュクリア
   * @param {string} pattern
   */
  async clear(pattern = null) {
    if (pattern) {
      // パターンマッチングでクリア
      const regex = new RegExp(pattern)
      for (const key of this.memoryCache.keys()) {
        if (regex.test(key)) {
          this.memoryCache.delete(key)
        }
      }
    } else {
      // 全クリア
      this.memoryCache.clear()
      
      if (this.indexedDBCache) {
        const transaction = this.indexedDBCache.transaction(['cache'], 'readwrite')
        const store = transaction.objectStore('cache')
        store.clear()
      }
    }
  }
  
  /**
   * 最も古いキーを検索
   * @returns {string}
   */
  findOldestKey() {
    let oldestKey = null
    let oldestTime = Date.now()
    
    for (const [key, item] of this.memoryCache.entries()) {
      if (item.lastAccessed < oldestTime) {
        oldestTime = item.lastAccessed
        oldestKey = key
      }
    }
    
    return oldestKey
  }
  
  /**
   * キャッシュ統計
   */
  get stats() {
    return computed(() => ({
      ...this.cacheStats.value,
      hitRate: this.cacheStats.value.hits / 
               (this.cacheStats.value.hits + this.cacheStats.value.misses) * 100,
      memorySize: this.memoryCache.size
    }))
  }
}

// グローバルキャッシュインスタンス
export const globalCache = new CacheManager()
```

## 5. ネットワーク最適化

### 5.1 リクエスト最適化
```javascript
// services/network/requestOptimizer.js
import { ref } from 'vue'

/**
 * ネットワークリクエスト最適化
 */
export class RequestOptimizer {
  constructor() {
    this.requestQueue = new Map()
    this.batchQueue = new Map()
    this.retryQueue = new Map()
    this.networkStatus = ref(navigator.onLine)
    
    this.initNetworkMonitoring()
    this.initRequestBatching()
  }
  
  /**
   * ネットワーク状態監視
   */
  initNetworkMonitoring() {
    window.addEventListener('online', () => {
      this.networkStatus.value = true
      this.processOfflineQueue()
    })
    
    window.addEventListener('offline', () => {
      this.networkStatus.value = false
    })
  }
  
  /**
   * リクエスト重複除去
   * @param {string} key
   * @param {Function} requestFunction
   * @returns {Promise}
   */
  async dedupeRequest(key, requestFunction) {
    if (this.requestQueue.has(key)) {
      return this.requestQueue.get(key)
    }
    
    const promise = requestFunction()
      .finally(() => {
        this.requestQueue.delete(key)
      })
    
    this.requestQueue.set(key, promise)
    return promise
  }
  
  /**
   * バッチリクエスト
   * @param {string} batchKey
   * @param {*} data
   * @param {Function} batchProcessor
   */
  async addToBatch(batchKey, data, batchProcessor) {
    if (!this.batchQueue.has(batchKey)) {
      this.batchQueue.set(batchKey, {
        items: [],
        processor: batchProcessor,
        timer: null
      })
    }
    
    const batch = this.batchQueue.get(batchKey)
    batch.items.push(data)
    
    // 100ms後または10件溜まったらバッチ処理実行
    if (batch.timer) clearTimeout(batch.timer)
    
    if (batch.items.length >= 10) {
      await this.processBatch(batchKey)
    } else {
      batch.timer = setTimeout(() => {
        this.processBatch(batchKey)
      }, 100)
    }
  }
  
  /**
   * バッチ処理実行
   * @param {string} batchKey
   */
  async processBatch(batchKey) {
    const batch = this.batchQueue.get(batchKey)
    if (!batch || batch.items.length === 0) return
    
    try {
      await batch.processor(batch.items)
      this.batchQueue.delete(batchKey)
    } catch (error) {
      console.error('バッチ処理エラー:', error)
      // リトライキューに追加
      this.addToRetryQueue(batchKey, batch.items, batch.processor)
    }
  }
  
  /**
   * 指数バックオフリトライ
   * @param {Function} requestFunction
   * @param {Object} options
   */
  async retryWithBackoff(requestFunction, options = {}) {
    const {
      maxRetries = 3,
      baseDelay = 1000,
      maxDelay = 10000,
      backoffFactor = 2
    } = options
    
    let attempt = 0
    
    while (attempt < maxRetries) {
      try {
        return await requestFunction()
      } catch (error) {
        attempt++
        
        if (attempt >= maxRetries) {
          throw error
        }
        
        const delay = Math.min(
          baseDelay * Math.pow(backoffFactor, attempt - 1),
          maxDelay
        )
        
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }
  
  /**
   * リトライキューへの追加
   * @param {string} key
   * @param {*} data
   * @param {Function} processor
   */
  addToRetryQueue(key, data, processor) {
    this.retryQueue.set(key, {
      data,
      processor,
      retryCount: 0,
      nextRetry: Date.now() + 5000 // 5秒後
    })
  }
  
  /**
   * オフラインキューの処理
   */
  async processOfflineQueue() {
    for (const [key, item] of this.retryQueue.entries()) {
      if (Date.now() >= item.nextRetry) {
        try {
          await item.processor(item.data)
          this.retryQueue.delete(key)
        } catch (error) {
          item.retryCount++
          if (item.retryCount < 3) {
            item.nextRetry = Date.now() + (5000 * item.retryCount)
          } else {
            this.retryQueue.delete(key)
            console.error('リトライ上限に達しました:', key, error)
          }
        }
      }
    }
  }
  
  /**
   * バッチリクエスト初期化
   */
  initRequestBatching() {
    // 定期的にバッチを処理
    setInterval(() => {
      for (const batchKey of this.batchQueue.keys()) {
        this.processBatch(batchKey)
      }
    }, 1000)
    
    // 定期的にリトライキューを処理
    setInterval(() => {
      if (this.networkStatus.value) {
        this.processOfflineQueue()
      }
    }, 5000)
  }
}

// グローバルリクエスト最適化インスタンス
export const requestOptimizer = new RequestOptimizer()
```

### 5.2 リアルタイム最適化
```javascript
// services/realtime/realtimeOptimizer.js
import { supabase } from '@/lib/supabase'
import { ref, computed } from 'vue'

/**
 * Supabaseリアルタイム最適化
 */
export class RealtimeOptimizer {
  constructor() {
    this.subscriptions = new Map()
    this.throttledUpdates = new Map()
    this.connectionStatus = ref('connecting')
    this.messageQueue = []
    
    this.initConnectionMonitoring()
  }
  
  /**
   * 接続状態監視
   */
  initConnectionMonitoring() {
    supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN') {
        this.connectionStatus.value = 'connected'
        this.processMessageQueue()
      } else if (event === 'SIGNED_OUT') {
        this.connectionStatus.value = 'disconnected'
        this.clearAllSubscriptions()
      }
    })
  }
  
  /**
   * 効率的なリアルタイム購読
   * @param {string} table
   * @param {Object} options
   * @returns {Function} unsubscribe function
   */
  subscribe(table, options = {}) {
    const {
      filter = null,
      onInsert = null,
      onUpdate = null,
      onDelete = null,
      throttleMs = 100
    } = options
    
    const subscriptionKey = `${table}_${JSON.stringify(filter)}`
    
    // 既存の購読があれば再利用
    if (this.subscriptions.has(subscriptionKey)) {
      return this.subscriptions.get(subscriptionKey).unsubscribe
    }
    
    let channel = supabase
      .channel(`table_${table}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table,
          ...(filter && { filter })
        },
        (payload) => this.handleRealtimeEvent(payload, {
          onInsert,
          onUpdate,
          onDelete,
          throttleMs,
          subscriptionKey
        })
      )
      .subscribe()
    
    const unsubscribe = () => {
      supabase.removeChannel(channel)
      this.subscriptions.delete(subscriptionKey)
      this.throttledUpdates.delete(subscriptionKey)
    }
    
    this.subscriptions.set(subscriptionKey, {
      channel,
      unsubscribe,
      lastUpdate: Date.now()
    })
    
    return unsubscribe
  }
  
  /**
   * リアルタイムイベント処理
   * @param {Object} payload
   * @param {Object} handlers
   */
  handleRealtimeEvent(payload, handlers) {
    const { 
      onInsert, 
      onUpdate, 
      onDelete, 
      throttleMs, 
      subscriptionKey 
    } = handlers
    
    // スロットリング
    if (this.throttledUpdates.has(subscriptionKey)) {
      clearTimeout(this.throttledUpdates.get(subscriptionKey))
    }
    
    this.throttledUpdates.set(subscriptionKey, setTimeout(() => {
      switch (payload.eventType) {
        case 'INSERT':
          onInsert?.(payload.new)
          break
        case 'UPDATE':
          onUpdate?.(payload.new, payload.old)
          break
        case 'DELETE':
          onDelete?.(payload.old)
          break
      }
      
      this.throttledUpdates.delete(subscriptionKey)
    }, throttleMs))
  }
  
  /**
   * プレゼンス機能（オンラインユーザー）
   * @param {string} roomId
   * @param {Object} userInfo
   */
  joinPresence(roomId, userInfo) {
    const channel = supabase.channel(`presence_${roomId}`)
    
    channel
      .on('presence', { event: 'sync' }, () => {
        const state = channel.presenceState()
        console.log('sync', state)
      })
      .on('presence', { event: 'join' }, ({ key, newPresences }) => {
        console.log('join', key, newPresences)
      })
      .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
        console.log('leave', key, leftPresences)
      })
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          const presenceTrackStatus = await channel.track(userInfo)
          console.log('Presence tracking:', presenceTrackStatus)
        }
      })
    
    return () => supabase.removeChannel(channel)
  }
  
  /**
   * ブロードキャスト最適化
   * @param {string} channel
   * @param {Object} message
   */
  broadcast(channel, message) {
    if (this.connectionStatus.value !== 'connected') {
      this.messageQueue.push({ channel, message })
      return
    }
    
    supabase.channel(channel).send({
      type: 'broadcast',
      event: 'message',
      payload: message
    })
  }
  
  /**
   * メッセージキューの処理
   */
  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const { channel, message } = this.messageQueue.shift()
      this.broadcast(channel, message)
    }
  }
  
  /**
   * 全ての購読をクリア
   */
  clearAllSubscriptions() {
    for (const subscription of this.subscriptions.values()) {
      subscription.unsubscribe()
    }
    this.subscriptions.clear()
    this.throttledUpdates.clear()
  }
  
  /**
   * 接続統計
   */
  get stats() {
    return computed(() => ({
      status: this.connectionStatus.value,
      subscriptionsCount: this.subscriptions.size,
      queuedMessages: this.messageQueue.length
    }))
  }
}

// グローバルリアルタイム最適化インスタンス
export const realtimeOptimizer = new RealtimeOptimizer()
```

## 6. 画像・アセット最適化

### 6.1 レスポンシブ画像最適化
```vue
<!-- components/ui/OptimizedImage.vue -->
<template>
  <div class="optimized-image" :class="containerClass">
    <picture v-if="sources.length > 0">
      <source
        v-for="source in sources"
        :key="source.media"
        :srcset="source.srcset"
        :media="source.media"
        :type="source.type"
      />
      <img
        ref="imageRef"
        :src="fallbackSrc"
        :alt="alt"
        :loading="loading"
        :decoding="decoding"
        :class="imageClass"
        @load="handleLoad"
        @error="handleError"
        @intersect="handleIntersection"
      />
    </picture>
    
    <!-- フォールバック -->
    <img
      v-else
      ref="imageRef"
      :src="currentSrc"
      :alt="alt"
      :loading="loading"
      :decoding="decoding"
      :class="imageClass"
      @load="handleLoad"
      @error="handleError"
    />
    
    <!-- プレースホルダー -->
    <div
      v-if="isLoading"
      class="placeholder"
      :style="placeholderStyle"
    >
      <div class="skeleton-loader"></div>
    </div>
    
    <!-- エラー表示 -->
    <div
      v-if="hasError"
      class="error-placeholder"
    >
      <svg class="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
      </svg>
      <span class="text-sm text-gray-500">画像を読み込めませんでした</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    required: true
  },
  // レスポンシブ画像の設定
  srcset: {
    type: [String, Array],
    default: ''
  },
  sizes: {
    type: String,
    default: '100vw'
  },
  // 最適化オプション
  loading: {
    type: String,
    default: 'lazy',
    validator: value => ['lazy', 'eager'].includes(value)
  },
  decoding: {
    type: String,
    default: 'async',
    validator: value => ['sync', 'async', 'auto'].includes(value)
  },
  // アスペクト比維持
  aspectRatio: {
    type: String,
    default: null // "16:9", "4:3", "1:1" など
  },
  // プレースホルダー
  placeholder: {
    type: String,
    default: null
  },
  // WebP対応
  webpSrc: {
    type: String,
    default: null
  },
  // クラス
  containerClass: {
    type: String,
    default: ''
  },
  imageClass: {
    type: String,
    default: 'w-full h-auto'
  }
})

const emit = defineEmits(['load', 'error'])

// 状態
const imageRef = ref(null)
const isLoading = ref(true)
const hasError = ref(false)
const isIntersecting = ref(false)

// 現在のsrc
const currentSrc = computed(() => {
  if (!isIntersecting.value && props.loading === 'lazy') {
    return props.placeholder || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB2aWV3Qm94PSIwIDAgMSAxIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNGM0Y0RjYiLz48L3N2Zz4='
  }
  return props.src
})

// レスポンシブソース生成
const sources = computed(() => {
  const sources = []
  
  // WebP対応
  if (props.webpSrc) {
    sources.push({
      srcset: props.webpSrc,
      type: 'image/webp',
      media: '(min-width: 1px)' // すべてのブラウザ
    })
  }
  
  // レスポンシブ画像
  if (props.srcset) {
    const srcsetArray = Array.isArray(props.srcset) ? props.srcset : [props.srcset]
    
    srcsetArray.forEach(srcset => {
      sources.push({
        srcset,
        media: '(min-width: 1px)'
      })
    })
  }
  
  return sources
})

// フォールバック画像
const fallbackSrc = computed(() => props.src)

// プレースホルダースタイル
const placeholderStyle = computed(() => {
  const styles = {}
  
  if (props.aspectRatio) {
    const [width, height] = props.aspectRatio.split(':').map(Number)
    styles.aspectRatio = `${width} / ${height}`
  }
  
  if (props.placeholder) {
    styles.backgroundImage = `url(${props.placeholder})`
    styles.backgroundSize = 'cover'
    styles.backgroundPosition = 'center'
  }
  
  return styles
})

// 交差監視
useIntersectionObserver(
  imageRef,
  ([{ isIntersecting: intersecting }]) => {
    isIntersecting.value = intersecting
  },
  {
    rootMargin: '50px'
  }
)

// イベントハンドラー
const handleLoad = () => {
  isLoading.value = false
  hasError.value = false
  emit('load')
}

const handleError = () => {
  isLoading.value = false
  hasError.value = true
  emit('error')
}

// 初期化
onMounted(() => {
  if (props.loading === 'eager') {
    isIntersecting.value = true
  }
})
</script>

<style scoped>
.optimized-image {
  position: relative;
  overflow: hidden;
}

.placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
}

.skeleton-loader {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.error-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background-color: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
```

### 6.2 アセット最適化ビルド設定
```javascript
// utils/build/assetOptimization.js

/**
 * アセット最適化設定
 */
export const assetOptimizationConfig = {
  images: {
    // 画像最適化設定
    optimization: {
      jpeg: {
        quality: 85,
        progressive: true
      },
      png: {
        quality: 90,
        compressionLevel: 6
      },
      webp: {
        quality: 85,
        method: 6
      },
      avif: {
        quality: 80,
        speed: 4
      }
    },
    
    // レスポンシブ画像の生成
    responsive: {
      breakpoints: [320, 640, 768, 1024, 1280, 1536],
      formats: ['webp', 'avif', 'jpeg'],
      densities: [1, 2] // 1x, 2x (Retina)
    }
  },
  
  fonts: {
    // フォント最適化
    subsetting: {
      unicodeRange: [
        'U+0020-007F', // Basic Latin
        'U+3040-309F', // Hiragana
        'U+30A0-30FF', // Katakana
        'U+4E00-9FAF'  // CJK Unified Ideographs
      ]
    },
    
    preload: [
      {
        href: '/fonts/Inter-Variable.woff2',
        as: 'font',
        type: 'font/woff2',
        crossorigin: 'anonymous'
      }
    ]
  },
  
  compression: {
    brotli: {
      enabled: true,
      threshold: 1024,
      compressionLevel: 11
    },
    gzip: {
      enabled: true,
      threshold: 1024,
      compressionLevel: 9
    }
  }
}

/**
 * 画像最適化ユーティリティ
 */
export class ImageOptimizer {
  /**
   * レスポンシブ画像URLの生成
   * @param {string} src
   * @param {Object} options
   * @returns {Object}
   */
  static generateResponsiveSources(src, options = {}) {
    const {
      breakpoints = [320, 640, 768, 1024, 1280],
      formats = ['webp', 'jpeg'],
      densities = [1, 2]
    } = options
    
    const sources = []
    
    formats.forEach(format => {
      breakpoints.forEach(breakpoint => {
        densities.forEach(density => {
          const width = breakpoint * density
          const url = this.generateOptimizedUrl(src, {
            width,
            format,
            quality: format === 'webp' ? 85 : 80
          })
          
          sources.push({
            srcset: `${url} ${density}x`,
            media: `(min-width: ${breakpoint}px)`,
            type: `image/${format}`
          })
        })
      })
    })
    
    return sources
  }
  
  /**
   * 最適化されたURL生成
   * @param {string} src
   * @param {Object} options
   * @returns {string}
   */
  static generateOptimizedUrl(src, options = {}) {
    const {
      width,
      height,
      format = 'webp',
      quality = 85,
      fit = 'cover'
    } = options
    
    // Supabase Transform APIの場合
    if (src.includes('supabase')) {
      const url = new URL(src)
      url.searchParams.set('width', width)
      if (height) url.searchParams.set('height', height)
      url.searchParams.set('format', format)
      url.searchParams.set('quality', quality)
      url.searchParams.set('resize', fit)
      return url.toString()
    }
    
    // 他の画像最適化サービス（Cloudinary、ImageKit等）
    // の場合の実装をここに追加
    
    return src
  }
  
  /**
   * 画像のプリロード
   * @param {string} src
   * @param {Object} options
   */
  static preloadImage(src, options = {}) {
    const { priority = 'low' } = options
    
    const link = document.createElement('link')
    link.rel = 'preload'
    link.as = 'image'
    link.href = src
    link.fetchPriority = priority
    
    document.head.appendChild(link)
  }
  
  /**
   * 重要画像のプリロード
   * @param {Array} images
   */
  static preloadCriticalImages(images) {
    images.forEach(src => {
      this.preloadImage(src, { priority: 'high' })
    })
  }
}
```

## まとめ

このパフォーマンス最適化設計書により、Vue.js + Supabaseアプリケーションの全体的なパフォーマンスを大幅に向上させることができます。主要な最適化ポイント：

1. **フロントエンド最適化**: Vue.jsのリアクティビティとレンダリングの効率化
2. **バンドル最適化**: Tree Shaking、コード分割、圧縮の適用
3. **データベース最適化**: クエリの効率化とキャッシュ戦略
4. **ネットワーク最適化**: リクエストの最適化とリアルタイム機能の効率化
5. **アセット最適化**: 画像とフォントの最適化

これらの最適化を段階的に適用し、定期的にパフォーマンス測定を行うことで、優れたユーザー体験を提供できます。