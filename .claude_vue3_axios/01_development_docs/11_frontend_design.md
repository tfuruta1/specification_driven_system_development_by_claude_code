# フロントエンド設計ガイド

## 概要

このドキュメントは、Vue.js 3 + JavaScript + Tailwind CSSを使用したフロントエンド開発における、コンポーネント設計、状態管理、スタイリングの方針を定義します。再利用性、保守性、パフォーマンスを重視した設計指針を提供します。

## 1. アーキテクチャ概要

### 1.1 技術スタック
```javascript
// 主要技術スタック
const techStack = {
  framework: "Vue.js 3.4+",
  language: "JavaScript (ES2022+)",
  styling: "Tailwind CSS 3.4+ & DaisyUI 4.0+",
  stateManagement: "Pinia 2.1+",
  routing: "Vue Router 4.4+",
  http: "@supabase/supabase-js 2.39+",
  validation: "zod 3.22+",
  testing: "Vitest 1.2+ & Playwright 1.41+"
}
```

### 1.2 ディレクトリ構造
```
src/
├── components/          # 再利用可能なコンポーネント
│   ├── ui/             # 基本UIコンポーネント
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Modal/
│   │   └── Card/
│   ├── features/       # 機能別コンポーネント
│   │   ├── auth/
│   │   ├── user/
│   │   └── dashboard/
│   └── layouts/        # レイアウトコンポーネント
│       ├── AppLayout.vue
│       ├── AuthLayout.vue
│       └── DashboardLayout.vue
├── composables/        # Composition API ロジック
├── stores/             # Pinia ストア
├── router/             # ルーティング設定
├── types/              # JSDoc型定義・共通型
├── utils/              # ユーティリティ関数
├── assets/             # 静的アセット
└── styles/             # グローバルスタイル
```

## 2. コンポーネント設計

### 2.1 コンポーネント分類

#### UIコンポーネント（Presentational）
```vue
<!-- components/ui/Button/Button.vue -->
<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <LoadingIcon v-if="loading" class="w-4 h-4 mr-2" />
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'
import LoadingIcon from '@/components/ui/icons/LoadingIcon.vue'

// Props定義
const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'ghost', 'danger'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

// Emits定義
const emit = defineEmits(['click'])

// 計算プロパティ
const buttonClasses = computed(() => {
  const base = 'btn transition-all duration-200'
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    ghost: 'btn-ghost',
    danger: 'btn-error'
  }
  const sizes = {
    sm: 'btn-sm',
    md: 'btn-md',
    lg: 'btn-lg'
  }
  
  return [
    base,
    variants[props.variant],
    sizes[props.size],
    props.fullWidth && 'w-full',
    props.loading && 'loading'
  ].filter(Boolean).join(' ')
})

// メソッド
const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
```

#### 機能コンポーネント（Container）
```vue
<!-- components/features/auth/LoginForm.vue -->
<template>
  <Card class="w-full max-w-md">
    <CardHeader>
      <h2 class="text-2xl font-bold">ログイン</h2>
    </CardHeader>
    
    <CardBody>
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <FormField
          v-model="form.email"
          label="メールアドレス"
          type="email"
          :error="errors.email"
          required
        />
        
        <FormField
          v-model="form.password"
          label="パスワード"
          type="password"
          :error="errors.password"
          required
        />
        
        <div class="flex items-center justify-between">
          <Checkbox v-model="form.remember" label="ログイン状態を保持" />
          <Link to="/forgot-password" class="text-sm text-primary">
            パスワードを忘れた方
          </Link>
        </div>
        
        <Button
          type="submit"
          :loading="isSubmitting"
          fullWidth
        >
          ログイン
        </Button>
      </form>
    </CardBody>
    
    <CardFooter>
      <p class="text-center text-sm text-gray-600">
        アカウントをお持ちでない方は
        <Link to="/register" class="text-primary">新規登録</Link>
      </p>
    </CardFooter>
  </Card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '@/composables/useNotification'
import Card from '@/components/ui/Card/Card.vue'
import CardHeader from '@/components/ui/Card/CardHeader.vue'
import CardBody from '@/components/ui/Card/CardBody.vue'
import CardFooter from '@/components/ui/Card/CardFooter.vue'
import FormField from '@/components/ui/Form/FormField.vue'
import Button from '@/components/ui/Button/Button.vue'
import Checkbox from '@/components/ui/Form/Checkbox.vue'
import Link from '@/components/ui/Link/Link.vue'

// バリデーションスキーマ
const loginSchema = z.object({
  email: z.string().email('有効なメールアドレスを入力してください'),
  password: z.string().min(8, 'パスワードは8文字以上である必要があります'),
  remember: z.boolean()
})

// 状態管理
const router = useRouter()
const authStore = useAuthStore()
const { showSuccess, showError } = useNotification()

// フォーム状態
const form = reactive({
  email: '',
  password: '',
  remember: false
})

const errors = reactive({})
const isSubmitting = ref(false)

// フォーム送信処理
const handleSubmit = async () => {
  try {
    // バリデーション
    const validatedData = loginSchema.parse(form)
    
    // エラーをクリア
    Object.keys(errors).forEach(key => delete errors[key])
    
    // ログイン処理
    isSubmitting.value = true
    await authStore.login({
      email: validatedData.email,
      password: validatedData.password,
      remember: validatedData.remember
    })
    
    showSuccess('ログインしました')
    router.push('/dashboard')
    
  } catch (error) {
    if (error instanceof z.ZodError) {
      // バリデーションエラー
      error.errors.forEach(err => {
        if (err.path[0]) {
          errors[err.path[0]] = err.message
        }
      })
    } else {
      // APIエラー
      showError('ログインに失敗しました')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

### 2.2 Props設計方針

#### Props定義とバリデーション
```javascript
// プロップスの定義例
const props = defineProps({
  // 必須プロップス
  id: {
    type: String,
    required: true
  },
  
  // オプショナルプロップス
  className: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  
  // 列挙型（バリデーター使用）
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger'].includes(value)
  },
  
  // オブジェクト型
  config: {
    type: Object,
    default: () => ({
      timeout: 5000,
      retryCount: 3
    })
  },
  
  // 関数型
  onUpdate: {
    type: Function,
    default: () => {}
  },
  
  // 配列型
  items: {
    type: Array,
    default: () => []
  }
})
```

#### JSDocによる型情報の提供
```javascript
/**
 * @typedef {Object} SelectOption
 * @property {string} value - 選択肢の値
 * @property {string} label - 表示ラベル
 * @property {boolean} [disabled] - 無効化フラグ
 */

/**
 * @typedef {Object} ComponentConfig
 * @property {number} [timeout=5000] - タイムアウト時間（ミリ秒）
 * @property {number} [retryCount=3] - リトライ回数
 */
```

#### デフォルト値の設定
```vue
<script setup>
// definePropsでのデフォルト値設定
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '入力してください'
  },
  maxLength: {
    type: Number,
    default: 100
  },
  showCounter: {
    type: Boolean,
    default: true
  }
})
</script>
```

### 2.3 コンポジション設計

#### 再利用可能なComposables
```javascript
// composables/useForm.js
import { ref, reactive, computed } from 'vue'
import { z } from 'zod'

/**
 * フォーム管理用のComposable
 * @param {Object} initialValues - フォームの初期値
 * @param {import('zod').ZodSchema} [schema] - バリデーションスキーマ
 */
export function useForm(initialValues, schema) {
  // フォーム状態
  const values = reactive({ ...initialValues })
  const errors = reactive({})
  const touched = reactive({})
  const isSubmitting = ref(false)
  
  // 計算プロパティ
  const isValid = computed(() => {
    if (!schema) return true
    try {
      schema.parse(values)
      return true
    } catch {
      return false
    }
  })
  
  const isDirty = computed(() => {
    return Object.keys(values).some(
      key => values[key] !== initialValues[key]
    )
  })
  
  // メソッド
  const validate = () => {
    if (!schema) return true
    
    try {
      schema.parse(values)
      Object.keys(errors).forEach(key => delete errors[key])
      return true
    } catch (error) {
      if (error instanceof z.ZodError) {
        error.errors.forEach(err => {
          const path = err.path[0]
          if (path) {
            errors[path] = err.message
          }
        })
      }
      return false
    }
  }
  
  /**
   * フィールドの値を設定
   * @param {string} field - フィールド名
   * @param {*} value - 設定する値
   */
  const setFieldValue = (field, value) => {
    values[field] = value
    touched[field] = true
    
    // フィールドレベルバリデーション
    if (schema && touched[field]) {
      try {
        const fieldSchema = schema.shape[field]
        if (fieldSchema) {
          fieldSchema.parse(value)
          delete errors[field]
        }
      } catch (error) {
        if (error instanceof z.ZodError) {
          errors[field] = error.errors[0]?.message
        }
      }
    }
  }
  
  const resetForm = () => {
    Object.assign(values, initialValues)
    Object.keys(errors).forEach(key => delete errors[key])
    Object.keys(touched).forEach(key => delete touched[key])
    isSubmitting.value = false
  }
  
  /**
   * フォーム送信処理
   * @param {Function} onSubmit - 送信時のコールバック関数
   */
  const handleSubmit = async (onSubmit) => {
    if (!validate()) return
    
    try {
      isSubmitting.value = true
      await onSubmit(values)
    } finally {
      isSubmitting.value = false
    }
  }
  
  return {
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    isDirty,
    setFieldValue,
    validate,
    resetForm,
    handleSubmit
  }
}
```

## 3. 状態管理設計

### 3.1 Piniaストア構成
```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/lib/supabase'

/**
 * @typedef {Object} User
 * @property {string} id - ユーザーID
 * @property {string} email - メールアドレス
 * @property {string} [role] - ユーザーロール
 */

/**
 * @typedef {Object} UserProfile
 * @property {string} userId - ユーザーID
 * @property {string} [displayName] - 表示名
 * @property {string} [avatar] - アバター画像URL
 * @property {string} [bio] - 自己紹介
 */

export const useUserStore = defineStore('user', () => {
  // State
  const currentUser = ref(null)
  const profile = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Getters
  const isAuthenticated = computed(() => !!currentUser.value)
  const displayName = computed(() => 
    profile.value?.displayName || currentUser.value?.email || 'ゲスト'
  )
  const avatar = computed(() => 
    profile.value?.avatar || '/default-avatar.png'
  )
  
  /**
   * プロフィール情報を取得
   * @param {string} userId - ユーザーID
   */
  const fetchProfile = async (userId) => {
    isLoading.value = true
    error.value = null
    
    try {
      const { data, error: supabaseError } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', userId)
        .single()
      
      if (supabaseError) throw supabaseError
      
      profile.value = data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '不明なエラー'
      console.error('プロフィール取得エラー:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * プロフィール情報を更新
   * @param {Partial<UserProfile>} updates - 更新するフィールド
   */
  const updateProfile = async (updates) => {
    if (!currentUser.value) throw new Error('認証が必要です')
    
    isLoading.value = true
    error.value = null
    
    try {
      const { data, error: supabaseError } = await supabase
        .from('profiles')
        .update(updates)
        .eq('user_id', currentUser.value.id)
        .select()
        .single()
      
      if (supabaseError) throw supabaseError
      
      profile.value = data
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '不明なエラー'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const clearUser = () => {
    currentUser.value = null
    profile.value = null
    error.value = null
  }
  
  return {
    // State
    currentUser,
    profile,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    displayName,
    avatar,
    
    // Actions
    fetchProfile,
    updateProfile,
    clearUser
  }
})
```

### 3.2 グローバル状態とローカル状態の使い分け

#### グローバル状態（Pinia）
- ユーザー認証情報
- アプリケーション設定
- 複数コンポーネントで共有されるデータ
- キャッシュが必要なAPIレスポンス

#### ローカル状態（Component State）
- フォームの入力値
- UIの開閉状態
- 一時的なローディング状態
- コンポーネント固有の設定

## 4. スタイリング設計

### 4.1 Tailwind CSS設計方針
```javascript
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3B82F6',
          50: '#EBF2FF',
          100: '#D4E2FF',
          // ... 他の色階調
        },
        secondary: {
          DEFAULT: '#8B5CF6',
          // ... 色階調
        }
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans JP', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      }
    },
  },
  plugins: [
    require('daisyui'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### 4.2 CSS設計パターン
```vue
<!-- コンポーネントでのスタイル適用 -->
<template>
  <div class="card-container">
    <div class="card-header">
      <h3 class="card-title">{{ title }}</h3>
    </div>
    <div class="card-body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
/* Tailwind @applyを使用したカスタムクラス */
.card-container {
  @apply bg-white rounded-lg shadow-md overflow-hidden;
}

.card-header {
  @apply px-6 py-4 border-b border-gray-200;
}

.card-title {
  @apply text-lg font-semibold text-gray-900;
}

.card-body {
  @apply p-6;
}

/* レスポンシブデザイン */
@media (max-width: 640px) {
  .card-container {
    @apply shadow-sm;
  }
  
  .card-body {
    @apply p-4;
  }
}
</style>
```

## 5. パフォーマンス最適化

### 5.1 コンポーネントの最適化
```vue
<script setup>
import { defineAsyncComponent, ref, computed, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'

// 遅延ローディング
const HeavyComponent = defineAsyncComponent({
  loader: () => import('./HeavyComponent.vue'),
  delay: 200,
  timeout: 3000,
  errorComponent: ErrorComponent,
  loadingComponent: LoadingComponent,
})

// メモ化
const expensiveComputation = computed(() => {
  // 重い計算処理
  return processLargeDataSet(props.data)
})

// デバウンス処理
const searchQuery = ref('')
const debouncedSearch = useDebounceFn(() => {
  performSearch(searchQuery.value)
}, 300)

watch(searchQuery, debouncedSearch)
</script>
```

### 5.2 バンドルサイズの最適化
```javascript
// 動的インポート
const loadChart = async () => {
  const { Chart } = await import('chart.js')
  return new Chart(canvasRef.value, chartConfig)
}

// Tree-shaking対応
import { debounce, throttle } from 'lodash-es'
// NG: import _ from 'lodash'
```

## 6. ベストプラクティス

### 6.1 命名規則
- **コンポーネント**: PascalCase（例: `UserProfile.vue`）
- **Composables**: use接頭辞（例: `useAuth.js`）
- **Props/Events**: camelCase（例: `modelValue`, `onUpdate`）
- **CSS クラス**: kebab-case（例: `user-profile-card`）

### 6.2 コンポーネント設計原則
1. **単一責任の原則**: 1つのコンポーネントは1つの責務のみ
2. **再利用性**: UIコンポーネントは汎用的に設計
3. **テスタビリティ**: ロジックはComposablesに分離
4. **アクセシビリティ**: ARIA属性、キーボード操作対応

### 6.3 JSDocによる型注釈
```javascript
/**
 * @typedef {Object} TableColumn
 * @property {string} key - カラムのキー
 * @property {string} label - 表示ラベル
 * @property {boolean} [sortable] - ソート可能かどうか
 * @property {Function} [formatter] - 値のフォーマット関数
 */

/**
 * テーブルカラムの設定
 * @type {TableColumn[]}
 */
const columns = [
  {
    key: 'name',
    label: '名前',
    sortable: true
  },
  {
    key: 'email',
    label: 'メールアドレス',
    sortable: true
  },
  {
    key: 'createdAt',
    label: '作成日',
    sortable: true,
    formatter: (value) => new Date(value).toLocaleDateString('ja-JP')
  }
]

/**
 * ユーザーオブジェクトかどうかを判定
 * @param {*} value - チェックする値
 * @returns {boolean} ユーザーオブジェクトの場合true
 */
function isUser(value) {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value
  )
}

/**
 * オブジェクトのディープコピーを作成
 * @template T
 * @param {T} obj - コピーするオブジェクト
 * @returns {T} ディープコピーされたオブジェクト
 */
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj))
}
```

## まとめ

このフロントエンド設計ガイドに従うことで、保守性が高く、パフォーマンスに優れたVue.jsアプリケーションを構築できます。JavaScriptの柔軟性を活かしつつ、JSDocによる型注釈とPropバリデーションにより、コードの品質を保ちながら開発を進めることができます。コンポーネントの分類、状態管理の使い分け、スタイリングの一貫性を保ちながら、チーム開発を効率的に進めることができます。