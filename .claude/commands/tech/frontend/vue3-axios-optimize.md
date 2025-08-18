# /vue3-axios-optimize - Vue3+Axios エンタープライズ最適化専用コマンド

## 概要
Vue3 + Axios を使用した大規模SPAアプリケーションの包括的な最適化コマンドです。エンタープライズ要件（パフォーマンス、セキュリティ、国際化）に完全対応します。

## 使用方法
```bash
/vue3-axios-optimize [feature] [action] [options]

# 使用例
/vue3-axios-optimize bundle analyze --tree-shake
/vue3-axios-optimize api optimize --cache-strategy=aggressive
/vue3-axios-optimize state pinia --devtools
/vue3-axios-optimize performance audit --lighthouse
/vue3-axios-optimize i18n setup --lazy-load
```

## Vue3+Axios 専用最適化機能

### 1. バンドルサイズ最適化
```javascript
// vite.config.js 最適化設定
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'
import { VitePWA } from 'vite-plugin-pwa'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'

export default defineConfig({
  plugins: [
    vue({
      // Reactivity Transform有効化
      reactivityTransform: true,
      // テンプレート最適化
      template: {
        compilerOptions: {
          isCustomElement: tag => tag.startsWith('ion-')
        }
      }
    }),
    
    // 自動インポート
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia', '@vueuse/core'],
      dts: 'src/auto-imports.d.ts',
      eslintrc: {
        enabled: true
      }
    }),
    
    // コンポーネント自動インポート
    Components({
      dts: 'src/components.d.ts',
      deep: true,
      dirs: ['src/components'],
      extensions: ['vue'],
      include: [/\.vue$/, /\.vue\?vue/]
    }),
    
    // Bundle分析
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true
    }),
    
    // 圧縮
    viteCompression({
      algorithm: 'brotliCompress',
      threshold: 10240
    })
  ],
  
  build: {
    // チャンクサイズ警告閾値
    chunkSizeWarningLimit: 500,
    
    // ロールアップ最適化
    rollupOptions: {
      output: {
        // マニュアルチャンク分割
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-library': ['element-plus'],
          'utils': ['lodash-es', 'dayjs'],
          'charts': ['echarts']
        },
        // チャンク名最適化
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? 
            chunkInfo.facadeModuleId.split('/').pop().split('.')[0] : 
            'vendor'
          return `js/${facadeModuleId}-[hash].js`
        }
      }
    },
    
    // ツリーシェイキング強化
    treeshake: {
      preset: 'recommended',
      manualPureFunctions: ['console.log']
    }
  }
})
```

### 2. Axios インターセプター最適化
```typescript
// api/axios-optimizer.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { setupCache } from 'axios-cache-adapter'
import axiosRetry from 'axios-retry'
import { useAuthStore } from '@/stores/auth'

class AxiosOptimizer {
  private instance: AxiosInstance
  private cache: any
  private requestQueue: Map<string, Promise<any>> = new Map()
  
  constructor() {
    // キャッシュ設定
    this.cache = setupCache({
      maxAge: 15 * 60 * 1000, // 15分
      exclude: {
        query: false,
        filter: (config: AxiosRequestConfig) => {
          // POSTリクエストはキャッシュしない
          return config.method !== 'get'
        }
      },
      // Redis連携（エンタープライズ）
      store: {
        getItem: async (key: string) => {
          return await redis.get(key)
        },
        setItem: async (key: string, value: any) => {
          await redis.setex(key, 900, JSON.stringify(value))
        },
        removeItem: async (key: string) => {
          await redis.del(key)
        }
      }
    })
    
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 30000,
      adapter: this.cache.adapter
    })
    
    this.setupInterceptors()
    this.setupRetry()
  }
  
  private setupInterceptors() {
    // リクエストインターセプター
    this.instance.interceptors.request.use(
      async (config) => {
        // トークン自動付与
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        
        // リクエスト重複防止
        const requestKey = this.getRequestKey(config)
        if (this.requestQueue.has(requestKey)) {
          return Promise.reject({
            __CANCEL__: true,
            promise: this.requestQueue.get(requestKey)
          })
        }
        
        // リクエスト圧縮
        if (config.data && JSON.stringify(config.data).length > 1024) {
          config.headers['Content-Encoding'] = 'gzip'
          config.data = await this.compress(config.data)
        }
        
        // パフォーマンストラッキング
        config.metadata = { startTime: Date.now() }
        
        return config
      },
      (error) => Promise.reject(error)
    )
    
    // レスポンスインターセプター
    this.instance.interceptors.response.use(
      (response) => {
        // パフォーマンス計測
        const duration = Date.now() - response.config.metadata.startTime
        this.trackPerformance(response.config.url, duration)
        
        // リクエストキューから削除
        const requestKey = this.getRequestKey(response.config)
        this.requestQueue.delete(requestKey)
        
        // レスポンス変換
        return this.transformResponse(response)
      },
      async (error) => {
        // キャンセルされたリクエストの処理
        if (error.__CANCEL__) {
          return error.promise
        }
        
        // エラー処理
        return this.handleError(error)
      }
    )
  }
  
  private setupRetry() {
    // 自動リトライ設定
    axiosRetry(this.instance, {
      retries: 3,
      retryDelay: (retryCount) => {
        return retryCount * 1000 // エクスポネンシャルバックオフ
      },
      retryCondition: (error) => {
        // ネットワークエラーまたは5xx系エラーの場合リトライ
        return axiosRetry.isNetworkOrIdempotentRequestError(error) ||
               (error.response?.status >= 500 && error.response?.status < 600)
      },
      onRetry: (retryCount, error, requestConfig) => {
        console.log(`Retry attempt ${retryCount} for ${requestConfig.url}`)
      }
    })
  }
  
  // バッチリクエスト最適化
  async batchRequest(requests: AxiosRequestConfig[]): Promise<any[]> {
    const batchPayload = {
      requests: requests.map(req => ({
        method: req.method,
        url: req.url,
        data: req.data,
        params: req.params
      }))
    }
    
    const response = await this.instance.post('/batch', batchPayload)
    return response.data.responses
  }
}
```

### 3. Pinia状態管理最適化
```typescript
// stores/optimized-store.ts
import { defineStore, acceptHMRUpdate } from 'pinia'
import { debounce, throttle } from 'lodash-es'

export const useOptimizedStore = defineStore('optimized', {
  state: () => ({
    data: new Map(),
    cache: new Map(),
    subscribers: new Set(),
    pendingMutations: []
  }),
  
  getters: {
    // メモ化されたゲッター
    memoizedData: (state) => {
      return (key: string) => {
        if (!state.cache.has(key)) {
          const result = expensiveComputation(state.data.get(key))
          state.cache.set(key, result)
        }
        return state.cache.get(key)
      }
    },
    
    // 仮想スクロール用ゲッター
    virtualizedList: (state) => {
      return (start: number, end: number) => {
        return Array.from(state.data.values()).slice(start, end)
      }
    }
  },
  
  actions: {
    // バッチ更新
    batchUpdate: debounce(function(mutations: any[]) {
      this.$patch((state) => {
        mutations.forEach(mutation => {
          mutation.apply(state)
        })
      })
    }, 100),
    
    // スロットル更新
    throttledUpdate: throttle(function(key: string, value: any) {
      this.data.set(key, value)
      this.invalidateCache(key)
    }, 300),
    
    // 楽観的更新
    async optimisticUpdate(key: string, value: any) {
      const previousValue = this.data.get(key)
      
      // 即座に更新
      this.data.set(key, value)
      
      try {
        // APIコール
        await api.update(key, value)
      } catch (error) {
        // ロールバック
        this.data.set(key, previousValue)
        throw error
      }
    },
    
    // 購読管理
    subscribe(callback: Function) {
      this.subscribers.add(callback)
      return () => this.subscribers.delete(callback)
    },
    
    // キャッシュ無効化
    invalidateCache(key?: string) {
      if (key) {
        this.cache.delete(key)
      } else {
        this.cache.clear()
      }
    }
  },
  
  // 永続化設定
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'optimized-store',
        storage: sessionStorage,
        paths: ['data'],
        // カスタムシリアライザー
        serializer: {
          serialize: (state) => {
            return JSON.stringify(Array.from(state.entries()))
          },
          deserialize: (value) => {
            return new Map(JSON.parse(value))
          }
        }
      }
    ]
  }
})

// HMR対応
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useOptimizedStore, import.meta.hot))
}
```

### 4. コンポーネント最適化
```vue
<template>
  <div class="optimized-component">
    <!-- 遅延レンダリング -->
    <LazyHydrate when-visible>
      <HeavyComponent v-if="isVisible" />
    </LazyHydrate>
    
    <!-- 仮想スクロール -->
    <VirtualList
      :items="items"
      :item-height="50"
      :overscan="5"
      v-slot="{ item, index }"
    >
      <ListItem :item="item" :key="item.id" />
    </VirtualList>
    
    <!-- 条件付きレンダリング最適化 -->
    <component
      :is="currentComponent"
      v-bind="currentProps"
      v-memo="[currentProps.id, currentProps.version]"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, shallowRef, triggerRef, watchEffect } from 'vue'
import { useIntersectionObserver, useThrottleFn } from '@vueuse/core'
import { storeToRefs } from 'pinia'

// Props定義
const props = defineProps<{
  items: Array<any>
  heavyData: any
}>()

// Shallow Refで不要な深い監視を防ぐ
const largeDataSet = shallowRef(props.heavyData)

// 遅延ローディング
const target = ref<HTMLElement>()
const { stop } = useIntersectionObserver(
  target,
  ([{ isIntersecting }]) => {
    if (isIntersecting) {
      loadMoreData()
      stop() // 一度だけ実行
    }
  },
  { threshold: 0.1 }
)

// スロットル処理
const handleScroll = useThrottleFn(() => {
  // スクロール処理
}, 100)

// 計算プロパティの最適化
const optimizedComputed = computed(() => {
  // キャッシュされる計算
  return expensiveCalculation(props.items)
}, {
  // 遅延評価
  lazy: true
})

// メモリリーク防止
onUnmounted(() => {
  // クリーンアップ
  clearAllTimers()
  removeAllListeners()
})
</script>

<style scoped>
/* クリティカルCSS */
.optimized-component {
  contain: layout style paint;
  will-change: transform;
}

/* 非クリティカルCSSの遅延ロード */
@import url('./heavy-styles.css') (min-width: 768px);
</style>
```

### 5. パフォーマンス監視
```typescript
// performance/monitor.ts
class PerformanceMonitor {
  private metrics: Map<string, any> = new Map()
  
  // Core Web Vitals監視
  initWebVitals() {
    import('web-vitals').then(({ getCLS, getFID, getLCP, getFCP, getTTFB }) => {
      getCLS(this.sendMetric)
      getFID(this.sendMetric)
      getLCP(this.sendMetric)
      getFCP(this.sendMetric)
      getTTFB(this.sendMetric)
    })
  }
  
  // Vue3パフォーマンス監視
  setupVueMonitoring(app: App) {
    app.config.performance = true
    
    // コンポーネントレンダリング時間
    app.mixin({
      beforeCreate() {
        this.$renderStart = performance.now()
      },
      mounted() {
        const duration = performance.now() - this.$renderStart
        this.trackComponentPerformance(this.$options.name, duration)
      }
    })
  }
  
  // API呼び出し監視
  trackAPICall(endpoint: string, duration: number, status: number) {
    this.metrics.set(`api:${endpoint}`, {
      duration,
      status,
      timestamp: Date.now()
    })
    
    // 閾値超過アラート
    if (duration > 3000) {
      this.sendAlert('Slow API', { endpoint, duration })
    }
  }
  
  // メモリ使用量監視
  monitorMemory() {
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory
        this.metrics.set('memory', {
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit
        })
        
        // メモリリーク検出
        if (memory.usedJSHeapSize / memory.jsHeapSizeLimit > 0.9) {
          this.sendAlert('Memory leak detected')
        }
      }, 10000)
    }
  }
  
  // レポート生成
  generateReport() {
    return {
      webVitals: this.getWebVitalsScore(),
      apiPerformance: this.getAPIStats(),
      componentPerformance: this.getComponentStats(),
      memoryUsage: this.getMemoryStats(),
      recommendations: this.generateRecommendations()
    }
  }
}
```

## 国際化・ローカライゼーション最適化
```typescript
// i18n/optimizer.ts
import { createI18n } from 'vue-i18n'

// 遅延ローディング対応
const loadLocaleMessages = async (locale: string) => {
  const messages = await import(`./locales/${locale}.json`)
  return messages.default
}

// 最適化されたi18n設定
export const i18n = createI18n({
  legacy: false,
  locale: 'ja',
  fallbackLocale: 'en',
  // メッセージコンパイラー最適化
  messageCompiler: (msg: string) => {
    // カスタムコンパイラーでパフォーマンス向上
    return compileMessage(msg)
  },
  // 数値フォーマット最適化
  numberFormats: {
    ja: {
      currency: {
        style: 'currency',
        currency: 'JPY',
        minimumFractionDigits: 0
      }
    }
  },
  // 日付フォーマット最適化
  datetimeFormats: {
    ja: {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }
    }
  }
})

// 動的ロケール切り替え
export async function switchLocale(locale: string) {
  if (!i18n.global.availableLocales.includes(locale)) {
    const messages = await loadLocaleMessages(locale)
    i18n.global.setLocaleMessage(locale, messages)
  }
  i18n.global.locale.value = locale
}
```

## 出力レポート
```markdown
# Vue3+Axios 最適化レポート

## 実施項目
✅ バンドルサイズ: 2.3MB → 680KB (70%削減)
✅ 初期ロード時間: 4.2秒 → 1.1秒 (74%改善)
✅ API応答時間: 平均350ms → 85ms (76%改善)
✅ メモリ使用量: 125MB → 45MB (64%削減)
✅ Core Web Vitals: すべて「良好」達成

## パフォーマンススコア
- Lighthouse: 98/100
- LCP: 1.2秒
- FID: 45ms
- CLS: 0.02

## 最適化手法
- Tree Shaking: 未使用コード60%削除
- Code Splitting: 15個のチャンク分割
- Lazy Loading: 80%のコンポーネント遅延
- API Cache: ヒット率85%達成

## 推奨事項
1. Service Worker導入でオフライン対応
2. WebSocketでリアルタイム更新
3. Edge Functionで地理的最適化
```

## 管理責任
- **管理部門**: システム開発部
- **専門性**: Vue3 + Axios エンタープライズ開発

---
*このコマンドはVue3+Axiosの大規模SPA開発に特化しています。*