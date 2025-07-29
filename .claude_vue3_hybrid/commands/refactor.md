# Refactor Command - コードリファクタリング・品質改善

## 概要
Vue.js + REST APIプロジェクトのコード品質向上、アーキテクチャ改善、技術的負債解消を目的とした体系的なリファクタリングを実行します。既存機能の動作を保持しながら、保守性、可読性、パフォーマンスを向上させます。

## 使用方法
```
/refactor [対象範囲またはリファクタリング目標]
```

## 前提条件
- `/analyze` コマンドの実行結果があることを推奨
- 既存機能の動作理解
- テストケースの存在（推奨）

## 実行プロセス

### 1. リファクタリング対象の評価

#### 1.1 技術的負債の特定
```javascript
// コード品質メトリクスの測定
const assessCodeQuality = async (targetScope) => {
  const metrics = {
    complexity: await measureComplexity(targetScope),
    duplication: await findDuplication(targetScope),
    coupling: await analyzeCoupling(targetScope),
    cohesion: await measureCohesion(targetScope),
    testCoverage: await checkTestCoverage(targetScope)
  }
  
  return prioritizeRefactoring(metrics)
}

// Vue.js特有のリファクタリング対象
const vueRefactoringTargets = {
  components: [
    {
      pattern: 'Large Components (>300 lines)',
      detection: file => countLines(file) > 300,
      improvement: 'コンポーネント分割',
      priority: 'high'
    },
    {
      pattern: 'Options API Usage',
      detection: file => hasOptionsAPI(file),
      improvement: 'Composition APIへの移行',
      priority: 'medium'
    },
    {
      pattern: 'Props Drilling',
      detection: component => analyzePropsDepth(component) > 3,
      improvement: 'Provide/Inject または Pinia 活用',
      priority: 'medium'
    },
    {
      pattern: 'Mixed Reactivity Patterns',
      detection: file => hasMixedReactivity(file),
      improvement: '一貫したリアクティブパターンへの統一',
      priority: 'high'
    }
  ],
  
  stores: [
    {
      pattern: 'Large Store Files',
      detection: store => Object.keys(store.actions).length > 15,
      improvement: 'ストアの分割・モジュール化',
      priority: 'medium'
    },
    {
      pattern: 'Vuex Usage',
      detection: project => hasVuex(project),
      improvement: 'Piniaへの移行',
      priority: 'high'
    }
  ],
  
  supabase: [
    {
      pattern: 'Direct Supabase Calls in Components',
      detection: component => hasDirectSupabaseCalls(component),
      improvement: 'Composables またはサービス層の導入',
      priority: 'high'
    },
    {
      pattern: 'Inconsistent Error Handling',
      detection: code => hasInconsistentErrorHandling(code),
      improvement: '統一的なエラーハンドリングパターン',
      priority: 'medium'
    }
  ]
}
```

#### 1.2 リファクタリング戦略の策定
```javascript
// リファクタリング戦略の決定
const createRefactoringStrategy = (codeAnalysis, businessConstraints) => {
  return {
    approach: selectApproach(codeAnalysis), // 'incremental' | 'big-bang' | 'strangler-fig'
    phases: createPhases(codeAnalysis),
    riskMitigation: planRiskMitigation(codeAnalysis),
    rollbackPlan: createRollbackPlan(),
    testing: planTestingStrategy(codeAnalysis)
  }
}

// 段階的リファクタリングの例
const incrementalRefactoring = {
  phase1: {
    name: '基盤整備',
    duration: '1-2週間',
    goals: [
      'テストカバレッジの向上',
      'リンティングルールの統一',
      '型定義の強化'
    ],
    deliverables: [
      'テストスイートの整備',
      'ESLint/Prettier設定の統一',
      'JSDoc型注釈の強化（段階的）'
    ]
  },
  
  phase2: {
    name: 'アーキテクチャ改善',
    duration: '2-3週間',
    goals: [
      'コンポーネントの責務分離',
      '状態管理の最適化',
      'API層の抽象化'
    ],
    deliverables: [
      'コンポーネント設計ガイドライン',
      'Pinia移行計画',
      'Composables設計パターン'
    ]
  },
  
  phase3: {
    name: 'パフォーマンス最適化',
    duration: '1-2週間',
    goals: [
      'バンドルサイズの最適化',
      'レンダリング最適化',
      'メモリ使用量の改善'
    ],
    deliverables: [
      '遅延読み込みの実装',
      'メモ化の適用',
      'パフォーマンス監視の実装'
    ]
  }
}
```

### 2. コンポーネントリファクタリング

#### 2.1 大きなコンポーネントの分割
```vue
<!-- リファクタリング前: 大きなコンポーネント -->
<template>
  <div class="user-dashboard">
    <!-- 300行以上のテンプレート -->
    <header class="dashboard-header">
      <!-- ヘッダーロジック -->
    </header>
    
    <nav class="dashboard-nav">
      <!-- ナビゲーションロジック -->
    </nav>
    
    <main class="dashboard-content">
      <!-- メインコンテンツロジック -->
    </main>
    
    <aside class="dashboard-sidebar">
      <!-- サイドバーロジック -->
    </aside>
  </div>
</template>

<script>
// 複雑な Options API （400行以上）
export default {
  data() {
    return {
      // 多数の状態
    }
  },
  computed: {
    // 複雑な computed properties
  },
  methods: {
    // 多数のメソッド
  }
}
</script>
```

```vue
<!-- リファクタリング後: 分割されたコンポーネント -->
<template>
  <div class="user-dashboard">
    <DashboardHeader 
      :user="user" 
      @logout="handleLogout" 
    />
    
    <DashboardLayout>
      <template #navigation>
        <DashboardNavigation 
          :current-route="currentRoute"
          @navigate="handleNavigation"
        />
      </template>
      
      <template #content>
        <DashboardContent 
          :loading="loading"
          :data="dashboardData"
        />
      </template>
      
      <template #sidebar>
        <DashboardSidebar 
          :notifications="notifications"
          :activity="recentActivity"
        />
      </template>
    </DashboardLayout>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDashboard } from '@/composables/useDashboard'
import { useAuth } from '@/composables/useAuth'

// 責務の分離されたComposition API
const { user, logout } = useAuth()
const { 
  loading, 
  dashboardData, 
  notifications, 
  recentActivity,
  currentRoute,
  navigate 
} = useDashboard()

const handleLogout = async () => {
  await logout()
}

const handleNavigation = (route) => {
  navigate(route)
}
</script>
```

#### 2.2 Composables への抽出
```javascript
// リファクタリング前: コンポーネント内に散在するロジック
export default {
  data() {
    return {
      posts: [],
      loading: false,
      error: null,
      filters: {
        category: '',
        status: 'published'
      }
    }
  },
  
  async mounted() {
    await this.fetchPosts()
  },
  
  methods: {
    async fetchPosts() {
      this.loading = true
      try {
        const response = await supabase
          .from('posts')
          .select('*')
          .eq('status', this.filters.status)
          .ilike('category', `%${this.filters.category}%`)
        
        this.posts = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    }
  }
}
```

```javascript
// リファクタリング後: 再利用可能なComposable
// composables/usePosts.js
import { ref, reactive, computed } from 'vue'
import { useSupabase } from './useSupabase'

export function usePosts(initialFilters = {}) {
  const { supabase } = useSupabase()
  
  // 状態管理
  const posts = ref([])
  const loading = ref(false)
  const error = ref(null)
  const filters = reactive({
    category: '',
    status: 'published',
    ...initialFilters
  })
  
  // 算出プロパティ
  const filteredPosts = computed(() => {
    return posts.value.filter(post => {
      if (filters.category && !post.category.includes(filters.category)) {
        return false
      }
      return post.status === filters.status
    })
  })
  
  // アクション
  const fetchPosts = async () => {
    loading.value = true
    error.value = null
    
    try {
      let query = supabase
        .from('posts')
        .select('*')
        .eq('status', filters.status)
      
      if (filters.category) {
        query = query.ilike('category', `%${filters.category}%`)
      }
      
      const { data, error: fetchError } = await query
      
      if (fetchError) throw fetchError
      
      posts.value = data || []
    } catch (err) {
      error.value = err.message
      console.error('Posts fetch error:', err)
    } finally {
      loading.value = false
    }
  }
  
  const updateFilters = (newFilters) => {
    Object.assign(filters, newFilters)
    fetchPosts()
  }
  
  const refreshPosts = () => {
    fetchPosts()
  }
  
  return {
    // 状態
    posts: filteredPosts,
    loading,
    error,
    filters,
    
    // アクション
    fetchPosts,
    updateFilters,
    refreshPosts
  }
}
```

### 3. 状態管理リファクタリング

#### 3.1 VuexからPiniaへの移行
```javascript
// リファクタリング前: Vuex Store
// store/modules/user.js
export default {
  namespaced: true,
  
  state: () => ({
    currentUser: null,
    profile: null,
    loading: false,
    error: null
  }),
  
  mutations: {
    SET_CURRENT_USER(state, user) {
      state.currentUser = user
    },
    SET_PROFILE(state, profile) {
      state.profile = profile
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  
  actions: {
    async fetchProfile({ commit, state }) {
      if (!state.currentUser) return
      
      commit('SET_LOADING', true)
      try {
        const { data, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('user_id', state.currentUser.id)
          .single()
        
        if (error) throw error
        commit('SET_PROFILE', data)
      } catch (error) {
        commit('SET_ERROR', error.message)
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },
  
  getters: {
    isAuthenticated: state => !!state.currentUser,
    userDisplayName: state => {
      return state.profile?.display_name || state.currentUser?.email || 'ゲスト'
    }
  }
}
```

```javascript
// リファクタリング後: Pinia Store
// stores/user.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/lib/supabase'

export const useUserStore = defineStore('user', () => {
  // 状態 (state)
  const currentUser = ref(null)
  const profile = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // 算出プロパティ (getters)
  const isAuthenticated = computed(() => !!currentUser.value)
  
  const userDisplayName = computed(() => {
    return profile.value?.display_name || 
           currentUser.value?.email || 
           'ゲスト'
  })
  
  // アクション (actions)
  const setCurrentUser = (user) => {
    currentUser.value = user
    error.value = null
  }
  
  const setProfile = (profileData) => {
    profile.value = profileData
  }
  
  const fetchProfile = async () => {
    if (!currentUser.value) return
    
    loading.value = true
    error.value = null
    
    try {
      const { data, error: fetchError } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', currentUser.value.id)
        .single()
      
      if (fetchError) throw fetchError
      
      setProfile(data)
    } catch (err) {
      error.value = err.message
      console.error('Profile fetch error:', err)
    } finally {
      loading.value = false
    }
  }
  
  const updateProfile = async (updates) => {
    if (!currentUser.value) throw new Error('認証が必要です')
    
    loading.value = true
    error.value = null
    
    try {
      const { data, error: updateError } = await supabase
        .from('profiles')
        .update(updates)
        .eq('user_id', currentUser.value.id)
        .select()
        .single()
      
      if (updateError) throw updateError
      
      setProfile(data)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 状態
    currentUser,
    profile,
    loading,
    error,
    
    // 算出プロパティ
    isAuthenticated,
    userDisplayName,
    
    // アクション
    setCurrentUser,
    setProfile,
    fetchProfile,
    updateProfile
  }
})
```

### 4. API層の抽象化

#### 4.1 Supabase API の抽象化
```javascript
// リファクタリング前: コンポーネント内の直接的なSupabase呼び出し
export default {
  methods: {
    async createPost() {
      const { data, error } = await supabase
        .from('posts')
        .insert({
          title: this.title,
          content: this.content,
          user_id: this.currentUser.id
        })
      
      if (error) {
        console.error(error)
      }
    }
  }
}
```

```javascript
// リファクタリング後: API層の抽象化
// services/api/posts.js
import { supabase } from '@/lib/supabase'
import { handleSupabaseError } from '@/utils/errorHandling'

export class PostsAPI {
  static async create(postData) {
    try {
      const { data, error } = await supabase
        .from('posts')
        .insert(postData)
        .select()
        .single()
      
      if (error) throw error
      
      return {
        success: true,
        data
      }
    } catch (error) {
      return {
        success: false,
        error: handleSupabaseError(error)
      }
    }
  }
  
  static async findById(id) {
    try {
      const { data, error } = await supabase
        .from('posts')
        .select(`
          *,
          author:profiles(display_name, avatar_url),
          comments(count)
        `)
        .eq('id', id)
        .single()
      
      if (error) throw error
      
      return {
        success: true,
        data
      }
    } catch (error) {
      return {
        success: false,
        error: handleSupabaseError(error)
      }
    }
  }
  
  static async update(id, updates) {
    try {
      const { data, error } = await supabase
        .from('posts')
        .update(updates)
        .eq('id', id)
        .select()
        .single()
      
      if (error) throw error
      
      return {
        success: true,
        data
      }
    } catch (error) {
      return {
        success: false,
        error: handleSupabaseError(error)
      }
    }
  }
  
  static async delete(id) {
    try {
      const { error } = await supabase
        .from('posts')
        .delete()
        .eq('id', id)
      
      if (error) throw error
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: handleSupabaseError(error)
      }
    }
  }
}

// composables/usePosts.js で活用
import { PostsAPI } from '@/services/api/posts'

export const usePosts = () => {
  const createPost = async (postData) => {
    loading.value = true
    
    const result = await PostsAPI.create(postData)
    
    if (result.success) {
      posts.value.unshift(result.data)
    } else {
      error.value = result.error
    }
    
    loading.value = false
    return result
  }
  
  // ...
}
```

### 5. JSDoc型注釈統合

#### 5.1 段階的JSDoc導入
```typescript
// types/database.ts - Supabase型定義
export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          user_id: string
          display_name: string | null
          avatar_url: string | null
          bio: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          display_name?: string | null
          avatar_url?: string | null
          bio?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          display_name?: string | null
          avatar_url?: string | null
          bio?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      posts: {
        Row: {
          id: string
          title: string
          content: string
          user_id: string
          status: 'draft' | 'published' | 'archived'
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          title: string
          content: string
          user_id: string
          status?: 'draft' | 'published' | 'archived'
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          content?: string
          user_id?: string
          status?: 'draft' | 'published' | 'archived'
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
}

// types/api.ts - API レスポンス型
export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  pagination?: {
    total: number
    page: number
    limit: number
    hasMore: boolean
  }
}
```

```typescript
// stores/user.ts - 型安全なPiniaストア
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@supabase/supabase-js'
import type { Database } from '@/types/database'

type Profile = Database['public']['Tables']['profiles']['Row']

export const useUserStore = defineStore('user', () => {
  // 型付き状態
  const currentUser = ref<User | null>(null)
  const profile = ref<Profile | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  
  // 型付き算出プロパティ
  const isAuthenticated = computed((): boolean => !!currentUser.value)
  
  const userDisplayName = computed((): string => {
    return profile.value?.display_name || 
           currentUser.value?.email || 
           'ゲスト'
  })
  
  // 型付きアクション
  const setCurrentUser = (user: User | null): void => {
    currentUser.value = user
    error.value = null
  }
  
  const setProfile = (profileData: Profile | null): void => {
    profile.value = profileData
  }
  
  const updateProfile = async (
    updates: Database['public']['Tables']['profiles']['Update']
  ): Promise<Profile> => {
    if (!currentUser.value) {
      throw new Error('認証が必要です')
    }
    
    loading.value = true
    error.value = null
    
    try {
      // API呼び出し（型安全）
      const result = await ProfilesAPI.update(currentUser.value.id, updates)
      
      if (!result.success) {
        throw new Error(result.error)
      }
      
      setProfile(result.data)
      return result.data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    currentUser,
    profile,
    loading,
    error,
    isAuthenticated,
    userDisplayName,
    setCurrentUser,
    setProfile,
    updateProfile
  }
})
```

### 6. パフォーマンス最適化

#### 6.1 コンポーネントの最適化
```vue
<!-- リファクタリング前: 最適化されていないコンポーネント -->
<template>
  <div>
    <div v-for="item in items" :key="item.id">
      {{ expensiveComputation(item) }}
    </div>
  </div>
</template>

<script setup>
const expensiveComputation = (item) => {
  // 重い計算処理（毎回実行される）
  return item.data.map(d => d.value * Math.random()).join(', ')
}
</script>
```

```vue
<!-- リファクタリング後: 最適化されたコンポーネント -->
<template>
  <div>
    <!-- 仮想スクロール対応 -->
    <virtual-list
      :items="items"
      :item-height="60"
      class="virtual-list"
    >
      <template #default="{ item }">
        <optimized-item
          :key="item.id"
          :item="item"
          :computed-value="computedValues[item.id]"
        />
      </template>
    </virtual-list>
  </div>
</template>

<script setup>
import { computed, useMemo } from 'vue'
import VirtualList from '@/components/ui/VirtualList.vue'
import OptimizedItem from './OptimizedItem.vue'

const props = defineProps<{
  items: Array<{
    id: string
    data: Array<{ value: number }>
  }>
}>()

// メモ化された計算結果
const computedValues = computed(() => {
  const cache = {}
  
  props.items.forEach(item => {
    cache[item.id] = useMemo(
      () => item.data.map(d => d.value * Math.random()).join(', '),
      [item.data] // 依存配列
    )
  })
  
  return cache
})
</script>
```

#### 6.2 バンドル最適化
```javascript
// vite.config.js - 最適化設定
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // ベンダーライブラリの分割
          vendor: ['vue', 'vue-router', 'pinia'],
          supabase: ['@supabase/supabase-js'],
          ui: ['@headlessui/vue', '@heroicons/vue']
        }
      }
    },
    
    // チャンクサイズ警告の調整
    chunkSizeWarningLimit: 1000
  },
  
  // 依存関係の最適化
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', '@supabase/supabase-js']
  }
})

// router/index.js - 遅延読み込みの実装
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    // プリフェッチを無効化（必要な場合のみ読み込み）
    meta: { preload: false }
  }
]
```

## 出力形式

### リファクタリング計画書（.tmp/refactoring_plan.md）
```markdown
# リファクタリング計画書

## 概要
- **対象**: Vue.js + REST API プロジェクト全体
- **期間**: 6週間（3フェーズ）
- **目標**: コード品質向上、保守性改善、パフォーマンス最適化

## 現状分析

### 技術的負債
1. **大きなコンポーネント**: 8個のコンポーネントが300行以上
2. **Options API使用率**: 65%（Composition API移行対象）
3. **直接的なSupabase呼び出し**: 45箇所
4. **テストカバレッジ**: 35%（目標: 80%）

### 優先度評価
| 項目 | 現状 | 目標 | 優先度 | 工数 |
|------|------|------|--------|------|
| コンポーネント分割 | 8個の大型コンポーネント | 全て適切なサイズに分割 | High | 2週間 |
| Composition API移行 | 35% | 90% | Medium | 3週間 |
| API層抽象化 | 0% | 100% | High | 1週間 |
| TypeScript導入 | 0% | 80% | Medium | 2週間 |
| テスト強化 | 35% | 80% | High | 継続的 |

## Phase 1: 基盤整備（2週間）

### Week 1
- [ ] 大型コンポーネントの分析と分割計画策定
- [ ] テストフレームワークの設定強化
- [ ] ESLint/Prettier設定の最適化
- [ ] TypeScriptコンフィグの準備

### Week 2
- [ ] UserDashboard.vue の分割実装
- [ ] PostList.vue の分割実装
- [ ] AdminPanel.vue の分割実装
- [ ] 分割されたコンポーネントのテスト作成

### 成果物
- 3つの大型コンポーネントの分割完了
- テストカバレッジ 50% 達成
- 統一されたコーディング規約

## Phase 2: アーキテクチャ改善（3週間）

### Week 3-4: API層抽象化
- [ ] Supabase API抽象化層の設計
- [ ] PostsAPI クラスの実装
- [ ] UsersAPI クラスの実装
- [ ] CommentsAPI クラスの実装
- [ ] エラーハンドリングの統一

### Week 5: Composition API移行
- [ ] 重要コンポーネントの移行（優先度順）
- [ ] Composables の作成（useAuth, usePosts, useComments）
- [ ] 既存テストの更新

### 成果物
- 統一されたAPI層
- Composition API使用率 70% 達成
- 再利用可能なComposables

## Phase 3: 最適化とTypeScript（1週間）

### Week 6
- [ ] 重要ファイルのTypeScript化
- [ ] パフォーマンス最適化の実装
- [ ] バンドルサイズの最適化
- [ ] 最終的なテスト・ドキュメント整備

### 成果物
- TypeScript化率 80% 達成
- パフォーマンス指標 20% 改善
- 包括的なドキュメント

## リスク管理

### 技術リスク
| リスク | 可能性 | 影響度 | 対策 |
|--------|--------|--------|------|
| 大規模な破綻的変更 | 中 | 高 | 段階的移行、十分なテスト |
| パフォーマンス劣化 | 低 | 中 | 継続的なパフォーマンス測定 |
| TypeScript移行の複雑さ | 高 | 中 | 段階的導入、型定義の段階的作成 |

### 対策
1. **フィーチャーフラグ**: 大きな変更には切り替え可能な機能として実装
2. **A/Bテスト**: パフォーマンス影響のある変更は段階的ロールアウト
3. **ロールバック計画**: 各フェーズでロールバック可能なポイントを設定

## 品質指標

### 目標指標
- **テストカバレッジ**: 35% → 80%
- **ESLintエラー**: 150個 → 0個
- **バンドルサイズ**: 2.5MB → 2.0MB
- **初期表示時間**: 2.3秒 → 1.8秒
- **Lighthouse スコア**: 65 → 85

### 測定方法
```javascript
// パフォーマンス測定の自動化
const performanceMetrics = {
  bundleSize: 'npm run build --report',
  testCoverage: 'npm run test:coverage',
  lintErrors: 'npm run lint --report',
  lighthouse: 'npm run lighthouse:ci'
}
```

## 実装ガイドライン

### コンポーネント分割
1. **単一責任原則**: 1つのコンポーネントは1つの責務
2. **適切なサイズ**: 150行以下を目安
3. **明確なProps/Emits**: インターフェースの明確化

### Composition API移行
```javascript
// 移行パターン
const migrationPattern = {
  data: 'ref() または reactive()',
  computed: 'computed()',
  methods: '通常の関数',
  lifecycle: 'onMounted, onUnmounted など',
  watch: 'watch() または watchEffect()'
}
```

### TypeScript導入
```typescript
// 段階的導入の順序
const migrationOrder = [
  '1. types/database.ts - データベース型定義',
  '2. stores/*.ts - Piniaストア',
  '3. composables/*.ts - Composables',
  '4. components/**/*.vue - コンポーネント',
  '5. pages/**/*.vue - ページコンポーネント'
]
```

## 成功基準

### Phase 1完了時
- [ ] 大型コンポーネント3個の分割完了
- [ ] テストカバレッジ50%達成
- [ ] ESLintエラー50%削減

### Phase 2完了時
- [ ] API層の抽象化完了
- [ ] Composition API使用率70%達成
- [ ] 主要なComposables作成完了

### Phase 3完了時
- [ ] TypeScript化率80%達成
- [ ] パフォーマンス指標20%改善
- [ ] 全体的なコード品質の大幅改善

## 継続的改善

### 自動化
- CI/CDでの品質チェック自動化
- パフォーマンス監視の継続
- 定期的なコードレビューとリファクタリング

### チーム教育
- リファクタリング手法の共有
- ベストプラクティスのドキュメント化
- 定期的な技術勉強会の開催
```

## TodoWrite連携

リファクタリング作業のタスクを自動生成：

```javascript
const refactoringTasks = [
  {
    id: 'refactor-001',
    content: 'リファクタリング対象の分析と優先度評価',
    status: 'completed',
    priority: 'high'
  },
  {
    id: 'refactor-002',
    content: 'Phase 1: テスト環境の整備',
    status: 'in_progress',
    priority: 'high'
  },
  {
    id: 'refactor-003',
    content: 'Phase 1: 大型コンポーネントの分割',
    status: 'pending',
    priority: 'high'
  },
  {
    id: 'refactor-004',
    content: 'Phase 2: API層の抽象化実装',
    status: 'pending',
    priority: 'high'
  },
  {
    id: 'refactor-005',
    content: 'Phase 2: Composition API移行',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'refactor-006',
    content: 'Phase 3: TypeScript導入',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'refactor-007',
    content: 'Phase 3: パフォーマンス最適化',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'refactor-008',
    content: '品質指標の測定と最終検証',
    status: 'pending',
    priority: 'low'
  }
]
```

## まとめ

このコマンドはVue.js + REST APIプロジェクトの体系的なリファクタリングを支援します：

1. **段階的アプローチ**: リスクを最小化した段階的な改善
2. **品質重視**: テスト、型安全性、パフォーマンスの向上
3. **チーム協働**: 明確な計画とドキュメント化による効率的な作業
4. **継続的改善**: 自動化とプロセス改善による持続可能な品質向上

リファクタリング完了後は `/analyze` コマンドで改善効果を測定し、継続的な品質向上を図ることを推奨します。