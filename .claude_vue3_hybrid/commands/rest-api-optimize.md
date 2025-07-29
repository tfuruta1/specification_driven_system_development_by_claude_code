# /rest-api-optimize - REST API パフォーマンス最適化コマンド

## 概要
ハイブリッド接続対応Vue.jsアプリケーション（REST API → Supabase → Offline）のパフォーマンス最適化を多角的に実行する統合コマンドです。**Claude Code + Gemini CLI + o3 MCP**の協調により、API連携・フロントエンド・インフラの包括的最適化を実現します。

## 🎯 使用場面・対象
- **ハイブリッド接続最適化**: REST API・Supabase・オフラインストレージの効率的切り替え
- **API連携パフォーマンス**: レスポンス時間・スループット改善
- **フロントエンド最適化**: レンダリング・バンドルサイズ・キャッシュ戦略
- **フォールバック対応**: 接続切り替え・データ同期・オフライン対応
- **運用効率**: 監視・デバッグ・メンテナンス性向上

## 🤖 マルチAI協調体制

### Claude Code（技術実装リーダー・統合責任者）
- **統合オーケストレーション**: 3つのAI成果物の統合・品質保証
- **フロントエンド最適化**: Vue.js コンポーネント・状態管理・レンダリング最適化
- **ハイブリッド接続最適化**: REST API・Supabase・オフライン接続の統合最適化
- **コード品質保証**: 実装品質・パフォーマンス計測・テスト戦略

### Gemini CLI（データ分析・ユーザー体験スペシャリスト）
- **ユーザー行動分析**: ハイブリッド接続利用パターン・パフォーマンスボトルネック分析
- **データ可視化**: パフォーマンス指標ダッシュボード・監視システム設計
- **UX最適化戦略**: 接続切り替えUX・プログレッシブローディング・ユーザビリティ改善
- **ビジネス価値分析**: 最適化ROI・ユーザー満足度・コンバージョン改善

### o3 MCP（インフラ・アーキテクチャスペシャリスト）
- **API Gateway最適化**: キャッシュ戦略・レート制限・負荷分散
- **CDN・エッジ戦略**: 静的リソース配信・地理的最適化
- **監視・可観測性**: APM・ログ分析・パフォーマンスメトリクス
- **スケーラビリティ**: 自動スケーリング・容量計画・障害対応

## 🚀 基本使用法

```bash
# 包括的パフォーマンス最適化（推奨）
/rest-api-optimize comprehensive --hybrid_focus="all"

# 特定領域の最適化
/rest-api-optimize api --focus="response_time,caching"
/rest-api-optimize frontend --focus="bundle_size,rendering"
/rest-api-optimize hybrid --focus="connection_switching,fallback"
/rest-api-optimize infrastructure --focus="cdn,monitoring"

# AI協調最適化（高精度・推奨）
/rest-api-optimize multiAI --ai_priority="balanced" --scope="hybrid_complete"
```

## 📋 最適化カテゴリー

### 1. ハイブリッド接続最適化（Claude Code主担当）

#### 接続戦略最適化
```javascript
// 最適化されたハイブリッド接続マネージャー
export class OptimizedHybridConnectionManager {
  constructor() {
    this.connectionStates = {
      api: { available: true, responseTime: 0, errorRate: 0 },
      supabase: { available: true, responseTime: 0, errorRate: 0 },
      offline: { available: true, dataFreshness: 0, storagePath: './data/offline/' }
    }
    
    this.performanceThresholds = {
      apiResponseTime: 2000, // 2秒以上でフォールバック検討
      errorRateThreshold: 0.05, // 5%以上のエラー率でフォールバック
      dataFreshnessLimit: 300000 // 5分以上古いデータは要更新
    }
    
    this.offlineStorage = new JSONFileStorage('./data/offline/')
  }
  
  async optimizedRequest(request) {
    // 接続状態の事前チェック
    const bestConnection = await this.selectOptimalConnection(request)
    
    try {
      // 最適接続での実行
      const result = await this.executeWithConnection(bestConnection, request)
      this.updateConnectionMetrics(bestConnection, 'success')
      return result
      
    } catch (error) {
      // 自動フォールバック
      const fallbackConnection = this.getFallbackConnection(bestConnection)
      if (fallbackConnection) {
        console.log(`Falling back from ${bestConnection} to ${fallbackConnection}`)
        return await this.executeWithConnection(fallbackConnection, request)
      }
      throw error
    }
  }
  
  async selectOptimalConnection(request) {
    // パフォーマンス指標ベースの接続選択
    const scores = {
      api: this.calculateConnectionScore('api', request),
      supabase: this.calculateConnectionScore('supabase', request),
      offline: this.calculateConnectionScore('offline', request)
    }
    
    return Object.keys(scores).reduce((best, current) => 
      scores[current] > scores[best] ? current : best
    )
  }
  
  calculateConnectionScore(connection, request) {
    const state = this.connectionStates[connection]
    let score = 100
    
    // レスポンス時間ペナルティ
    score -= Math.min(state.responseTime / 100, 50)
    
    // エラー率ペナルティ
    score -= state.errorRate * 1000
    
    // 接続固有のボーナス/ペナルティ
    switch (connection) {
      case 'api':
        score += request.requiresRealtime ? 30 : 0
        break
      case 'supabase':
        score += request.requiresAuth ? 20 : 0
        break
      case 'offline':
        score += request.canUseCache ? 10 : -50
        break
    }
    
    return Math.max(score, 0)
  }
}
```

#### 予測的データ同期
```javascript
// 予測的データ同期システム
export class PredictiveDataSync {
  constructor() {
    this.syncQueue = new PriorityQueue()
    this.userBehaviorAnalyzer = new UserBehaviorAnalyzer()
    this.syncStrategy = {
      critical: 'immediate',
      important: 'within_5s',
      normal: 'within_30s',
      background: 'when_idle'
    }
  }
  
  async predictAndSync() {
    // ユーザー行動予測
    const predictions = await this.userBehaviorAnalyzer.getPredictions()
    
    predictions.forEach(prediction => {
      if (prediction.confidence > 0.8) {
        this.preloadData(prediction.resource, 'important')
      } else if (prediction.confidence > 0.6) {
        this.preloadData(prediction.resource, 'normal')
      }
    })
  }
  
  async preloadData(resource, priority) {
    const syncTask = {
      resource,
      priority,
      timestamp: Date.now(),
      retryCount: 0
    }
    
    this.syncQueue.enqueue(syncTask, this.getPriorityValue(priority))
    this.processSyncQueue()
  }
  
  async smartSync(data, options = {}) {
    // データの変更頻度・重要度分析
    const syncMetadata = this.analyzeSyncRequirements(data)
    
    // 複数バックエンドへの効率的同期
    const syncPromises = []
    
    if (syncMetadata.requiresImmediate) {
      syncPromises.push(this.syncToAPI(data))
    }
    
    if (syncMetadata.requiresBackup) {
      syncPromises.push(this.syncToSupabase(data))
    }
    
    // JSONファイルオフラインストレージは常に更新
    syncPromises.push(this.syncToJSONFile(data))
    
    // 並列実行で同期時間短縮
    const results = await Promise.allSettled(syncPromises)
    
    return {
      api: results[0]?.status === 'fulfilled',
      supabase: results[1]?.status === 'fulfilled', 
      jsonFile: results[2]?.status === 'fulfilled'
    }
  }
}
```

#### JSONファイルベースオフラインストレージ
```javascript
// JSONファイルオフラインストレージクラス
export class JSONFileStorage {
  constructor(basePath = './data/offline/') {
    this.basePath = basePath
    this.fs = require('fs').promises
    this.path = require('path')
  }
  
  // データフォルダ初期化
  async initializeStorage() {
    try {
      await this.fs.mkdir(this.basePath, { recursive: true })
      console.log(`Offline storage initialized: ${this.basePath}`)
    } catch (error) {
      console.error('Failed to initialize offline storage:', error)
    }
  }
  
  // データ保存
  async saveData(key, data) {
    const filePath = this.path.join(this.basePath, `${key}.json`)
    const dataWithMetadata = {
      data,
      timestamp: Date.now(),
      key,
      version: '1.0.0'
    }
    
    try {
      await this.fs.writeFile(filePath, JSON.stringify(dataWithMetadata, null, 2))
      console.log(`Data saved to offline storage: ${key}`)
      return true
    } catch (error) {
      console.error(`Failed to save data ${key}:`, error)
      return false
    }
  }
  
  // データ取得
  async loadData(key) {
    const filePath = this.path.join(this.basePath, `${key}.json`)
    
    try {
      const fileContent = await this.fs.readFile(filePath, 'utf8')
      const parsedData = JSON.parse(fileContent)
      
      // データの鮮度チェック
      const dataAge = Date.now() - parsedData.timestamp
      const maxAge = 24 * 60 * 60 * 1000 // 24時間
      
      return {
        data: parsedData.data,
        timestamp: parsedData.timestamp,
        isStale: dataAge > maxAge,
        age: dataAge
      }
    } catch (error) {
      console.error(`Failed to load data ${key}:`, error)
      return null
    }
  }
  
  // 複数データ取得
  async loadMultipleData(keys) {
    const results = {}
    
    for (const key of keys) {
      results[key] = await this.loadData(key)
    }
    
    return results
  }
  
  // データ存在確認
  async exists(key) {
    const filePath = this.path.join(this.basePath, `${key}.json`)
    
    try {
      await this.fs.access(filePath)
      return true
    } catch (error) {
      return false
    }
  }
  
  // データ削除
  async deleteData(key) {
    const filePath = this.path.join(this.basePath, `${key}.json`)
    
    try {
      await this.fs.unlink(filePath)
      console.log(`Data deleted from offline storage: ${key}`)
      return true
    } catch (error) {
      console.error(`Failed to delete data ${key}:`, error)
      return false
    }
  }
  
  // 全データリスト取得
  async listAll() {
    try {
      const files = await this.fs.readdir(this.basePath)
      return files
        .filter(file => file.endsWith('.json'))
        .map(file => file.replace('.json', ''))
    } catch (error) {
      console.error('Failed to list offline data:', error)
      return []
    }
  }
  
  // ストレージクリーンアップ（古いデータ削除）
  async cleanup(maxAge = 7 * 24 * 60 * 60 * 1000) { // 7日間
    const keys = await this.listAll()
    let deletedCount = 0
    
    for (const key of keys) {
      const data = await this.loadData(key)
      if (data && (Date.now() - data.timestamp) > maxAge) {
        await this.deleteData(key)
        deletedCount++
      }
    }
    
    console.log(`Cleaned up ${deletedCount} old offline data files`)
    return deletedCount
  }
}
```

### 2. フロントエンド最適化（Claude Code主担当）

#### Vue.js パフォーマンス最適化（ハイブリッド対応）
```javascript
// ハイブリッド対応コンポーネント最適化
export default {
  name: 'OptimizedHybridComponent',
  
  setup() {
    // 接続状態に応じた適応的ローディング
    const { connectionState, isOnline } = useHybridConnection()
    const { data, loading, error } = useAdaptiveData()
    
    // 接続状態別の表示戦略
    const displayStrategy = computed(() => {
      if (!isOnline.value) return 'offline'
      if (connectionState.value.api.available) return 'realtime'
      if (connectionState.value.supabase.available) return 'neartime'
      return 'cached'
    })
    
    // 条件付きリアクティビティ（不要な更新を削減）
    const optimizedData = computed(() => {
      // オフライン時はリアクティビティを最小化
      if (displayStrategy.value === 'offline') {
        return shallowRef(data.value)
      }
      return data.value
    })
    
    // 効率的な更新スケジューリング
    const { throttledUpdate } = useThrottledUpdate(1000)
    
    watch(connectionState, (newState, oldState) => {
      if (newState.primary !== oldState.primary) {
        throttledUpdate(() => {
          // 接続切り替え時の効率的なデータ再取得
          data.refresh({ force: true })
        })
      }
    })
    
    return {
      displayStrategy,
      optimizedData,
      loading,
      error
    }
  }
}

// 仮想スクロール + ハイブリッドデータ
const HybridVirtualScroller = {
  setup(props) {
    const hybridDataManager = new HybridDataManager()
    
    // 効率的なデータ取得（接続に応じて最適化）
    const loadItems = async (startIndex, endIndex) => {
      const connectionType = await hybridDataManager.getBestConnection()
      
      switch (connectionType) {
        case 'api':
          return await loadItemsFromAPI(startIndex, endIndex)
        case 'supabase':  
          return await loadItemsFromSupabase(startIndex, endIndex)
        case 'offline':
          return await loadItemsFromJSONFiles(startIndex, endIndex)
      }
    }
    
    // プリローディング戦略
    const preloadStrategy = computed(() => {
      const connection = hybridDataManager.getCurrentConnection()
      return {
        api: { preloadRadius: 50, batchSize: 20 },
        supabase: { preloadRadius: 30, batchSize: 15 },
        offline: { preloadRadius: 100, batchSize: 50 } // JSONファイルは高速
      }[connection] || { preloadRadius: 20, batchSize: 10 }
    })
    
    return {
      loadItems,
      preloadStrategy
    }
  }
}
```

#### バンドル最適化（ハイブリッド対応）
```javascript
// Vite設定最適化（vite.config.js）
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // ハイブリッド接続関連を分離
          'hybrid-core': ['@/services/hybridConnection', '@/services/offlineStorage'],
          'api-clients': ['axios', '@supabase/supabase-js'],
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['@headlessui/vue', 'daisyui'],
          utils: ['date-fns', 'lodash-es']
        }
      }
    },
    
    // 接続タイプ別の最適化
    define: {
      __ENABLE_API_CONNECTION__: process.env.ENABLE_API !== 'false',
      __ENABLE_SUPABASE_CONNECTION__: process.env.ENABLE_SUPABASE !== 'false',
      __ENABLE_OFFLINE_MODE__: process.env.ENABLE_OFFLINE !== 'false'
    }
  },
  
  // 開発サーバー最適化（複数接続対応）
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy, options) => {
          // API接続のヘルスチェック
          proxy.on('error', (err, req, res) => {
            console.log('API proxy error, falling back to Supabase')
          })
        }
      }
    }
  }
})
```

### 3. ユーザー体験最適化（Gemini CLI主担当）

#### ハイブリッド接続UX戦略
```javascript
// 接続状態可視化・UX最適化
export const hybridUXOptimizer = {
  // 接続状態の直感的表示
  getConnectionStatusDisplay(connectionState) {
    const indicators = {
      api: {
        icon: '🟢',
        label: 'リアルタイム',
        description: 'すべての機能が利用可能です'
      },
      supabase: {
        icon: '🟡', 
        label: '準リアルタイム',
        description: '主要機能が利用可能です'
      },
      offline: {
        icon: '🔴',
        label: 'オフライン',
        description: 'ローカルJSONファイルで動作中です'
      },
      switching: {
        icon: '🔄',
        label: '接続切り替え中',
        description: '最適な接続を選択しています'
      }
    }
    
    return indicators[connectionState] || indicators.offline
  },
  
  // 適応的ローディング戦略
  getAdaptiveLoadingStrategy(connectionType, dataSize) {
    const strategies = {
      api: {
        small: 'instant',
        medium: 'progressive',
        large: 'chunked'
      },
      supabase: {
        small: 'smooth',
        medium: 'stepped',
        large: 'background'
      },
      offline: {
        small: 'instant',
        medium: 'instant', // JSONファイルは高速
        large: 'json_paging'
      }
    }
    
    const sizeCategory = dataSize < 100 ? 'small' : 
                        dataSize < 1000 ? 'medium' : 'large'
    
    return strategies[connectionType]?.[sizeCategory] || 'progressive'
  },
  
  // プロアクティブユーザー通知
  generateUserNotifications(connectionEvents) {
    const notifications = []
    
    connectionEvents.forEach(event => {
      switch (event.type) {
        case 'connection_degraded':
          notifications.push({
            type: 'warning',
            message: '接続が不安定です。一部機能が制限される可能性があります。',
            actions: ['再接続', '詳細']
          })
          break
          
        case 'fallback_activated':
          notifications.push({
            type: 'info',
            message: `${event.from}から${event.to}に切り替えました。`,
            actions: ['理解しました']
          })
          break
          
        case 'sync_pending':
          notifications.push({
            type: 'info',
            message: `${event.pendingCount}件のデータが同期待ちです。`,
            actions: ['今すぐ同期', '後で']
          })
          break
      }
    })
    
    return notifications
  }
}
```

#### エラー処理・復旧戦略（ハイブリッド対応）
```javascript
// ハイブリッド対応エラー復旧システム
export const hybridErrorRecovery = {
  // 自動復旧戦略
  async autoRecover(error, context) {
    const recoveryPlan = this.generateRecoveryPlan(error, context)
    
    for (const strategy of recoveryPlan) {
      try {
        const result = await this.executeRecoveryStrategy(strategy)
        if (result.success) {
          return result
        }
      } catch (recoveryError) {
        console.log(`Recovery strategy ${strategy.name} failed:`, recoveryError)
      }
    }
    
    // 全復旧戦略が失敗した場合
    return this.gracefulDegradation(error, context)
  },
  
  generateRecoveryPlan(error, context) {
    const plans = []
    
    if (error.type === 'network') {
      plans.push(
        { name: 'retry_with_exponential_backoff', priority: 1 },
        { name: 'switch_to_supabase', priority: 2 },
        { name: 'use_json_files', priority: 3 }
      )
    } else if (error.type === 'authentication') {
      plans.push(
        { name: 'refresh_token', priority: 1 },
        { name: 'switch_to_supabase_auth', priority: 2 },
        { name: 'prompt_relogin', priority: 3 }
      )
    } else if (error.type === 'rate_limit') {
      plans.push(
        { name: 'exponential_backoff', priority: 1 },
        { name: 'switch_to_alternative_endpoint', priority: 2 },
        { name: 'queue_request', priority: 3 }
      )
    }
    
    return plans.sort((a, b) => a.priority - b.priority)
  },
  
  // 段階的機能縮退
  async gracefulDegradation(error, context) {
    const degradationLevels = [
      {
        level: 1,
        description: '非重要機能の無効化',
        actions: ['disable_animations', 'reduce_polling_frequency']
      },
      {
        level: 2, 
        description: 'JSONファイルモード移行',
        actions: ['switch_to_json_files', 'show_limited_functionality_notice']
      },
      {
        level: 3,
        description: '最小機能モード',
        actions: ['enable_read_only_mode', 'disable_real_time_features']
      }
    ]
    
    for (const level of degradationLevels) {
      try {
        await this.applyDegradationLevel(level)
        return { success: true, level: level.level }
      } catch (degradationError) {
        console.log(`Degradation level ${level.level} failed`)
      }
    }
    
    // 最終手段：リロード推奨
    return {
      success: false,
      recommendation: 'page_reload',
      message: 'アプリケーションの再読み込みが必要です'
    }
  }
}
```

### 4. インフラ・監視最適化（o3 MCP主担当）

#### ハイブリッド監視戦略
```javascript
// ハイブリッド接続監視システム
export const hybridMonitoring = {
  // 接続品質監視
  monitorConnectionQuality() {
    const connections = ['api', 'supabase', 'offline']
    
    connections.forEach(connection => {
      this.startConnectionMetrics(connection)
    })
  },
  
  startConnectionMetrics(connectionType) {
    const metricsCollector = {
      responseTime: [],
      errorRate: 0,
      throughput: 0,
      availability: 100
    }
    
    // リアルタイムメトリクス収集
    setInterval(() => {
      this.collectConnectionMetrics(connectionType, metricsCollector)
    }, 5000)
    
    // アラート設定
    this.setupConnectionAlerts(connectionType, metricsCollector)
  },
  
  collectConnectionMetrics(connectionType, collector) {
    // 各接続タイプ固有のメトリクス収集
    switch (connectionType) {
      case 'api':
        this.collectAPIMetrics(collector)
        break
      case 'supabase':
        this.collectSupabaseMetrics(collector)
        break
      case 'offline':
        this.collectOfflineMetrics(collector)
        break
    }
    
    // パフォーマンスデータベースに送信
    this.sendMetrics(connectionType, collector)
  },
  
  // ハイブリッド切り替え監視
  monitorConnectionSwitching() {
    const switchingEvents = []
    
    window.addEventListener('hybrid-connection-switch', (event) => {
      const switchEvent = {
        timestamp: Date.now(),
        from: event.detail.from,
        to: event.detail.to,
        reason: event.detail.reason,
        userImpact: this.assessUserImpact(event.detail)
      }
      
      switchingEvents.push(switchEvent)
      this.analyzeSwichingPatterns(switchingEvents)
    })
  },
  
  // Core Web Vitals（ハイブリッド対応）
  trackHybridVitals() {
    // 接続タイプ別のパフォーマンス指標
    const hybridVitals = {
      connectionSwitchTime: this.measureConnectionSwitchTime(),
      dataFreshness: this.measureDataFreshness(),
      offlineFunctionality: this.measureOfflineFunctionality(),
      syncEfficiency: this.measureSyncEfficiency()
    }
    
    // 標準のCore Web Vitalsと合わせて監視
    this.trackStandardVitals()
    this.sendHybridVitals(hybridVitals)
  }
}
```

## 📊 最適化成果指標・KPI（ハイブリッド対応）

### ハイブリッド接続指標
- **接続切り替え時間**: 500ms以内達成
- **フォールバック成功率**: 99.5%以上
- **データ同期効率**: 95%以上の整合性維持
- **オフライン機能率**: 主要機能の80%以上オフライン利用可能

### パフォーマンス指標
- **API レスポンス時間**: 50%以上短縮目標
- **初期ページロード**: 3秒以内達成（全接続モード）
- **バンドルサイズ**: 30%以上削減
- **Core Web Vitals**: Good範囲達成（LCP <2.5s, FID <100ms, CLS <0.1）

### ユーザー体験指標  
- **体感速度**: 接続切り替え時の遅延感削減
- **エラー率**: 接続エラー90%以上削減（フォールバック効果）
- **オフライン対応**: 基本機能の完全利用継続
- **レスポンシブ性**: 全デバイス・全接続モードでの快適操作

### 運用効率指標
- **障害影響範囲**: ハイブリッド対応による50%以上削減
- **復旧時間**: 自動フォールバックによる大幅短縮
- **監視効率**: 統合監視による運用コスト削減

## 🎯 実行フロー・手順（ハイブリッド対応）

### Phase 1: ハイブリッド接続分析（Gemini CLI）
```bash
# ユーザー行動・接続パターン分析
/research hybrid_usage --focus="connection_patterns,fallback_scenarios"

# パフォーマンス課題抽出（接続別）
/research performance_analysis --scope="api,supabase,offline" --metrics="response_time,error_rate"
```

### Phase 2: アーキテクチャ設計（o3 MCP）
```bash
# ハイブリッドインフラ最適化戦略
/architecture hybrid_optimization --scope="connection_management,fallback_strategy"

# 監視・可観測性設計
/devops hybrid_monitoring --environment="production" --focus="connection_metrics"
```

### Phase 3: 実装・統合（Claude Code）
```bash
# ハイブリッド接続最適化実装
/enhance hybrid_performance --focus="connection_switching,sync_optimization"

# フロントエンド最適化（ハイブリッド対応）
/refactor vue_hybrid --focus="adaptive_components,efficient_rendering"

# 品質保証・テスト
/analyze hybrid_integration --scope="frontend,connections,fallback"
```

### Phase 4: 統合品質保証（All AI協調）
```bash
# 統合検証・最終調整
/rest-api-optimize validation --ai_collaboration="intensive" --hybrid_mode="enabled"

# パフォーマンステスト・監視設定
/devops hybrid_testing --load_test="all_connections" --monitoring="production"
```

## 📚 技術参考・ベストプラクティス

### ハイブリッド接続リファレンス
- [Progressive Web App Patterns](https://web.dev/progressive-web-apps/)
- [Offline-First Architecture](https://offlinefirst.org/)
- [Connection-Aware Components](https://developer.mozilla.org/en-US/docs/Web/API/Network_Information_API)

### API最適化リファレンス
- [Axios Performance Guide](https://axios-http.com/docs/optimizing)
- [Supabase Performance Best Practices](https://supabase.com/docs/guides/performance)
- [REST API Caching Strategies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)

### Vue.js パフォーマンス
- [Vue.js Performance Guide](https://vuejs.org/guide/best-practices/performance.html)
- [Bundle Optimization with Vite](https://vitejs.dev/guide/build.html#chunking-strategy)
- [Web Performance Metrics](https://web.dev/vitals/)

## 🔄 継続改善・メンテナンス

### 定期最適化サイクル
```bash
# 月次ハイブリッドパフォーマンスレビュー
/rest-api-optimize monthly_review --period="last_30_days" --hybrid_focus="enabled"

# 四半期接続戦略見直し
/devops connection_strategy_review --scope="hybrid_patterns,user_behavior"

# 年次技術スタック評価
/architecture technology_assessment --focus="hybrid_architecture,scalability"
```

### 自動化・監視
- **自動接続切り替えテスト**: CI/CD統合
- **ハイブリッド接続アラート**: 閾値ベースの自動通知  
- **接続品質レポート**: 定期的な最適化効果測定

---

**🎯 コマンド目標**: ハイブリッド接続対応Vue.jsアプリケーションで、REST API・Supabase・オフラインストレージの最適な組み合わせにより、ユーザー体験・開発効率・運用品質すべてを向上させる包括的パフォーマンス最適化を、3つのAI専門分野協調により実現する。