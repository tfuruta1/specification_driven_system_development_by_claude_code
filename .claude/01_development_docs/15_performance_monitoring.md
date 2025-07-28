# パフォーマンス監視設計書

## 概要

このドキュメントでは、Vue.js + Supabaseアプリケーションにおけるパフォーマンス監視の包括的な戦略を定義します。リアルタイムでのパフォーマンス測定、ユーザー体験の監視、ボトルネックの特定、自動アラートシステムまで、継続的なパフォーマンス改善を支援する監視システムを設計します。

## 1. 監視アーキテクチャ

### 1.1 監視対象の分類
```javascript
// 監視対象の体系化
const monitoringTargets = {
  frontend: {
    coreWebVitals: "Core Web Vitals（LCP、FID、CLS）",
    loadingPerformance: "読み込みパフォーマンス",
    runtimePerformance: "実行時パフォーマンス",
    errorTracking: "エラートラッキング",
    userExperience: "ユーザー体験指標"
  },
  
  backend: {
    apiResponse: "APIレスポンス時間",
    databaseQuery: "データベースクエリ性能",
    serverResources: "サーバーリソース使用状況",
    errorRates: "エラー率"
  },
  
  infrastructure: {
    networking: "ネットワーク性能",
    cdn: "CDN効率",
    caching: "キャッシュ効率",
    security: "セキュリティイベント"
  },
  
  business: {
    conversionRates: "コンバージョン率",
    userEngagement: "ユーザーエンゲージメント",
    sessionDuration: "セッション継続時間",
    bounceRate: "直帰率"
  }
}
```

### 1.2 監視アーキテクチャ設計
```javascript
// 監視システムアーキテクチャ
const monitoringArchitecture = {
  collection: {
    clientSide: "ブラウザベースの測定",
    serverSide: "サーバーサイド監視",
    realUserMonitoring: "リアルユーザー監視（RUM）",
    syntheticMonitoring: "合成監視"
  },
  
  processing: {
    aggregation: "データ集約処理",
    analysis: "パフォーマンス分析",
    alerting: "アラート処理",
    reporting: "レポート生成"
  },
  
  storage: {
    timeSeries: "時系列データベース",
    logging: "ログストレージ",
    metrics: "メトリクスストレージ",
    traces: "トレースデータ"
  },
  
  visualization: {
    dashboards: "リアルタイムダッシュボード",
    alerts: "アラート通知",
    reports: "定期レポート",
    analytics: "分析ツール"
  }
}
```

## 2. フロントエンド監視

### 2.1 Core Web Vitals監視
```javascript
// composables/usePerformanceMonitoring.js
import { ref, onMounted, onUnmounted } from 'vue'

/**
 * パフォーマンス監視 Composable
 */
export function usePerformanceMonitoring() {
  const metrics = ref({
    lcp: null,      // Largest Contentful Paint
    fid: null,      // First Input Delay
    cls: null,      // Cumulative Layout Shift
    fcp: null,      // First Contentful Paint
    ttfb: null,     // Time to First Byte
    inp: null       // Interaction to Next Paint
  })
  
  const isSupported = ref(false)
  const observers = []
  
  /**
   * Performance Observer の初期化
   */
  const initPerformanceObservers = () => {
    if (!('PerformanceObserver' in window)) {
      console.warn('PerformanceObserver is not supported')
      return
    }
    
    isSupported.value = true
    
    // LCP 監視
    const lcpObserver = new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries()
      const lastEntry = entries[entries.length - 1]
      metrics.value.lcp = Math.round(lastEntry.startTime)
      
      // データ送信
      sendMetric('lcp', metrics.value.lcp)
    })
    
    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true })
    observers.push(lcpObserver)
    
    // FID 監視
    const fidObserver = new PerformanceObserver((entryList) => {
      entryList.getEntries().forEach((entry) => {
        metrics.value.fid = Math.round(entry.processingStart - entry.startTime)
        sendMetric('fid', metrics.value.fid)
      })
    })
    
    fidObserver.observe({ type: 'first-input', buffered: true })
    observers.push(fidObserver)
    
    // CLS 監視
    let clsValue = 0
    const clsObserver = new PerformanceObserver((entryList) => {
      entryList.getEntries().forEach((entry) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value
          metrics.value.cls = Math.round(clsValue * 1000) / 1000
        }
      })
      
      sendMetric('cls', metrics.value.cls)
    })
    
    clsObserver.observe({ type: 'layout-shift', buffered: true })
    observers.push(clsObserver)
    
    // Navigation Timing API
    const navigationObserver = new PerformanceObserver((entryList) => {
      entryList.getEntries().forEach((entry) => {
        metrics.value.fcp = Math.round(entry.firstContentfulPaint || 0)
        metrics.value.ttfb = Math.round(entry.responseStart - entry.requestStart)
        
        sendMetric('fcp', metrics.value.fcp)
        sendMetric('ttfb', metrics.value.ttfb)
      })
    })
    
    navigationObserver.observe({ type: 'navigation', buffered: true })
    observers.push(navigationObserver)
  }
  
  /**
   * メトリクスデータの送信
   * @param {string} metricName
   * @param {number} value
   */
  const sendMetric = async (metricName, value) => {
    try {
      // パフォーマンスデータをバックエンドに送信
      await fetch('/api/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          metric: metricName,
          value,
          timestamp: Date.now(),
          url: window.location.href,
          userAgent: navigator.userAgent,
          connectionType: navigator.connection?.effectiveType || 'unknown',
          deviceMemory: navigator.deviceMemory || 'unknown'
        })
      })
    } catch (error) {
      console.error('メトリクス送信エラー:', error)
    }
  }
  
  /**
   * カスタムメトリクスの測定
   * @param {string} name
   * @param {Function} fn
   */
  const measureCustomMetric = async (name, fn) => {
    const startTime = performance.now()
    
    try {
      const result = await fn()
      const duration = performance.now() - startTime
      
      // カスタムメトリクスとして記録
      performance.mark(`${name}-start`)
      performance.mark(`${name}-end`)
      performance.measure(name, `${name}-start`, `${name}-end`)
      
      sendMetric(`custom_${name}`, Math.round(duration))
      
      return result
    } catch (error) {
      const duration = performance.now() - startTime
      sendMetric(`custom_${name}_error`, Math.round(duration))
      throw error
    }
  }
  
  /**
   * クリーンアップ
   */
  const cleanup = () => {
    observers.forEach(observer => observer.disconnect())
    observers.length = 0
  }
  
  onMounted(() => {
    initPerformanceObservers()
  })
  
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    metrics,
    isSupported,
    measureCustomMetric,
    sendMetric
  }
}
```

### 2.2 エラー監視
```javascript
// services/monitoring/errorMonitoring.js
import { ref } from 'vue'

/**
 * エラー監視サービス
 */
export class ErrorMonitoringService {
  constructor() {
    this.errorCount = ref(0)
    this.errors = ref([])
    this.isInitialized = false
    
    this.init()
  }
  
  /**
   * エラー監視の初期化
   */
  init() {
    if (this.isInitialized) return
    
    // JavaScript エラー監視
    window.addEventListener('error', (event) => {
      this.handleError({
        type: 'javascript',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack,
        timestamp: Date.now()
      })
    })
    
    // Promise rejection 監視
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError({
        type: 'promise',
        message: event.reason?.message || 'Unhandled Promise Rejection',
        reason: event.reason,
        timestamp: Date.now()
      })
    })
    
    // Vue.js エラー監視
    this.initVueErrorHandler()
    
    // Network エラー監視
    this.initNetworkErrorMonitoring()
    
    this.isInitialized = true
  }
  
  /**
   * Vue.js エラーハンドラーの設定
   */
  initVueErrorHandler() {
    const originalErrorHandler = window.Vue?.config?.errorHandler
    
    if (window.Vue?.config) {
      window.Vue.config.errorHandler = (err, instance, info) => {
        this.handleError({
          type: 'vue',
          message: err.message,
          stack: err.stack,
          componentInfo: info,
          instance: instance?.$options?.name || 'Unknown',
          timestamp: Date.now()
        })
        
        // 元のエラーハンドラーも実行
        if (originalErrorHandler) {
          originalErrorHandler(err, instance, info)
        }
      }
    }
  }
  
  /**
   * ネットワークエラー監視
   */
  initNetworkErrorMonitoring() {
    // Fetch API の監視
    const originalFetch = window.fetch
    window.fetch = async (...args) => {
      try {
        const response = await originalFetch(...args)
        
        if (!response.ok) {
          this.handleError({
            type: 'network',
            message: `HTTP ${response.status}: ${response.statusText}`,
            url: args[0],
            status: response.status,
            timestamp: Date.now()
          })
        }
        
        return response
      } catch (error) {
        this.handleError({
          type: 'network',
          message: error.message,
          url: args[0],
          timestamp: Date.now()
        })
        throw error
      }
    }
    
    // XMLHttpRequest の監視
    const originalXHROpen = XMLHttpRequest.prototype.open
    const originalXHRSend = XMLHttpRequest.prototype.send
    
    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
      this._url = url
      this._method = method
      return originalXHROpen.call(this, method, url, ...rest)
    }
    
    XMLHttpRequest.prototype.send = function(...args) {
      this.addEventListener('error', () => {
        this.handleError({
          type: 'xhr',
          message: 'XMLHttpRequest failed',
          url: this._url,
          method: this._method,
          timestamp: Date.now()
        })
      })
      
      this.addEventListener('load', () => {
        if (this.status >= 400) {
          this.handleError({
            type: 'xhr',
            message: `HTTP ${this.status}: ${this.statusText}`,
            url: this._url,
            method: this._method,
            status: this.status,
            timestamp: Date.now()
          })
        }
      })
      
      return originalXHRSend.call(this, ...args)
    }
  }
  
  /**
   * エラー処理
   * @param {Object} errorInfo
   */
  handleError(errorInfo) {
    this.errorCount.value++
    this.errors.value.push(errorInfo)
    
    // エラーレベルの判定
    const level = this.determineErrorLevel(errorInfo)
    
    // エラーデータの送信
    this.sendErrorToBackend({
      ...errorInfo,
      level,
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: this.getCurrentUserId(),
      sessionId: this.getSessionId()
    })
    
    // 重要なエラーの場合は即座にアラート
    if (level === 'critical') {
      this.sendImmediateAlert(errorInfo)
    }
  }
  
  /**
   * エラーレベルの判定
   * @param {Object} errorInfo
   * @returns {string}
   */
  determineErrorLevel(errorInfo) {
    // 重要なエラーの条件
    const criticalConditions = [
      errorInfo.message?.includes('ChunkLoadError'),
      errorInfo.message?.includes('Loading chunk'),
      errorInfo.message?.includes('auth'),
      errorInfo.status >= 500
    ]
    
    if (criticalConditions.some(condition => condition)) {
      return 'critical'
    }
    
    // 警告レベルのエラー
    const warningConditions = [
      errorInfo.status >= 400 && errorInfo.status < 500,
      errorInfo.type === 'vue',
      errorInfo.message?.includes('Script error')
    ]
    
    if (warningConditions.some(condition => condition)) {
      return 'warning'
    }
    
    return 'info'
  }
  
  /**
   * バックエンドへのエラー送信
   * @param {Object} errorData
   */
  async sendErrorToBackend(errorData) {
    try {
      await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(errorData)
      })
    } catch (error) {
      console.error('エラー送信失敗:', error)
      // ローカルストレージに保存してリトライ
      this.storeErrorLocally(errorData)
    }
  }
  
  /**
   * 即座のアラート送信
   * @param {Object} errorInfo
   */
  async sendImmediateAlert(errorInfo) {
    try {
      await fetch('/api/alerts/immediate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: 'critical_error',
          error: errorInfo,
          timestamp: Date.now()
        })
      })
    } catch (error) {
      console.error('即座アラート送信失敗:', error)
    }
  }
  
  /**
   * ローカルエラー保存
   * @param {Object} errorData
   */
  storeErrorLocally(errorData) {
    try {
      const storedErrors = JSON.parse(localStorage.getItem('pending_errors') || '[]')
      storedErrors.push(errorData)
      
      // 最大100件まで保存
      if (storedErrors.length > 100) {
        storedErrors.splice(0, storedErrors.length - 100)
      }
      
      localStorage.setItem('pending_errors', JSON.stringify(storedErrors))
    } catch (error) {
      console.error('ローカルエラー保存失敗:', error)
    }
  }
  
  /**
   * 保留中のエラーを送信
   */
  async sendPendingErrors() {
    try {
      const pendingErrors = JSON.parse(localStorage.getItem('pending_errors') || '[]')
      
      if (pendingErrors.length === 0) return
      
      await fetch('/api/errors/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ errors: pendingErrors })
      })
      
      localStorage.removeItem('pending_errors')
    } catch (error) {
      console.error('保留エラー送信失敗:', error)
    }
  }
  
  /**
   * 現在のユーザーIDを取得
   * @returns {string|null}
   */
  getCurrentUserId() {
    // 実装はアプリケーション固有
    return window.user?.id || null
  }
  
  /**
   * セッションIDを取得
   * @returns {string}
   */
  getSessionId() {
    let sessionId = sessionStorage.getItem('session_id')
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      sessionStorage.setItem('session_id', sessionId)
    }
    return sessionId
  }
  
  /**
   * エラー統計の取得
   * @returns {Object}
   */
  getErrorStats() {
    return {
      totalErrors: this.errorCount.value,
      recentErrors: this.errors.value.slice(-10),
      errorsByType: this.getErrorsByType(),
      errorRate: this.calculateErrorRate()
    }
  }
  
  /**
   * タイプ別エラー集計
   * @returns {Object}
   */
  getErrorsByType() {
    return this.errors.value.reduce((acc, error) => {
      acc[error.type] = (acc[error.type] || 0) + 1
      return acc
    }, {})
  }
  
  /**
   * エラー率の計算
   * @returns {number}
   */
  calculateErrorRate() {
    const totalActions = parseInt(sessionStorage.getItem('total_actions') || '0')
    return totalActions > 0 ? (this.errorCount.value / totalActions) * 100 : 0
  }
}

// グローバルエラー監視インスタンス
export const errorMonitoring = new ErrorMonitoringService()
```

## 3. ユーザー体験監視

### 3.1 ユーザー行動トラッキング
```javascript
// services/monitoring/userExperienceMonitoring.js
import { ref, reactive } from 'vue'

/**
 * ユーザー体験監視サービス
 */
export class UserExperienceMonitoring {
  constructor() {
    this.sessionData = reactive({
      sessionId: this.generateSessionId(),
      startTime: Date.now(),
      pageViews: 0,
      interactions: 0,
      errors: 0,
      performance: {}
    })
    
    this.userActions = ref([])
    this.vitals = reactive({
      engagementTime: 0,
      scrollDepth: 0,
      clickCount: 0,
      formInteractions: 0
    })
    
    this.init()
  }
  
  /**
   * 監視の初期化
   */
  init() {
    this.trackPageViews()
    this.trackUserInteractions()
    this.trackScrollBehavior()
    this.trackFormInteractions()
    this.trackEngagementTime()
    this.trackVisibilityChanges()
  }
  
  /**
   * ページビュートラッキング
   */
  trackPageViews() {
    // 初期ページビュー
    this.recordPageView()
    
    // SPA ルート変更の監視
    const originalPushState = history.pushState
    const originalReplaceState = history.replaceState
    
    history.pushState = function(...args) {
      originalPushState.apply(history, args)
      this.recordPageView()
    }.bind(this)
    
    history.replaceState = function(...args) {
      originalReplaceState.apply(history, args)
      this.recordPageView()
    }.bind(this)
    
    window.addEventListener('popstate', () => {
      this.recordPageView()
    })
  }
  
  /**
   * ページビューの記録
   */
  recordPageView() {
    this.sessionData.pageViews++
    
    const pageData = {
      type: 'pageview',
      url: window.location.href,
      title: document.title,
      timestamp: Date.now(),
      referrer: document.referrer,
      loadTime: performance.timing?.loadEventEnd - performance.timing?.navigationStart || 0
    }
    
    this.userActions.value.push(pageData)
    this.sendUserAction(pageData)
  }
  
  /**
   * ユーザーインタラクションの追跡
   */
  trackUserInteractions() {
    // クリックイベント
    document.addEventListener('click', (event) => {
      this.sessionData.interactions++
      this.vitals.clickCount++
      
      const interactionData = {
        type: 'click',
        element: this.getElementSelector(event.target),
        text: event.target.textContent?.trim().substring(0, 100),
        timestamp: Date.now(),
        coordinates: { x: event.clientX, y: event.clientY }
      }
      
      this.recordUserAction(interactionData)
    })
    
    // キーボードイベント
    document.addEventListener('keydown', (event) => {
      // パスワードフィールドなどの機密情報は除外
      if (event.target.type === 'password') return
      
      const keyData = {
        type: 'keydown',
        key: event.key,
        element: this.getElementSelector(event.target),
        timestamp: Date.now()
      }
      
      this.recordUserAction(keyData)
    })
  }
  
  /**
   * スクロール行動の追跡
   */
  trackScrollBehavior() {
    let maxScrollDepth = 0
    let scrollTimeout = null
    
    window.addEventListener('scroll', () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight
      const scrollPercent = Math.round((scrollTop / documentHeight) * 100)
      
      if (scrollPercent > maxScrollDepth) {
        maxScrollDepth = scrollPercent
        this.vitals.scrollDepth = scrollPercent
      }
      
      // スクロール終了を検知
      clearTimeout(scrollTimeout)
      scrollTimeout = setTimeout(() => {
        this.recordUserAction({
          type: 'scroll',
          depth: scrollPercent,
          maxDepth: maxScrollDepth,
          timestamp: Date.now()
        })
      }, 150)
    })
  }
  
  /**
   * フォームインタラクションの追跡
   */
  trackFormInteractions() {
    document.addEventListener('focus', (event) => {
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        this.vitals.formInteractions++
        
        this.recordUserAction({
          type: 'form_focus',
          element: this.getElementSelector(event.target),
          fieldType: event.target.type,
          timestamp: Date.now()
        })
      }
    })
    
    document.addEventListener('submit', (event) => {
      const formData = new FormData(event.target)
      const fieldCount = [...formData.keys()].length
      
      this.recordUserAction({
        type: 'form_submit',
        element: this.getElementSelector(event.target),
        fieldCount,
        timestamp: Date.now()
      })
    })
  }
  
  /**
   * エンゲージメント時間の追跡
   */
  trackEngagementTime() {
    let startTime = Date.now()
    let isActive = true
    
    // ページがアクティブな時間を測定
    const updateEngagementTime = () => {
      if (isActive) {
        this.vitals.engagementTime = Date.now() - startTime
      }
    }
    
    // 定期的に更新
    setInterval(updateEngagementTime, 1000)
    
    // 非アクティブ状態の検知
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        updateEngagementTime()
        isActive = false
      } else {
        startTime = Date.now()
        isActive = true
      }
    })
    
    // マウス移動やキーボード入力でアクティブ状態を更新
    let inactivityTimer = null
    const resetInactivityTimer = () => {
      isActive = true
      clearTimeout(inactivityTimer)
      inactivityTimer = setTimeout(() => {
        isActive = false
      }, 30000) // 30秒間操作がないと非アクティブ
    }
    
    document.addEventListener('mousemove', resetInactivityTimer)
    document.addEventListener('keydown', resetInactivityTimer)
    document.addEventListener('click', resetInactivityTimer)
  }
  
  /**
   * 可視性変更の追跡
   */
  trackVisibilityChanges() {
    document.addEventListener('visibilitychange', () => {
      this.recordUserAction({
        type: 'visibility_change',
        hidden: document.hidden,
        timestamp: Date.now()
      })
    })
  }
  
  /**
   * ユーザーアクションの記録
   * @param {Object} actionData
   */
  recordUserAction(actionData) {
    this.userActions.value.push(actionData)
    
    // 最新500件のみ保持
    if (this.userActions.value.length > 500) {
      this.userActions.value.splice(0, this.userActions.value.length - 500)
    }
    
    this.sendUserAction(actionData)
  }
  
  /**
   * ユーザーアクションの送信
   * @param {Object} actionData
   */
  async sendUserAction(actionData) {
    try {
      await fetch('/api/user-actions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sessionId: this.sessionData.sessionId,
          action: actionData,
          vitals: this.vitals,
          userAgent: navigator.userAgent,
          url: window.location.href
        })
      })
    } catch (error) {
      console.error('ユーザーアクション送信エラー:', error)
    }
  }
  
  /**
   * 要素セレクターの取得
   * @param {Element} element
   * @returns {string}
   */
  getElementSelector(element) {
    if (element.id) {
      return `#${element.id}`
    }
    
    if (element.className) {
      return `.${element.className.split(' ').join('.')}`
    }
    
    let selector = element.tagName.toLowerCase()
    let parent = element.parentElement
    
    while (parent && selector.split(' ').length < 3) {
      if (parent.id) {
        selector = `#${parent.id} ${selector}`
        break
      } else if (parent.className) {
        selector = `.${parent.className.split(' ')[0]} ${selector}`
      } else {
        selector = `${parent.tagName.toLowerCase()} ${selector}`
      }
      parent = parent.parentElement
    }
    
    return selector
  }
  
  /**
   * セッションIDの生成
   * @returns {string}
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  /**
   * セッションサマリーの生成
   * @returns {Object}
   */
  getSessionSummary() {
    const sessionDuration = Date.now() - this.sessionData.startTime
    
    return {
      sessionId: this.sessionData.sessionId,
      duration: sessionDuration,
      pageViews: this.sessionData.pageViews,
      interactions: this.sessionData.interactions,
      engagementTime: this.vitals.engagementTime,
      engagementRate: (this.vitals.engagementTime / sessionDuration) * 100,
      scrollDepth: this.vitals.scrollDepth,
      clickCount: this.vitals.clickCount,
      formInteractions: this.vitals.formInteractions,
      bounceRate: this.sessionData.pageViews === 1 ? 100 : 0
    }
  }
  
  /**
   * セッション終了時の処理
   */
  endSession() {
    const summary = this.getSessionSummary()
    
    // セッションサマリーを送信
    navigator.sendBeacon('/api/session-end', JSON.stringify(summary))
  }
}

// グローバルユーザー体験監視インスタンス
export const uxMonitoring = new UserExperienceMonitoring()

// ページアンロード時にセッション終了
window.addEventListener('beforeunload', () => {
  uxMonitoring.endSession()
})
```

## 4. バックエンド監視

### 4.1 API パフォーマンス監視
```javascript
// services/monitoring/apiMonitoring.js
import { supabase } from '@/lib/supabase'

/**
 * API監視サービス
 */
export class APIMonitoring {
  constructor() {
    this.metrics = new Map()
    this.init()
  }
  
  /**
   * API監視の初期化
   */
  init() {
    this.interceptSupabaseRequests()
    this.monitorNetworkConditions()
  }
  
  /**
   * Supabaseリクエストの監視
   */
  interceptSupabaseRequests() {
    // Supabase client のリクエストを監視
    const originalRequest = supabase.rest.request.bind(supabase.rest)
    
    supabase.rest.request = async (config) => {
      const startTime = performance.now()
      const requestId = this.generateRequestId()
      
      try {
        const response = await originalRequest(config)
        const endTime = performance.now()
        const duration = endTime - startTime
        
        this.recordAPIMetric({
          requestId,
          method: config.method,
          url: config.url,
          duration,
          status: response.status,
          success: true,
          timestamp: Date.now()
        })
        
        return response
      } catch (error) {
        const endTime = performance.now()
        const duration = endTime - startTime
        
        this.recordAPIMetric({
          requestId,
          method: config.method,
          url: config.url,
          duration,
          status: error.status || 0,
          success: false,
          error: error.message,
          timestamp: Date.now()
        })
        
        throw error
      }
    }
  }
  
  /**
   * APIメトリクスの記録
   * @param {Object} metricData
   */
  recordAPIMetric(metricData) {
    const key = `${metricData.method}_${metricData.url}`
    
    if (!this.metrics.has(key)) {
      this.metrics.set(key, {
        requests: [],
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        averageDuration: 0,
        p95Duration: 0,
        errorRate: 0
      })
    }
    
    const metric = this.metrics.get(key)
    metric.requests.push(metricData)
    metric.totalRequests++
    
    if (metricData.success) {
      metric.successfulRequests++
    } else {
      metric.failedRequests++
    }
    
    // 最新100件のみ保持
    if (metric.requests.length > 100) {
      metric.requests.splice(0, metric.requests.length - 100)
    }
    
    // 統計値の更新
    this.updateStatistics(metric)
    
    // メトリクスの送信
    this.sendAPIMetric(metricData)
  }
  
  /**
   * 統計値の更新
   * @param {Object} metric
   */
  updateStatistics(metric) {
    const durations = metric.requests
      .filter(r => r.success)
      .map(r => r.duration)
      .sort((a, b) => a - b)
    
    if (durations.length > 0) {
      // 平均レスポンス時間
      metric.averageDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length
      
      // 95パーセンタイル
      const p95Index = Math.floor(durations.length * 0.95)
      metric.p95Duration = durations[p95Index] || durations[durations.length - 1]
    }
    
    // エラー率
    metric.errorRate = (metric.failedRequests / metric.totalRequests) * 100
  }
  
  /**
   * ネットワーク状況の監視
   */
  monitorNetworkConditions() {
    if ('connection' in navigator) {
      const connection = navigator.connection
      
      const logNetworkChange = () => {
        this.sendNetworkMetric({
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt,
          saveData: connection.saveData,
          timestamp: Date.now()
        })
      }
      
      connection.addEventListener('change', logNetworkChange)
      
      // 初期状態を記録
      logNetworkChange()
    }
  }
  
  /**
   * APIメトリクスの送信
   * @param {Object} metricData
   */
  async sendAPIMetric(metricData) {
    try {
      await fetch('/api/metrics/api', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(metricData)
      })
    } catch (error) {
      console.error('APIメトリクス送信エラー:', error)
    }
  }
  
  /**
   * ネットワークメトリクスの送信
   * @param {Object} networkData
   */
  async sendNetworkMetric(networkData) {
    try {
      await fetch('/api/metrics/network', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(networkData)
      })
    } catch (error) {
      console.error('ネットワークメトリクス送信エラー:', error)
    }
  }
  
  /**
   * リクエストIDの生成
   * @returns {string}
   */
  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  /**
   * API統計の取得
   * @returns {Object}
   */
  getAPIStatistics() {
    const stats = {}
    
    for (const [endpoint, metric] of this.metrics.entries()) {
      stats[endpoint] = {
        totalRequests: metric.totalRequests,
        successRate: (metric.successfulRequests / metric.totalRequests) * 100,
        errorRate: metric.errorRate,
        averageDuration: Math.round(metric.averageDuration),
        p95Duration: Math.round(metric.p95Duration)
      }
    }
    
    return stats
  }
}

// グローバルAPI監視インスタンス
export const apiMonitoring = new APIMonitoring()
```

## 5. アラートシステム

### 5.1 アラート設定
```javascript
// services/monitoring/alertSystem.js
import { ref, computed } from 'vue'

/**
 * アラートシステム
 */
export class AlertSystem {
  constructor() {
    this.alerts = ref([])
    this.alertRules = ref([])
    this.thresholds = reactive({
      lcp: { warning: 2500, critical: 4000 },
      fid: { warning: 100, critical: 300 },
      cls: { warning: 0.1, critical: 0.25 },
      errorRate: { warning: 5, critical: 10 },
      apiResponseTime: { warning: 1000, critical: 3000 }
    })
    
    this.init()
  }
  
  /**
   * アラートシステムの初期化
   */
  init() {
    this.setupDefaultRules()
    this.startMonitoring()
  }
  
  /**
   * デフォルトアラートルールの設定
   */
  setupDefaultRules() {
    this.alertRules.value = [
      {
        id: 'lcp_threshold',
        name: 'LCP閾値超過',
        condition: (metrics) => metrics.lcp > this.thresholds.lcp.critical,
        severity: 'critical',
        cooldown: 300000, // 5分
        enabled: true
      },
      {
        id: 'error_rate_high',
        name: 'エラー率上昇',
        condition: (metrics) => metrics.errorRate > this.thresholds.errorRate.critical,
        severity: 'critical',
        cooldown: 180000, // 3分
        enabled: true
      },
      {
        id: 'api_slow_response',
        name: 'API応答時間遅延',
        condition: (metrics) => metrics.averageApiTime > this.thresholds.apiResponseTime.warning,
        severity: 'warning',
        cooldown: 600000, // 10分
        enabled: true
      },
      {
        id: 'cls_degradation',
        name: 'レイアウトシフト増加',
        condition: (metrics) => metrics.cls > this.thresholds.cls.warning,
        severity: 'warning',
        cooldown: 900000, // 15分
        enabled: true
      }
    ]
  }
  
  /**
   * 監視の開始
   */
  startMonitoring() {
    // 定期的にメトリクスをチェック
    setInterval(() => {
      this.checkAlerts()
    }, 30000) // 30秒間隔
  }
  
  /**
   * アラートチェック
   */
  async checkAlerts() {
    try {
      const currentMetrics = await this.gatherCurrentMetrics()
      
      for (const rule of this.alertRules.value) {
        if (!rule.enabled) continue
        
        const shouldAlert = rule.condition(currentMetrics)
        
        if (shouldAlert && this.shouldTriggerAlert(rule)) {
          await this.triggerAlert(rule, currentMetrics)
        }
      }
    } catch (error) {
      console.error('アラートチェックエラー:', error)
    }
  }
  
  /**
   * 現在のメトリクス収集
   * @returns {Promise<Object>}
   */
  async gatherCurrentMetrics() {
    try {
      const response = await fetch('/api/metrics/current')
      return await response.json()
    } catch (error) {
      console.error('メトリクス取得エラー:', error)
      return {}
    }
  }
  
  /**
   * アラートトリガー判定
   * @param {Object} rule
   * @returns {boolean}
   */
  shouldTriggerAlert(rule) {
    const lastAlert = this.alerts.value
      .filter(alert => alert.ruleId === rule.id)
      .sort((a, b) => b.timestamp - a.timestamp)[0]
    
    if (!lastAlert) return true
    
    // クールダウン期間をチェック
    return Date.now() - lastAlert.timestamp > rule.cooldown
  }
  
  /**
   * アラートトリガー
   * @param {Object} rule
   * @param {Object} metrics
   */
  async triggerAlert(rule, metrics) {
    const alert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ruleId: rule.id,
      name: rule.name,
      severity: rule.severity,
      metrics,
      timestamp: Date.now(),
      status: 'active',
      acknowledged: false
    }
    
    this.alerts.value.push(alert)
    
    // アラート送信
    await this.sendAlert(alert)
    
    // 重要度に応じて追加アクション
    if (rule.severity === 'critical') {
      await this.handleCriticalAlert(alert)
    }
  }
  
  /**
   * アラート送信
   * @param {Object} alert
   */
  async sendAlert(alert) {
    try {
      // バックエンドにアラートを送信
      await fetch('/api/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(alert)
      })
      
      // ブラウザ通知
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(`${alert.severity.toUpperCase()}: ${alert.name}`, {
          body: `パフォーマンス問題が検出されました`,
          icon: '/icons/alert.png'
        })
      }
      
    } catch (error) {
      console.error('アラート送信エラー:', error)
    }
  }
  
  /**
   * 重要アラートの処理
   * @param {Object} alert
   */
  async handleCriticalAlert(alert) {
    try {
      // Slack/Teams/Discord等への即座通知
      await fetch('/api/alerts/critical', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          alert,
          urgency: 'immediate',
          channel: '#alerts'
        })
      })
      
      // 自動診断の実行
      await this.runAutoDiagnostics(alert)
      
    } catch (error) {
      console.error('重要アラート処理エラー:', error)
    }
  }
  
  /**
   * 自動診断の実行
   * @param {Object} alert
   */
  async runAutoDiagnostics(alert) {
    const diagnostics = {
      timestamp: Date.now(),
      alertId: alert.id,
      browserInfo: {
        userAgent: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        },
        connection: navigator.connection ? {
          effectiveType: navigator.connection.effectiveType,
          downlink: navigator.connection.downlink,
          rtt: navigator.connection.rtt
        } : null
      },
      performanceEntries: performance.getEntriesByType('navigation'),
      memoryInfo: performance.memory ? {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
      } : null,
      resourceTimings: performance.getEntriesByType('resource').slice(-20),
      console: this.getRecentConsoleEvents()
    }
    
    try {
      await fetch('/api/diagnostics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(diagnostics)
      })
    } catch (error) {
      console.error('診断データ送信エラー:', error)
    }
  }
  
  /**
   * 最近のコンソールイベント取得
   * @returns {Array}
   */
  getRecentConsoleEvents() {
    // 実際の実装では、console.log等を監視して記録
    return []
  }
  
  /**
   * アラート承認
   * @param {string} alertId
   */
  async acknowledgeAlert(alertId) {
    const alert = this.alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.acknowledged = true
      alert.acknowledgedAt = Date.now()
      
      try {
        await fetch(`/api/alerts/${alertId}/acknowledge`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
      } catch (error) {
        console.error('アラート承認エラー:', error)
      }
    }
  }
  
  /**
   * アラート解決
   * @param {string} alertId
   */
  async resolveAlert(alertId) {
    const alert = this.alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.status = 'resolved'
      alert.resolvedAt = Date.now()
      
      try {
        await fetch(`/api/alerts/${alertId}/resolve`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
      } catch (error) {
        console.error('アラート解決エラー:', error)
      }
    }
  }
  
  /**
   * アクティブアラート取得
   */
  get activeAlerts() {
    return computed(() => 
      this.alerts.value
        .filter(alert => alert.status === 'active')
        .sort((a, b) => {
          // 重要度順でソート
          const severityOrder = { critical: 3, warning: 2, info: 1 }
          return severityOrder[b.severity] - severityOrder[a.severity]
        })
    )
  }
  
  /**
   * アラート統計
   */
  get alertStats() {
    return computed(() => {
      const total = this.alerts.value.length
      const active = this.activeAlerts.value.length
      const critical = this.alerts.value.filter(a => a.severity === 'critical').length
      const acknowledged = this.alerts.value.filter(a => a.acknowledged).length
      
      return {
        total,
        active,
        critical,
        acknowledged,
        acknowledgmentRate: total > 0 ? (acknowledged / total) * 100 : 0
      }
    })
  }
}

// グローバルアラートシステムインスタンス
export const alertSystem = new AlertSystem()
```

## 6. ダッシュボード

### 6.1 リアルタイムダッシュボード
```vue
<!-- components/monitoring/PerformanceDashboard.vue -->
<template>
  <div class="performance-dashboard">
    <!-- ヘッダー -->
    <div class="dashboard-header mb-6">
      <h1 class="text-3xl font-bold text-gray-900">パフォーマンス監視ダッシュボード</h1>
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <div :class="connectionStatusClass" class="w-3 h-3 rounded-full"></div>
          <span class="text-sm text-gray-600">{{ connectionStatus }}</span>
        </div>
        <button
          @click="refreshData"
          :disabled="isRefreshing"
          class="btn btn-sm btn-outline"
        >
          <RefreshIcon :class="{ 'animate-spin': isRefreshing }" class="w-4 h-4" />
          更新
        </button>
      </div>
    </div>
    
    <!-- アラート状況 -->
    <AlertPanel
      v-if="activeAlerts.length > 0"
      :alerts="activeAlerts"
      @acknowledge="handleAcknowledge"
      @resolve="handleResolve"
      class="mb-6"
    />
    
    <!-- Core Web Vitals -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <MetricCard
        title="LCP (Largest Contentful Paint)"
        :value="metrics.lcp"
        unit="ms"
        :threshold="{ good: 2500, poor: 4000 }"
        :trend="trends.lcp"
      />
      <MetricCard
        title="FID (First Input Delay)"
        :value="metrics.fid"
        unit="ms"
        :threshold="{ good: 100, poor: 300 }"
        :trend="trends.fid"
      />
      <MetricCard
        title="CLS (Cumulative Layout Shift)"
        :value="metrics.cls"
        unit=""
        :threshold="{ good: 0.1, poor: 0.25 }"
        :trend="trends.cls"
      />
    </div>
    
    <!-- パフォーマンス詳細 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- レスポンス時間グラフ -->
      <div class="card bg-white shadow-lg">
        <div class="card-body">
          <h3 class="card-title">APIレスポンス時間</h3>
          <LineChart
            :data="apiResponseData"
            :options="chartOptions"
            height="300"
          />
        </div>
      </div>
      
      <!-- エラー率グラフ -->
      <div class="card bg-white shadow-lg">
        <div class="card-body">
          <h3 class="card-title">エラー率</h3>
          <AreaChart
            :data="errorRateData"
            :options="chartOptions"
            height="300"
          />
        </div>
      </div>
    </div>
    
    <!-- ユーザー体験指標 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div class="card bg-white shadow-lg">
        <div class="card-body">
          <h3 class="card-title">アクティブユーザー</h3>
          <div class="text-3xl font-bold text-primary">{{ userStats.active }}</div>
          <div class="text-sm text-gray-600">
            過去24時間: {{ userStats.daily }}
          </div>
        </div>
      </div>
      
      <div class="card bg-white shadow-lg">
        <div class="card-body">
          <h3 class="card-title">平均セッション時間</h3>
          <div class="text-3xl font-bold text-success">{{ formatDuration(userStats.avgSession) }}</div>
          <div class="text-sm text-gray-600">
            直帰率: {{ userStats.bounceRate }}%
          </div>
        </div>
      </div>
      
      <div class="card bg-white shadow-lg">
        <div class="card-body">
          <h3 class="card-title">ページビュー</h3>
          <div class="text-3xl font-bold text-info">{{ userStats.pageViews }}</div>
          <div class="text-sm text-gray-600">
            前日比: {{ userStats.pageViewsChange > 0 ? '+' : '' }}{{ userStats.pageViewsChange }}%
          </div>
        </div>
      </div>
    </div>
    
    <!-- 詳細テーブル -->
    <div class="card bg-white shadow-lg">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h3 class="card-title">ページ別パフォーマンス</h3>
          <div class="flex space-x-2">
            <select v-model="selectedTimeRange" class="select select-sm select-bordered">
              <option value="1h">過去1時間</option>
              <option value="24h">過去24時間</option>
              <option value="7d">過去7日間</option>
              <option value="30d">過去30日間</option>
            </select>
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="table table-zebra w-full">
            <thead>
              <tr>
                <th>ページ</th>
                <th>PV</th>
                <th>平均LCP</th>
                <th>エラー率</th>
                <th>直帰率</th>
                <th>状態</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in pageMetrics" :key="page.url">
                <td class="font-medium">{{ page.title }}</td>
                <td>{{ page.pageViews.toLocaleString() }}</td>
                <td>
                  <span :class="getPerformanceClass(page.avgLcp)">
                    {{ page.avgLcp }}ms
                  </span>
                </td>
                <td>
                  <span :class="getErrorRateClass(page.errorRate)">
                    {{ page.errorRate }}%
                  </span>
                </td>
                <td>{{ page.bounceRate }}%</td>
                <td>
                  <div :class="getStatusClass(page.status)" class="badge badge-sm">
                    {{ page.status }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePerformanceMonitoring } from '@/composables/usePerformanceMonitoring'
import { alertSystem } from '@/services/monitoring/alertSystem'
import AlertPanel from './AlertPanel.vue'
import MetricCard from './MetricCard.vue'
import LineChart from './charts/LineChart.vue'
import AreaChart from './charts/AreaChart.vue'
import RefreshIcon from '@/components/icons/RefreshIcon.vue'

// 状態
const isRefreshing = ref(false)
const selectedTimeRange = ref('24h')
const refreshInterval = ref(null)

// パフォーマンス監視
const { metrics } = usePerformanceMonitoring()

// データ
const trends = ref({
  lcp: { direction: 'up', percentage: 5.2 },
  fid: { direction: 'down', percentage: -2.1 },
  cls: { direction: 'stable', percentage: 0.1 }
})

const userStats = ref({
  active: 1247,
  daily: 8934,
  avgSession: 342000, // ミリ秒
  bounceRate: 24.5,
  pageViews: 15678,
  pageViewsChange: 12.3
})

const apiResponseData = ref({
  labels: [],
  datasets: [{
    label: '平均レスポンス時間',
    data: [],
    borderColor: '#3B82F6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)'
  }]
})

const errorRateData = ref({
  labels: [],
  datasets: [{
    label: 'エラー率',
    data: [],
    borderColor: '#EF4444',
    backgroundColor: 'rgba(239, 68, 68, 0.1)'
  }]
})

const pageMetrics = ref([])

// 計算プロパティ
const activeAlerts = computed(() => alertSystem.activeAlerts.value)

const connectionStatus = computed(() => {
  return navigator.onLine ? '接続中' : '切断'
})

const connectionStatusClass = computed(() => {
  return navigator.onLine ? 'bg-green-500' : 'bg-red-500'
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// メソッド
const refreshData = async () => {
  isRefreshing.value = true
  
  try {
    await Promise.all([
      fetchPerformanceData(),
      fetchUserStats(),
      fetchPageMetrics()
    ])
  } catch (error) {
    console.error('データ更新エラー:', error)
  } finally {
    isRefreshing.value = false
  }
}

const fetchPerformanceData = async () => {
  try {
    const response = await fetch(`/api/metrics/performance?range=${selectedTimeRange.value}`)
    const data = await response.json()
    
    apiResponseData.value = data.apiResponse
    errorRateData.value = data.errorRate
  } catch (error) {
    console.error('パフォーマンスデータ取得エラー:', error)
  }
}

const fetchUserStats = async () => {
  try {
    const response = await fetch(`/api/analytics/users?range=${selectedTimeRange.value}`)
    const data = await response.json()
    
    userStats.value = data
  } catch (error) {
    console.error('ユーザー統計取得エラー:', error)
  }
}

const fetchPageMetrics = async () => {
  try {
    const response = await fetch(`/api/metrics/pages?range=${selectedTimeRange.value}`)
    const data = await response.json()
    
    pageMetrics.value = data
  } catch (error) {
    console.error('ページメトリクス取得エラー:', error)
  }
}

const formatDuration = (milliseconds) => {
  const minutes = Math.floor(milliseconds / 60000)
  const seconds = Math.floor((milliseconds % 60000) / 1000)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

const getPerformanceClass = (lcp) => {
  if (lcp <= 2500) return 'text-green-600'
  if (lcp <= 4000) return 'text-yellow-600'
  return 'text-red-600'
}

const getErrorRateClass = (rate) => {
  if (rate <= 1) return 'text-green-600'
  if (rate <= 5) return 'text-yellow-600'
  return 'text-red-600'
}

const getStatusClass = (status) => {
  const classes = {
    good: 'badge-success',
    warning: 'badge-warning',
    critical: 'badge-error'
  }
  return classes[status] || 'badge-ghost'
}

const handleAcknowledge = (alertId) => {
  alertSystem.acknowledgeAlert(alertId)
}

const handleResolve = (alertId) => {
  alertSystem.resolveAlert(alertId)
}

// ライフサイクル
onMounted(() => {
  refreshData()
  
  // 30秒ごとに自動更新
  refreshInterval.value = setInterval(refreshData, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.performance-dashboard {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 2rem;
}

.card {
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}

.table th {
  background-color: #f8fafc;
  font-weight: 600;
}
</style>
```

## まとめ

このパフォーマンス監視設計書により、Vue.js + Supabaseアプリケーションの包括的なパフォーマンス監視システムを構築できます。主要な監視要素：

1. **フロントエンド監視**: Core Web Vitals、エラートラッキング、カスタムメトリクス
2. **ユーザー体験監視**: 行動トラッキング、エンゲージメント測定、セッション分析
3. **バックエンド監視**: API監視、データベースパフォーマンス、ネットワーク状況
4. **アラートシステム**: 自動アラート、エスカレーション、診断機能
5. **ダッシュボード**: リアルタイム可視化、トレンド分析、詳細レポート

これらの監視システムにより、問題の早期発見、パフォーマンス劣化の防止、継続的な改善を実現できます。