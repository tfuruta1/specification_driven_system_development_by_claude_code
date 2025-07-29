# Vueコンポーネント設計パターン

## 📚 関連ドキュメント

このガイドの実装パターンを効果的に活用するために、以下のドキュメントを事前にご確認ください：

- **[🎨 デザインシステム概要](./00_design_overview.md)** - ブランドガイドラインとデザイン原則
- **[⚙️ Tailwind CSS設定ガイド](./01_tailwind_config.md)** - CSS設定とカスタマイズ方法
- **[🧩 DaisyUIコンポーネント活用ガイド](./02_daisyui_components.md)** - 基盤となるUIコンポーネント
- **[🎨 デザイントークンリファレンス](./04_design_tokens.md)** - トークンの詳細仕様

## 概要

Tailwind CSS + DaisyUI + Supabaseアプリケーション向けのVue 3コンポーネント高度設計パターン。コンポジションパターン、状態管理、パフォーマンス最適化、テスト戦略を含みます。

## 目次

1. [コンポーネントアーキテクチャ](#コンポーネントアーキテクチャ)
2. [Composition APIパターン](#composition-apiパターン)
3. [PropsとEvents設計](#propsとevents設計)
4. [スロットパターン](#スロットパターン)
5. [状態管理パターン](#状態管理パターン)
6. [非同期コンポーネントパターン](#非同期コンポーネントパターン)
7. [フォームコンポーネント](#フォームコンポーネント)
8. [レイアウトコンポーネント](#レイアウトコンポーネント)
9. [データ可視化コンポーネント](#データ可視化コンポーネント)
10. [パフォーマンス最適化](#パフォーマンス最適化)
11. [テストパターン](#テストパターン)
12. [TypeScript統合](#typescript統合)

## コンポーネントアーキテクチャ

### ベースコンポーネント構造

```vue
<!-- BaseComponent.vue -->
<template>
  <div
    :class="computedClasses"
    :style="computedStyles"
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>

<script setup>
import { computed, useAttrs } from 'vue'

// コンポーネントインターフェースの定義
interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  rounded?: boolean
  disabled?: boolean
  loading?: boolean
}

// デフォルト値付きProps
const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  rounded: false,
  disabled: false,
  loading: false
})

// Emits
const emit = defineEmits<{
  click: [event: MouseEvent]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
}>()

// 算出クラス
const computedClasses = computed(() => {
  const classes = ['component-base']
  
  // バリアントクラス
  classes.push(`component-${props.variant}`)
  
  // サイズクラス
  classes.push(`component-${props.size}`)
  
  // 状態クラス
  if (props.rounded) classes.push('component-rounded')
  if (props.disabled) classes.push('component-disabled')
  if (props.loading) classes.push('component-loading')
  
  return classes
})

// 算出スタイル
const computedStyles = computed(() => {
  const styles = {}
  
  // Propsに基づく動的スタイル
  if (props.disabled) {
    styles.opacity = '0.5'
    styles.pointerEvents = 'none'
  }
  
  return styles
})

// ルート要素への属性フォワード
const attrs = useAttrs()

// コンポーネントメソッド/プロパティの公開
defineExpose({
  focus: () => {
    // フォーカス実装
  },
  blur: () => {
    // ブラー実装
  }
})
</script>

<style scoped>
.component-base {
  @apply transition-all duration-200 ease-in-out;
}

.component-primary {
  @apply bg-primary text-primary-content;
}

.component-secondary {
  @apply bg-secondary text-secondary-content;
}

.component-success {
  @apply bg-success text-success-content;
}

.component-warning {
  @apply bg-warning text-warning-content;
}

.component-error {
  @apply bg-error text-error-content;
}

.component-xs {
  @apply text-xs px-2 py-1;
}

.component-sm {
  @apply text-sm px-3 py-2;
}

.component-md {
  @apply text-base px-4 py-2;
}

.component-lg {
  @apply text-lg px-6 py-3;
}

.component-xl {
  @apply text-xl px-8 py-4;
}

.component-rounded {
  @apply rounded-full;
}

.component-loading {
  @apply relative overflow-hidden;
}

.component-loading::after {
  content: '';
  @apply absolute inset-0 bg-white/20 animate-pulse;
}
</style>
```

### コンポーネントコンポジションパターン

```vue
<!-- ComposableButton.vue -->
<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
    @focus="handleFocus"
    @blur="handleBlur"
  >
    <span v-if="loading" class="loading loading-spinner loading-sm mr-2"></span>
    <component v-if="icon && !loading" :is="icon" class="w-4 h-4 mr-2" />
    
    <slot>{{ label }}</slot>
    
    <span v-if="badge" class="badge badge-sm ml-2">{{ badge }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useButtonStyles } from '@/composables/useButtonStyles'
import { useClickHandler } from '@/composables/useClickHandler'
import { useFocusHandler } from '@/composables/useFocusHandler'

const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  outline: Boolean,
  ghost: Boolean,
  disabled: Boolean,
  loading: Boolean,
  icon: Object,
  label: String,
  badge: [String, Number],
  href: String,
  to: [String, Object]
})

const emit = defineEmits(['click', 'focus', 'blur'])

// 再利用可能なロジック用コンポーザブルを使用
const { buttonClasses } = useButtonStyles(props)
const { handleClick } = useClickHandler(props, emit)
const { handleFocus, handleBlur } = useFocusHandler(emit)
</script>
```

### 高階コンポーネントパターン

```vue
<!-- WithLoading.vue -->
<template>
  <div class="relative">
    <Transition
      enter-active-class="transition-opacity duration-300"
      leave-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="loading"
        class="absolute inset-0 flex items-center justify-center bg-base-100/80 z-10"
      >
        <div class="flex flex-col items-center space-y-2">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <span v-if="loadingText" class="text-sm text-base-content/70">
            {{ loadingText }}
          </span>
        </div>
      </div>
    </Transition>
    
    <div :class="{ 'opacity-50 pointer-events-none': loading }">
      <slot />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  loading: Boolean,
  loadingText: String
})
</script>
```

### レンダー関数コンポーネント

```javascript
// FunctionalButton.js
import { h, computed } from 'vue'

export default function FunctionalButton(props, { slots, emit }) {
  const classes = computed(() => {
    const baseClasses = ['btn']
    
    if (props.variant) baseClasses.push(`btn-${props.variant}`)
    if (props.size) baseClasses.push(`btn-${props.size}`)
    if (props.outline) baseClasses.push('btn-outline')
    if (props.ghost) baseClasses.push('btn-ghost')
    
    return baseClasses
  })

  const handleClick = (event) => {
    if (!props.disabled && !props.loading) {
      emit('click', event)
    }
  }

  return h(
    'button',
    {
      class: classes.value,
      disabled: props.disabled || props.loading,
      onClick: handleClick
    },
    [
      props.loading && h('span', { class: 'loading loading-spinner loading-sm mr-2' }),
      props.icon && !props.loading && h(props.icon, { class: 'w-4 h-4 mr-2' }),
      slots.default?.() || props.label,
      props.badge && h('span', { class: 'badge badge-sm ml-2' }, props.badge)
    ]
  )
}

FunctionalButton.props = ['variant', 'size', 'outline', 'ghost', 'disabled', 'loading', 'icon', 'label', 'badge']
FunctionalButton.emits = ['click']
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

### カスタムコンポーザブル

```javascript
// composables/useApi.js
import { ref, reactive, computed } from 'vue'
import { supabase } from '@/lib/supabase'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)
  const data = ref(null)

  const state = reactive({
    loading: false,
    error: null,
    data: null
  })

  const isLoading = computed(() => state.loading)
  const hasError = computed(() => !!state.error)
  const hasData = computed(() => !!state.data)

  const execute = async (apiCall) => {
    state.loading = true
    state.error = null
    
    try {
      const result = await apiCall()
      state.data = result
      return result
    } catch (err) {
      state.error = err
      throw err
    } finally {
      state.loading = false
    }
  }

  const reset = () => {
    state.loading = false
    state.error = null
    state.data = null
  }

  return {
    state,
    isLoading,
    hasError,
    hasData,
    execute,
    reset
  }
}

// composables/useSupabaseQuery.js
import { ref, watch, onMounted } from 'vue'
import { supabase } from '@/lib/supabase'

export function useSupabaseQuery(table, options = {}) {
  const data = ref([])
  const loading = ref(false)
  const error = ref(null)
  const count = ref(0)

  const {
    select = '*',
    filters = [],
    orderBy = null,
    limit = null,
    realtime = false
  } = options

  const fetchData = async () => {
    loading.value = true
    error.value = null

    try {
      let query = supabase.from(table).select(select, { count: 'exact' })

      // フィルターを適用
      filters.forEach(filter => {
        const { column, operator, value } = filter
        query = query[operator](column, value)
      })

      // ソートを適用
      if (orderBy) {
        query = query.order(orderBy.column, { ascending: orderBy.ascending })
      }

      // 制限を適用
      if (limit) {
        query = query.limit(limit)
      }

      const { data: result, error: queryError, count: totalCount } = await query

      if (queryError) throw queryError

      data.value = result || []
      count.value = totalCount || 0
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }

  const refresh = () => fetchData()

  // リアルタイム購読の設定
  let subscription = null
  if (realtime) {
    subscription = supabase
      .channel(`${table}_changes`)
      .on('postgres_changes', { event: '*', schema: 'public', table }, () => {
        fetchData()
      })
      .subscribe()
  }

  // クリーンアップ
  const cleanup = () => {
    if (subscription) {
      supabase.removeChannel(subscription)
    }
  }

  onMounted(fetchData)

  return {
    data,
    loading,
    error,
    count,
    refresh,
    cleanup
  }
}

// composables/useFormValidation.js
import { ref, reactive, computed, watch } from 'vue'

export function useFormValidation(schema) {
  const formData = reactive({})
  const errors = reactive({})
  const touched = reactive({})
  const isSubmitting = ref(false)

  const isValid = computed(() => {
    return Object.keys(errors).length === 0 && Object.keys(touched).length > 0
  })

  const validateField = (field, value) => {
    const rules = schema[field]
    if (!rules) return true

    delete errors[field]

    // 必須バリデーション
    if (rules.required && (!value || value.toString().trim() === '')) {
      errors[field] = rules.message || `${field} は必須項目です`
      return false
    }

    // パターンバリデーション
    if (rules.pattern && value && !rules.pattern.test(value)) {
      errors[field] = rules.message || `${field} の形式が無効です`
      return false
    }

    // カスタムバリデーション
    if (rules.validator) {
      const result = rules.validator(value, formData)
      if (result !== true) {
        errors[field] = result
        return false
      }
    }

    return true
  }

  const validateForm = () => {
    let isFormValid = true
    
    Object.keys(schema).forEach(field => {
      const isFieldValid = validateField(field, formData[field])
      if (!isFieldValid) isFormValid = false
      touched[field] = true
    })

    return isFormValid
  }

  const resetForm = () => {
    Object.keys(formData).forEach(key => delete formData[key])
    Object.keys(errors).forEach(key => delete errors[key])
    Object.keys(touched).forEach(key => delete touched[key])
    isSubmitting.value = false
  }

  // フィールド変更の監視
  const setupWatchers = () => {
    Object.keys(schema).forEach(field => {
      watch(
        () => formData[field],
        (newValue) => {
          if (touched[field]) {
            validateField(field, newValue)
          }
        },
        { deep: true }
      )
    })
  }

  return {
    formData,
    errors,
    touched,
    isValid,
    isSubmitting,
    validateField,
    validateForm,
    resetForm,
    setupWatchers
  }
}
```

### Provide/Injectパターン

```vue
<!-- DataProvider.vue -->
<template>
  <div>
    <slot :data="data" :loading="loading" :error="error" :refresh="refresh" />
  </div>
</template>

<script setup>
import { provide, ref, onMounted } from 'vue'
import { useSupabaseQuery } from '@/composables/useSupabaseQuery'

const props = defineProps({
  table: { type: String, required: true },
  select: { type: String, default: '*' },
  filters: { type: Array, default: () => [] },
  realtime: { type: Boolean, default: false }
})

const { data, loading, error, refresh } = useSupabaseQuery(props.table, {
  select: props.select,
  filters: props.filters,
  realtime: props.realtime
})

// 子コンポーネントにデータを提供
provide('tableData', {
  data,
  loading,
  error,
  refresh
})

onMounted(() => {
  console.log(`${props.table}用DataProviderがマウントされました`)
})
</script>
```

```vue
<!-- DataConsumer.vue -->
<template>
  <div class="data-consumer">
    <div v-if="loading" class="loading loading-spinner loading-lg"></div>
    
    <div v-else-if="error" class="alert alert-error">
      <span>エラー: {{ error.message }}</span>
      <button @click="refresh" class="btn btn-sm">再試行</button>
    </div>
    
    <div v-else-if="data.length === 0" class="alert alert-info">
      <span>データがありません</span>
    </div>
    
    <div v-else>
      <slot :items="data" />
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'

const tableData = inject('tableData', {
  data: [],
  loading: false,
  error: null,
  refresh: () => {}
})

const { data, loading, error, refresh } = tableData
</script>
```

## PropsとEvents設計

### 高度なPropsパターン

```vue
<!-- AdvancedComponent.vue -->
<script setup>
import { computed, useSlots } from 'vue'

// Props用ユニオン型
interface Props {
  // 厳密な型付けを持つバリアントprop
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  
  // 複雑なオブジェクトprop
  config?: {
    theme: string
    animations: boolean
    accessibility: {
      ariaLabel?: string
      describedBy?: string
    }
  }
  
  // カスタムレンダリング用関数prop
  renderItem?: (item: any, index: number) => VNode
  
  // バリデーター付きprop
  items?: Array<{
    id: string | number
    name: string
    active?: boolean
  }>
  
  // 動的コンポーネントprop
  as?: string | Component
  
  // イベントハンドラーprops
  onItemClick?: (item: any, index: number) => void
  onSelectionChange?: (selectedItems: any[]) => void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  config: () => ({
    theme: 'light',
    animations: true,
    accessibility: {}
  }),
  items: () => [],
  as: 'div'
})

// propsの検証
const validatedItems = computed(() => {
  return props.items.filter(item => 
    item && 
    typeof item === 'object' && 
    (typeof item.id === 'string' || typeof item.id === 'number') &&
    typeof item.name === 'string'
  )
})

// ペイロード型付きイベントエミッター
const emit = defineEmits<{
  'item-click': [item: any, index: number]
  'selection-change': [selectedItems: any[]]
  'config-change': [config: Props['config']]
}>()

// 型チェック付きスロット
const slots = useSlots()
const hasHeaderSlot = computed(() => !!slots.header)
const hasFooterSlot = computed(() => !!slots.footer)
</script>
```

### イベントバスパターン

```javascript
// eventBus.js
import { ref } from 'vue'

class EventBus {
  constructor() {
    this.events = {}
  }

  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(data))
    }
  }

  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(callback)
  }

  off(event, callback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback)
    }
  }

  once(event, callback) {
    const onceCallback = (data) => {
      callback(data)
      this.off(event, onceCallback)
    }
    this.on(event, onceCallback)
  }
}

export const eventBus = new EventBus()

// イベントバス用コンポーザブル
export function useEventBus() {
  const emit = (event, data) => eventBus.emit(event, data)
  const on = (event, callback) => eventBus.on(event, callback)
  const off = (event, callback) => eventBus.off(event, callback)
  const once = (event, callback) => eventBus.once(event, callback)

  return { emit, on, off, once }
}
```

## スロットパターン

### 高度なスロットパターン

```vue
<!-- FlexibleCard.vue -->
<template>
  <div class="card bg-base-100 shadow-xl">
    <!-- 条件付きヘッダー -->
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header" :title="title" :subtitle="subtitle">
        <h2 class="card-title">{{ title }}</h2>
        <p v-if="subtitle" class="text-base-content/70">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- 複数のスロットバリエーションを持つメインコンテンツ -->
    <div class="card-body">
      <!-- フォールバック付き名前付きスロット -->
      <slot name="content" :data="data" :loading="loading">
        <!-- デフォルトコンテンツスロット -->
        <slot :data="data" :loading="loading">
          <div v-if="loading" class="loading loading-spinner loading-lg mx-auto"></div>
          <div v-else-if="data" class="prose max-w-none">
            {{ data }}
          </div>
          <div v-else class="text-center text-base-content/60">
            コンテンツがありません
          </div>
        </slot>
      </slot>

      <!-- リストアイテム用動的スロット -->
      <template v-if="items.length > 0">
        <div class="space-y-2">
          <div
            v-for="(item, index) in items"
            :key="item.id || index"
            class="border-b border-base-200 last:border-b-0 pb-2 last:pb-0"
          >
            <slot
              name="item"
              :item="item"
              :index="index"
              :isFirst="index === 0"
              :isLast="index === items.length - 1"
            >
              <div class="flex items-center justify-between">
                <span>{{ item.name || item.title || item }}</span>
                <slot name="item-actions" :item="item" :index="index">
                  <button class="btn btn-ghost btn-xs">編集</button>
                </slot>
              </div>
            </slot>
          </div>
        </div>
      </template>
    </div>

    <!-- 条件付きフッター -->
    <div v-if="$slots.footer || $slots.actions" class="card-actions justify-end p-4">
      <slot name="footer">
        <slot name="actions" :data="data" :refresh="refresh">
          <button class="btn btn-primary">アクション</button>
        </slot>
      </slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: String,
  subtitle: String,
  data: [Object, Array, String, Number],
  items: { type: Array, default: () => [] },
  loading: Boolean
})

const refresh = () => {
  // リフレッシュロジック
}
</script>
```

### レンダーレスコンポーネント

```vue
<!-- DataFetcher.vue - レンダーレスコンポーネント -->
<template>
  <slot
    :data="data"
    :loading="loading"
    :error="error"
    :refresh="refresh"
    :hasMore="hasMore"
    :loadMore="loadMore"
  />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { supabase } from '@/lib/supabase'

const props = defineProps({
  table: { type: String, required: true },
  select: { type: String, default: '*' },
  filters: { type: Array, default: () => [] },
  pageSize: { type: Number, default: 20 }
})

const data = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(0)
const totalCount = ref(0)

const hasMore = computed(() => {
  return data.value.length < totalCount.value
})

const fetchData = async (append = false) => {
  loading.value = true
  error.value = null

  try {
    let query = supabase
      .from(props.table)
      .select(props.select, { count: 'exact' })
      .range(
        currentPage.value * props.pageSize,
        (currentPage.value + 1) * props.pageSize - 1
      )

    // フィルターを適用
    props.filters.forEach(filter => {
      query = query[filter.method](filter.column, filter.value)
    })

    const { data: result, error: queryError, count } = await query

    if (queryError) throw queryError

    if (append) {
      data.value.push(...result)
    } else {
      data.value = result
    }

    totalCount.value = count
    currentPage.value++
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  currentPage.value = 0
  fetchData(false)
}

const loadMore = () => {
  if (hasMore.value && !loading.value) {
    fetchData(true)
  }
}

onMounted(() => {
  fetchData()
})
</script>
```

## 状態管理パターン

### コンポーザブル状態管理

```javascript
// stores/useUserStore.js
import { ref, computed, readonly } from 'vue'
import { supabase } from '@/lib/supabase'

// プライベート状態
const _user = ref(null)
const _loading = ref(false)
const _error = ref(null)

// パブリックリアクティブ状態
export const user = readonly(_user)
export const loading = readonly(_loading)
export const error = readonly(_error)

// 算出状態
export const isAuthenticated = computed(() => !!_user.value)
export const userRole = computed(() => _user.value?.role || 'guest')
export const userPermissions = computed(() => _user.value?.permissions || [])

// アクション
export const login = async (email, password) => {
  _loading.value = true
  _error.value = null

  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) throw error

    _user.value = data.user
    return data.user
  } catch (err) {
    _error.value = err
  } finally {
    _loading.value = false
  }
}

export const logout = async () => {
  _loading.value = true

  try {
    await supabase.auth.signOut()
    _user.value = null
  } catch (err) {
    _error.value = err
  } finally {
    _loading.value = false
  }
}

export const updateProfile = async (updates) => {
  _loading.value = true
  _error.value = null

  try {
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', _user.value.id)
      .select()
      .single()

    if (error) throw error

    _user.value = { ..._user.value, ...data }
    return data
  } catch (err) {
    _error.value = err
  } finally {
    _loading.value = false
  }
}

// 認証状態の初期化
supabase.auth.onAuthStateChange((event, session) => {
  _user.value = session?.user || null
})

// useUserStoreコンポーザブル
export function useUserStore() {
  return {
    // 状態
    user,
    loading,
    error,
    
    // 算出
    isAuthenticated,
    userRole,
    userPermissions,
    
    // アクション
    login,
    logout,
    updateProfile
  }
}
```

### Provide/Injectによるグローバル状態

```vue
<!-- GlobalStateProvider.vue -->
<template>
  <div>
    <slot />
  </div>
</template>

<script setup>
import { provide, reactive, computed } from 'vue'

// グローバルアプリケーション状態
const state = reactive({
  theme: 'light',
  sidebarOpen: false,
  notifications: [],
  user: null,
  preferences: {
    language: 'ja',
    timezone: 'Asia/Tokyo',
    animations: true
  }
})

// 算出ゲッター
const getters = {
  isDarkTheme: computed(() => state.theme === 'dark'),
  unreadNotifications: computed(() => 
    state.notifications.filter(n => !n.read).length
  ),
  isAuthenticated: computed(() => !!state.user)
}

// アクション/ミューテーション
const actions = {
  setTheme(theme) {
    state.theme = theme
    document.documentElement.setAttribute('data-theme', theme)
  },
  
  toggleSidebar() {
    state.sidebarOpen = !state.sidebarOpen
  },
  
  addNotification(notification) {
    state.notifications.push({
      id: Date.now(),
      read: false,
      createdAt: new Date(),
      ...notification
    })
  },
  
  markNotificationRead(id) {
    const notification = state.notifications.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  },
  
  updatePreferences(updates) {
    Object.assign(state.preferences, updates)
  }
}

// グローバル状態を提供
provide('globalState', {
  state,
  getters,
  actions
})
</script>
```

```javascript
// composables/useGlobalState.js
import { inject } from 'vue'

export function useGlobalState() {
  const globalState = inject('globalState')
  
  if (!globalState) {
    throw new Error('useGlobalStateはGlobalStateProvider内で使用する必要があります')
  }
  
  return globalState
}
```

## 非同期コンポーネントパターン

### Suspenseによる遅延ローディング

```vue
<!-- AsyncComponentWrapper.vue -->
<template>
  <Suspense>
    <template #default>
      <component :is="dynamicComponent" v-bind="componentProps" />
    </template>
    
    <template #fallback>
      <div class="flex items-center justify-center p-8">
        <div class="text-center">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <p class="mt-2 text-sm text-base-content/70">コンポーネントを読み込み中...</p>
        </div>
      </div>
    </template>
  </Suspense>
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue'

const props = defineProps({
  componentName: { type: String, required: true },
  componentProps: { type: Object, default: () => ({}) }
})

const dynamicComponent = computed(() => {
  return defineAsyncComponent({
    loader: () => import(`@/components/${props.componentName}.vue`),
    loadingComponent: () => h('div', { class: 'loading loading-dots loading-lg' }),
    errorComponent: () => h('div', { 
      class: 'alert alert-error' 
    }, 'コンポーネントの読み込みに失敗しました'),
    delay: 200,
    timeout: 10000
  })
})
</script>
```

### エラーバウンダリパターン

```vue
<!-- ErrorBoundary.vue -->
<template>
  <div>
    <div v-if="error" class="alert alert-error shadow-lg">
      <div>
        <svg class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h3 class="font-bold">問題が発生しました！</h3>
          <div class="text-xs">{{ error.message }}</div>
        </div>
      </div>
      <div class="flex-none">
        <button @click="retry" class="btn btn-sm btn-ghost">
          再試行
        </button>
        <button v-if="showDetails" @click="toggleDetails" class="btn btn-sm btn-ghost">
          詳細を{{ showingDetails ? '隠す' : '表示' }}
        </button>
      </div>
    </div>
    
    <div v-if="error && showingDetails" class="mt-4 p-4 bg-base-200 rounded-lg">
      <details>
        <summary class="cursor-pointer font-medium">エラー詳細</summary>
        <pre class="mt-2 text-xs overflow-x-auto">{{ error.stack }}</pre>
      </details>
    </div>
    
    <slot v-if="!error" />
  </div>
</template>

<script setup>
import { ref, onErrorCaptured, nextTick } from 'vue'

const props = defineProps({
  fallback: {
    type: [String, Object],
    default: null
  },
  showDetails: {
    type: Boolean,
    default: process.env.NODE_ENV === 'development'
  }
})

const emit = defineEmits(['error'])

const error = ref(null)
const showingDetails = ref(false)

const retry = async () => {
  error.value = null
  await nextTick()
}

const toggleDetails = () => {
  showingDetails.value = !showingDetails.value
}

onErrorCaptured((err, instance, info) => {
  error.value = err
  emit('error', { error: err, instance, info })
  
  console.error('ErrorBoundaryがエラーをキャッチしました:', err)
  
  // エラーがさらに伝播しないようにfalseを返す
  return false
})
</script>
```

## フォームコンポーネント

### 高度なフォームビルダー

```vue
<!-- FormBuilder.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div
      v-for="field in fields"
      :key="field.name"
      class="form-control w-full"
    >
      <!-- 動的フィールドレンダリング -->
      <component
        :is="getFieldComponent(field.type)"
        v-model="formData[field.name]"
        v-bind="field.props"
        :error="errors[field.name]"
        :touched="touched[field.name]"
        @blur="handleFieldBlur(field.name)"
        @input="handleFieldInput(field.name, $event)"
      />
    </div>
    
    <!-- フォームアクション -->
    <div class="form-control mt-8">
      <div class="flex justify-end space-x-4">
        <button
          v-if="showCancel"
          type="button"
          @click="handleCancel"
          class="btn btn-outline"
        >
          キャンセル
        </button>
        
        <button
          type="submit"
          :disabled="!isValid || isSubmitting"
          class="btn btn-primary"
        >
          <span v-if="isSubmitting" class="loading loading-spinner loading-sm mr-2"></span>
          {{ submitText }}
        </button>
      </div>
    </div>
  </form>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import InputField from './form-fields/InputField.vue'
import SelectField from './form-fields/SelectField.vue'
import TextareaField from './form-fields/TextareaField.vue'
import CheckboxField from './form-fields/CheckboxField.vue'
import RadioField from './form-fields/RadioField.vue'
import FileUploadField from './form-fields/FileUploadField.vue'
import DatePickerField from './form-fields/DatePickerField.vue'

const props = defineProps({
  fields: { type: Array, required: true },
  initialData: { type: Object, default: () => ({}) },
  submitText: { type: String, default: '送信' },
  showCancel: { type: Boolean, default: false },
  validation: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['submit', 'cancel', 'change'])

// フォーム状態
const formData = reactive({ ...props.initialData })
const errors = reactive({})
const touched = reactive({})
const isSubmitting = ref(false)

// フィールドコンポーネントマッピング
const fieldComponents = {
  text: InputField,
  email: InputField,
  password: InputField,
  number: InputField,
  select: SelectField,
  textarea: TextareaField,
  checkbox: CheckboxField,
  radio: RadioField,
  file: FileUploadField,
  date: DatePickerField
}

const getFieldComponent = (type) => {
  return fieldComponents[type] || InputField
}

// バリデーション
const isValid = computed(() => {
  return Object.keys(errors).length === 0 && 
         props.fields.every(field => 
           !field.required || formData[field.name]
         )
})

const validateField = (fieldName, value) => {
  const field = props.fields.find(f => f.name === fieldName)
  const rules = props.validation[fieldName]
  
  delete errors[fieldName]
  
  // 必須バリデーション
  if (field.required && (!value || value.toString().trim() === '')) {
    errors[fieldName] = `${field.label || fieldName} は必須項目です`
    return false
  }
  
  // カスタムバリデーションルール
  if (rules) {
    for (const rule of Array.isArray(rules) ? rules : [rules]) {
      const result = rule(value, formData)
      if (result !== true) {
        errors[fieldName] = result
        return false
      }
    }
  }
  
  return true
}

// イベントハンドラー
const handleFieldInput = (fieldName, value) => {
  formData[fieldName] = value
  
  if (touched[fieldName]) {
    validateField(fieldName, value)
  }
  
  emit('change', { field: fieldName, value, formData: { ...formData } })
}

const handleFieldBlur = (fieldName) => {
  touched[fieldName] = true
  validateField(fieldName, formData[fieldName])
}

const handleSubmit = async () => {
  // 全フィールドのバリデーション
  let isFormValid = true
  props.fields.forEach(field => {
    touched[field.name] = true
    const isFieldValid = validateField(field.name, formData[field.name])
    if (!isFieldValid) isFormValid = false
  })
  
  if (!isFormValid) return
  
  isSubmitting.value = true
  
  try {
    await emit('submit', { ...formData })
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

// 不足しているフィールドのフォームデータを初期化
props.fields.forEach(field => {
  if (!(field.name in formData)) {
    formData[field.name] = field.defaultValue || ''
  }
})
</script>
```

## パフォーマンス最適化

### 仮想スクロールコンポーネント

```vue
<!-- VirtualScroll.vue -->
<template>
  <div
    ref="containerRef"
    class="virtual-scroll-container overflow-auto"
    :style="{ height: containerHeight + 'px' }"
    @scroll="handleScroll"
  >
    <!-- 仮想スペーサー（上） -->
    <div :style="{ height: offsetY + 'px' }"></div>
    
    <!-- 表示アイテム -->
    <div
      v-for="item in visibleItems"
      :key="item.index"
      :ref="(el) => setItemRef(el, item.index)"
      class="virtual-scroll-item"
      :style="{ height: itemHeight + 'px' }"
    >
      <slot
        :item="item.data"
        :index="item.index"
        :isVisible="true"
      >
        {{ item.data }}
      </slot>
    </div>
    
    <!-- 仮想スペーサー（下） -->
    <div :style="{ height: remainingHeight + 'px' }"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  itemHeight: { type: Number, default: 50 },
  containerHeight: { type: Number, default: 400 },
  overscan: { type: Number, default: 5 },
  threshold: { type: Number, default: 0.1 }
})

const emit = defineEmits(['scroll', 'visible-range-change'])

const containerRef = ref(null)
const itemRefs = ref(new Map())
const scrollTop = ref(0)
const isScrolling = ref(false)
const scrollTimeout = ref(null)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const startIndex = computed(() => {
  return Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.overscan)
})

const endIndex = computed(() => {
  const visibleCount = Math.ceil(props.containerHeight / props.itemHeight)
  return Math.min(
    props.items.length - 1,
    startIndex.value + visibleCount + props.overscan * 2
  )
})

const visibleItems = computed(() => {
  const items = []
  for (let i = startIndex.value; i <= endIndex.value; i++) {
    if (props.items[i]) {
      items.push({
        index: i,
        data: props.items[i]
      })
    }
  }
  return items
})

const offsetY = computed(() => startIndex.value * props.itemHeight)

const remainingHeight = computed(() => {
  const visibleHeight = (endIndex.value - startIndex.value + 1) * props.itemHeight
  return Math.max(0, totalHeight.value - offsetY.value - visibleHeight)
})

const setItemRef = (el, index) => {
  if (el) {
    itemRefs.value.set(index, el)
  } else {
    itemRefs.value.delete(index)
  }
}

const handleScroll = (event) => {
  scrollTop.value = event.target.scrollTop
  isScrolling.value = true
  
  // 既存のタイムアウトをクリア
  if (scrollTimeout.value) {
    clearTimeout(scrollTimeout.value)
  }
  
  // スクロール終了検出用の新しいタイムアウトを設定
  scrollTimeout.value = setTimeout(() => {
    isScrolling.value = false
  }, 150)
  
  emit('scroll', {
    scrollTop: scrollTop.value,
    isScrolling: isScrolling.value
  })
}

// パフォーマンス追跡用Intersection Observer
let intersectionObserver = null

const setupIntersectionObserver = () => {
  if (!window.IntersectionObserver) return
  
  intersectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        const index = parseInt(entry.target.dataset.index)
        if (entry.isIntersecting) {
          // アイテムが表示されている
        } else {
          // アイテムが表示されていない
        }
      })
    },
    {
      root: containerRef.value,
      threshold: props.threshold
    }
  )
}

// 特定のアイテムにスクロール
const scrollToItem = (index, alignment = 'auto') => {
  if (!containerRef.value) return
  
  const targetScrollTop = index * props.itemHeight
  let scrollPosition = targetScrollTop
  
  switch (alignment) {
    case 'start':
      scrollPosition = targetScrollTop
      break
    case 'center':
      scrollPosition = targetScrollTop - (props.containerHeight - props.itemHeight) / 2
      break
    case 'end':
      scrollPosition = targetScrollTop - props.containerHeight + props.itemHeight
      break
    case 'auto':
    default:
      const currentScrollTop = containerRef.value.scrollTop
      const currentScrollBottom = currentScrollTop + props.containerHeight
      
      if (targetScrollTop < currentScrollTop) {
        scrollPosition = targetScrollTop
      } else if (targetScrollTop + props.itemHeight > currentScrollBottom) {
        scrollPosition = targetScrollTop - props.containerHeight + props.itemHeight
      } else {
        return // アイテムは既に表示されている
      }
  }
  
  containerRef.value.scrollTo({
    top: Math.max(0, scrollPosition),
    behavior: 'smooth'
  })
}

// トップにスクロール
const scrollToTop = () => {
  if (containerRef.value) {
    containerRef.value.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// ボトムにスクロール
const scrollToBottom = () => {
  if (containerRef.value) {
    containerRef.value.scrollTo({ 
      top: totalHeight.value, 
      behavior: 'smooth' 
    })
  }
}

// 表示範囲変更の監視
watch([startIndex, endIndex], ([newStart, newEnd], [oldStart, oldEnd]) => {
  if (newStart !== oldStart || newEnd !== oldEnd) {
    emit('visible-range-change', {
      startIndex: newStart,
      endIndex: newEnd,
      visibleItems: visibleItems.value
    })
  }
})

onMounted(() => {
  setupIntersectionObserver()
})

onUnmounted(() => {
  if (intersectionObserver) {
    intersectionObserver.disconnect()
  }
  if (scrollTimeout.value) {
    clearTimeout(scrollTimeout.value)
  }
})

defineExpose({
  scrollToItem,
  scrollToTop,
  scrollToBottom,
  containerRef
})
</script>

<style scoped>
.virtual-scroll-container {
  @apply relative;
}

.virtual-scroll-item {
  @apply flex-shrink-0;
}
</style>
```

### 遅延ローディング用コンポーザブル

```javascript
// composables/useLazyLoading.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useLazyLoading(options = {}) {
  const {
    threshold = 0.1,
    rootMargin = '50px',
    triggerOnce = true
  } = options

  const targetRef = ref(null)
  const isVisible = ref(false)
  const isLoaded = ref(false)

  let observer = null

  const observe = () => {
    if (!targetRef.value || !window.IntersectionObserver) return

    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          isVisible.value = true
          
          if (triggerOnce) {
            isLoaded.value = true
            disconnect()
          }
        } else {
          isVisible.value = false
        }
      },
      {
        threshold,
        rootMargin
      }
    )

    observer.observe(targetRef.value)
  }

  const disconnect = () => {
    if (observer) {
      observer.disconnect()
      observer = null
    }
  }

  onMounted(() => {
    observe()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    targetRef,
    isVisible,
    isLoaded,
    observe,
    disconnect
  }
}
```

## テストパターン

### コンポーネントテストセットアップ

```javascript
// tests/components/Button.test.js
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Button from '@/components/Button.vue'

describe('Buttonコンポーネント', () => {
  const createWrapper = (props = {}, slots = {}) => {
    return mount(Button, {
      props,
      slots,
      global: {
        stubs: {
          // テスト用アイコンコンポーネントのスタブ
          'icon-component': true
        }
      }
    })
  }

  it('デフォルトpropsで正しくレンダリングされる', () => {
    const wrapper = createWrapper()
    
    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.classes()).toContain('btn')
    expect(wrapper.classes()).toContain('btn-primary')
  })

  it('バリアントクラスが正しく適用される', () => {
    const wrapper = createWrapper({ variant: 'secondary' })
    
    expect(wrapper.classes()).toContain('btn-secondary')
    expect(wrapper.classes()).not.toContain('btn-primary')
  })

  it('クリック時にクリックイベントが発行される', async () => {
    const wrapper = createWrapper()
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('無効時はクリックイベントが発行されない', async () => {
    const wrapper = createWrapper({ disabled: true })
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('click')).toBeUndefined()
  })

  it('ローディング状態が正しく表示される', () => {
    const wrapper = createWrapper({ loading: true })
    
    expect(wrapper.find('.loading').exists()).toBe(true)
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('スロットコンテンツがレンダリングされる', () => {
    const wrapper = createWrapper({}, {
      default: 'クリックしてください！'
    })
    
    expect(wrapper.text()).toContain('クリックしてください！')
  })

  it('非同期クリックハンドラーを処理する', async () => {
    const asyncHandler = vi.fn().mockResolvedValue('success')
    const wrapper = createWrapper({ onClick: asyncHandler })
    
    await wrapper.find('button').trigger('click')
    
    expect(asyncHandler).toHaveBeenCalledTimes(1)
  })
})
```

### コンポーザブルテスト

```javascript
// tests/composables/useApi.test.js
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useApi } from '@/composables/useApi'

// Supabaseのモック
vi.mock('@/lib/supabase', () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => Promise.resolve({ data: [], error: null }))
      }))
    }))
  }
}))

describe('useApiコンポーザブル', () => {
  let api

  beforeEach(() => {
    api = useApi()
  })

  it('正しいデフォルト状態で初期化される', () => {
    expect(api.state.loading).toBe(false)
    expect(api.state.error).toBe(null)
    expect(api.state.data).toBe(null)
  })

  it('成功したAPIコールを処理する', async () => {
    const mockData = [{ id: 1, name: 'テスト' }]
    const mockApiCall = vi.fn().mockResolvedValue(mockData)

    const result = await api.execute(mockApiCall)

    expect(api.state.data).toEqual(mockData)
    expect(api.state.error).toBe(null)
    expect(api.state.loading).toBe(false)
    expect(result).toEqual(mockData)
  })

  it('APIエラーを処理する', async () => {
    const mockError = new Error('APIエラー')
    const mockApiCall = vi.fn().mockRejectedValue(mockError)

    await expect(api.execute(mockApiCall)).rejects.toThrow('APIエラー')
    
    expect(api.state.error).toBe(mockError)
    expect(api.state.data).toBe(null)
    expect(api.state.loading).toBe(false)
  })

  it('APIコール中にローディング状態を設定する', async () => {
    const mockApiCall = vi.fn(() => new Promise(resolve => {
      // プロミスが保留中のローディング状態をチェック
      expect(api.state.loading).toBe(true)
      resolve([])
    }))

    await api.execute(mockApiCall)
    
    expect(api.state.loading).toBe(false)
  })

  it('状態を正しくリセットする', () => {
    api.state.data = 'テスト'
    api.state.error = new Error('テスト')
    api.state.loading = true

    api.reset()

    expect(api.state.data).toBe(null)
    expect(api.state.error).toBe(null)
    expect(api.state.loading).toBe(false)
  })
})
```

## TypeScript統合

### コンポーネント型定義

```typescript
// types/components.ts
import type { Component, VNode } from 'vue'

export interface BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
}

export interface ButtonProps extends BaseComponentProps {
  type?: 'button' | 'submit' | 'reset'
  outline?: boolean
  ghost?: boolean
  icon?: Component
  href?: string
  to?: string | object
}

export interface FormFieldProps {
  modelValue?: any
  label?: string
  placeholder?: string
  error?: string
  helpText?: string
  required?: boolean
  disabled?: boolean
  readonly?: boolean
}

export interface InputProps extends FormFieldProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url'
  autocomplete?: string
  pattern?: string
  minlength?: number
  maxlength?: number
}

export interface SelectProps extends FormFieldProps {
  options: Array<{
    value: any
    label: string
    disabled?: boolean
  }>
  multiple?: boolean
  searchable?: boolean
}

export interface TableColumn {
  key: string
  title: string
  sortable?: boolean
  formatter?: (value: any, row: any) => string
  component?: Component
  width?: string
  align?: 'left' | 'center' | 'right'
  headerClass?: string
  cellClass?: string
}

export interface TableAction {
  key: string
  label: string
  icon?: Component
  class?: string
  disabled?: (row: any) => boolean
  visible?: (row: any) => boolean
}

export interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string | string[]
    borderWidth?: number
  }>
}

// コンポーネントインスタンス型
export type ButtonInstance = InstanceType<typeof import('@/components/Button.vue')['default']>
export type InputInstance = InstanceType<typeof import('@/components/InputField.vue')['default']>
export type TableInstance = InstanceType<typeof import('@/components/DataTable.vue')['default']>
```

### 型付きコンポーザブル

```typescript
// composables/useTypedApi.ts
import { ref, reactive, computed, type Ref, type ComputedRef } from 'vue'
import type { Database } from '@/types/database'

export interface ApiState<T> {
  loading: boolean
  error: Error | null
  data: T | null
}

export interface ApiReturn<T> {
  state: ApiState<T>
  isLoading: ComputedRef<boolean>
  hasError: ComputedRef<boolean>
  hasData: ComputedRef<boolean>
  execute: (apiCall: () => Promise<T>) => Promise<T>
  reset: () => void
}

export function useTypedApi<T = any>(): ApiReturn<T> {
  const state = reactive<ApiState<T>>({
    loading: false,
    error: null,
    data: null
  })

  const isLoading = computed(() => state.loading)
  const hasError = computed(() => !!state.error)
  const hasData = computed(() => !!state.data)

  const execute = async (apiCall: () => Promise<T>): Promise<T> => {
    state.loading = true
    state.error = null

    try {
      const result = await apiCall()
      state.data = result
      return result
    } catch (error) {
      state.error = error as Error
      throw error
    } finally {
      state.loading = false
    }
  }

  const reset = () => {
    state.loading = false
    state.error = null
    state.data = null
  }

  return {
    state,
    isLoading,
    hasError,
    hasData,
    execute,
    reset
  }
}

// 型付きSupabaseクエリコンポーザブル
export interface SupabaseQueryOptions {
  select?: string
  filters?: Array<{
    column: string
    operator: string
    value: any
  }>
  orderBy?: {
    column: string
    ascending: boolean
  }
  limit?: number
  realtime?: boolean
}

export function useSupabaseQuery<T extends keyof Database['public']['Tables']>(
  table: T,
  options: SupabaseQueryOptions = {}
) {
  type TableData = Database['public']['Tables'][T]['Row']
  
  const data = ref<TableData[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const count = ref(0)

  // 実装はJavaScript版と同様だが、適切なTypeScript型付きで

  return {
    data: data as Ref<TableData[]>,
    loading,
    error,
    count,
    refresh: () => {}, // 実装
    cleanup: () => {} // 実装
  }
}
```

### 型安全なイベントシステム

```typescript
// types/events.ts
export interface AppEvents {
  'user:login': { user: User }
  'user:logout': void
  'notification:show': { 
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    duration?: number
  }
  'modal:open': { id: string; props?: Record<string, any> }
  'modal:close': { id: string }
  'route:change': { from: string; to: string }
}

// composables/useTypedEventBus.ts
import type { AppEvents } from '@/types/events'

type EventHandler<T> = T extends void ? () => void : (payload: T) => void

class TypedEventBus {
  private events: Record<string, Function[]> = {}

  emit<K extends keyof AppEvents>(event: K, payload: AppEvents[K]): void {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(payload))
    }
  }

  on<K extends keyof AppEvents>(event: K, callback: EventHandler<AppEvents[K]>): void {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(callback)
  }

  off<K extends keyof AppEvents>(event: K, callback: EventHandler<AppEvents[K]>): void {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback)
    }
  }

  once<K extends keyof AppEvents>(event: K, callback: EventHandler<AppEvents[K]>): void {
    const onceCallback = (payload: AppEvents[K]) => {
      callback(payload)
      this.off(event, onceCallback as EventHandler<AppEvents[K]>)
    }
    this.on(event, onceCallback as EventHandler<AppEvents[K]>)
  }
}

export const eventBus = new TypedEventBus()

export function useTypedEventBus() {
  return eventBus
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

- **[🎨 デザインシステム概要](./00_design_overview.md)** - ブランドガイドラインとデザイントークン
- **[⚙️ Tailwind CSS設定](./01_tailwind_config.md)** - CSS設定とカスタマイズ
- **[🧩 DaisyUIコンポーネントガイド](./02_daisyui_components.md)** - UIコンポーネント実装パターン
- **[🎨 デザイントークンリファレンス](./04_design_tokens.md)** - トークンの詳細仕様
- **[🔐 認証パターン](../01_authentication/03_vue_auth_patterns.md)** - 認証機能の実装
- **[📊 Supabase統合](../03_library_docs/02_supabase_integration.md)** - データベース連携

## リソース

- [Vue 3 ドキュメント](https://vuejs.org)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Vue Test Utils](https://test-utils.vuejs.org)
- [Vitestテスティングフレームワーク](https://vitest.dev)
- [TypeScript Vueプラグイン](https://github.com/johnsoncodehk/volar)
- [Vue DevTools](https://devtools.vuejs.org)