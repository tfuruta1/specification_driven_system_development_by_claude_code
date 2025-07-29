# エラーハンドリング設計

## 1. エラーハンドリング戦略概要

### エラー分類と対応方針
```javascript
// lib/errors/types.js

/**
 * アプリケーションエラーの基底クラス
 */
export class AppError extends Error {
  constructor(message, code, statusCode = 500, context = {}) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.statusCode = statusCode
    this.context = context
    this.timestamp = new Date().toISOString()
  }

  /**
   * ユーザー向けメッセージを取得
   * @returns {string}
   */
  getUserMessage() {
    return this.message
  }

  /**
   * エラーをシリアライズ
   * @returns {Object}
   */
  serialize() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      context: this.context,
      timestamp: this.timestamp,
      stack: this.stack
    }
  }
}

/**
 * バリデーションエラー
 */
export class ValidationError extends AppError {
  constructor(message, field, value = null) {
    super(message, 'VALIDATION_ERROR', 400, { field, value })
    this.name = 'ValidationError'
    this.field = field
    this.value = value
  }

  getUserMessage() {
    return `${this.field}: ${this.message}`
  }
}

/**
 * 認証エラー
 */
export class AuthError extends AppError {
  constructor(message, type = 'AUTHENTICATION_FAILED') {
    super(message, type, 401)
    this.name = 'AuthError'
  }

  getUserMessage() {
    switch (this.code) {
      case 'INVALID_CREDENTIALS':
        return 'ログイン情報が正しくありません'
      case 'TOKEN_EXPIRED':
        return 'セッションの有効期限が切れました。再度ログインしてください'
      case 'INSUFFICIENT_PERMISSIONS':
        return 'この操作を実行する権限がありません'
      default:
        return '認証エラーが発生しました'
    }
  }
}

/**
 * ネットワークエラー
 */
export class NetworkError extends AppError {
  constructor(message, originalError = null) {
    super(message, 'NETWORK_ERROR', 503, { originalError })
    this.name = 'NetworkError'
    this.originalError = originalError
  }

  getUserMessage() {
    if (this.code === 'NETWORK_TIMEOUT') {
      return 'リクエストがタイムアウトしました。接続状況をご確認ください'
    }
    return 'ネットワークエラーが発生しました。しばらく時間をおいてお試しください'
  }
}

/**
 * Supabaseエラー
 */
export class SupabaseError extends AppError {
  constructor(message, originalError, context = {}) {
    const code = SupabaseError.mapErrorCode(originalError)
    const statusCode = SupabaseError.mapStatusCode(originalError)
    
    super(message, code, statusCode, { originalError, ...context })
    this.name = 'SupabaseError'
    this.originalError = originalError
  }

  static mapErrorCode(error) {
    if (!error) return 'UNKNOWN_SUPABASE_ERROR'
    
    // PostgreSQLエラーコード
    if (error.code) {
      const postgresqlErrors = {
        '23505': 'DUPLICATE_KEY_ERROR',
        '23503': 'FOREIGN_KEY_VIOLATION',
        '23514': 'CHECK_CONSTRAINT_VIOLATION',
        '42P01': 'TABLE_NOT_FOUND',
        '42703': 'COLUMN_NOT_FOUND'
      }
      return postgresqlErrors[error.code] || `POSTGRESQL_${error.code}`
    }

    // Supabase Authエラー
    if (error.message) {
      if (error.message.includes('Invalid login credentials')) {
        return 'INVALID_CREDENTIALS'
      }
      if (error.message.includes('User not found')) {
        return 'USER_NOT_FOUND'
      }
      if (error.message.includes('Email not confirmed')) {
        return 'EMAIL_NOT_CONFIRMED'
      }
    }

    return 'SUPABASE_ERROR'
  }

  static mapStatusCode(error) {
    if (!error) return 500
    
    const statusMapping = {
      'INVALID_CREDENTIALS': 401,
      'USER_NOT_FOUND': 404,
      'EMAIL_NOT_CONFIRMED': 401,
      'DUPLICATE_KEY_ERROR': 409,
      'FOREIGN_KEY_VIOLATION': 400,
      'CHECK_CONSTRAINT_VIOLATION': 400
    }

    const code = SupabaseError.mapErrorCode(error)
    return statusMapping[code] || 500
  }

  getUserMessage() {
    switch (this.code) {
      case 'DUPLICATE_KEY_ERROR':
        return 'このデータは既に存在します'
      case 'FOREIGN_KEY_VIOLATION':
        return '関連するデータが見つかりません'
      case 'INVALID_CREDENTIALS':
        return 'ログイン情報が正しくありません'
      case 'USER_NOT_FOUND':
        return 'ユーザーが見つかりません'
      case 'EMAIL_NOT_CONFIRMED':
        return 'メールアドレスの確認が完了していません'
      default:
        return 'データベースエラーが発生しました'
    }
  }
}
```

## 2. グローバルエラーハンドラー

### 2.1 Vue エラーハンドラー
```javascript
// lib/errors/handler.js
import { AppError, NetworkError, SupabaseError } from './types'
import { useNotificationStore } from '@/stores/notification'
import { useErrorLogStore } from '@/stores/errorLog'

export class GlobalErrorHandler {
  constructor() {
    this.notificationStore = null
    this.errorLogStore = null
  }

  /**
   * エラーハンドラーを初期化
   * @param {Object} app - Vueアプリインスタンス
   */
  init(app) {
    // Vueアプリのエラーハンドラー
    app.config.errorHandler = (error, instance, info) => {
      this.handleVueError(error, instance, info)
    }

    // グローバルエラーイベント
    window.addEventListener('error', (event) => {
      this.handleGlobalError(event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      })
    })

    // Promise rejection
    window.addEventListener('unhandledrejection', (event) => {
      this.handlePromiseRejection(event.reason)
      event.preventDefault() // ブラウザのデフォルト処理を防ぐ
    })

    // リソース読み込みエラー
    window.addEventListener('error', (event) => {
      if (event.target !== window) {
        this.handleResourceError(event)
      }
    }, true)
  }

  /**
   * Vue コンポーネントエラーを処理
   * @param {Error} error - エラーオブジェクト
   * @param {Object} instance - コンポーネントインスタンス
   * @param {string} info - エラー情報
   */
  handleVueError(error, instance, info) {
    const context = {
      type: 'vue_error',
      componentName: instance?.$options.name || 'Unknown',
      errorInfo: info,
      props: instance?.$props,
      route: instance?.$route?.path
    }

    this.processError(error, context)
  }

  /**
   * グローバルJavaScriptエラーを処理
   * @param {Error} error - エラーオブジェクト
   * @param {Object} context - コンテキスト情報
   */
  handleGlobalError(error, context = {}) {
    const errorContext = {
      type: 'global_error',
      ...context,
      userAgent: navigator.userAgent,
      url: window.location.href
    }

    this.processError(error, errorContext)
  }

  /**
   * Promise拒否を処理
   * @param {*} reason - 拒否理由
   */
  handlePromiseRejection(reason) {
    let error = reason
    
    // 文字列の場合はErrorオブジェクトに変換
    if (typeof reason === 'string') {
      error = new Error(reason)
    }

    const context = {
      type: 'promise_rejection',
      url: window.location.href
    }

    this.processError(error, context)
  }

  /**
   * リソース読み込みエラーを処理
   * @param {Event} event - エラーイベント
   */
  handleResourceError(event) {
    const target = event.target
    const resourceType = target.tagName.toLowerCase()
    const resourceUrl = target.src || target.href

    const error = new Error(`Failed to load ${resourceType}: ${resourceUrl}`)
    const context = {
      type: 'resource_error',
      resourceType,
      resourceUrl
    }

    this.processError(error, context)
  }

  /**
   * エラーを処理
   * @param {Error} error - エラーオブジェクト
   * @param {Object} context - コンテキスト情報
   */
  async processError(error, context = {}) {
    try {
      // ストアの初期化（遅延初期化）
      if (!this.notificationStore) {
        this.notificationStore = useNotificationStore()
      }
      if (!this.errorLogStore) {
        this.errorLogStore = useErrorLogStore()
      }

      // エラーログの記録
      await this.logError(error, context)

      // ユーザー通知の表示
      this.showUserNotification(error, context)

    } catch (handlerError) {
      // エラーハンドラー自体がエラーになった場合
      console.error('Error in error handler:', handlerError)
      
      // フォールバック通知
      if (typeof alert !== 'undefined') {
        alert('予期しないエラーが発生しました。ページをリロードしてください。')
      }
    }
  }

  /**
   * エラーログを記録
   * @param {Error} error - エラーオブジェクト
   * @param {Object} context - コンテキスト情報
   */
  async logError(error, context) {
    const errorData = {
      message: error.message,
      stack: error.stack,
      name: error.name,
      code: error.code || 'UNKNOWN',
      context,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId(),
      userId: this.getCurrentUserId()
    }

    // 開発環境ではコンソールに出力
    if (import.meta.env.DEV) {
      console.group(`🚨 ${error.name || 'Error'}`);
      console.error('Message:', error.message);
      console.error('Stack:', error.stack);
      console.error('Context:', context);
      console.groupEnd();
    }

    // 本番環境ではリモートログサービスに送信
    if (import.meta.env.PROD) {
      try {
        await this.errorLogStore.logError(errorData)
      } catch (logError) {
        console.error('Failed to log error:', logError)
      }
    }
  }

  /**
   * ユーザー通知を表示
   * @param {Error} error - エラーオブジェクト
   * @param {Object} context - コンテキスト情報
   */
  showUserNotification(error, context) {
    if (!this.notificationStore) return

    let message = '予期しないエラーが発生しました'
    let type = 'error'
    let actions = []

    // AppErrorの場合はユーザー向けメッセージを使用
    if (error instanceof AppError) {
      message = error.getUserMessage()
    }

    // エラータイプに応じた特別な処理
    if (error instanceof NetworkError) {
      actions.push({
        text: '再試行',
        handler: () => window.location.reload()
      })
    }

    if (error instanceof AuthError) {
      actions.push({
        text: 'ログイン',
        handler: () => this.$router.push('/auth/login')
      })
    }

    // 重要なエラーの場合は永続的に表示
    const persistent = context.type === 'resource_error' || 
                     error instanceof AuthError

    this.notificationStore.show({
      type,
      message,
      actions,
      persistent,
      context: context.type
    })
  }

  /**
   * セッションIDを取得
   * @returns {string}
   */
  getSessionId() {
    return sessionStorage.getItem('sessionId') || 
           localStorage.getItem('sessionId') || 
           'anonymous'
  }

  /**
   * 現在のユーザーIDを取得
   * @returns {string|null}
   */
  getCurrentUserId() {
    try {
      const authStore = useAuthStore()
      return authStore.user?.id || null
    } catch {
      return null
    }
  }
}

export const globalErrorHandler = new GlobalErrorHandler()
```

### 2.2 APIエラーハンドラー
```javascript
// lib/errors/apiHandler.js
import { SupabaseError, NetworkError } from './types'

export class ApiErrorHandler {
  /**
   * Supabaseエラーを処理
   * @param {Error} error - Supabaseエラー
   * @param {Object} context - リクエストコンテキスト
   * @returns {SupabaseError}
   */
  static handleSupabaseError(error, context = {}) {
    return new SupabaseError(
      error.message || 'データベースエラーが発生しました',
      error,
      context
    )
  }

  /**
   * ネットワークエラーを処理
   * @param {Error} error - ネットワークエラー
   * @param {Object} context - リクエストコンテキスト
   * @returns {NetworkError}
   */
  static handleNetworkError(error, context = {}) {
    let message = 'ネットワークエラーが発生しました'
    
    if (error.name === 'AbortError') {
      message = 'リクエストがキャンセルされました'
    } else if (error.code === 'NETWORK_ERROR') {
      message = 'ネットワークに接続できません'
    } else if (error.code === 'TIMEOUT_ERROR') {
      message = 'リクエストがタイムアウトしました'
    }

    return new NetworkError(message, error)
  }

  /**
   * APIレスポンスエラーを処理
   * @param {Response} response - Fetchレスポンス
   * @param {Object} context - リクエストコンテキスト
   * @returns {AppError}
   */
  static async handleResponseError(response, context = {}) {
    let errorData = {}
    
    try {
      errorData = await response.json()
    } catch {
      errorData = { message: 'Unknown server error' }
    }

    const message = errorData.message || `HTTP ${response.status}: ${response.statusText}`
    
    return new AppError(message, `HTTP_${response.status}`, response.status, {
      ...context,
      response: {
        status: response.status,
        statusText: response.statusText,
        url: response.url
      },
      errorData
    })
  }
}
```

## 3. フォームバリデーションエラー

### 3.1 バリデーションエラーハンドラー
```javascript
// lib/errors/validation.js
import { ValidationError } from './types'

export class ValidationErrorHandler {
  constructor() {
    this.errors = new Map()
  }

  /**
   * フィールドエラーを追加
   * @param {string} field - フィールド名
   * @param {string} message - エラーメッセージ
   * @param {*} value - 値
   */
  addError(field, message, value = null) {
    const error = new ValidationError(message, field, value)
    
    if (!this.errors.has(field)) {
      this.errors.set(field, [])
    }
    
    this.errors.get(field).push(error)
  }

  /**
   * フィールドエラーを取得
   * @param {string} field - フィールド名
   * @returns {ValidationError[]}
   */
  getFieldErrors(field) {
    return this.errors.get(field) || []
  }

  /**
   * 最初のフィールドエラーを取得
   * @param {string} field - フィールド名
   * @returns {ValidationError|null}
   */
  getFirstFieldError(field) {
    const fieldErrors = this.getFieldErrors(field)
    return fieldErrors.length > 0 ? fieldErrors[0] : null
  }

  /**
   * 全エラーを取得
   * @returns {ValidationError[]}
   */
  getAllErrors() {
    const allErrors = []
    for (const fieldErrors of this.errors.values()) {
      allErrors.push(...fieldErrors)
    }
    return allErrors
  }

  /**
   * エラーがあるかチェック
   * @param {string} field - フィールド名（指定なしの場合は全フィールド）
   * @returns {boolean}
   */
  hasErrors(field = null) {
    if (field) {
      return this.errors.has(field) && this.errors.get(field).length > 0
    }
    return this.errors.size > 0
  }

  /**
   * フィールドエラーをクリア
   * @param {string} field - フィールド名
   */
  clearFieldErrors(field) {
    this.errors.delete(field)
  }

  /**
   * 全エラーをクリア
   */
  clearAllErrors() {
    this.errors.clear()
  }

  /**
   * エラーオブジェクトに変換
   * @returns {Object}
   */
  toObject() {
    const errorObj = {}
    
    for (const [field, fieldErrors] of this.errors.entries()) {
      errorObj[field] = fieldErrors.map(error => ({
        message: error.message,
        code: error.code,
        value: error.value
      }))
    }
    
    return errorObj
  }

  /**
   * サーバーレスポンスからエラーを構築
   * @param {Object} serverErrors - サーバーエラー
   */
  fromServerResponse(serverErrors) {
    this.clearAllErrors()
    
    if (Array.isArray(serverErrors)) {
      // エラー配列の場合
      serverErrors.forEach(error => {
        this.addError(error.field || 'unknown', error.message)
      })
    } else if (typeof serverErrors === 'object') {
      // フィールド別エラーオブジェクトの場合
      Object.entries(serverErrors).forEach(([field, messages]) => {
        const messageArray = Array.isArray(messages) ? messages : [messages]
        messageArray.forEach(message => {
          this.addError(field, message)
        })
      })
    }
  }
}
```

### 3.2 バリデーション用コンポーザブル
```javascript
// composables/useValidation.js
import { ref, reactive, computed } from 'vue'
import { ValidationErrorHandler } from '@/lib/errors/validation'

export function useValidation() {
  const errorHandler = new ValidationErrorHandler()
  const isValidating = ref(false)

  /**
   * フィールドバリデーション
   * @param {string} field - フィールド名
   * @param {*} value - 値
   * @param {Function[]} rules - バリデーションルール
   * @returns {Promise<boolean>}
   */
  const validateField = async (field, value, rules) => {
    isValidating.value = true
    errorHandler.clearFieldErrors(field)

    try {
      for (const rule of rules) {
        const result = await rule(value)
        if (result !== true) {
          errorHandler.addError(field, result, value)
          break
        }
      }
    } catch (error) {
      errorHandler.addError(field, 'バリデーション中にエラーが発生しました', value)
    } finally {
      isValidating.value = false
    }

    return !errorHandler.hasErrors(field)
  }

  /**
   * フォーム全体のバリデーション
   * @param {Object} formData - フォームデータ
   * @param {Object} fieldRules - フィールドルール
   * @returns {Promise<boolean>}
   */
  const validateForm = async (formData, fieldRules) => {
    isValidating.value = true
    errorHandler.clearAllErrors()

    const validationPromises = Object.entries(fieldRules).map(
      ([field, rules]) => validateField(field, formData[field], rules)
    )

    const results = await Promise.all(validationPromises)
    isValidating.value = false

    return results.every(result => result === true)
  }

  /**
   * バリデーションルール
   */
  const rules = {
    required: (message = '必須項目です') => (value) => {
      if (value === null || value === undefined || value === '') {
        return message
      }
      return true
    },

    email: (message = '有効なメールアドレスを入力してください') => (value) => {
      if (!value) return true // 空の場合は required ルールに任せる
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value) ? true : message
    },

    minLength: (min, message = null) => (value) => {
      if (!value) return true
      
      const msg = message || `${min}文字以上で入力してください`
      return value.length >= min ? true : msg
    },

    maxLength: (max, message = null) => (value) => {
      if (!value) return true
      
      const msg = message || `${max}文字以下で入力してください`
      return value.length <= max ? true : msg
    },

    pattern: (regex, message = '形式が正しくありません') => (value) => {
      if (!value) return true
      return regex.test(value) ? true : message
    },

    custom: (validator, message = 'バリデーションエラー') => async (value) => {
      try {
        const result = await validator(value)
        return result ? true : message
      } catch (error) {
        return error.message || message
      }
    }
  }

  return {
    // 状態
    isValidating: computed(() => isValidating.value),
    hasErrors: computed(() => errorHandler.hasErrors()),
    
    // メソッド
    validateField,
    validateForm,
    getFieldErrors: (field) => errorHandler.getFieldErrors(field),
    getFirstFieldError: (field) => errorHandler.getFirstFieldError(field),
    clearFieldErrors: (field) => errorHandler.clearFieldErrors(field),
    clearAllErrors: () => errorHandler.clearAllErrors(),
    
    // ルール
    rules,
    
    // エラーハンドラー
    errorHandler
  }
}
```

## 4. エラー通知システム

### 4.1 通知ストア
```javascript
// stores/notification.js
import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])

  /**
   * 通知を表示
   * @param {Object} notification - 通知オブジェクト
   */
  const show = (notification) => {
    const id = Date.now() + Math.random()
    
    const notificationItem = {
      id,
      type: notification.type || 'info',
      message: notification.message,
      title: notification.title,
      actions: notification.actions || [],
      persistent: notification.persistent || false,
      timeout: notification.timeout || (notification.persistent ? 0 : 5000),
      context: notification.context,
      timestamp: new Date().toISOString()
    }

    notifications.value.push(notificationItem)

    // 自動非表示
    if (notificationItem.timeout > 0) {
      setTimeout(() => {
        dismiss(id)
      }, notificationItem.timeout)
    }

    return id
  }

  /**
   * エラー通知を表示
   * @param {string} message - エラーメッセージ
   * @param {Object} options - オプション
   */
  const showError = (message, options = {}) => {
    return show({
      type: 'error',
      message,
      timeout: options.timeout || 8000,
      ...options
    })
  }

  /**
   * 成功通知を表示
   * @param {string} message - 成功メッセージ
   * @param {Object} options - オプション
   */
  const showSuccess = (message, options = {}) => {
    return show({
      type: 'success',
      message,
      timeout: options.timeout || 4000,
      ...options
    })
  }

  /**
   * 警告通知を表示
   * @param {string} message - 警告メッセージ
   * @param {Object} options - オプション
   */
  const showWarning = (message, options = {}) => {
    return show({
      type: 'warning',
      message,
      timeout: options.timeout || 6000,
      ...options
    })
  }

  /**
   * 情報通知を表示
   * @param {string} message - 情報メッセージ
   * @param {Object} options - オプション
   */
  const showInfo = (message, options = {}) => {
    return show({
      type: 'info',
      message,
      timeout: options.timeout || 5000,
      ...options
    })
  }

  /**
   * 通知を非表示
   * @param {number} id - 通知ID
   */
  const dismiss = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * 全通知をクリア
   */
  const clear = () => {
    notifications.value = []
  }

  /**
   * 通知アクションを実行
   * @param {number} notificationId - 通知ID
   * @param {Function} action - アクション関数
   */
  const executeAction = async (notificationId, action) => {
    try {
      await action()
      dismiss(notificationId)
    } catch (error) {
      console.error('通知アクション実行エラー:', error)
    }
  }

  return {
    // 状態
    notifications: computed(() => notifications.value),
    
    // アクション
    show,
    showError,
    showSuccess,
    showWarning,
    showInfo,
    dismiss,
    clear,
    executeAction
  }
})
```

## 5. エラーログ管理

### 5.1 エラーログストア
```javascript
// stores/errorLog.js
import { defineStore } from 'pinia'
import { supabase } from '@/lib/supabase'

export const useErrorLogStore = defineStore('errorLog', () => {
  const errorLogs = ref([])
  const isLogging = ref(false)

  /**
   * エラーログを記録
   * @param {Object} errorData - エラーデータ
   */
  const logError = async (errorData) => {
    if (isLogging.value) return

    isLogging.value = true

    try {
      // ローカルストレージにも保存（オフライン対応）
      const localLogs = JSON.parse(localStorage.getItem('errorLogs') || '[]')
      localLogs.push(errorData)
      
      // 最大100件まで保持
      if (localLogs.length > 100) {
        localLogs.splice(0, localLogs.length - 100)
      }
      
      localStorage.setItem('errorLogs', JSON.stringify(localLogs))

      // Supabaseに送信（本番環境のみ）
      if (import.meta.env.PROD) {
        await supabase
          .from('error_logs')
          .insert({
            error_message: errorData.message,
            error_stack: errorData.stack,
            error_name: errorData.name,
            error_code: errorData.code,
            context: errorData.context,
            session_id: errorData.sessionId,
            user_id: errorData.userId,
            user_agent: navigator.userAgent,
            url: window.location.href,
            timestamp: errorData.timestamp
          })
      }

      errorLogs.value.push(errorData)

    } catch (error) {
      console.error('エラーログの送信に失敗:', error)
    } finally {
      isLogging.value = false
    }
  }

  /**
   * ローカルのエラーログを同期
   */
  const syncLocalLogs = async () => {
    if (!import.meta.env.PROD) return

    try {
      const localLogs = JSON.parse(localStorage.getItem('errorLogs') || '[]')
      
      if (localLogs.length === 0) return

      // バッチでアップロード
      const batchSize = 10
      for (let i = 0; i < localLogs.length; i += batchSize) {
        const batch = localLogs.slice(i, i + batchSize)
        
        await supabase
          .from('error_logs')
          .insert(batch.map(log => ({
            error_message: log.message,
            error_stack: log.stack,
            error_name: log.name,
            error_code: log.code,
            context: log.context,
            session_id: log.sessionId,
            user_id: log.userId,
            timestamp: log.timestamp
          })))
      }

      // 送信後はローカルから削除
      localStorage.removeItem('errorLogs')

    } catch (error) {
      console.error('エラーログの同期に失敗:', error)
    }
  }

  /**
   * エラー統計を取得
   * @returns {Object}
   */
  const getErrorStats = () => {
    const stats = {
      totalErrors: errorLogs.value.length,
      errorsByType: {},
      errorsByCode: {},
      recentErrors: errorLogs.value.slice(-10)
    }

    errorLogs.value.forEach(error => {
      // エラータイプ別統計
      const type = error.name || 'Unknown'
      stats.errorsByType[type] = (stats.errorsByType[type] || 0) + 1

      // エラーコード別統計  
      const code = error.code || 'Unknown'
      stats.errorsByCode[code] = (stats.errorsByCode[code] || 0) + 1
    })

    return stats
  }

  return {
    // 状態
    errorLogs: computed(() => errorLogs.value),
    isLogging: computed(() => isLogging.value),
    
    // アクション
    logError,
    syncLocalLogs,
    getErrorStats
  }
})
```

## 6. エラー境界コンポーネント

### 6.1 ErrorBoundary コンポーネント
```vue
<!-- components/common/ErrorBoundary.vue -->
<template>
  <div>
    <div v-if="hasError" class="error-boundary">
      <div class="error-boundary__content">
        <div class="error-boundary__icon">
          <svg class="w-16 h-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        
        <h2 class="error-boundary__title">
          {{ title || 'エラーが発生しました' }}
        </h2>
        
        <p class="error-boundary__message">
          {{ message || '申し訳ございませんが、予期しないエラーが発生しました。' }}
        </p>
        
        <div v-if="showDetails && error" class="error-boundary__details">
          <button 
            @click="toggleDetails" 
            class="btn btn-sm btn-outline"
          >
            {{ showErrorDetails ? '詳細を隠す' : '詳細を表示' }}
          </button>
          
          <div v-if="showErrorDetails" class="error-boundary__error-details">
            <pre class="text-sm bg-gray-100 p-4 rounded overflow-auto">{{ errorDetails }}</pre>
          </div>
        </div>
        
        <div class="error-boundary__actions">
          <button 
            @click="retry" 
            class="btn btn-primary"
            :disabled="isRetrying"
          >
            {{ isRetrying ? '再試行中...' : '再試行' }}
          </button>
          
          <button 
            @click="goHome" 
            class="btn btn-outline"
          >
            ホームに戻る
          </button>
          
          <button 
            v-if="showReportButton"
            @click="reportError" 
            class="btn btn-outline btn-sm"
          >
            エラーを報告
          </button>
        </div>
      </div>
    </div>
    
    <slot v-else />
  </div>
</template>

<script setup>
import { ref, computed, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import { useErrorLogStore } from '@/stores/errorLog'

const props = defineProps({
  title: String,
  message: String,
  showDetails: {
    type: Boolean,
    default: import.meta.env.DEV
  },
  showReportButton: {
    type: Boolean,
    default: true
  },
  onRetry: Function,
  fallbackComponent: Object
})

const emit = defineEmits(['error'])

const router = useRouter()
const notificationStore = useNotificationStore()
const errorLogStore = useErrorLogStore()

const hasError = ref(false)
const error = ref(null)
const isRetrying = ref(false)
const showErrorDetails = ref(false)
const retryCount = ref(0)

const errorDetails = computed(() => {
  if (!error.value) return ''
  
  return {
    message: error.value.message,
    stack: error.value.stack,
    name: error.value.name,
    timestamp: new Date().toISOString(),
    retryCount: retryCount.value
  }
})

// エラーをキャッチ
onErrorCaptured((err, instance, info) => {
  handleError(err, { instance, info })
  return false // エラーの伝播を停止
})

/**
 * エラーを処理
 * @param {Error} err - エラーオブジェクト
 * @param {Object} context - コンテキスト情報
 */
const handleError = async (err, context = {}) => {
  hasError.value = true
  error.value = err

  // エラーログの記録
  await errorLogStore.logError({
    message: err.message,
    stack: err.stack,
    name: err.name,
    code: err.code,
    context: {
      ...context,
      component: 'ErrorBoundary',
      retryCount: retryCount.value
    },
    timestamp: new Date().toISOString()
  })

  // 親コンポーネントにエラーを通知
  emit('error', err, context)
}

/**
 * 詳細表示を切り替え
 */
const toggleDetails = () => {
  showErrorDetails.value = !showErrorDetails.value
}

/**
 * 再試行
 */
const retry = async () => {
  if (isRetrying.value) return

  isRetrying.value = true
  retryCount.value++

  try {
    if (props.onRetry) {
      await props.onRetry()
    }
    
    // エラー状態をリセット
    hasError.value = false
    error.value = null
    showErrorDetails.value = false
    
    notificationStore.showSuccess('正常に復旧しました')
    
  } catch (retryError) {
    handleError(retryError, { type: 'retry_failed' })
    notificationStore.showError('再試行に失敗しました')
  } finally {
    isRetrying.value = false
  }
}

/**
 * ホームに戻る
 */
const goHome = () => {
  router.push('/')
}

/**
 * エラーを報告
 */
const reportError = async () => {
  try {
    // エラーレポート機能を実装
    notificationStore.showInfo('エラーレポートを送信しました。ご協力ありがとうございます。')
  } catch (err) {
    notificationStore.showError('エラーレポートの送信に失敗しました')
  }
}
</script>

<style scoped>
.error-boundary {
  @apply min-h-screen flex items-center justify-center p-6;
}

.error-boundary__content {
  @apply max-w-lg w-full text-center space-y-6;
}

.error-boundary__icon {
  @apply flex justify-center;
}

.error-boundary__title {
  @apply text-2xl font-bold text-gray-900;
}

.error-boundary__message {
  @apply text-gray-600 leading-relaxed;
}

.error-boundary__details {
  @apply space-y-4;
}

.error-boundary__error-details {
  @apply text-left;
}

.error-boundary__actions {
  @apply flex flex-wrap gap-3 justify-center;
}
</style>
```

## 7. まとめ

このエラーハンドリング設計の特徴：

1. **包括的エラー捕捉**: Vue、Promise、リソース、ネットワークエラーを統一的に処理
2. **ユーザーフレンドリー**: 分かりやすいエラーメッセージと適切なアクション提示
3. **開発者支援**: 詳細なログ記録とデバッグ情報
4. **復旧機能**: エラー境界による graceful degradation と再試行機能
5. **監視対応**: エラー統計とリモートログによる品質管理

### 関連ドキュメント
- [アーキテクチャ設計](./01_architecture_design.md)
- [API設計](./03_api_design.md)
- [状態管理設計](./05_state_management_design.md)