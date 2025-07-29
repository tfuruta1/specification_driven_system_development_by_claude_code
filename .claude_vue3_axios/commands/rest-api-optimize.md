# /rest-api-optimize - REST API パフォーマンス最適化コマンド

## 概要
REST APIベースのVue.jsアプリケーションのパフォーマンス最適化を多角的に実行する統合コマンドです。**Claude Code + Gemini CLI + o3 MCP**の協調により、API連携・フロントエンド・インフラの包括的最適化を実現します。

## 🎯 使用場面・対象
- **API連携パフォーマンス**: レスポンス時間・スループット改善
- **フロントエンド最適化**: レンダリング・バンドルサイズ・キャッシュ戦略
- **ユーザビリティ**: API遅延対応・オフライン対応・エラーハンドリング
- **運用効率**: 監視・デバッグ・メンテナンス性向上

## 🤖 マルチAI協調体制

### Claude Code（技術実装リーダー・統合責任者）
- **統合オーケストレーション**: 3つのAI成果物の統合・品質保証
- **フロントエンド最適化**: Vue.js コンポーネント・状態管理・レンダリング最適化
- **API統合最適化**: Axios設定・リクエスト最適化・エラーハンドリング改善
- **コード品質保証**: 実装品質・パフォーマンス計測・テスト戦略

### Gemini CLI（データ分析・ユーザー体験スペシャリスト）
- **ユーザー行動分析**: API利用パターン・パフォーマンスボトルネック分析
- **データ可視化**: パフォーマンス指標ダッシュボード・監視システム設計
- **UX最適化戦略**: ローディング戦略・プログレッシブローディング・ユーザビリティ改善
- **ビジネス価値分析**: 最適化ROI・ユーザー満足度・コンバージョン改善

### o3 MCP（インフラ・アーキテクチャスペシャリスト）
- **API Gateway最適化**: キャッシュ戦略・レート制限・負荷分散
- **CDN・エッジ戦略**: 静的リソース配信・地理的最適化
- **監視・可観測性**: APM・ログ分析・パフォーマンスメトリクス
- **スケーラビリティ**: 自動スケーリング・容量計画・障害対応

## 🚀 基本使用法

```bash
# 包括的パフォーマンス最適化（推奨）
/rest-api-optimize comprehensive

# 特定領域の最適化
/rest-api-optimize api --focus="response_time,caching"
/rest-api-optimize frontend --focus="bundle_size,rendering"
/rest-api-optimize infrastructure --focus="cdn,monitoring"

# AI協調最適化（高精度・推奨）
/rest-api-optimize multiAI --ai_priority="balanced" --scope="all"
```

## 📋 最適化カテゴリー

### 1. API連携最適化（Claude Code主担当）

#### Axios設定最適化
```javascript
// 最適化されたAxios設定
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL,
  timeout: 15000, // 適切なタイムアウト設定
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // 接続プール最適化
  maxRedirects: 5,
  maxContentLength: 50 * 1024 * 1024, // 50MB
  // Keep-Alive設定
  keepAlive: true,
  keepAliveMsecs: 1000
})

// リクエスト・レスポンス圧縮
apiClient.defaults.headers.common['Accept-Encoding'] = 'gzip, deflate, br'
```

#### 効率的キャッシュ戦略
```javascript
// HTTP キャッシュ戦略
const cacheInterceptor = {
  request: (config) => {
    // GET リクエストのキャッシュ制御
    if (config.method === 'get') {
      config.headers['Cache-Control'] = 'max-age=300' // 5分キャッシュ
    }
    return config
  },
  
  response: (response) => {
    // レスポンスキャッシュ
    if (response.config.method === 'get') {
      cacheStore.set(response.config.url, response.data, 300000) // 5分
    }
    return response
  }
}
```

#### 並列リクエスト最適化
```javascript
// バッチリクエスト戦略
export const batchApiService = {
  async getBatchData(requests) {
    // 並列実行で全体レスポンス時間短縮
    const results = await Promise.allSettled(
      requests.map(req => apiClient(req))
    )
    
    return results.map((result, index) => ({
      request: requests[index],
      success: result.status === 'fulfilled',
      data: result.status === 'fulfilled' ? result.value.data : null,
      error: result.status === 'rejected' ? result.reason : null
    }))
  },
  
  // 優先度付きリクエスト
  async getPriorityData(highPriority, lowPriority) {
    // 高優先度を先に実行
    const critical = await Promise.all(highPriority.map(req => apiClient(req)))
    
    // 低優先度は後続で実行
    setTimeout(() => {
      Promise.all(lowPriority.map(req => apiClient(req)))
    }, 100)
    
    return critical
  }
}
```

### 2. フロントエンド最適化（Claude Code主担当）

#### Vue.js パフォーマンス最適化
```javascript
// 効率的コンポーネント設計
export default {
  name: 'OptimizedComponent',
  
  // 計算プロパティのメモ化
  computed: {
    expensiveValue() {
      return this.largeDataSet.reduce((acc, item) => {
        return acc + this.complexCalculation(item)
      }, 0)
    }
  },
  
  // 監視の最適化
  watch: {
    // 深い監視を避けて、必要な部分のみ監視
    'user.preferences': {
      handler(newVal, oldVal) {
        this.updateUserSettings(newVal)
      },
      deep: false // 浅い監視で性能向上
    }
  },
  
  // 仮想スクロール対応
  components: {
    VirtualScroller: () => import('@/components/VirtualScroller.vue')
  }
}
```

#### バンドル最適化
```javascript
// Vite設定最適化（vite.config.js）
export default defineConfig({
  build: {
    // コード分割戦略
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['@headlessui/vue', 'daisyui'],
          utils: ['axios', 'date-fns', 'lodash-es']
        }
      }
    },
    
    // 圧縮最適化
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // プロダクションでconsole削除
        drop_debugger: true
      }
    }
  },
  
  // 開発サーバー最適化
  server: {
    hmr: {
      overlay: false // エラーオーバーレイ無効化で高速化
    }
  }
})
```

### 3. ユーザー体験最適化（Gemini CLI主担当）

#### 体感速度向上戦略
```javascript
// プログレッシブローディング
export const progressiveLoader = {
  // 重要コンテンツ優先読み込み
  async loadCriticalContent() {
    const criticalData = await apiClient.get('/api/critical')
    this.renderCriticalUI(criticalData)
    
    // 非重要コンテンツは後から読み込み
    setTimeout(() => {
      this.loadSecondaryContent()
    }, 100)
  },
  
  // スケルトンローディング
  showSkeleton() {
    return {
      template: `
        <div class="animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      `
    }
  },
  
  // 予測的プリローディング
  async predictivePreload(userBehavior) {
    const predictions = this.analyzeBehavior(userBehavior)
    predictions.forEach(prediction => {
      if (prediction.confidence > 0.7) {
        this.preloadContent(prediction.resource)
      }
    })
  }
}
```

#### エラー処理・オフライン対応
```javascript
// Robust Error Handling
export const errorRecoveryService = {
  // 自動リトライ戦略
  async apiWithRetry(request, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await apiClient(request)
      } catch (error) {
        if (attempt === maxRetries) throw error
        
        // 指数バックオフ
        const delay = Math.pow(2, attempt) * 1000
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  },
  
  // オフライン検知・対応
  setupOfflineHandling() {
    window.addEventListener('online', () => {
      this.syncOfflineData()
      this.showConnectionRestored()
    })
    
    window.addEventListener('offline', () => {
      this.enableOfflineMode()
      this.showOfflineNotice()
    })
  },
  
  // サービスワーカーキャッシュ
  async enableServiceWorker() {
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.register('/sw.js')
      console.log('Service Worker registered:', registration)
    }
  }
}
```

### 4. インフラ・監視最適化（o3 MCP主担当）

#### API Gateway・CDN戦略
```yaml
# API Gateway設定例（AWS API Gateway）
api_gateway_config:
  caching:
    enabled: true
    ttl: 300 # 5分キャッシュ
    key_parameters:
      - method.request.querystring.userId
      - method.request.header.Authorization
  
  throttling:
    rate_limit: 10000 # requests per second
    burst_limit: 5000
  
  compression:
    enabled: true
    minimum_size: 1024 # 1KB以上で圧縮

# CDN設定（CloudFront）
cdn_config:
  cache_behaviors:
    - path_pattern: "/api/*"
      cache_policy: "APIOptimized"
      ttl: 0 # API は毎回オリジンから
    - path_pattern: "/assets/*"
      cache_policy: "Optimized"
      ttl: 86400 # 静的アセットは1日キャッシュ
  
  compression: gzip, brotli
  http2: enabled
```

#### 監視・可観測性
```javascript
// パフォーマンス監視設定
export const performanceMonitoring = {
  // Core Web Vitals監視
  trackCoreVitals() {
    // Largest Contentful Paint
    new PerformanceObserver((list) => {
      const entries = list.getEntries()
      entries.forEach(entry => {
        console.log('LCP:', entry.startTime)
        this.sendMetric('lcp', entry.startTime)
      })
    }).observe({ entryTypes: ['largest-contentful-paint'] })
    
    // First Input Delay
    new PerformanceObserver((list) => {
      const entries = list.getEntries()
      entries.forEach(entry => {
        console.log('FID:', entry.processingStart - entry.startTime)
        this.sendMetric('fid', entry.processingStart - entry.startTime)
      })
    }).observe({ entryTypes: ['first-input'] })
  },
  
  // API パフォーマンス監視
  monitorAPIPerformance() {
    const originalRequest = apiClient.request
    apiClient.request = async (config) => {
      const startTime = performance.now()
      
      try {
        const response = await originalRequest.call(apiClient, config)
        const endTime = performance.now()
        
        this.sendMetric('api_response_time', {
          url: config.url,
          method: config.method,
          duration: endTime - startTime,
          status: response.status
        })
        
        return response
      } catch (error) {
        const endTime = performance.now()
        
        this.sendMetric('api_error', {
          url: config.url,
          method: config.method,
          duration: endTime - startTime,
          error: error.message
        })
        
        throw error
      }
    }
  }
}
```

## 📊 最適化成果指標・KPI

### パフォーマンス指標
- **API レスポンス時間**: 50%以上短縮目標
- **初期ページロード**: 3秒以内達成
- **バンドルサイズ**: 30%以上削減
- **Core Web Vitals**: Good範囲達成（LCP <2.5s, FID <100ms, CLS <0.1）

### ユーザー体験指標  
- **体感速度**: ローディング時間短縮・スケルトンUI
- **エラー率**: API エラー50%以上削減
- **オフライン対応**: 基本機能の利用継続
- **レスポンシブ性**: 全デバイスでの快適な操作

### 運用効率指標
- **デバッグ時間**: 包括的ログ・監視による短縮
- **障害検知時間**: リアルタイム監視による迅速対応
- **メンテナンス効率**: 自動化・可視化による向上

## 🎯 実行フロー・手順

### Phase 1: 現状分析（Gemini CLI）
```bash
# ユーザー行動・パフォーマンス分析
/research user_behavior --focus="api_usage,performance_bottlenecks"

# データ可視化・課題抽出
/research performance_analysis --metrics="response_time,error_rate,user_satisfaction"
```

### Phase 2: アーキテクチャ設計（o3 MCP）
```bash
# インフラ最適化戦略
/architecture performance_optimization --scope="api_gateway,cdn,monitoring"

# 監視・可観測性設計
/devops monitoring --environment="production" --focus="performance_metrics"
```

### Phase 3: 実装・統合（Claude Code）
```bash
# フロントエンド最適化実装
/enhance performance --focus="vue_optimization,bundle_optimization"

# API統合最適化
/refactor api_integration --focus="axios_optimization,caching_strategy"

# 品質保証・テスト
/analyze performance --scope="frontend,api,infrastructure"
```

### Phase 4: 統合品質保証（All AI協調）
```bash
# 統合検証・最終調整
/rest-api-optimize validation --ai_collaboration="intensive"

# パフォーマンステスト・監視設定
/devops performance_testing --load_test="enabled" --monitoring="production"
```

## 📚 技術参考・ベストプラクティス

### API最適化リファレンス
- [Axios Performance Guide](https://axios-http.com/docs/optimizing)
- [HTTP/2 & HTTP/3 Best Practices](https://web.dev/http2/)
- [REST API Caching Strategies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)

### Vue.js パフォーマンス
- [Vue.js Performance Guide](https://vuejs.org/guide/best-practices/performance.html)
- [Bundle Optimization with Vite](https://vitejs.dev/guide/build.html#chunking-strategy)
- [Web Performance Metrics](https://web.dev/vitals/)

### インフラ・監視
- [AWS API Gateway Performance](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html)
- [CloudFlare Performance Features](https://developers.cloudflare.com/fundamentals/get-started/concepts/performance/)
- [Application Performance Monitoring](https://www.datadoghq.com/knowledge-center/application-performance-monitoring/)

## 🔄 継続改善・メンテナンス

### 定期最適化サイクル
```bash
# 月次パフォーマンスレビュー
/rest-api-optimize monthly_review --period="last_30_days"

# 四半期インフラ見直し
/devops infrastructure_review --scope="capacity,cost,performance"

# 年次技術スタック評価
/architecture technology_assessment --focus="performance,scalability,maintainability"
```

### 自動化・監視
- **自動パフォーマンステスト**: CI/CD統合
- **アラート設定**: 閾値ベースの自動通知  
- **レポート生成**: 定期的な最適化効果測定

---

**🎯 コマンド目標**: REST APIベースのVue.jsアプリケーションで、ユーザー体験・開発効率・運用品質すべてを向上させる包括的パフォーマンス最適化を、3つのAI専門分野協調により実現する。