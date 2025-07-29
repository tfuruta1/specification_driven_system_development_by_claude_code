# Fix Command - バグ修正・問題解決

## 概要
Vue.js + REST APIプロジェクトの特定の問題やバグを迅速に特定・修正し、根本原因を解決します。トラブルシューティングから修正、テスト、再発防止まで包括的にサポートします。

## 使用方法
```
/fix [問題の説明またはエラーメッセージ]
```

## 実行プロセス

### 1. 問題の特定と分析

#### 1.1 エラー情報の収集
```javascript
// エラー情報の構造化
const analyzeErrorInfo = (userInput) => {
  return {
    type: classifyErrorType(userInput), // 'runtime', 'build', 'console', 'visual'
    severity: assessSeverity(userInput), // 'critical', 'high', 'medium', 'low'
    context: extractContext(userInput),
    symptoms: extractSymptoms(userInput),
    reproduction: extractReproductionSteps(userInput)
  }
}

// エラータイプの分類
const classifyErrorType = (input) => {
  const patterns = {
    runtime: /error.*at.*runtime|TypeError|ReferenceError|Cannot read property/i,
    build: /build.*failed|compilation.*error|vite.*error|webpack.*error/i,
    console: /console.*error|uncaught.*exception|failed.*to.*fetch/i,
    visual: /not.*displayed|broken.*layout|styling.*issue|responsive.*problem/i,
    performance: /slow.*loading|performance.*issue|memory.*leak|lag/i,
    auth: /authentication.*failed|unauthorized|login.*issue|supabase.*auth/i,
    database: /database.*error|query.*failed|rls.*policy|supabase.*error/i
  }
  
  for (const [type, pattern] of Object.entries(patterns)) {
    if (pattern.test(input)) return type
  }
  
  return 'unknown'
}
```

#### 1.2 システム状態の診断
```javascript
// 現在のシステム状態を確認
const performSystemDiagnostics = async () => {
  const diagnostics = {
    environment: await checkEnvironment(),
    dependencies: await checkDependencies(),
    services: await checkServices(),
    database: await checkDatabase(),
    auth: await checkAuthentication(),
    build: await checkBuildStatus()
  }
  
  return diagnostics
}

// 環境チェック
const checkEnvironment = async () => {
  return {
    node: process.version,
    npm: await getPackageVersion('npm'),
    vue: await getPackageVersion('vue'),
    vite: await getPackageVersion('vite'),
    supabase: await getPackageVersion('@supabase/supabase-js'),
    envVars: checkRequiredEnvVars()
  }
}

// Supabase接続チェック
const checkSupabaseConnection = async () => {
  try {
    const { data, error } = await supabase.from('profiles').select('count').limit(1)
    return {
      status: 'connected',
      latency: performance.now(),
      error: null
    }
  } catch (err) {
    return {
      status: 'error',
      error: err.message,
      possibleCauses: [
        '不正なSupabase URL',
        '無効なAPIキー',
        'ネットワーク接続問題',
        'RLSポリシーの設定問題'
      ]
    }
  }
}
```

### 2. 問題の分類と優先度評価

#### 2.1 問題の分類マトリックス
```javascript
// 問題の重要度と緊急度を評価
const prioritizeIssue = (errorInfo, systemState) => {
  const matrix = {
    critical: {
      criteria: [
        'アプリケーションが起動しない',
        'データ損失の可能性',
        '認証システムの障害',
        '本番環境での全機能停止'
      ],
      response: 'immediate', // 15分以内
      team: ['tech-lead', 'devops']
    },
    high: {
      criteria: [
        '主要機能の障害',
        'データベース接続エラー',
        'ビルド失敗',
        'ユーザー体験への重大な影響'
      ],
      response: '1-2時間',
      team: ['developer', 'qa']
    },
    medium: {
      criteria: [
        'UI表示の問題',
        'パフォーマンス低下',
        '一部機能の不具合',
        '開発環境での問題'
      ],
      response: '4-8時間',
      team: ['developer']
    },
    low: {
      criteria: [
        'コンソール警告',
        '微細なスタイリング問題',
        '開発者体験の改善'
      ],
      response: '1-2日',
      team: ['developer']
    }
  }
  
  return assessPriority(errorInfo, matrix)
}
```

### 3. 修正戦略の立案

#### 3.1 Vue.js特有の問題パターン
```javascript
// Vue.js関連の一般的な問題と解決策
const vueFixPatterns = {
  reactivity: {
    symptoms: ['データが更新されない', 'computed が動作しない'],
    commonCauses: [
      'reactive() の代わりに Object.assign を使用',
      'deep watch の不備',
      'v-model のバインディング問題'
    ],
    solutions: [
      {
        issue: 'Object.assign での状態更新',
        fix: `
// 問題のあるコード
Object.assign(state.user, newUserData)

// 修正版
state.user = { ...state.user, ...newUserData }
// または
Object.keys(newUserData).forEach(key => {
  state.user[key] = newUserData[key]
})`,
        explanation: 'Vue 3のreactivityシステムは新しいオブジェクト参照を必要とします'
      }
    ]
  },
  
  composition: {
    symptoms: ['setup関数でエラー', 'composableが動作しない'],
    solutions: [
      {
        issue: 'ref/reactive の誤用',
        fix: `
// 問題: primitiveにreactiveを使用
const count = reactive(0) // ❌

// 修正: primitiveにはrefを使用
const count = ref(0) // ✅

// 問題: objectにrefを使用
const user = ref({ name: 'John' }) // 動作するが非効率

// 修正: objectにはreactiveを使用
const user = reactive({ name: 'John' }) // ✅`
      }
    ]
  },
  
  lifecycle: {
    symptoms: ['メモリリーク', 'unmountでエラー'],
    solutions: [
      {
        issue: 'イベントリスナーのクリーンアップ不備',
        fix: `
// 修正版のlifecycle管理
import { onMounted, onUnmounted } from 'vue'

export default {
  setup() {
    const handleResize = () => { /* ... */ }
    
    onMounted(() => {
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })
  }
}`
      }
    ]
  }
}

// Supabase特有の問題パターン
const supabaseFixPatterns = {
  auth: {
    symptoms: ['ログインできない', '認証状態が保持されない'],
    solutions: [
      {
        issue: 'セッション管理の問題',
        fix: `
// 正しいセッション管理
const { data: { session } } = await supabase.auth.getSession()

// セッション変更の監視
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_OUT') {
    // クリーンアップ処理
    router.push('/login')
  }
})`
      }
    ]
  },
  
  database: {
    symptoms: ['クエリが失敗する', 'RLSエラー'],
    solutions: [
      {
        issue: 'RLSポリシーの設定不備',
        fix: `
-- 適切なRLSポリシー
CREATE POLICY "Users can view own profile" 
  ON profiles FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" 
  ON profiles FOR UPDATE 
  USING (auth.uid() = user_id) 
  WITH CHECK (auth.uid() = user_id);`
      }
    ]
  },
  
  realtime: {
    symptoms: ['リアルタイム更新が動作しない', 'メモリリーク'],
    solutions: [
      {
        issue: 'チャンネルのクリーンアップ不備',
        fix: `
// 適切なリアルタイム管理
const setupRealtime = (postId) => {
  const channel = supabase
    .channel(\`post:\${postId}\`)
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'comments',
      filter: \`post_id=eq.\${postId}\`
    }, handleChange)
    .subscribe()
  
  // クリーンアップ関数を返す
  return () => {
    supabase.removeChannel(channel)
  }
}`
      }
    ]
  }
}
```

### 4. 修正の実装

#### 4.1 段階的修正アプローチ
```javascript
// 修正の実装計画
const createFixPlan = (problemAnalysis) => {
  return {
    phases: [
      {
        name: '緊急対応',
        duration: '15-30分',
        actions: [
          '問題の一時的な回避策実装',
          'エラーログの詳細確認',
          '影響範囲の限定'
        ],
        rollback: '変更の即座の取り消し可能'
      },
      {
        name: '根本原因の修正',
        duration: '1-4時間',
        actions: [
          '原因の特定と修正',
          'ローカル環境でのテスト',
          '関連する箇所の確認'
        ],
        validation: '修正内容の動作確認'
      },
      {
        name: '品質保証',
        duration: '30分-2時間',
        actions: [
          'テストケースの作成・実行',
          'リグレッションテスト',
          'パフォーマンス影響の確認'
        ]
      },
      {
        name: '再発防止',
        duration: '30分-1時間',
        actions: [
          'lint ルールの追加',
          'ドキュメント更新',
          'チーム共有'
        ]
      }
    ]
  }
}
```

#### 4.2 修正コードの生成
```vue
<!-- 問題修正の例: リアクティビティの問題 -->
<template>
  <div class="user-profile">
    <h2>{{ user.name }}</h2>
    <p>フォロワー: {{ user.followers_count }}</p>
    
    <!-- 修正: v-model の適切な使用 -->
    <input 
      v-model="editableUser.name" 
      @blur="updateUser"
      :disabled="updating"
    />
    
    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 修正前: 直接 reactive オブジェクトを編集
// const user = reactive(userStore.currentUser) // ❌ 参照の問題

// 修正後: 適切な状態管理
const user = computed(() => userStore.currentUser)
const editableUser = reactive({ ...user.value })
const updating = ref(false)
const error = ref(null)

// 修正: deep watch で変更を監視
watch(
  () => user.value,
  (newUser) => {
    if (newUser) {
      Object.assign(editableUser, newUser)
    }
  },
  { deep: true }
)

const updateUser = async () => {
  if (!editableUser.name.trim()) {
    error.value = '名前は必須です'
    return
  }
  
  updating.value = true
  error.value = null
  
  try {
    await userStore.updateUser(editableUser)
  } catch (err) {
    error.value = '更新に失敗しました: ' + err.message
    // 修正: エラー時のロールバック
    Object.assign(editableUser, user.value)
  } finally {
    updating.value = false
  }
}
</script>
```

### 5. テストと検証

#### 5.1 修正内容のテスト
```javascript
// 修正内容のテストプラン
const createTestPlan = (fixDetails) => {
  return {
    unit: [
      {
        component: fixDetails.affectedComponents,
        scenarios: [
          '正常なデータでの動作確認',
          'エラーケースの動作確認',
          'エッジケースの動作確認'
        ]
      }
    ],
    integration: [
      {
        flow: '修正箇所を含む機能フロー',
        scenarios: [
          'ユーザーシナリオの実行',
          '他コンポーネントとの連携確認',
          'データ整合性の確認'
        ]
      }
    ],
    regression: [
      {
        scope: '修正の影響範囲',
        scenarios: [
          '既存機能への影響確認',
          'パフォーマンス影響の測定',
          'セキュリティ影響の確認'
        ]
      }
    ]
  }
}

// 自動テストの生成例
describe('UserProfile修正のテスト', () => {
  it('ユーザー名の更新が正常に動作する', async () => {
    const wrapper = mount(UserProfile, {
      props: { userId: '123' }
    })
    
    // 修正前の問題: reactivityが動作しない
    await wrapper.setData({ 'editableUser.name': '新しい名前' })
    await wrapper.find('input').trigger('blur')
    
    expect(mockUserStore.updateUser).toHaveBeenCalledWith({
      name: '新しい名前'
    })
  })
  
  it('エラー時に適切にロールバックされる', async () => {
    mockUserStore.updateUser.mockRejectedValue(new Error('更新失敗'))
    
    const wrapper = mount(UserProfile)
    const originalName = wrapper.vm.user.name
    
    await wrapper.setData({ 'editableUser.name': '無効な名前' })
    await wrapper.find('input').trigger('blur')
    
    // エラー後、元の値に戻ることを確認
    expect(wrapper.vm.editableUser.name).toBe(originalName)
    expect(wrapper.find('.alert-error').exists()).toBe(true)
  })
})
```

### 6. 再発防止策

#### 6.1 プロセス改善
```javascript
// 再発防止のためのチェックリスト
const preventionMeasures = {
  codeQuality: [
    {
      measure: 'ESLint ルールの追加',
      implementation: `
// .eslintrc.js に追加
rules: {
  // Vue 3 reactivity のベストプラクティス
  'vue/no-ref-as-operand': 'error',
  'vue/no-reactive-value-as-computed': 'error',
  
  // Supabase のベストプラクティス
  'no-unused-vars': ['error', { 
    varsIgnorePattern: '^(supabase|channel)$' 
  }]
}`
    },
    {
      measure: 'JSDoc 型チェックの強化',
      implementation: `
// types/supabase.js

/**
 * @typedef {Object} DatabaseError
 * @property {string} code - エラーコード
 * @property {string} details - エラー詳細
 * @property {string} [hint] - ヒント
 */

/**
 * 型安全なエラーハンドリング
 * @param {DatabaseError} error - データベースエラー
 * @returns {string} ユーザーフレンドリーなエラーメッセージ
 */
const handleDatabaseError = (error) => {
  switch (error.code) {
    case '23505': // unique_violation
      return 'この値は既に使用されています'
    case '23503': // foreign_key_violation  
      return '関連するデータが存在しません'
    default:
      return 'データベースエラーが発生しました'
  }
}`
    }
  ],
  
  monitoring: [
    {
      measure: 'エラー監視の実装',
      implementation: `
// utils/errorTracking.js
export const trackError = (error, context) => {
  // Sentry, LogRocket などへの送信
  console.error('Application Error:', {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href
  })
}`
    }
  ],
  
  documentation: [
    {
      measure: 'トラブルシューティングガイドの作成',
      location: 'docs/troubleshooting.md',
      content: '一般的な問題と解決策のドキュメント化'
    }
  ]
}
```

## 出力形式

### 修正レポート（.tmp/fix_report.md）
```markdown
# 修正レポート

## 問題概要
- **報告日時**: 2024-01-15 14:30:00
- **問題**: ユーザープロフィール更新時にリアクティビティが動作しない
- **影響範囲**: ユーザープロフィール機能
- **優先度**: High

## 1. 問題分析

### 症状
- ユーザー名を変更してもUIに反映されない
- コンソールエラーは発生しない
- ページリロードすると正しい値が表示される

### 根本原因
```javascript
// 問題のあったコード
const user = reactive(userStore.currentUser) // ❌

// 問題: userStore.currentUser が変更されても、
// reactive() で作成した user オブジェクトは更新されない
```

### 影響箇所
- `src/components/UserProfile.vue`
- `src/stores/user.js`（間接的）

## 2. 修正内容

### 実装した修正
```javascript
// 修正後のコード
const user = computed(() => userStore.currentUser) // ✅
const editableUser = reactive({ ...user.value })

// 変更の監視とシンク
watch(
  () => user.value,
  (newUser) => {
    if (newUser) {
      Object.assign(editableUser, newUser)
    }
  },
  { deep: true }
)
```

### 修正理由
1. `computed` を使用してストアの状態を適切に追跡
2. 編集用の独立した reactive オブジェクトを作成
3. `watch` でストアの変更を監視し、編集用オブジェクトを同期

## 3. テスト結果

### 実行したテスト
- ✅ ユーザー名更新の正常動作確認
- ✅ エラー時のロールバック動作確認
- ✅ 他のプロフィール項目への影響確認
- ✅ パフォーマンス影響の測定（影響なし）

### テストケース
```javascript
// 追加されたテストケース
describe('UserProfile Reactivity Fix', () => {
  it('stores state changes are reflected in UI', async () => {
    // テスト実装...
  })
})
```

## 4. 再発防止策

### 実装済み対策
1. **ESLint ルール追加**
   ```javascript
   // .eslintrc.js
   'vue/no-ref-as-operand': 'error'
   ```

2. **ドキュメント更新**
   - `docs/vue-reactivity-best-practices.md` を作成
   - チーム内での知識共有実施

3. **コードレビューチェックリスト更新**
   - Reactive状態管理のチェック項目を追加

## 5. 影響範囲と検証

### 影響したファイル
- `src/components/UserProfile.vue`（修正）
- `tests/components/UserProfile.test.js`（テスト追加）
- `.eslintrc.js`（ルール追加）

### 検証済み項目
- ✅ 既存機能への影響なし
- ✅ パフォーマンス劣化なし
- ✅ セキュリティ影響なし
- ✅ 他のコンポーネントへの影響なし

## 6. デプロイメント

### デプロイ手順
1. ステージング環境でのテスト完了
2. コードレビュー完了
3. 本番環境へのデプロイ実行（2024-01-15 16:00）

### ロールバック計画
- 修正前のコードをバックアップ済み
- 問題発生時は即座にロールバック可能

## 7. 学習内容

### チームで共有すべき知識
1. Vue 3 Composition API でのリアクティビティの正しい使用法
2. computed vs reactive の適切な使い分け
3. ストア状態の変更監視パターン

### ベストプラクティス
```javascript
// 推奨パターン
const storeValue = computed(() => store.someValue)
const editableValue = reactive({ ...storeValue.value })

// 監視パターン
watch(storeValue, (newValue) => {
  Object.assign(editableValue, newValue)
}, { deep: true })
```

## 8. 次のアクション

### 短期（1週間以内）
- [ ] 類似パターンが他にないかコードベース全体をレビュー
- [ ] チーム勉強会でVue 3リアクティビティについて共有

### 中期（1ヶ月以内）
- [ ] 自動テストでリアクティビティの問題を検出するツール検討
- [ ] 開発ガイドラインの更新

## 9. まとめ

この修正により、ユーザープロフィール更新機能が正常に動作するようになりました。
根本原因はVue 3のリアクティビティシステムの理解不足によるものでしたが、
適切な修正と再発防止策により、同様の問題を防ぐことができます。

**修正時間**: 2時間30分
**テスト時間**: 1時間15分
**総所要時間**: 3時間45分
```

## TodoWrite連携

修正作業のタスクを自動生成：

```javascript
const fixTasks = [
  {
    id: 'fix-001',
    content: '問題の分析と原因特定',
    status: 'completed',
    priority: 'high'
  },
  {
    id: 'fix-002',
    content: '緊急対応（一時的な回避策）',
    status: 'completed',
    priority: 'high'
  },
  {
    id: 'fix-003',
    content: '根本原因の修正実装',
    status: 'in_progress',
    priority: 'high'
  },
  {
    id: 'fix-004',
    content: 'ローカル環境でのテスト実行',
    status: 'pending',
    priority: 'high'
  },
  {
    id: 'fix-005',
    content: 'ユニットテストの作成',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'fix-006',
    content: 'リグレッションテスト実行',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'fix-007',
    content: '再発防止策の実装',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'fix-008',
    content: 'ドキュメント更新と知識共有',
    status: 'pending',
    priority: 'low'
  }
]
```

## 緊急対応フロー

```javascript
// 緊急度に応じた対応フロー
const emergencyFlow = {
  critical: {
    response: '15分以内',
    actions: [
      '即座の影響範囲確認',
      '一時的な機能停止（必要な場合）',
      'ログ情報の収集',
      'ステークホルダーへの報告'
    ],
    team: ['tech-lead', 'devops', 'pm']
  },
  high: {
    response: '1時間以内',
    actions: [
      '問題の詳細分析',
      '回避策の検討・実装',
      '修正スケジュールの計画',
      '関係者への状況共有'
    ],
    team: ['developer', 'qa']
  }
}
```

## エラーパターン辞書

```javascript
// よくある問題パターンと解決策
const commonPatterns = {
  'hydration-mismatch': {
    symptoms: ['Hydration completed but contains mismatches'],
    solution: 'SSR/SPA環境での差異を確認し、ClientOnlyコンポーネントを使用',
    prevention: 'process.client チェックの実装'
  },
  'supabase-rls-error': {
    symptoms: ['new row violates row-level security'],
    solution: 'RLSポリシーの確認と修正',
    prevention: 'RLSポリシーのテスト自動化'
  },
  'vue-warn-runtime-error': {
    symptoms: ['[Vue warn]: Unhandled error during execution'],
    solution: 'try-catchの実装とエラーバウンダリの設置',
    prevention: 'グローバルエラーハンドラーの実装'
  }
}
```

## まとめ

このコマンドはVue.js + REST APIプロジェクトでの問題解決を迅速かつ体系的にサポートします：

1. **迅速な対応**: 問題の重要度に応じた段階的な対応フロー
2. **根本解決**: 一時的な対処ではなく、根本原因への対応
3. **再発防止**: ESLintルール、テスト、ドキュメント化による予防策
4. **知識蓄積**: チーム全体での学習と問題パターンの蓄積

修正完了後は関連する他のコマンド（analyze, enhance, refactor）での継続的改善を推奨します。