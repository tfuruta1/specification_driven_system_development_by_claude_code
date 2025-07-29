# セキュリティ設計書

## 概要

このドキュメントは、Vue.js + Supabaseアプリケーションにおけるセキュリティ設計方針を定義します。認証・認可の仕組み、入力値検証、ファイルアップロードの制限など、セキュリティホールを作らないための包括的な指針を提供します。

## 1. セキュリティアーキテクチャ

### 1.1 多層防御の原則
```javascript
// セキュリティレイヤー構成
const securityLayers = {
  frontend: {
    validation: "クライアントサイド検証",
    sanitization: "入力値のサニタイズ",
    authentication: "認証状態管理"
  },
  api: {
    authentication: "JWT/セッショントークン検証",
    authorization: "RLS (Row Level Security)",
    validation: "サーバーサイド検証"
  },
  database: {
    policies: "Supabase RLSポリシー",
    encryption: "保存時暗号化",
    backup: "自動バックアップ"
  },
  infrastructure: {
    https: "SSL/TLS通信",
    firewall: "WAF設定",
    monitoring: "セキュリティ監視"
  }
}
```

### 1.2 ゼロトラストアーキテクチャ
- すべてのリクエストを検証
- 最小権限の原則
- セッション管理の厳格化
- 継続的な監視とログ記録

## 2. 認証・認可システム

### 2.1 認証フロー設計
```javascript
// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/lib/supabase'

/**
 * 認証ストア - セキュアな認証状態管理
 */
export const useAuthStore = defineStore('auth', () => {
  // 状態
  const user = ref(null)
  const session = ref(null)
  const isLoading = ref(true)
  
  // 計算プロパティ
  const isAuthenticated = computed(() => !!session.value)
  const userRole = computed(() => user.value?.app_metadata?.role || 'user')
  
  /**
   * セキュアなログイン処理
   * @param {Object} credentials
   * @param {string} credentials.email
   * @param {string} credentials.password
   */
  const login = async ({ email, password }) => {
    try {
      // レート制限チェック
      const canAttempt = await checkRateLimit(email)
      if (!canAttempt) {
        throw new Error('ログイン試行回数が上限に達しました。しばらくお待ちください。')
      }
      
      // Supabase認証
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.toLowerCase().trim(),
        password
      })
      
      if (error) {
        await recordFailedAttempt(email)
        throw error
      }
      
      // セッション確立
      session.value = data.session
      user.value = data.user
      
      // セキュリティヘッダーの設定
      setSecurityHeaders()
      
      // ログイン成功の記録
      await recordSuccessfulLogin(user.value.id)
      
    } catch (error) {
      console.error('ログインエラー:', error)
      throw error
    }
  }
  
  /**
   * セキュアなログアウト処理
   */
  const logout = async () => {
    try {
      // サーバーサイドでセッション無効化
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      
      // ローカルステートのクリア
      user.value = null
      session.value = null
      
      // セキュリティ関連のストレージクリア
      clearSecurityStorage()
      
    } catch (error) {
      console.error('ログアウトエラー:', error)
      // エラーでも強制的にクリア
      user.value = null
      session.value = null
    }
  }
  
  /**
   * セッションの検証と更新
   */
  const validateSession = async () => {
    try {
      const { data: { session: currentSession } } = await supabase.auth.getSession()
      
      if (!currentSession) {
        throw new Error('セッションが無効です')
      }
      
      // セッションの有効期限チェック
      const expiresAt = new Date(currentSession.expires_at * 1000)
      const now = new Date()
      
      if (expiresAt <= now) {
        throw new Error('セッションの有効期限が切れています')
      }
      
      // セッションリフレッシュが必要な場合
      const refreshThreshold = new Date(now.getTime() + 5 * 60 * 1000) // 5分前
      if (expiresAt <= refreshThreshold) {
        await refreshSession()
      }
      
      session.value = currentSession
      user.value = currentSession.user
      
    } catch (error) {
      await logout()
      throw error
    }
  }
  
  /**
   * レート制限チェック
   * @param {string} email
   * @returns {Promise<boolean>}
   */
  const checkRateLimit = async (email) => {
    const key = `login_attempts_${email}`
    const attempts = JSON.parse(localStorage.getItem(key) || '[]')
    
    // 直近1時間の試行をフィルタ
    const recentAttempts = attempts.filter(timestamp => {
      const hourAgo = Date.now() - 60 * 60 * 1000
      return timestamp > hourAgo
    })
    
    // 1時間に5回まで
    if (recentAttempts.length >= 5) {
      return false
    }
    
    return true
  }
  
  /**
   * 失敗したログイン試行を記録
   * @param {string} email
   */
  const recordFailedAttempt = async (email) => {
    const key = `login_attempts_${email}`
    const attempts = JSON.parse(localStorage.getItem(key) || '[]')
    attempts.push(Date.now())
    
    // 直近1時間のみ保持
    const hourAgo = Date.now() - 60 * 60 * 1000
    const recentAttempts = attempts.filter(t => t > hourAgo)
    
    localStorage.setItem(key, JSON.stringify(recentAttempts))
  }
  
  return {
    user,
    session,
    isLoading,
    isAuthenticated,
    userRole,
    login,
    logout,
    validateSession
  }
})
```

### 2.2 認可（権限管理）システム
```javascript
// composables/usePermissions.js
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * 権限管理Composable
 */
export function usePermissions() {
  const authStore = useAuthStore()
  
  // ロール定義
  const ROLES = {
    ADMIN: 'admin',
    MODERATOR: 'moderator',
    USER: 'user',
    GUEST: 'guest'
  }
  
  // 権限定義
  const PERMISSIONS = {
    // ユーザー管理
    USER_CREATE: ['admin'],
    USER_READ: ['admin', 'moderator', 'user'],
    USER_UPDATE: ['admin', 'moderator'],
    USER_DELETE: ['admin'],
    
    // コンテンツ管理
    CONTENT_CREATE: ['admin', 'moderator', 'user'],
    CONTENT_READ: ['admin', 'moderator', 'user', 'guest'],
    CONTENT_UPDATE: ['admin', 'moderator'],
    CONTENT_DELETE: ['admin'],
    
    // 設定管理
    SETTINGS_READ: ['admin', 'moderator', 'user'],
    SETTINGS_UPDATE: ['admin']
  }
  
  /**
   * 現在のユーザーロール
   */
  const currentRole = computed(() => {
    return authStore.userRole || ROLES.GUEST
  })
  
  /**
   * 権限チェック
   * @param {string} permission - チェックする権限
   * @returns {boolean}
   */
  const hasPermission = (permission) => {
    const allowedRoles = PERMISSIONS[permission] || []
    return allowedRoles.includes(currentRole.value)
  }
  
  /**
   * 複数権限のANDチェック
   * @param {string[]} permissions
   * @returns {boolean}
   */
  const hasAllPermissions = (permissions) => {
    return permissions.every(p => hasPermission(p))
  }
  
  /**
   * 複数権限のORチェック
   * @param {string[]} permissions
   * @returns {boolean}
   */
  const hasAnyPermission = (permissions) => {
    return permissions.some(p => hasPermission(p))
  }
  
  /**
   * リソース所有者チェック
   * @param {string} resourceOwnerId
   * @returns {boolean}
   */
  const isResourceOwner = (resourceOwnerId) => {
    return authStore.user?.id === resourceOwnerId
  }
  
  /**
   * アクセス可能性チェック（所有者または権限保持者）
   * @param {string} permission
   * @param {string} resourceOwnerId
   * @returns {boolean}
   */
  const canAccess = (permission, resourceOwnerId) => {
    return hasPermission(permission) || isResourceOwner(resourceOwnerId)
  }
  
  return {
    ROLES,
    PERMISSIONS,
    currentRole,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    isResourceOwner,
    canAccess
  }
}
```

### 2.3 ルートガード実装
```javascript
// router/guards/auth.guard.js
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'

/**
 * 認証ガード
 */
export const requireAuth = async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    // セッション検証
    await authStore.validateSession()
    
    if (!authStore.isAuthenticated) {
      return next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
    }
    
    next()
  } catch (error) {
    console.error('認証エラー:', error)
    next({ name: 'login' })
  }
}

/**
 * 権限ガード
 * @param {string[]} requiredPermissions
 */
export const requirePermissions = (requiredPermissions) => {
  return async (to, from, next) => {
    const authStore = useAuthStore()
    const { hasAllPermissions } = usePermissions()
    
    // 認証チェック
    if (!authStore.isAuthenticated) {
      return next({ name: 'login' })
    }
    
    // 権限チェック
    if (!hasAllPermissions(requiredPermissions)) {
      return next({ name: 'forbidden' })
    }
    
    next()
  }
}

/**
 * ゲストガード（認証済みユーザーのアクセスを防ぐ）
 */
export const requireGuest = (to, from, next) => {
  const authStore = useAuthStore()
  
  if (authStore.isAuthenticated) {
    return next({ name: 'dashboard' })
  }
  
  next()
}
```

## 3. 入力値検証とサニタイゼーション

### 3.1 バリデーションスキーマ
```javascript
// utils/validation/schemas.js
import { z } from 'zod'

/**
 * 共通バリデーションルール
 */
export const commonValidations = {
  // メールアドレス
  email: z.string()
    .trim()
    .toLowerCase()
    .email('有効なメールアドレスを入力してください')
    .max(255, 'メールアドレスは255文字以内で入力してください'),
  
  // パスワード
  password: z.string()
    .min(8, 'パスワードは8文字以上で入力してください')
    .max(72, 'パスワードは72文字以内で入力してください')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'パスワードは大文字・小文字・数字・特殊文字を含む必要があります'
    ),
  
  // ユーザー名
  username: z.string()
    .trim()
    .min(3, 'ユーザー名は3文字以上で入力してください')
    .max(30, 'ユーザー名は30文字以内で入力してください')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'ユーザー名は英数字、ハイフン、アンダースコアのみ使用できます'
    ),
  
  // 表示名
  displayName: z.string()
    .trim()
    .min(1, '表示名を入力してください')
    .max(50, '表示名は50文字以内で入力してください')
    .regex(
      /^[^<>'"&]+$/,
      '表示名に特殊文字は使用できません'
    ),
  
  // URL
  url: z.string()
    .trim()
    .url('有効なURLを入力してください')
    .regex(
      /^https:\/\//,
      'HTTPSプロトコルのURLのみ許可されています'
    ),
  
  // 電話番号
  phoneNumber: z.string()
    .trim()
    .regex(
      /^[0-9+\-\s()]+$/,
      '有効な電話番号を入力してください'
    )
    .min(10, '電話番号は10文字以上で入力してください')
    .max(20, '電話番号は20文字以内で入力してください')
}

/**
 * ユーザー登録スキーマ
 */
export const registerSchema = z.object({
  email: commonValidations.email,
  password: commonValidations.password,
  confirmPassword: z.string(),
  displayName: commonValidations.displayName,
  agreeToTerms: z.boolean().refine(val => val === true, {
    message: '利用規約に同意する必要があります'
  })
}).refine(data => data.password === data.confirmPassword, {
  message: 'パスワードが一致しません',
  path: ['confirmPassword']
})

/**
 * プロフィール更新スキーマ
 */
export const profileUpdateSchema = z.object({
  displayName: commonValidations.displayName,
  bio: z.string()
    .max(500, '自己紹介は500文字以内で入力してください')
    .optional(),
  website: commonValidations.url.optional(),
  phoneNumber: commonValidations.phoneNumber.optional()
})
```

### 3.2 入力値サニタイゼーション
```javascript
// utils/sanitization.js
import DOMPurify from 'dompurify'

/**
 * XSS対策用サニタイゼーション
 */
export const sanitizers = {
  /**
   * HTMLサニタイズ
   * @param {string} html
   * @param {Object} options
   * @returns {string}
   */
  html: (html, options = {}) => {
    const defaultConfig = {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
      ALLOWED_ATTR: ['href', 'target', 'rel'],
      ALLOW_DATA_ATTR: false
    }
    
    const config = { ...defaultConfig, ...options }
    return DOMPurify.sanitize(html, config)
  },
  
  /**
   * SQLインジェクション対策
   * @param {string} input
   * @returns {string}
   */
  sql: (input) => {
    if (typeof input !== 'string') return input
    
    // Supabaseは内部でパラメータ化クエリを使用するため、
    // 基本的なエスケープのみ実施
    return input
      .replace(/'/g, "''")
      .replace(/;/g, '')
      .replace(/--/g, '')
      .replace(/\/\*/g, '')
      .replace(/\*\//g, '')
  },
  
  /**
   * ファイル名サニタイズ
   * @param {string} filename
   * @returns {string}
   */
  filename: (filename) => {
    return filename
      .replace(/[^a-zA-Z0-9._-]/g, '_')
      .replace(/\.{2,}/g, '.')
      .substring(0, 255)
  },
  
  /**
   * JSONサニタイズ
   * @param {*} data
   * @returns {*}
   */
  json: (data) => {
    try {
      // 循環参照を除去
      const seen = new WeakSet()
      return JSON.parse(JSON.stringify(data, (key, value) => {
        if (typeof value === 'object' && value !== null) {
          if (seen.has(value)) {
            return undefined
          }
          seen.add(value)
        }
        return value
      }))
    } catch {
      return null
    }
  },
  
  /**
   * URLパラメータサニタイズ
   * @param {string} param
   * @returns {string}
   */
  urlParam: (param) => {
    return encodeURIComponent(param)
      .replace(/[!'()*]/g, c => `%${c.charCodeAt(0).toString(16)}`)
  }
}

/**
 * フォームデータの一括サニタイズ
 * @param {Object} formData
 * @param {Object} rules
 * @returns {Object}
 */
export function sanitizeFormData(formData, rules = {}) {
  const sanitized = {}
  
  for (const [key, value] of Object.entries(formData)) {
    const rule = rules[key] || 'text'
    
    switch (rule) {
      case 'html':
        sanitized[key] = sanitizers.html(value)
        break
      case 'sql':
        sanitized[key] = sanitizers.sql(value)
        break
      case 'filename':
        sanitized[key] = sanitizers.filename(value)
        break
      case 'json':
        sanitized[key] = sanitizers.json(value)
        break
      case 'url':
        sanitized[key] = sanitizers.urlParam(value)
        break
      default:
        // デフォルトはテキストとして扱う
        sanitized[key] = String(value).trim()
    }
  }
  
  return sanitized
}
```

## 4. ファイルアップロードセキュリティ

### 4.1 ファイルアップロード制限
```javascript
// utils/upload/restrictions.js

/**
 * ファイルアップロード制限設定
 */
export const uploadRestrictions = {
  // 画像アップロード設定
  image: {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    allowedExtensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    maxDimensions: {
      width: 4096,
      height: 4096
    }
  },
  
  // ドキュメントアップロード設定
  document: {
    maxSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ],
    allowedExtensions: ['.pdf', '.doc', '.docx', '.txt']
  },
  
  // CSVアップロード設定
  csv: {
    maxSize: 2 * 1024 * 1024, // 2MB
    allowedTypes: ['text/csv', 'application/csv'],
    allowedExtensions: ['.csv'],
    maxRows: 10000
  }
}

/**
 * ファイル検証クラス
 */
export class FileValidator {
  /**
   * ファイルサイズ検証
   * @param {File} file
   * @param {number} maxSize
   * @returns {boolean}
   */
  static validateSize(file, maxSize) {
    return file.size <= maxSize
  }
  
  /**
   * ファイルタイプ検証（MIMEタイプ）
   * @param {File} file
   * @param {string[]} allowedTypes
   * @returns {boolean}
   */
  static validateType(file, allowedTypes) {
    return allowedTypes.includes(file.type)
  }
  
  /**
   * ファイル拡張子検証
   * @param {File} file
   * @param {string[]} allowedExtensions
   * @returns {boolean}
   */
  static validateExtension(file, allowedExtensions) {
    const extension = '.' + file.name.split('.').pop().toLowerCase()
    return allowedExtensions.includes(extension)
  }
  
  /**
   * 画像寸法検証
   * @param {File} file
   * @param {Object} maxDimensions
   * @returns {Promise<boolean>}
   */
  static async validateImageDimensions(file, maxDimensions) {
    return new Promise((resolve) => {
      const img = new Image()
      const url = URL.createObjectURL(file)
      
      img.onload = () => {
        URL.revokeObjectURL(url)
        const isValid = img.width <= maxDimensions.width && 
                       img.height <= maxDimensions.height
        resolve(isValid)
      }
      
      img.onerror = () => {
        URL.revokeObjectURL(url)
        resolve(false)
      }
      
      img.src = url
    })
  }
  
  /**
   * ファイル内容の検証（マジックナンバー）
   * @param {File} file
   * @returns {Promise<boolean>}
   */
  static async validateFileContent(file) {
    const buffer = await file.slice(0, 4).arrayBuffer()
    const bytes = new Uint8Array(buffer)
    
    // ファイルシグネチャ（マジックナンバー）の検証
    const signatures = {
      jpeg: [0xFF, 0xD8, 0xFF],
      png: [0x89, 0x50, 0x4E, 0x47],
      gif: [0x47, 0x49, 0x46],
      pdf: [0x25, 0x50, 0x44, 0x46]
    }
    
    // 拡張子から期待されるシグネチャを取得
    const extension = file.name.split('.').pop().toLowerCase()
    const expectedSignature = signatures[extension]
    
    if (!expectedSignature) {
      return true // 未知のファイルタイプは追加検証をスキップ
    }
    
    // シグネチャの比較
    return expectedSignature.every((byte, index) => bytes[index] === byte)
  }
  
  /**
   * 統合ファイル検証
   * @param {File} file
   * @param {string} uploadType
   * @returns {Promise<Object>}
   */
  static async validate(file, uploadType) {
    const restrictions = uploadRestrictions[uploadType]
    
    if (!restrictions) {
      return {
        valid: false,
        error: '不明なアップロードタイプです'
      }
    }
    
    // サイズ検証
    if (!this.validateSize(file, restrictions.maxSize)) {
      return {
        valid: false,
        error: `ファイルサイズは${restrictions.maxSize / 1024 / 1024}MB以下にしてください`
      }
    }
    
    // タイプ検証
    if (!this.validateType(file, restrictions.allowedTypes)) {
      return {
        valid: false,
        error: '許可されていないファイル形式です'
      }
    }
    
    // 拡張子検証
    if (!this.validateExtension(file, restrictions.allowedExtensions)) {
      return {
        valid: false,
        error: '許可されていない拡張子です'
      }
    }
    
    // ファイル内容検証
    const isContentValid = await this.validateFileContent(file)
    if (!isContentValid) {
      return {
        valid: false,
        error: 'ファイルの内容が不正です'
      }
    }
    
    // 画像の場合は寸法検証
    if (uploadType === 'image' && restrictions.maxDimensions) {
      const isDimensionValid = await this.validateImageDimensions(
        file,
        restrictions.maxDimensions
      )
      if (!isDimensionValid) {
        return {
          valid: false,
          error: `画像サイズは${restrictions.maxDimensions.width}x${restrictions.maxDimensions.height}以下にしてください`
        }
      }
    }
    
    return { valid: true }
  }
}
```

### 4.2 セキュアなファイルアップロード実装
```javascript
// composables/useFileUpload.js
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'
import { FileValidator } from '@/utils/upload/restrictions'
import { sanitizers } from '@/utils/sanitization'

/**
 * ファイルアップロードComposable
 */
export function useFileUpload() {
  const isUploading = ref(false)
  const uploadProgress = ref(0)
  const error = ref(null)
  
  /**
   * セキュアなファイルアップロード
   * @param {File} file
   * @param {Object} options
   * @returns {Promise<Object>}
   */
  const uploadFile = async (file, options = {}) => {
    const {
      bucket = 'uploads',
      uploadType = 'image',
      generateUniqueName = true,
      onProgress = null
    } = options
    
    isUploading.value = true
    uploadProgress.value = 0
    error.value = null
    
    try {
      // 1. ファイル検証
      const validation = await FileValidator.validate(file, uploadType)
      if (!validation.valid) {
        throw new Error(validation.error)
      }
      
      // 2. ファイル名の生成とサニタイズ
      let fileName = file.name
      if (generateUniqueName) {
        const timestamp = Date.now()
        const random = Math.random().toString(36).substring(7)
        const extension = file.name.split('.').pop()
        fileName = `${timestamp}_${random}.${extension}`
      }
      fileName = sanitizers.filename(fileName)
      
      // 3. ユーザー固有のパスを生成
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('認証が必要です')
      
      const filePath = `${user.id}/${uploadType}/${fileName}`
      
      // 4. ウイルススキャン用メタデータ
      const metadata = {
        uploadedBy: user.id,
        uploadedAt: new Date().toISOString(),
        originalName: file.name,
        fileType: file.type,
        fileSize: file.size
      }
      
      // 5. Supabaseへアップロード
      const { data, error: uploadError } = await supabase.storage
        .from(bucket)
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false,
          metadata
        })
      
      if (uploadError) throw uploadError
      
      // 6. アップロード記録の保存
      const { error: recordError } = await supabase
        .from('file_uploads')
        .insert({
          user_id: user.id,
          file_path: data.path,
          file_name: fileName,
          original_name: file.name,
          file_type: file.type,
          file_size: file.size,
          bucket_name: bucket,
          upload_type: uploadType
        })
      
      if (recordError) {
        // ロールバック: アップロードされたファイルを削除
        await supabase.storage.from(bucket).remove([data.path])
        throw recordError
      }
      
      // 7. 公開URLの生成（必要な場合）
      const { data: urlData } = supabase.storage
        .from(bucket)
        .getPublicUrl(data.path)
      
      return {
        path: data.path,
        publicUrl: urlData.publicUrl,
        metadata
      }
      
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isUploading.value = false
      uploadProgress.value = 100
    }
  }
  
  /**
   * ファイルの削除
   * @param {string} filePath
   * @param {string} bucket
   */
  const deleteFile = async (filePath, bucket = 'uploads') => {
    try {
      // 権限チェック
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('認証が必要です')
      
      // ファイル所有者の確認
      const { data: fileRecord } = await supabase
        .from('file_uploads')
        .select('user_id')
        .eq('file_path', filePath)
        .single()
      
      if (!fileRecord || fileRecord.user_id !== user.id) {
        throw new Error('ファイルを削除する権限がありません')
      }
      
      // ファイル削除
      const { error: deleteError } = await supabase.storage
        .from(bucket)
        .remove([filePath])
      
      if (deleteError) throw deleteError
      
      // レコード削除
      await supabase
        .from('file_uploads')
        .delete()
        .eq('file_path', filePath)
      
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  return {
    isUploading,
    uploadProgress,
    error,
    uploadFile,
    deleteFile
  }
}
```

## 5. CSRF対策

### 5.1 CSRFトークン管理
```javascript
// utils/security/csrf.js
import { v4 as uuidv4 } from 'uuid'

/**
 * CSRF保護ユーティリティ
 */
export class CSRFProtection {
  static TOKEN_KEY = 'csrf_token'
  static TOKEN_HEADER = 'X-CSRF-Token'
  
  /**
   * CSRFトークンの生成
   * @returns {string}
   */
  static generateToken() {
    const token = uuidv4()
    sessionStorage.setItem(this.TOKEN_KEY, token)
    return token
  }
  
  /**
   * 現在のCSRFトークンを取得
   * @returns {string}
   */
  static getToken() {
    let token = sessionStorage.getItem(this.TOKEN_KEY)
    if (!token) {
      token = this.generateToken()
    }
    return token
  }
  
  /**
   * トークンの検証
   * @param {string} token
   * @returns {boolean}
   */
  static validateToken(token) {
    const storedToken = sessionStorage.getItem(this.TOKEN_KEY)
    return storedToken && storedToken === token
  }
  
  /**
   * HTTPリクエストへのトークン追加
   * @param {Object} headers
   * @returns {Object}
   */
  static addTokenToHeaders(headers = {}) {
    return {
      ...headers,
      [this.TOKEN_HEADER]: this.getToken()
    }
  }
}

// Axiosインターセプター設定例
import axios from 'axios'

axios.interceptors.request.use(
  config => {
    // CSRFトークンを自動的に追加
    if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
      config.headers = CSRFProtection.addTokenToHeaders(config.headers)
    }
    return config
  },
  error => Promise.reject(error)
)
```

## 6. XSS対策

### 6.1 コンテンツセキュリティポリシー（CSP）
```javascript
// utils/security/csp.js

/**
 * CSPヘッダー生成
 */
export function generateCSPHeader() {
  const policies = {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      "'unsafe-inline'", // Vue.jsに必要
      "https://cdn.jsdelivr.net", // 外部CDN
      "https://*.supabase.co" // Supabase
    ],
    'style-src': [
      "'self'",
      "'unsafe-inline'", // Tailwind CSSに必要
      "https://fonts.googleapis.com"
    ],
    'img-src': [
      "'self'",
      "data:",
      "https://*.supabase.co",
      "https://avatars.githubusercontent.com"
    ],
    'font-src': [
      "'self'",
      "https://fonts.gstatic.com"
    ],
    'connect-src': [
      "'self'",
      "https://*.supabase.co",
      "wss://*.supabase.co" // WebSocket
    ],
    'frame-src': ["'none'"],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  }
  
  return Object.entries(policies)
    .map(([directive, values]) => `${directive} ${values.join(' ')}`)
    .join('; ')
}

// Vite設定での適用例
export const securityHeaders = {
  'Content-Security-Policy': generateCSPHeader(),
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
}
```

### 6.2 Vue.jsでの安全なレンダリング
```vue
<!-- components/SafeContent.vue -->
<template>
  <div class="safe-content">
    <!-- テキストコンテンツ（自動的にエスケープされる） -->
    <p>{{ userContent }}</p>
    
    <!-- HTMLコンテンツ（サニタイズ必須） -->
    <div v-html="sanitizedHtml"></div>
    
    <!-- 属性バインディング（自動的にエスケープされる） -->
    <a :href="userUrl" :title="userTitle">リンク</a>
    
    <!-- イベントハンドラー（安全） -->
    <button @click="handleClick">クリック</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { sanitizers } from '@/utils/sanitization'

const props = defineProps({
  userContent: String,
  userHtml: String,
  userUrl: String,
  userTitle: String
})

// HTMLコンテンツのサニタイズ
const sanitizedHtml = computed(() => {
  return sanitizers.html(props.userHtml)
})

// URLの検証とサニタイズ
const safeUrl = computed(() => {
  try {
    const url = new URL(props.userUrl)
    // HTTPSのみ許可
    if (url.protocol !== 'https:') {
      return '#'
    }
    return url.href
  } catch {
    return '#'
  }
})

const handleClick = () => {
  // イベントハンドラーは安全
  console.log('Clicked')
}
</script>
```

## 7. セキュリティログとモニタリング

### 7.1 セキュリティイベントログ
```javascript
// services/security/logger.js
import { supabase } from '@/lib/supabase'

/**
 * セキュリティイベントロガー
 */
export class SecurityLogger {
  static EVENTS = {
    LOGIN_SUCCESS: 'login_success',
    LOGIN_FAILURE: 'login_failure',
    LOGOUT: 'logout',
    PASSWORD_CHANGE: 'password_change',
    PERMISSION_DENIED: 'permission_denied',
    SUSPICIOUS_ACTIVITY: 'suspicious_activity',
    FILE_UPLOAD: 'file_upload',
    DATA_ACCESS: 'data_access',
    API_ERROR: 'api_error'
  }
  
  /**
   * セキュリティイベントをログに記録
   * @param {string} eventType
   * @param {Object} details
   */
  static async log(eventType, details = {}) {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      
      const logEntry = {
        event_type: eventType,
        user_id: user?.id || null,
        ip_address: await this.getClientIP(),
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        details: {
          ...details,
          url: window.location.href,
          referrer: document.referrer
        }
      }
      
      // データベースに記録
      await supabase
        .from('security_logs')
        .insert(logEntry)
      
      // 重要なイベントは即座にアラート
      if (this.isCriticalEvent(eventType)) {
        await this.sendAlert(logEntry)
      }
      
    } catch (error) {
      console.error('セキュリティログエラー:', error)
      // ログ記録の失敗は通常のフローを妨げない
    }
  }
  
  /**
   * クライアントIPの取得（プロキシ経由も考慮）
   * @returns {Promise<string>}
   */
  static async getClientIP() {
    try {
      // 実際の実装では、サーバーサイドのAPIエンドポイントから取得
      const response = await fetch('/api/client-ip')
      const data = await response.json()
      return data.ip || 'unknown'
    } catch {
      return 'unknown'
    }
  }
  
  /**
   * 重要イベントの判定
   * @param {string} eventType
   * @returns {boolean}
   */
  static isCriticalEvent(eventType) {
    const criticalEvents = [
      this.EVENTS.PERMISSION_DENIED,
      this.EVENTS.SUSPICIOUS_ACTIVITY
    ]
    return criticalEvents.includes(eventType)
  }
  
  /**
   * アラート送信
   * @param {Object} logEntry
   */
  static async sendAlert(logEntry) {
    // 実装例: Slackやメールでの通知
    console.warn('セキュリティアラート:', logEntry)
  }
}
```

## 8. セキュリティベストプラクティス

### 8.1 開発時のセキュリティチェックリスト
```javascript
/**
 * セキュリティチェックリスト
 */
export const securityChecklist = {
  authentication: [
    '強力なパスワードポリシーの実装',
    '多要素認証（MFA）のサポート',
    'セッション管理の適切な実装',
    'ログイン試行回数の制限',
    'アカウントロックアウト機能'
  ],
  
  authorization: [
    'ロールベースアクセス制御（RBAC）',
    'リソースレベルの権限チェック',
    'APIエンドポイントの保護',
    '最小権限の原則の適用'
  ],
  
  dataProtection: [
    'HTTPS通信の強制',
    '機密データの暗号化',
    'パスワードのハッシュ化（bcrypt/argon2）',
    'PIIデータの適切な管理'
  ],
  
  inputValidation: [
    'すべての入力値の検証',
    'SQLインジェクション対策',
    'XSS対策',
    'パストラバーサル対策'
  ],
  
  fileUpload: [
    'ファイルタイプの制限',
    'ファイルサイズの制限',
    'ウイルススキャン',
    'セキュアなファイル保存'
  ],
  
  errorHandling: [
    'エラーメッセージの適切な処理',
    'スタックトレースの非表示',
    'ログの適切な管理',
    'エラー時の安全なフォールバック'
  ],
  
  dependencies: [
    '定期的な依存関係の更新',
    '脆弱性スキャンの実施',
    'ライセンスチェック',
    'サプライチェーンセキュリティ'
  ],
  
  deployment: [
    '環境変数の安全な管理',
    'シークレットの暗号化',
    'セキュリティヘッダーの設定',
    'ファイアウォール設定'
  ]
}
```

### 8.2 コードレビューセキュリティガイドライン
```javascript
/**
 * セキュリティコードレビューガイド
 */
export const codeReviewGuidelines = {
  // 認証・認可
  checkAuthentication: (code) => {
    return {
      hasAuthCheck: code.includes('requireAuth'),
      hasPermissionCheck: code.includes('hasPermission'),
      hasSessionValidation: code.includes('validateSession')
    }
  },
  
  // 入力検証
  checkValidation: (code) => {
    return {
      hasInputValidation: code.includes('validate') || code.includes('schema'),
      hasSanitization: code.includes('sanitize'),
      hasEscaping: code.includes('escape')
    }
  },
  
  // セキュアなコーディング
  checkSecureCoding: (code) => {
    return {
      noHardcodedSecrets: !code.match(/api[_-]?key\s*=\s*["'][^"']+["']/i),
      noUnsafeEval: !code.includes('eval('),
      noInnerHTML: !code.includes('.innerHTML'),
      useStrictMode: code.includes("'use strict'") || code.includes('"use strict"')
    }
  }
}
```

## まとめ

このセキュリティ設計書に従うことで、Vue.js + Supabaseアプリケーションにおいて堅牢なセキュリティを実現できます。重要なポイントは以下の通りです：

1. **多層防御**: フロントエンド、API、データベースの各層でセキュリティ対策を実施
2. **ゼロトラスト**: すべてのリクエストを検証し、最小権限の原則を適用
3. **継続的な監視**: セキュリティイベントのログ記録と監視
4. **定期的な更新**: 依存関係の更新とセキュリティパッチの適用

セキュリティは継続的なプロセスです。新しい脅威に対応するため、定期的にこの設計書を見直し、更新することが重要です。