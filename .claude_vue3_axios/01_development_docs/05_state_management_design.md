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
      throw new Error(`ビジネスルール "${ruleKey}" が