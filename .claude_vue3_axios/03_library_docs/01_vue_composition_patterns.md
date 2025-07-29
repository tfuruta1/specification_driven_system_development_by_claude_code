# Vue Composition パターン集

実用的でプロダクション対応のVue 3 Composition APIパターンを解説します。

## 📚 目次

1. [基本的なCompositionパターン](#基本的なcompositionパターン)
2. [リアクティブ状態管理](#リアクティブ状態管理)
3. [ライフサイクル管理](#ライフサイクル管理)
4. [イベントハンドリングパターン](#イベントハンドリングパターン)
5. [Template RefとDOM操作](#template-refとdom操作)
6. [Composable設計パターン](#composable設計パターン)
7. [パフォーマンス最適化](#パフォーマンス最適化)
8. [TypeScriptでの型安全性](#typescriptでの型安全性)

## 基本的なCompositionパターン

### 基本的なComposition設定

```javascript
// composables/useCounter.js
import { ref, computed, readonly } from 'vue'

/**
 * カウンター機能を提供するComposable
 * @param {number} initialValue - 初期値
 * @returns {Object} カウンター状態とメソッド
 */
export function useCounter(initialValue = 0) {
  const count = ref(initialValue)
  
  const doubleCount = computed(() => count.value * 2)
  const isEven = computed(() => count.value % 2 === 0)
  
  /**
   * 指定された値だけカウンターを増加
   * @param {number} amount - 増加量
   */
  const increment = (amount = 1) => {
    count.value += amount
  }
  
  /**
   * 指定された値だけカウンターを減少
   * @param {number} amount - 減少量
   */
  const decrement = (amount = 1) => {
    count.value -= amount
  }
  
  /**
   * カウンターを初期値にリセット
   */
  const reset = () => {
    count.value = initialValue
  }
  
  return {
    // 状態（外部からの変更を防ぐためreadonly）
    count: readonly(count),
    doubleCount,
    isEven,
    // アクション
    increment,
    decrement,
    reset
  }
}
```

### コンポーネントでの使用例

```vue
<!-- components/CounterDisplay.vue -->
<template>
  <div class="counter-display">
    <h2>カウンター: {{ count }}</h2>
    <p>倍数: {{ doubleCount }}</p>
    <p>偶数: {{ isEven ? 'はい' : 'いいえ' }}</p>
    
    <div class="controls">
      <button @click="increment()" :disabled="loading">+</button>
      <button @click="decrement()" :disabled="loading">-</button>
      <button @click="reset()" :disabled="loading">リセット</button>
    </div>
  </div>
</template>

<script setup>
import { useCounter } from '@/composables/useCounter'
import { watch } from 'vue'

// Props
const props = defineProps({
  initialValue: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['countChanged'])

// Composables
const { count, doubleCount, isEven, increment, decrement, reset } = useCounter(props.initialValue)

// カウント変更の監視とイベント発火
watch(count, (newValue) => {
  emit('countChanged', newValue)
})

// デモ用のローディング状態
const loading = ref(false)
</script>
```

## リアクティブ状態管理

### 複雑なリアクティブ状態

```javascript
// composables/useFormState.js
import { reactive, computed, toRefs } from 'vue'

/**
 * バリデーション付きフォーム状態管理
 * @param {Object} initialData - 初期データ
 * @param {Object} validationRules - バリデーションルール
 * @returns {Object} フォーム状態とユーティリティ
 */
export function useFormState(initialData = {}, validationRules = {}) {
  const state = reactive({
    data: { ...initialData },
    errors: {},
    touched: {},
    submitting: false,
    submitted: false
  })
  
  const isValid = computed(() => {
    return Object.keys(state.errors).length === 0
  })
  
  const isDirty = computed(() => {
    return JSON.stringify(state.data) !== JSON.stringify(initialData)
  })
  
  const touchedFields = computed(() => {
    return Object.keys(state.touched).filter(key => state.touched[key])
  })
  
  /**
   * フィールド値を更新
   * @param {string} field - フィールド名
   * @param {any} value - フィールド値
   */
  const updateField = (field, value) => {
    state.data[field] = value
    state.touched[field] = true
    validateField(field)
  }
  
  /**
   * 単一フィールドのバリデーション
   * @param {string} field - フィールド名
   */
  const validateField = (field) => {
    const rules = validationRules[field]
    if (!rules) return
    
    const value = state.data[field]
    const errors = []
    
    if (rules.required && (!value || value.toString().trim() === '')) {
      errors.push(`${field}は必須です`)
    }
    
    if (rules.minLength && value && value.length < rules.minLength) {
      errors.push(`${field}は${rules.minLength}文字以上で入力してください`)
    }
    
    if (rules.maxLength && value && value.length > rules.maxLength) {
      errors.push(`${field}は${rules.maxLength}文字以下で入力してください`)
    }
    
    if (rules.pattern && value && !rules.pattern.test(value)) {
      errors.push(rules.patternMessage || `${field}の形式が正しくありません`)
    }
    
    if (rules.custom && typeof rules.custom === 'function') {
      const customError = rules.custom(value, state.data)
      if (customError) errors.push(customError)
    }
    
    if (errors.length > 0) {
      state.errors[field] = errors
    } else {
      delete state.errors[field]
    }
  }
  
  /**
   * 全フィールドのバリデーション
   */
  const validateAll = () => {
    Object.keys(validationRules).forEach(field => {
      validateField(field)
    })
  }
  
  /**
   * フォームを初期状態にリセット
   */
  const reset = () => {
    state.data = { ...initialData }
    state.errors = {}
    state.touched = {}
    state.submitting = false
    state.submitted = false
  }
  
  /**
   * フィールドを操作済みとしてマーク
   * @param {string} field - フィールド名
   */
  const touchField = (field) => {
    state.touched[field] = true
  }
  
  /**
   * フォーム送信
   * @param {Function} submitFn - 送信関数
   */
  const submit = async (submitFn) => {
    validateAll()
    
    if (!isValid.value) {
      return { success: false, errors: state.errors }
    }
    
    try {
      state.submitting = true
      const result = await submitFn(state.data)
      state.submitted = true
      return { success: true, data: result }
    } catch (error) {
    showNotification(`インポートに失敗しました: ${error.message}`, 'error')
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
}

// ライフサイクル
onMounted(() => {
  fetchUsers()
})

// フィルター変更時のページリセット
watch([searchQuery, filters], () => {
  currentPage.value = 1
}, { deep: true })
</script>
```

### 関連するコンポーザブル

```javascript
// composables/useUserManagement.js
import { ref, reactive, computed } from 'vue'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/stores/auth'

export function useUserManagement() {
  const authStore = useAuthStore()
  
  // 状態
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const stats = reactive({
    total: 0,
    active: 0,
    pending: 0,
    inactive: 0,
    totalTrend: 0,
    activeTrend: 0,
    pendingTrend: 0,
    inactiveTrend: 0
  })

  // 計算プロパティ
  const activeUsers = computed(() => 
    users.value.filter(user => user.status === 'active')
  )
  
  const pendingUsers = computed(() => 
    users.value.filter(user => user.status === 'pending')
  )

  // メソッド
  const fetchUsers = async (options = {}) => {
    loading.value = true
    error.value = null
    
    try {
      let query = supabase
        .from('users')
        .select(`
          id,
          name,
          email,
          role,
          status,
          department,
          avatar_url,
          last_login,
          created_at,
          updated_at
        `)
        .order('created_at', { ascending: false })

      // フィルター適用
      if (options.role) {
        query = query.eq('role', options.role)
      }
      
      if (options.status) {
        query = query.eq('status', options.status)
      }
      
      if (options.department) {
        query = query.eq('department', options.department)
      }

      const { data, error: fetchError, count } = await query

      if (fetchError) throw fetchError

      users.value = data || []
      
      // 統計を更新
      await updateStats()
      
    } catch (err) {
      error.value = err
      console.error('ユーザー取得エラー:', err)
    } finally {
      loading.value = false
    }
  }

  const createUser = async (userData) => {
    loading.value = true
    
    try {
      // ユーザー作成API呼び出し
      const { data, error } = await supabase.auth.admin.createUser({
        email: userData.email,
        password: userData.password,
        email_confirm: true,
        user_metadata: {
          name: userData.name,
          role: userData.role,
          department: userData.department
        }
      })

      if (error) throw error

      // プロフィール情報を追加
      const { error: profileError } = await supabase
        .from('user_profiles')
        .insert({
          user_id: data.user.id,
          name: userData.name,
          role: userData.role,
          department: userData.department,
          status: 'pending'
        })

      if (profileError) throw profileError

      // ユーザーリストを再取得
      await fetchUsers()
      
      return data.user
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (userId, updates) => {
    loading.value = true
    
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .select()
        .single()

      if (error) throw error

      // ローカル状態を更新
      const userIndex = users.value.findIndex(u => u.id === userId)
      if (userIndex !== -1) {
        users.value[userIndex] = { ...users.value[userIndex], ...data }
      }

      return data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteUser = async (userId) => {
    loading.value = true
    
    try {
      // ソフトデリート（実際は無効化）
      const { error } = await supabase
        .from('user_profiles')
        .update({ 
          status: 'deleted',
          deleted_at: new Date().toISOString()
        })
        .eq('user_id', userId)

      if (error) throw error

      // ローカル状態からユーザーを削除
      users.value = users.value.filter(u => u.id !== userId)
      
      await updateStats()
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const bulkUpdateUsers = async (userIds, updates) => {
    loading.value = true
    
    try {
      const { error } = await supabase
        .from('user_profiles')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .in('user_id', userIds)

      if (error) throw error

      // ローカル状態を更新
      userIds.forEach(userId => {
        const userIndex = users.value.findIndex(u => u.id === userId)
        if (userIndex !== -1) {
          users.value[userIndex] = { ...users.value[userIndex], ...updates }
        }
      })

      await updateStats()
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const exportUsers = async (options) => {
    try {
      let query = supabase.from('user_profiles').select('*')
      
      // フィルター適用
      if (options.filters?.role) {
        query = query.eq('role', options.filters.role)
      }
      
      const { data, error } = await query
      
      if (error) throw error

      // CSV形式でエクスポート
      const csv = convertToCSV(data)
      downloadCSV(csv, 'users-export.csv')
      
    } catch (err) {
      error.value = err
      throw err
    }
  }

  const importUsers = async (file) => {
    try {
      const csvData = await parseCSVFile(file)
      const results = { success: 0, errors: [] }
      
      for (const userData of csvData) {
        try {
          await createUser(userData)
          results.success++
        } catch (err) {
          results.errors.push({
            user: userData,
            error: err.message
          })
        }
      }
      
      return results
    } catch (err) {
      error.value = err
      throw err
    }
  }

  const updateStats = async () => {
    try {
      const { data, error } = await supabase
        .from('user_stats_view')
        .select('*')
        .single()

      if (error) throw error

      Object.assign(stats, data)
    } catch (err) {
      console.error('統計更新エラー:', err)
    }
  }

  // ヘルパー関数
  const convertToCSV = (data) => {
    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => row[header]).join(','))
    ].join('\n')
    return csvContent
  }

  const downloadCSV = (csv, filename) => {
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const parseCSVFile = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const csv = e.target.result
          const lines = csv.split('\n')
          const headers = lines[0].split(',')
          const data = lines.slice(1).map(line => {
            const values = line.split(',')
            return headers.reduce((obj, header, index) => {
              obj[header.trim()] = values[index]?.trim()
              return obj
            }, {})
          })
          resolve(data)
        } catch (err) {
          reject(err)
        }
      }
      reader.onerror = () => reject(new Error('ファイル読み込みエラー'))
      reader.readAsText(file)
    })
  }

  return {
    // 状態
    users,
    loading,
    error,
    stats,
    
    // 計算プロパティ
    activeUsers,
    pendingUsers,
    
    // メソッド
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    bulkUpdateUsers,
    exportUsers,
    importUsers,
    updateStats
  }
}
```

## ✅ 開発品質チェックリスト

### デザインとUI
- [ ] **デザイントークン**: CSS変数とデザインシステムを使用
- [ ] **レスポンシブ**: モバイルファーストで全デバイス対応
- [ ] **アクセシビリティ**: WCAG AA準拠（コントラスト、キーボード操作、スクリーンリーダー）
- [ ] **ダークモード**: テーマ切り替えが正常に動作
- [ ] **アニメーション**: 適切なトランジションとmotion設定

### Vue実装
- [ ] **TypeScript**: 適切な型定義と型安全性
- [ ] **Composition API**: コンポーザブルでロジック分離
- [ ] **リアクティビティ**: 適切なref/reactiveの使用
- [ ] **ライフサイクル**: メモリリークなく適切にクリーンアップ
- [ ] **エラーハンドリング**: エラーバウンダリとユーザーフレンドリーなメッセージ

### パフォーマンス
- [ ] **遅延ローディング**: 大きなコンポーネントとルートで適用
- [ ] **メモ化**: 重い計算処理をcomputedやmemoで最適化
- [ ] **仮想スクロール**: 1000+アイテムのリストで実装
- [ ] **バンドル最適化**: 適切なコード分割とツリーシェイキング
- [ ] **画像最適化**: 遅延読み込みと適切なフォーマット

### セキュリティ
- [ ] **認証**: 適切なトークン管理とセッション処理
- [ ] **認可**: 権限ベースのアクセス制御
- [ ] **入力検証**: フロントエンドとバックエンドでダブルチェック
- [ ] **XSS対策**: ユーザー入力の適切なサニタイズ
- [ ] **CSRF対策**: APIリクエストの適切な保護

### テスト
- [ ] **単体テスト**: コンポーネントとコンポーザブルをカバー
- [ ] **統合テスト**: ユーザーフローの主要パスをテスト
- [ ] **E2Eテスト**: クリティカルな機能をテスト
- [ ] **アクセシビリティテスト**: 自動テストツールでチェック
- [ ] **カバレッジ**: 80%以上のコードカバレッジ

### 運用
- [ ] **エラー監視**: 本番環境でのエラー追跡
- [ ] **パフォーマンス監視**: Core Web Vitalsの測定
- [ ] **ログ**: 適切なレベルでの構造化ログ
- [ ] **デプロイ**: CI/CDパイプラインでの自動化
- [ ] **ドキュメント**: コードとAPIの適切な文書化

## 🎯 ベストプラクティス集

### 1. コンポーネント設計原則

```javascript
// ✅ 良い例: 単一責任と再利用性
export default defineComponent({
  name: 'UserCard',
  props: {
    user: { type: Object, required: true },
    actions: { type: Array, default: () => [] },
    size: { type: String, default: 'md' }
  },
  emits: ['action', 'edit', 'delete'],
  setup(props, { emit }) {
    // 単一の責任: ユーザー情報の表示
    // 再利用可能: 異なるサイズとアクションに対応
    // テスタブル: プロップスとイベントが明確
  }
})

// ❌ 悪い例: 複数の責任と密結合
export default defineComponent({
  name: 'UserManagementComponent',
  setup() {
    // ユーザーデータ取得、表示、編集、削除を全て含む
    // 再利用不可能で、テストが困難
  }
})
```

### 2. 状態管理のベストプラクティス

```javascript
// ✅ 良い例: コンポーザブルによる状態分離
export function useUserData(userId) {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchUser = async () => {
    loading.value = true
    try {
      const data = await api.getUser(userId)
      user.value = data
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }

  return { user, loading, error, fetchUser }
}

// ❌ 悪い例: コンポーネント内での直接API呼び出し
export default defineComponent({
  setup() {
    const user = ref(null)
    
    // コンポーネント内で直接API呼び出し
    onMounted(async () => {
      user.value = await api.getUser(props.userId)
    })
  }
})
```

### 3. エラーハンドリングパターン

```vue
<!-- ✅ 良い例: 包括的なエラーハンドリング -->
<template>
  <ErrorBoundary @error="handleError">
    <Suspense>
      <template #default>
        <UserProfile :user-id="userId" />
      </template>
      <template #fallback>
        <UserProfileSkeleton />
      </template>
    </Suspense>
  </ErrorBoundary>
</template>

<script setup>
const handleError = (error) => {
  // エラーログ送信
  errorReporting.captureException(error)
  
  // ユーザーフレンドリーな通知
  showNotification('問題が発生しました。しばらくしてから再試行してください。', 'error')
}
</script>
```

### 4. パフォーマンス最適化パターン

```vue
<!-- ✅ 良い例: 適切な最適化 -->
<template>
  <div>
    <!-- 重いリスト: 仮想スクロール -->
    <VirtualScroller
      v-if="items.length > 100"
      :items="items"
      :item-height="60"
      v-slot="{ item }"
    >
      <UserCard :user="item" />
    </VirtualScroller>
    
    <!-- 軽いリスト: 通常のレンダリング -->
    <div v-else class="space-y-2">
      <UserCard
        v-for="item in items"
        :key="item.id"
        :user="item"
      />
    </div>
  </div>
</template>

<script setup>
// 重い計算のメモ化
const expensiveComputation = computed(() => {
  return heavyCalculation(props.data)
})

// 適切なリアクティビティ
const { data, loading } = useAsyncData(
  'users',
  () => api.getUsers(),
  { 
    server: false, // CSRで実行
    lazy: true,    // 遅延実行
    default: () => [] // デフォルト値
  }
)
</script>
```

### 5. TypeScript活用パターン

```typescript
// ✅ 良い例: 厳密な型定義
interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user' | 'guest'
  status: 'active' | 'inactive' | 'pending'
}

interface UserFormData {
  name: string
  email: string
  role: User['role']
  department?: string
}

// コンポーザブルの型定義
export function useUserForm(
  initialData?: Partial<UserFormData>
): {
  formData: Ref<UserFormData>
  errors: Ref<Record<string, string>>
  isValid: ComputedRef<boolean>
  submit: () => Promise<User>
  reset: () => void
} {
  // 実装...
}
```

### 6. テストパターン

```javascript
// ✅ 良い例: 包括的なテスト
describe('UserCard', () => {
  const defaultProps = {
    user: {
      id: '1',
      name: 'テストユーザー',
      email: 'test@example.com',
      role: 'user'
    }
  }

  it('ユーザー情報を正しく表示する', () => {
    const wrapper = mount(UserCard, { props: defaultProps })
    
    expect(wrapper.text()).toContain('テストユーザー')
    expect(wrapper.text()).toContain('test@example.com')
  })

  it('編集ボタンクリック時にイベントを発行する', async () => {
    const wrapper = mount(UserCard, { props: defaultProps })
    
    await wrapper.find('[data-testid="edit-button"]').trigger('click')
    
    expect(wrapper.emitted('edit')).toHaveLength(1)
    expect(wrapper.emitted('edit')[0][0]).toEqual(defaultProps.user)
  })

  it('ローディング状態を正しく表示する', () => {
    const wrapper = mount(UserCard, {
      props: { ...defaultProps, loading: true }
    })
    
    expect(wrapper.find('.loading').exists()).toBe(true)
  })
})
```

### 7. アクセシビリティパターン

```vue
<!-- ✅ 良い例: アクセシブルなフォーム -->
<template>
  <form @submit.prevent="handleSubmit" novalidate>
    <fieldset :disabled="loading">
      <legend class="sr-only">ユーザー情報</legend>
      
      <div class="form-control">
        <label 
          :for="nameFieldId" 
          class="label"
          :class="{ 'text-error': errors.name }"
        >
          <span class="label-text">
            ユーザー名
            <span class="text-error" aria-label="必須">*</span>
          </span>
        </label>
        <input
          :id="nameFieldId"
          v-model="formData.name"
          type="text"
          class="input input-bordered"
          :class="{ 'input-error': errors.name }"
          :aria-invalid="!!errors.name"
          :aria-describedby="errors.name ? `${nameFieldId}-error` : undefined"
          required
          autocomplete="name"
        >
        <div
          v-if="errors.name"
          :id="`${nameFieldId}-error`"
          class="label-text-alt text-error mt-1"
          role="alert"
          aria-live="polite"
        >
          {{ errors.name }}
        </div>
      </div>
    </fieldset>
    
    <div class="form-control mt-6">
      <button
        type="submit"
        class="btn btn-primary"
        :disabled="!isValid || loading"
        :aria-describedby="loading ? 'submit-status' : undefined"
      >
        <span v-if="loading" class="loading loading-spinner loading-sm mr-2"></span>
        {{ loading ? '送信中...' : '送信' }}
      </button>
      <div
        v-if="loading"
        id="submit-status"
        class="sr-only"
        aria-live="polite"
      >
        フォームを送信しています
      </div>
    </div>
  </form>
</template>

<script setup>
import { generateId } from '@/utils/accessibility'

const nameFieldId = generateId('name-field')
</script>
```

## 📊 パフォーマンス監視

### Core Web Vitals追跡

```javascript
// utils/performance.js
export function trackWebVitals() {
  // LCP (Largest Contentful Paint)
  new PerformanceObserver((list) => {
    const entries = list.getEntries()
    const lastEntry = entries[entries.length - 1]
    
    analytics.track('web_vital', {
      name: 'LCP',
      value: lastEntry.startTime,
      rating: lastEntry.startTime > 2500 ? 'poor' : 
              lastEntry.startTime > 1200 ? 'needs-improvement' : 'good'
    })
  }).observe({ entryTypes: ['largest-contentful-paint'] })

  // FID (First Input Delay)
  new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
      analytics.track('web_vital', {
        name: 'FID',
        value: entry.processingStart - entry.startTime,
        rating: entry.processingStart - entry.startTime > 100 ? 'poor' :
                entry.processingStart - entry.startTime > 25 ? 'needs-improvement' : 'good'
      })
    })
  }).observe({ entryTypes: ['first-input'] })

  // CLS (Cumulative Layout Shift)
  let clsValue = 0
  new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
      if (!entry.hadRecentInput) {
        clsValue += entry.value
      }
    })
    
    analytics.track('web_vital', {
      name: 'CLS',
      value: clsValue,
      rating: clsValue > 0.25 ? 'poor' :
              clsValue > 0.1 ? 'needs-improvement' : 'good'
    })
  }).observe({ entryTypes: ['layout-shift'] })
}
```

## 🚀 本番環境チェックリスト

### デプロイ前確認
- [ ] **環境変数**: 本番用設定に更新
- [ ] **API URL**: 本番エンドポイントに設定
- [ ] **エラー監視**: Sentry等のツール設定
- [ ] **アナリティクス**: GA4等の計測ツール設定
- [ ] **SEO**: メタタグとOGPの設定

### セキュリティ確認
- [ ] **HTTPS**: SSL証明書の設定
- [ ] **CSP**: Content Security Policyの設定
- [ ] **CORS**: 適切なオリジン制限
- [ ] **認証**: トークンの適切な保護
- [ ] **入力検証**: XSS/SQLインジェクション対策

### パフォーマンス確認
- [ ] **Lighthouse**: スコア90以上を目標
- [ ] **バンドルサイズ**: 主要チャンクが250KB以下
- [ ] **CDN**: 静的アセットの配信設定
- [ ] **キャッシュ**: 適切なキャッシュ戦略
- [ ] **圧縮**: Gzip/Brotli圧縮の有効化

## 📚 関連ドキュメント

- **[Pinia状態管理パターン](./02_pinia_store_patterns.md)** - 状態管理との統合
- **[Supabase連携パターン](./03_supabase_integration.md)** - データベース操作
- **[Vite設定ガイド](./04_vite_configuration.md)** - ビルド設定とパフォーマンス最適化

## ベストプラクティス

1. **Composable命名**: `use`プレフィックスを使用
2. **戻り値オブジェクト**: 配列ではなく名前付きプロパティを返す
3. **読み取り専用状態**: 外部から変更されるべきでない状態はreadonly
4. **クリーンアップ**: `onUnmounted`でリソースを適切にクリーンアップ
5. **エラーハンドリング**: 一貫したエラーハンドリングパターンを提供
6. **TypeScript**: より良い開発体験と型安全性のためにTypeScriptを使用
7. **テスト**: 複雑なComposableには単体テストを作成
8. **ドキュメント**: JSDocコメントでComposableを文書化) {
      return { success: false, error: error.message }
    } finally {
      state.submitting = false
    }
  }
  
  return {
    // 状態
    ...toRefs(state),
    // 計算プロパティ
    isValid,
    isDirty,
    touchedFields,
    // メソッド
    updateField,
    validateField,
    validateAll,
    reset,
    touchField,
    submit
  }
}
```

### 非同期状態管理

```javascript
// composables/useAsyncState.js
import { ref, readonly, computed } from 'vue'

/**
 * 非同期操作の状態管理
 * @param {Function} asyncFn - 実行する非同期関数
 * @param {any} initialData - 初期データ値
 * @returns {Object} 非同期状態ユーティリティ
 */
export function useAsyncState(asyncFn, initialData = null) {
  const data = ref(initialData)
  const loading = ref(false)
  const error = ref(null)
  const lastExecuted = ref(null)
  
  const isReady = computed(() => !loading.value && error.value === null)
  const hasData = computed(() => data.value !== null && data.value !== undefined)
  const isStale = computed(() => {
    if (!lastExecuted.value) return true
    return Date.now() - lastExecuted.value > 300000 // 5分
  })
  
  /**
   * 非同期関数を実行
   * @param  {...any} args - 非同期関数に渡す引数
   * @returns {Promise<any>} 非同期関数の結果
   */
  const execute = async (...args) => {
    try {
      loading.value = true
      error.value = null
      
      const result = await asyncFn(...args)
      data.value = result
      lastExecuted.value = Date.now()
      
      return result
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * データを再取得（最後の引数で再実行）
   */
  const refresh = async () => {
    if (lastArgs.value) {
      return execute(...lastArgs.value)
    }
    return execute()
  }
  
  /**
   * 状態をリセット
   */
  const reset = () => {
    data.value = initialData
    loading.value = false
    error.value = null
    lastExecuted.value = null
  }
  
  // リフレッシュ機能用に最後の引数を記録
  const lastArgs = ref(null)
  const originalExecute = execute
  const wrappedExecute = async (...args) => {
    lastArgs.value = args
    return originalExecute(...args)
  }
  
  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    isReady,
    hasData,
    isStale,
    execute: wrappedExecute,
    refresh,
    reset
  }
}
```

## ライフサイクル管理

### 高度なライフサイクルパターン

```javascript
// composables/useLifecycle.js
import { 
  onMounted, 
  onUnmounted, 
  onBeforeUnmount,
  onUpdated,
  onActivated,
  onDeactivated,
  ref
} from 'vue'

/**
 * 拡張ライフサイクル管理
 * @returns {Object} ライフサイクルユーティリティ
 */
export function useLifecycle() {
  const isMounted = ref(false)
  const isActive = ref(false)
  const mountTime = ref(null)
  const updateCount = ref(0)
  
  const cleanupTasks = []
  
  /**
   * クリーンアップタスクを登録
   * @param {Function} cleanupFn - クリーンアップ関数
   */
  const onCleanup = (cleanupFn) => {
    cleanupTasks.push(cleanupFn)
  }
  
  /**
   * クリーンアップタスクを実行
   */
  const executeCleanup = () => {
    cleanupTasks.forEach(task => {
      try {
        task()
      } catch (error) {
        console.warn('クリーンアップタスクが失敗しました:', error)
      }
    })
    cleanupTasks.length = 0
  }
  
  onMounted(() => {
    isMounted.value = true
    mountTime.value = Date.now()
  })
  
  onActivated(() => {
    isActive.value = true
  })
  
  onDeactivated(() => {
    isActive.value = false
  })
  
  onUpdated(() => {
    updateCount.value++
  })
  
  onBeforeUnmount(() => {
    executeCleanup()
  })
  
  onUnmounted(() => {
    isMounted.value = false
    isActive.value = false
  })
  
  return {
    isMounted: readonly(isMounted),
    isActive: readonly(isActive),
    mountTime: readonly(mountTime),
    updateCount: readonly(updateCount),
    onCleanup
  }
}
```

### インターバルとタイムアウト管理

```javascript
// composables/useTimer.js
import { ref, onUnmounted, computed } from 'vue'

/**
 * 自動クリーンアップ付きタイマー管理
 * @returns {Object} タイマーユーティリティ
 */
export function useTimer() {
  const activeTimers = ref(new Set())
  
  /**
   * 自動クリーンアップ付きsetTimeout
   * @param {Function} callback - コールバック関数
   * @param {number} delay - 遅延時間（ミリ秒）
   * @returns {number} タイマーID
   */
  const setTimeout = (callback, delay) => {
    const timerId = window.setTimeout(() => {
      callback()
      activeTimers.value.delete(timerId)
    }, delay)
    
    activeTimers.value.add(timerId)
    return timerId
  }
  
  /**
   * 自動クリーンアップ付きsetInterval
   * @param {Function} callback - コールバック関数
   * @param {number} delay - インターバル（ミリ秒）
   * @returns {number} タイマーID
   */
  const setInterval = (callback, delay) => {
    const timerId = window.setInterval(callback, delay)
    activeTimers.value.add(timerId)
    return timerId
  }
  
  /**
   * 特定のタイマーをクリア
   * @param {number} timerId - クリアするタイマーID
   */
  const clearTimer = (timerId) => {
    if (activeTimers.value.has(timerId)) {
      window.clearTimeout(timerId)
      window.clearInterval(timerId)
      activeTimers.value.delete(timerId)
    }
  }
  
  /**
   * 全てのアクティブタイマーをクリア
   */
  const clearAllTimers = () => {
    activeTimers.value.forEach(timerId => {
      window.clearTimeout(timerId)
      window.clearInterval(timerId)
    })
    activeTimers.value.clear()
  }
  
  // アンマウント時のクリーンアップ
  onUnmounted(() => {
    clearAllTimers()
  })
  
  return {
    setTimeout,
    setInterval,
    clearTimer,
    clearAllTimers,
    activeTimerCount: computed(() => activeTimers.value.size)
  }
}
```

## イベントハンドリングパターン

### 高度なイベント管理

```javascript
// composables/useEventListener.js
import { onMounted, onUnmounted } from 'vue'

/**
 * 自動クリーンアップ付きイベントリスナー管理
 * @param {string|Array} events - 監視するイベント名
 * @param {EventTarget} target - イベントターゲット（デフォルト: window）
 * @param {Object} options - イベントリスナーオプション
 * @returns {Object} イベントリスナーユーティリティ
 */
export function useEventListener(events, target = window, options = {}) {
  const listeners = new Map()
  
  /**
   * イベントリスナーを追加
   * @param {string} event - イベント名
   * @param {Function} handler - イベントハンドラー
   * @param {Object} opts - イベントオプション
   */
  const addEventListener = (event, handler, opts = {}) => {
    const eventOptions = { ...options, ...opts }
    
    target.addEventListener(event, handler, eventOptions)
    
    if (!listeners.has(event)) {
      listeners.set(event, new Set())
    }
    listeners.get(event).add({ handler, options: eventOptions })
  }
  
  /**
   * イベントリスナーを削除
   * @param {string} event - イベント名
   * @param {Function} handler - イベントハンドラー
   */
  const removeEventListener = (event, handler) => {
    const eventListeners = listeners.get(event)
    if (eventListeners) {
      const listener = Array.from(eventListeners).find(l => l.handler === handler)
      if (listener) {
        target.removeEventListener(event, handler, listener.options)
        eventListeners.delete(listener)
        
        if (eventListeners.size === 0) {
          listeners.delete(event)
        }
      }
    }
  }
  
  /**
   * イベントの全リスナーを削除
   * @param {string} event - イベント名
   */
  const removeAllListeners = (event) => {
    const eventListeners = listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach(({ handler, options }) => {
        target.removeEventListener(event, handler, options)
      })
      listeners.delete(event)
    }
  }
  
  /**
   * 全リスナーをクリーンアップ
   */
  const cleanup = () => {
    listeners.forEach((eventListeners, event) => {
      eventListeners.forEach(({ handler, options }) => {
        target.removeEventListener(event, handler, options)
      })
    })
    listeners.clear()
  }
  
  // 初期リスナーの設定（提供された場合）
  onMounted(() => {
    if (Array.isArray(events)) {
      events.forEach(event => {
        if (typeof event === 'string') {
          addEventListener(event, () => {})
        } else if (event.name && event.handler) {
          addEventListener(event.name, event.handler, event.options)
        }
      })
    }
  })
  
  // アンマウント時のクリーンアップ
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    addEventListener,
    removeEventListener,
    removeAllListeners,
    cleanup
  }
}
```

### カスタムイベントエミッター

```javascript
// composables/useEventEmitter.js
import { ref } from 'vue'

/**
 * コンポーネント間通信用カスタムイベントエミッター
 * @returns {Object} イベントエミッターユーティリティ
 */
export function useEventEmitter() {
  const listeners = ref(new Map())
  
  /**
   * イベントリスナーを追加
   * @param {string} event - イベント名
   * @param {Function} handler - イベントハンドラー
   * @returns {Function} 購読解除関数
   */
  const on = (event, handler) => {
    if (!listeners.value.has(event)) {
      listeners.value.set(event, new Set())
    }
    
    listeners.value.get(event).add(handler)
    
    // 購読解除関数を返す
    return () => off(event, handler)
  }
  
  /**
   * 一度だけ実行されるイベントリスナーを追加
   * @param {string} event - イベント名
   * @param {Function} handler - イベントハンドラー
   * @returns {Function} 購読解除関数
   */
  const once = (event, handler) => {
    const onceHandler = (...args) => {
      handler(...args)
      off(event, onceHandler)
    }
    
    return on(event, onceHandler)
  }
  
  /**
   * イベントリスナーを削除
   * @param {string} event - イベント名
   * @param {Function} handler - イベントハンドラー
   */
  const off = (event, handler) => {
    const eventListeners = listeners.value.get(event)
    if (eventListeners) {
      eventListeners.delete(handler)
      
      if (eventListeners.size === 0) {
        listeners.value.delete(event)
      }
    }
  }
  
  /**
   * 全リスナーにイベントを発火
   * @param {string} event - イベント名
   * @param  {...any} args - イベント引数
   */
  const emit = (event, ...args) => {
    const eventListeners = listeners.value.get(event)
    if (eventListeners) {
      eventListeners.forEach(handler => {
        try {
          handler(...args)
        } catch (error) {
          console.error(`"${event}"のイベントハンドラーでエラーが発生しました:`, error)
        }
      })
    }
  }
  
  /**
   * 全リスナーを削除
   */
  const clear = () => {
    listeners.value.clear()
  }
  
  /**
   * イベントのリスナー数を取得
   * @param {string} event - イベント名
   * @returns {number} リスナー数
   */
  const listenerCount = (event) => {
    const eventListeners = listeners.value.get(event)
    return eventListeners ? eventListeners.size : 0
  }
  
  return {
    on,
    once,
    off,
    emit,
    clear,
    listenerCount
  }
}
```

## Template RefとDOM操作

### Template Ref管理

```javascript
// composables/useTemplateRef.js
import { ref, onMounted, nextTick } from 'vue'

/**
 * 拡張Template Ref管理
 * @param {string} refName - Template ref名
 * @returns {Object} Template refユーティリティ
 */
export function useTemplateRef(refName) {
  const elementRef = ref(null)
  const isReady = ref(false)
  
  /**
   * 要素が利用可能になるまで待機
   * @returns {Promise<HTMLElement>} 要素リファレンス
   */
  const waitForElement = async () => {
    if (elementRef.value) {
      return elementRef.value
    }
    
    return new Promise((resolve) => {
      const checkElement = () => {
        if (elementRef.value) {
          resolve(elementRef.value)
        } else {
          nextTick(checkElement)
        }
      }
      checkElement()
    })
  }
  
  /**
   * 要素にフォーカス
   * @param {Object} options - フォーカスオプション
   */
  const focus = async (options = {}) => {
    const element = await waitForElement()
    if (element && element.focus) {
      element.focus(options)
    }
  }
  
  /**
   * 要素を画面内にスクロール
   * @param {Object} options - スクロールオプション
   */
  const scrollIntoView = async (options = {}) => {
    const element = await waitForElement()
    if (element && element.scrollIntoView) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        ...options
      })
    }
  }
  
  /**
   * 要素のサイズを取得
   * @returns {Promise<Object>} 要素のサイズ
   */
  const getDimensions = async () => {
    const element = await waitForElement()
    if (element) {
      const rect = element.getBoundingClientRect()
      return {
        width: rect.width,
        height: rect.height,
        top: rect.top,
        left: rect.left,
        bottom: rect.bottom,
        right: rect.right
      }
    }
    return null
  }
  
  onMounted(() => {
    nextTick(() => {
      if (elementRef.value) {
        isReady.value = true
      }
    })
  })
  
  return {
    elementRef,
    isReady: readonly(isReady),
    waitForElement,
    focus,
    scrollIntoView,
    getDimensions
  }
}
```

### DOM Observerパターン

```javascript
// composables/useIntersectionObserver.js
import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 要素の表示状態を監視するIntersection Observer
 * @param {Object} options - Observerオプション
 * @returns {Object} Intersection observerユーティリティ
 */
export function useIntersectionObserver(options = {}) {
  const isVisible = ref(false)
  const target = ref(null)
  const observer = ref(null)
  
  const defaultOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1,
    ...options
  }
  
  /**
   * 対象要素の監視を開始
   */
  const observe = () => {
    if (!target.value || observer.value) return
    
    observer.value = new IntersectionObserver(
      (entries) => {
        const entry = entries[0]
        isVisible.value = entry.isIntersecting
        
        if (options.once && entry.isIntersecting) {
          unobserve()
        }
      },
      defaultOptions
    )
    
    observer.value.observe(target.value)
  }
  
  /**
   * 監視を停止
   */
  const unobserve = () => {
    if (observer.value) {
      observer.value.disconnect()
      observer.value = null
    }
  }
  
  onMounted(() => {
    if (target.value) {
      observe()
    }
  })
  
  onUnmounted(() => {
    unobserve()
  })
  
  return {
    target,
    isVisible: readonly(isVisible),
    observe,
    unobserve
  }
}
```

## Composable設計パターン

### Composableファクトリーパターン

```javascript
// composables/useResourceFactory.js
import { ref, computed } from 'vue'

/**
 * リソース管理Composableを作成するファクトリー
 * @param {string} resourceName - リソース名
 * @param {Object} config - リソース設定
 * @returns {Function} リソースComposableファクトリー
 */
export function createResourceComposable(resourceName, config = {}) {
  const {
    apiEndpoint,
    defaultFilters = {},
    cacheTimeout = 300000,
    transformData = (data) => data
  } = config
  
  return function useResource(initialFilters = {}) {
    const data = ref([])
    const loading = ref(false)
    const error = ref(null)
    const filters = ref({ ...defaultFilters, ...initialFilters })
    const cache = ref(new Map())
    
    const filteredData = computed(() => {
      return data.value.filter(item => {
        return Object.entries(filters.value).every(([key, value]) => {
          if (!value) return true
          return item[key]?.toString().toLowerCase().includes(value.toString().toLowerCase())
        })
      })
    })
    
    const isEmpty = computed(() => filteredData.value.length === 0)
    const count = computed(() => filteredData.value.length)
    
    /**
     * リソースデータを取得
     * @param {Object} options - 取得オプション
     */
    const fetch = async (options = {}) => {
      const cacheKey = JSON.stringify({ ...filters.value, ...options })
      const cached = cache.value.get(cacheKey)
      
      if (cached && Date.now() - cached.timestamp < cacheTimeout) {
        data.value = cached.data
        return cached.data
      }
      
      try {
        loading.value = true
        error.value = null
        
        // モックAPI呼び出し - 実際の実装に置き換えてください
        const response = await fetch(`${apiEndpoint}?${new URLSearchParams(filters.value)}`)
        const result = await response.json()
        const transformedData = transformData(result)
        
        data.value = transformedData
        cache.value.set(cacheKey, {
          data: transformedData,
          timestamp: Date.now()
        })
        
        return transformedData
      } catch (err) {
        error.value = err.message
        throw err
      } finally {
        loading.value = false
      }
    }
    
    /**
     * フィルターを更新
     * @param {Object} newFilters - 新しいフィルター値
     */
    const updateFilters = (newFilters) => {
      filters.value = { ...filters.value, ...newFilters }
    }
    
    /**
     * フィルターをデフォルトにリセット
     */
    const resetFilters = () => {
      filters.value = { ...defaultFilters }
    }
    
    /**
     * キャッシュをクリア
     */
    const clearCache = () => {
      cache.value.clear()
    }
    
    return {
      // 状態
      data: readonly(data),
      loading: readonly(loading),
      error: readonly(error),
      filters: readonly(filters),
      // 計算プロパティ
      filteredData,
      isEmpty,
      count,
      // メソッド
      fetch,
      updateFilters,
      resetFilters,
      clearCache
    }
  }
}

// 使用例
const useUsers = createResourceComposable('users', {
  apiEndpoint: '/api/users',
  defaultFilters: { active: true },
  transformData: (users) => users.map(user => ({
    ...user,
    fullName: `${user.firstName} ${user.lastName}`
  }))
})
```

### プラグインパターン

```javascript
// composables/usePlugin.js
import { ref, inject, provide } from 'vue'

const PLUGIN_KEY = Symbol('plugin')

/**
 * Composableを拡張するプラグインシステム
 * @returns {Object} プラグインユーティリティ
 */
export function usePlugin() {
  const plugins = ref(new Map())
  
  /**
   * プラグインを登録
   * @param {string} name - プラグイン名
   * @param {Object} plugin - プラグイン実装
   */
  const registerPlugin = (name, plugin) => {
    plugins.value.set(name, plugin)
  }
  
  /**
   * 登録されたプラグインを取得
   * @param {string} name - プラグイン名
   * @returns {Object} プラグイン実装
   */
  const getPlugin = (name) => {
    return plugins.value.get(name)
  }
  
  /**
   * プラグインが登録されているかチェック
   * @param {string} name - プラグイン名
   * @returns {boolean} プラグインの存在
   */
  const hasPlugin = (name) => {
    return plugins.value.has(name)
  }
  
  /**
   * プラグインをComposableに適用
   * @param {string} pluginName - プラグイン名
   * @param {Object} composable - 拡張するComposable
   * @param {Object} options - プラグインオプション
   * @returns {Object} 拡張されたComposable
   */
  const applyPlugin = (pluginName, composable, options = {}) => {
    const plugin = getPlugin(pluginName)
    if (!plugin) {
      console.warn(`プラグイン "${pluginName}" が見つかりません`)
      return composable
    }
    
    return plugin.apply(composable, options)
  }
  
  return {
    plugins: readonly(plugins),
    registerPlugin,
    getPlugin,
    hasPlugin,
    applyPlugin
  }
}

/**
 * プラグインシステムを提供
 * @param {Object} initialPlugins - 初期プラグイン
 */
export function providePlugins(initialPlugins = {}) {
  const pluginSystem = usePlugin()
  
  Object.entries(initialPlugins).forEach(([name, plugin]) => {
    pluginSystem.registerPlugin(name, plugin)
  })
  
  provide(PLUGIN_KEY, pluginSystem)
  return pluginSystem
}

/**
 * プラグインシステムを注入
 * @returns {Object} プラグインシステム
 */
export function injectPlugins() {
  const pluginSystem = inject(PLUGIN_KEY)
  if (!pluginSystem) {
    throw new Error('プラグインシステムが提供されていません')
  }
  return pluginSystem
}
```

## パフォーマンス最適化

### メモ化パターン

```javascript
// composables/useMemoization.js
import { ref, computed, readonly } from 'vue'

/**
 * 重い計算のメモ化ユーティリティ
 * @returns {Object} メモ化ユーティリティ
 */
export function useMemoization() {
  const cache = ref(new Map())
  const stats = ref({
    hits: 0,
    misses: 0,
    size: 0
  })
  
  /**
   * 関数の結果をメモ化
   * @param {Function} fn - メモ化する関数
   * @param {Function} keyFn - キー生成関数
   * @param {number} ttl - 生存時間（ミリ秒）
   * @returns {Function} メモ化された関数
   */
  const memoize = (fn, keyFn = JSON.stringify, ttl = Infinity) => {
    return (...args) => {
      const key = keyFn(args)
      const cached = cache.value.get(key)
      
      // キャッシュヒット確認
      if (cached && (ttl === Infinity || Date.now() - cached.timestamp < ttl)) {
        stats.value.hits++
        return cached.value
      }
      
      // キャッシュミス - 値を計算
      stats.value.misses++
      const result = fn(...args)
      
      cache.value.set(key, {
        value: result,
        timestamp: Date.now()
      })
      
      stats.value.size = cache.value.size
      return result
    }
  }
  
  /**
   * メモ化されたcomputed propertyを作成
   * @param {Function} fn - 計算関数
   * @param {Array} deps - 依存関係配列
   * @returns {ComputedRef} メモ化されたcomputed
   */
  const memoizedComputed = (fn, deps = []) => {
    const memoizedFn = memoize(fn, () => deps.map(dep => dep.value).join('|'))
    return computed(() => memoizedFn())
  }
  
  /**
   * キャッシュをクリア
   */
  const clearCache = () => {
    cache.value.clear()
    stats.value = { hits: 0, misses: 0, size: 0 }
  }
  
  /**
   * 期限切れエントリを削除
   * @param {number} ttl - 生存時間（ミリ秒）
   */
  const cleanupExpired = (ttl) => {
    const now = Date.now()
    for (const [key, value] of cache.value) {
      if (now - value.timestamp > ttl) {
        cache.value.delete(key)
      }
    }
    stats.value.size = cache.value.size
  }
  
  const hitRate = computed(() => {
    const total = stats.value.hits + stats.value.misses
    return total > 0 ? stats.value.hits / total : 0
  })
  
  return {
    cache: readonly(cache),
    stats: readonly(stats),
    hitRate,
    memoize,
    memoizedComputed,
    clearCache,
    cleanupExpired
  }
}
```

### デバウンス・スロットル

```javascript
// composables/useDebounceThrottle.js
import { ref, watch } from 'vue'

/**
 * デバウンス・スロットルユーティリティ
 * @returns {Object} デバウンス/スロットルユーティリティ
 */
export function useDebounceThrottle() {
  /**
   * 値をデバウンス
   * @param {Ref} value - デバウンスするリアクティブ値
   * @param {number} delay - デバウンス遅延（ミリ秒）
   * @returns {Ref} デバウンスされた値
   */
  const debounceRef = (value, delay = 300) => {
    const debouncedValue = ref(value.value)
    let timeoutId = null
    
    watch(value, (newValue) => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      
      timeoutId = setTimeout(() => {
        debouncedValue.value = newValue
        timeoutId = null
      }, delay)
    })
    
    return debouncedValue
  }
  
  /**
   * 値をスロットル
   * @param {Ref} value - スロットルするリアクティブ値
   * @param {number} limit - スロットル制限（ミリ秒）
   * @returns {Ref} スロットルされた値
   */
  const throttleRef = (value, limit = 300) => {
    const throttledValue = ref(value.value)
    let inThrottle = false
    
    watch(value, (newValue) => {
      if (!inThrottle) {
        throttledValue.value = newValue
        inThrottle = true
        
        setTimeout(() => {
          inThrottle = false
        }, limit)
      }
    })
    
    return throttledValue
  }
  
  /**
   * 関数をデバウンス
   * @param {Function} fn - デバウンスする関数
   * @param {number} delay - デバウンス遅延（ミリ秒）
   * @returns {Function} デバウンスされた関数
   */
  const debounce = (fn, delay = 300) => {
    let timeoutId = null
    
    return (...args) => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      
      timeoutId = setTimeout(() => {
        fn(...args)
        timeoutId = null
      }, delay)
    }
  }
  
  /**
   * 関数をスロットル
   * @param {Function} fn - スロットルする関数
   * @param {number} limit - スロットル制限（ミリ秒）
   * @returns {Function} スロットルされた関数
   */
  const throttle = (fn, limit = 300) => {
    let inThrottle = false
    
    return (...args) => {
      if (!inThrottle) {
        fn(...args)
        inThrottle = true
        
        setTimeout(() => {
          inThrottle = false
        }, limit)
      }
    }
  }
  
  return {
    debounceRef,
    throttleRef,
    debounce,
    throttle
  }
}
```

## TypeScriptでの型安全性

### TypeScript Composableパターン

```typescript
// composables/useTypedComposable.ts
import { ref, computed, readonly, Ref, ComputedRef } from 'vue'

/**
 * 型安全なリソースComposable
 * @template T - リソース型
 * @param initialData - 初期データ
 * @returns 型付きリソースユーティリティ
 */
export function useTypedResource<T>(
  initialData: T[] = []
): {
  data: Readonly<Ref<T[]>>
  loading: Readonly<Ref<boolean>>
  error: Readonly<Ref<string | null>>
  isEmpty: ComputedRef<boolean>
  count: ComputedRef<number>
  add: (item: T) => void
  remove: (predicate: (item: T) => boolean) => void
  update: (predicate: (item: T) => boolean, updates: Partial<T>) => void
  clear: () => void
} {
  const data = ref<T[]>(initialData)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const isEmpty = computed(() => data.value.length === 0)
  const count = computed(() => data.value.length)
  
  const add = (item: T): void => {
    data.value.push(item)
  }
  
  const remove = (predicate: (item: T) => boolean): void => {
    data.value = data.value.filter(item => !predicate(item))
  }
  
  const update = (predicate: (item: T) => boolean, updates: Partial<T>): void => {
    data.value = data.value.map(item => 
      predicate(item) ? { ...item, ...updates } : item
    )
  }
  
  const clear = (): void => {
    data.value = []
  }
  
  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    isEmpty,
    count,
    add,
    remove,
    update,
    clear
  }
}

// 特定の型での使用例
interface User {
  id: number
  name: string
  email: string
  active: boolean
}

export function useUsers() {
  return useTypedResource<User>()
}
```

### 高度なTypeScriptパターン

```typescript
// composables/useAdvancedTypes.ts
import { ref, Ref, UnwrapRef } from 'vue'

// ユーティリティ型
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P]
}

type NonEmptyArray<T> = [T, ...T[]]

interface ValidationRule<T> {
  validator: (value: T) => boolean
  message: string
}

interface FormField<T> {
  value: T
  rules: ValidationRule<T>[]
  error: string | null
  touched: boolean
}

/**
 * 型安全なフォームComposable
 * @template T - フォームデータ型
 */
export function useTypedForm<T extends Record<string, any>>(
  initialData: T,
  validationRules: Partial<Record<keyof T, NonEmptyArray<ValidationRule<T[keyof T]>>>>
) {
  const formData = ref<T>(initialData)
  const errors = ref<Partial<Record<keyof T, string>>>({})
  const touched = ref<Partial<Record<keyof T, boolean>>>({})
  
  const validateField = <K extends keyof T>(field: K, value: T[K]): boolean => {
    const rules = validationRules[field]
    if (!rules) return true
    
    for (const rule of rules) {
      if (!rule.validator(value)) {
        errors.value[field] = rule.message
        return false
      }
    }
    
    delete errors.value[field]
    return true
  }
  
  const updateField = <K extends keyof T>(field: K, value: T[K]): void => {
    (formData.value as any)[field] = value
    touched.value[field] = true
    validateField(field, value)
  }
  
  const isValid = computed(() => Object.keys(errors.value).length === 0)
  
  return {
    formData: readonly(formData),
    errors: readonly(errors),
    touched: readonly(touched),
    isValid,
    updateField,
    validateField
  }
}
```

## 🎯 実用的なビジネスロジック例

### ユーザー管理システム

実際のビジネス要件を満たすユーザー管理システムの実装例：

```vue
<!-- UserManagementDashboard.vue -->
<template>
  <div class="container-fluid">
    <!-- ページヘッダー -->
    <header class="mb-8">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-display-large text-text-primary">ユーザー管理</h1>
          <p class="text-body-medium text-text-secondary mt-2">
            システムユーザーの管理と権限設定
          </p>
        </div>
        <div class="flex gap-2">
          <ExportButton @export="handleExport" :loading="exporting" />
          <ImportButton @import="handleImport" />
          <button @click="showCreateModal = true" class="btn btn-primary">
            <Icon name="plus" size="sm" class="mr-2" />
            新規ユーザー
          </button>
        </div>
      </div>
    </header>

    <!-- 統計カード -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <StatCard
        v-for="stat in userStats"
        :key="stat.id"
        :title="stat.title"
        :value="stat.value"
        :trend="stat.trend"
        :icon="stat.icon"
        :color="stat.color"
      />
    </div>

    <!-- フィルターとアクション -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <div class="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
          <!-- 検索 -->
          <div class="form-control flex-1">
            <SearchInput
              v-model="searchQuery"
              placeholder="ユーザー名、メール、部署で検索..."
              :debounce="300"
              @search="handleSearch"
            />
          </div>

          <!-- フィルター -->
          <div class="flex gap-2 flex-wrap">
            <RoleFilter
              v-model="filters.role"
              :options="roleOptions"
              @change="handleFilterChange"
            />
            <StatusFilter
              v-model="filters.status"
              :options="statusOptions"
              @change="handleFilterChange"
            />
            <DepartmentFilter
              v-model="filters.department"
              :options="departmentOptions"
              @change="handleFilterChange"
            />
          </div>

          <!-- バルクアクション -->
          <div v-if="selectedUsers.length > 0" class="flex gap-2">
            <button
              @click="handleBulkAction('activate')"
              class="btn btn-sm btn-success"
            >
              一括有効化
            </button>
            <button
              @click="handleBulkAction('deactivate')"
              class="btn btn-sm btn-warning"
            >
              一括無効化
            </button>
            <button
              @click="handleBulkAction('delete')"
              class="btn btn-sm btn-error"
            >
              一括削除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ユーザーテーブル -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <UserDataTable
          :data="filteredUsers"
          :columns="userColumns"
          :loading="loading"
          :selected-items="selectedUsers"
          @selection-change="handleSelectionChange"
          @edit="handleEdit"
          @delete="handleDelete"
          @role-change="handleRoleChange"
          @status-change="handleStatusChange"
        />
      </div>
    </div>

    <!-- ページネーション -->
    <PaginationControls
      v-if="totalPages > 1"
      v-model="currentPage"
      :total-pages="totalPages"
      :total-items="totalItems"
      :page-size="pageSize"
      @page-change="handlePageChange"
    />

    <!-- モーダル -->
    <UserFormModal
      v-model="showCreateModal"
      title="新規ユーザー作成"
      @submit="handleCreateUser"
    />

    <UserFormModal
      v-model="showEditModal"
      title="ユーザー編集"
      :initial-data="editingUser"
      @submit="handleUpdateUser"
    />

    <ConfirmationModal
      v-model="showDeleteModal"
      title="ユーザー削除確認"
      :message="`${deletingUser?.name} を削除してもよろしいですか？`"
      confirm-text="削除"
      confirm-class="btn-error"
      @confirm="handleConfirmDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserManagement } from '@/composables/useUserManagement'
import { useNotification } from '@/composables/useNotification'
import { usePermissions } from '@/composables/usePermissions'

// コンポーネントインポート
import StatCard from '@/components/StatCard.vue'
import SearchInput from '@/components/SearchInput.vue'
import RoleFilter from '@/components/filters/RoleFilter.vue'
import StatusFilter from '@/components/filters/StatusFilter.vue'
import DepartmentFilter from '@/components/filters/DepartmentFilter.vue'
import UserDataTable from '@/components/UserDataTable.vue'
import PaginationControls from '@/components/PaginationControls.vue'
import UserFormModal from '@/components/modals/UserFormModal.vue'
import ConfirmationModal from '@/components/modals/ConfirmationModal.vue'
import ExportButton from '@/components/ExportButton.vue'
import ImportButton from '@/components/ImportButton.vue'
import Icon from '@/components/Icon.vue'

// コンポーザブル
const {
  users,
  loading,
  stats,
  fetchUsers,
  createUser,
  updateUser,
  deleteUser,
  bulkUpdateUsers,
  exportUsers,
  importUsers
} = useUserManagement()

const { showNotification } = useNotification()
const { hasPermission } = usePermissions()

// リアクティブ状態
const searchQuery = ref('')
const filters = ref({
  role: '',
  status: '',
  department: ''
})
const selectedUsers = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const exporting = ref(false)

// モーダル状態
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)

// 計算プロパティ
const filteredUsers = computed(() => {
  let result = users.value

  // 検索フィルター
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(user =>
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.department?.toLowerCase().includes(query)
    )
  }

  // ロールフィルター
  if (filters.value.role) {
    result = result.filter(user => user.role === filters.value.role)
  }

  // ステータスフィルター
  if (filters.value.status) {
    result = result.filter(user => user.status === filters.value.status)
  }

  // 部署フィルター
  if (filters.value.department) {
    result = result.filter(user => user.department === filters.value.department)
  }

  return result
})

const totalItems = computed(() => filteredUsers.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

const userStats = computed(() => [
  {
    id: 'total',
    title: '総ユーザー数',
    value: stats.value.total,
    trend: stats.value.totalTrend,
    icon: 'user-solid',
    color: 'primary'
  },
  {
    id: 'active',
    title: 'アクティブ',
    value: stats.value.active,
    trend: stats.value.activeTrend,
    icon: 'check-solid',
    color: 'success'
  },
  {
    id: 'pending',
    title: '承認待ち',
    value: stats.value.pending,
    trend: stats.value.pendingTrend,
    icon: 'clock',
    color: 'warning'
  },
  {
    id: 'inactive',
    title: '無効',
    value: stats.value.inactive,
    trend: stats.value.inactiveTrend,
    icon: 'x-mark',
    color: 'error'
  }
])

const userColumns = computed(() => [
  {
    key: 'avatar',
    title: '',
    sortable: false,
    width: '60px',
    component: 'UserAvatar'
  },
  {
    key: 'name',
    title: 'ユーザー名',
    sortable: true
  },
  {
    key: 'email',
    title: 'メールアドレス',
    sortable: true
  },
  {
    key: 'role',
    title: '権限',
    sortable: true,
    component: 'RoleBadge'
  },
  {
    key: 'department',
    title: '部署',
    sortable: true
  },
  {
    key: 'status',
    title: 'ステータス',
    sortable: true,
    component: 'StatusBadge'
  },
  {
    key: 'lastLogin',
    title: '最終ログイン',
    sortable: true,
    type: 'datetime'
  },
  {
    key: 'actions',
    title: 'アクション',
    sortable: false,
    width: '120px'
  }
])

// フィルターオプション
const roleOptions = computed(() => [
  { value: '', label: '全ての権限' },
  { value: 'admin', label: '管理者' },
  { value: 'manager', label: 'マネージャー' },
  { value: 'user', label: '一般ユーザー' },
  { value: 'guest', label: 'ゲスト' }
])

const statusOptions = computed(() => [
  { value: '', label: '全てのステータス' },
  { value: 'active', label: 'アクティブ' },
  { value: 'pending', label: '承認待ち' },
  { value: 'inactive', label: '無効' },
  { value: 'suspended', label: '停止中' }
])

const departmentOptions = computed(() => [
  { value: '', label: '全ての部署' },
  { value: 'engineering', label: '開発部' },
  { value: 'sales', label: '営業部' },
  { value: 'marketing', label: 'マーケティング部' },
  { value: 'hr', label: '人事部' },
  { value: 'finance', label: '財務部' }
])

// イベントハンドラー
const handleSearch = (query) => {
  searchQuery.value = query
  currentPage.value = 1
}

const handleFilterChange = () => {
  currentPage.value = 1
}

const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

const handleEdit = (user) => {
  if (!hasPermission('users:update')) {
    showNotification('ユーザーを編集する権限がありません', 'error')
    return
  }
  
  editingUser.value = user
  showEditModal.value = true
}

const handleDelete = (user) => {
  if (!hasPermission('users:delete')) {
    showNotification('ユーザーを削除する権限がありません', 'error')
    return
  }
  
  deletingUser.value = user
  showDeleteModal.value = true
}

const handleCreateUser = async (userData) => {
  try {
    await createUser(userData)
    showCreateModal.value = false
    showNotification('ユーザーが正常に作成されました', 'success')
  } catch (error) {
    showNotification(`ユーザー作成に失敗しました: ${error.message}`, 'error')
  }
}

const handleUpdateUser = async (userData) => {
  try {
    await updateUser(editingUser.value.id, userData)
    showEditModal.value = false
    editingUser.value = null
    showNotification('ユーザー情報が正常に更新されました', 'success')
  } catch (error) {
    showNotification(`ユーザー更新に失敗しました: ${error.message}`, 'error')
  }
}

const handleConfirmDelete = async () => {
  try {
    await deleteUser(deletingUser.value.id)
    showDeleteModal.value = false
    deletingUser.value = null
    showNotification('ユーザーが正常に削除されました', 'success')
  } catch (error) {
    showNotification(`ユーザー削除に失敗しました: ${error.message}`, 'error')
  }
}

const handleBulkAction = async (action) => {
  if (!hasPermission(`users:${action}`)) {
    showNotification(`一括${action}する権限がありません`, 'error')
    return
  }

  try {
    await bulkUpdateUsers(selectedUsers.value, { action })
    selectedUsers.value = []
    showNotification(`選択されたユーザーの${action}が完了しました`, 'success')
  } catch (error) {
    showNotification(`一括操作に失敗しました: ${error.message}`, 'error')
  }
}

const handleRoleChange = async (user, newRole) => {
  try {
    await updateUser(user.id, { role: newRole })
    showNotification('権限が正常に変更されました', 'success')
  } catch (error) {
    showNotification(`権限変更に失敗しました: ${error.message}`, 'error')
  }
}

const handleStatusChange = async (user, newStatus) => {
  try {
    await updateUser(user.id, { status: newStatus })
    showNotification('ステータスが正常に変更されました', 'success')
  } catch (error) {
    showNotification(`ステータス変更に失敗しました: ${error.message}`, 'error')
  }
}

const handleExport = async () => {
  exporting.value = true
  try {
    await exportUsers({
      filters: filters.value,
      searchQuery: searchQuery.value,
      format: 'csv'
    })
    showNotification('ユーザーデータのエクスポートが完了しました', 'success')
  } catch (error) {
    showNotification(`エクスポートに失敗しました: ${error.message}`, 'error')
  } finally {
    exporting.value = false
  }
}

const handleImport = async (file) => {
  try {
    const result = await importUsers(file)
    showNotification(
      `${result.success}件のユーザーがインポートされました`,
      'success'
    )
    if (result.errors.length > 0) {
      showNotification(
        `${result.errors.length}件のエラーがありました`,
        'warning'
      )
    }
  } catch (error