# Document Command - ドキュメント生成・整備

## 概要
Vue.js + REST APIプロジェクトの既存コードから包括的なドキュメントを自動生成し、開発者・利用者・運用者向けの実用的なドキュメンテーションを整備します。コードの実装内容を分析して、実際の動作に基づいた正確なドキュメントを作成します。

## 使用方法
```
/document [ドキュメント種別またはスコープ]
```

### ドキュメント種別
- `api` - API仕様書
- `components` - コンポーネントカタログ
- `architecture` - アーキテクチャドキュメント
- `deployment` - デプロイメントガイド
- `user` - ユーザーマニュアル
- `developer` - 開発者ガイド
- `all` - 全てのドキュメント

## 実行プロセス

### 1. コードベース分析

#### 1.1 プロジェクト構造の解析
```javascript
// プロジェクト構成の自動解析
const analyzeProjectStructure = async () => {
  const structure = {
    framework: await detectFramework(), // Vue.js version, build tool
    architecture: await analyzeArchitecture(), // SPA/SSR, routing pattern
    stateManagement: await detectStateManagement(), // Pinia/Vuex
    styling: await detectStyling(), // Tailwind, CSS modules, etc.
    backend: await analyzeBackend(), // Supabase configuration
    deployment: await analyzeDeployment(), // Vercel, Netlify, etc.
    testing: await analyzeTestSetup() // Vitest, Cypress, etc.
  }
  
  return structure
}

// コンポーネント階層の分析
const analyzeComponentHierarchy = async () => {
  const components = await findVueComponents()
  const hierarchy = new Map()
  
  for (const component of components) {
    const analysis = await analyzeComponent(component)
    hierarchy.set(component.path, {
      name: component.name,
      type: classifyComponentType(analysis), // 'page', 'layout', 'ui', 'form'
      dependencies: analysis.imports,
      props: analysis.props,
      emits: analysis.emits,
      slots: analysis.slots,
      composition: analysis.composition, // composables used
      complexity: calculateComplexity(analysis)
    })
  }
  
  return buildHierarchyTree(hierarchy)
}
```

#### 1.2 API エンドポイントの抽出
```javascript
// Supabase操作の自動抽出
const extractSupabaseOperations = async () => {
  const operations = {
    tables: new Map(),
    realtime: [],
    auth: [],
    storage: [],
    functions: []
  }
  
  // .from() 呼び出しの解析
  const fromCalls = await findPatterns([
    /\.from\(['"`](\w+)['"`]\)/g,
    /supabase\.from\(['"`](\w+)['"`]\)/g
  ])
  
  for (const call of fromCalls) {
    const tableName = call.match[1]
    if (!operations.tables.has(tableName)) {
      operations.tables.set(tableName, {
        name: tableName,
        operations: [],
        relations: [],
        rls: []
      })
    }
    
    // 操作タイプの特定
    const operationType = await analyzeOperation(call.context)
    operations.tables.get(tableName).operations.push({
      type: operationType, // 'select', 'insert', 'update', 'delete'
      context: call.context,
      file: call.file,
      line: call.line
    })
  }
  
  // リアルタイム機能の抽出
  const realtimeCalls = await findPatterns([
    /\.channel\(['"`]([^'"`]+)['"`]\)/g,
    /\.on\(['"`]([^'"`]+)['"`]/g
  ])
  
  operations.realtime = realtimeCalls.map(call => ({
    channel: call.match[1],
    events: extractRealtimeEvents(call.context),
    file: call.file
  }))
  
  return operations
}

// データベーススキーマの推測
const inferDatabaseSchema = async (supabaseOperations) => {
  const schema = new Map()
  
  for (const [tableName, tableOps] of supabaseOperations.tables) {
    const columns = new Set()
    const relationships = []
    
    // SELECT文から列名を抽出
    for (const op of tableOps.operations) {
      if (op.type === 'select') {
        const selectColumns = extractSelectColumns(op.context)
        selectColumns.forEach(col => columns.add(col))
      }
      
      // 外部キー関係の推測
      const relations = extractRelations(op.context)
      relationships.push(...relations)
    }
    
    schema.set(tableName, {
      name: tableName,
      columns: Array.from(columns),
      relationships,
      estimatedStructure: await generateTableStructure(tableName, columns)
    })
  }
  
  return schema
}
```

### 2. コンポーネントドキュメント生成

#### 2.1 コンポーネントカタログの作成
```vue
<!-- 自動生成されるコンポーネントドキュメント例 -->
<!-- UserProfile.vue の分析結果 -->
<template>
  <div class="component-doc">
    <h2>UserProfile</h2>
    
    <!-- 概要 -->
    <section class="overview">
      <h3>概要</h3>
      <p>ユーザーのプロフィール情報を表示・編集するコンポーネント</p>
      
      <div class="meta">
        <span class="badge">UI Component</span>
        <span class="badge">Form Handling</span>
        <span class="badge">Supabase Integration</span>
      </div>
    </section>
    
    <!-- Props -->
    <section class="props">
      <h3>Props</h3>
      <table class="props-table">
        <thead>
          <tr>
            <th>名前</th>
            <th>型</th>
            <th>必須</th>
            <th>デフォルト</th>
            <th>説明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>userId</code></td>
            <td><code>String</code></td>
            <td>Yes</td>
            <td>-</td>
            <td>表示するユーザーのID</td>
          </tr>
          <tr>
            <td><code>editable</code></td>
            <td><code>Boolean</code></td>
            <td>No</td>
            <td><code>false</code></td>
            <td>編集モードの有効/無効</td>
          </tr>
          <tr>
            <td><code>showAvatar</code></td>
            <td><code>Boolean</code></td>
            <td>No</td>
            <td><code>true</code></td>
            <td>アバター画像の表示/非表示</td>
          </tr>
        </tbody>
      </table>
    </section>
    
    <!-- Events -->
    <section class="events">
      <h3>Events</h3>
      <table class="events-table">
        <thead>
          <tr>
            <th>イベント名</th>
            <th>ペイロード</th>
            <th>説明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>profile-updated</code></td>
            <td><code>{ profile: Object }</code></td>
            <td>プロフィール更新時に発火</td>
          </tr>
          <tr>
            <td><code>edit-cancelled</code></td>
            <td>-</td>
            <td>編集キャンセル時に発火</td>
          </tr>
        </tbody>
      </table>
    </section>
    
    <!-- Slots -->
    <section class="slots">
      <h3>Slots</h3>
      <table class="slots-table">
        <thead>
          <tr>
            <th>スロット名</th>
            <th>スコープ</th>
            <th>説明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>header</code></td>
            <td><code>{ user, isEditing }</code></td>
            <td>ヘッダー部分のカスタマイズ</td>
          </tr>
          <tr>
            <td><code>actions</code></td>
            <td><code>{ save, cancel, edit }</code></td>
            <td>アクションボタンのカスタマイズ</td>
          </tr>
        </tbody>
      </table>
    </section>
    
    <!-- 使用例 -->
    <section class="usage">
      <h3>使用例</h3>
      
      <h4>基本的な使用方法</h4>
      <code-block language="vue">
&lt;template&gt;
  &lt;UserProfile 
    :user-id="currentUser.id"
    :editable="true"
    @profile-updated="handleProfileUpdate"
  /&gt;
&lt;/template&gt;

&lt;script setup&gt;
import UserProfile from '@/components/UserProfile.vue'

const handleProfileUpdate = (data) =&gt; {
  console.log('Profile updated:', data.profile)
}
&lt;/script&gt;
      </code-block>
      
      <h4>カスタムヘッダーの使用</h4>
      <code-block language="vue">
&lt;UserProfile :user-id="userId"&gt;
  &lt;template #header="{ user, isEditing }"&gt;
    &lt;div class="custom-header"&gt;
      &lt;h2&gt;{{ user.displayName }}&lt;/h2&gt;
      &lt;span v-if="isEditing" class="editing-indicator"&gt;編集中&lt;/span&gt;
    &lt;/div&gt;
  &lt;/template&gt;
&lt;/UserProfile&gt;
      </code-block>
    </section>
    
    <!-- 依存関係 -->
    <section class="dependencies">
      <h3>依存関係</h3>
      <ul>
        <li><strong>Composables</strong>: useAuth, useProfile</li>
        <li><strong>Components</strong>: Avatar, FormField, LoadingSpinner</li>
        <li><strong>Services</strong>: ProfilesAPI</li>
        <li><strong>Utilities</strong>: validateEmail, formatDate</li>
      </ul>
    </section>
  </div>
</template>
```

#### 2.2 自動スタイルガイド生成
```javascript
// デザインシステムの自動抽出
const generateStyleGuide = async () => {
  const styleGuide = {
    colors: await extractColors(),
    typography: await extractTypography(),
    spacing: await extractSpacing(),
    components: await extractComponentStyles(),
    utilities: await extractUtilityClasses()
  }
  
  // Tailwind CSS クラスの分析
  const tailwindClasses = await analyzeTailwindUsage()
  
  return {
    ...styleGuide,
    designTokens: generateDesignTokens(styleGuide),
    componentLibrary: generateComponentLibrary(tailwindClasses)
  }
}

// カラーパレットの抽出
const extractColors = async () => {
  const colorPatterns = [
    /(?:bg-|text-|border-)(\w+-\d+)/g, // Tailwind colors
    /#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})/g, // Hex colors
    /rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/g // RGB colors
  ]
  
  const colors = new Map()
  
  for (const file of await findStyleFiles()) {
    const content = await readFile(file)
    
    for (const pattern of colorPatterns) {
      const matches = content.matchAll(pattern)
      for (const match of matches) {
        const colorValue = match[0]
        if (!colors.has(colorValue)) {
          colors.set(colorValue, {
            value: colorValue,
            usage: [],
            category: categorizeColor(colorValue)
          })
        }
        colors.get(colorValue).usage.push(file)
      }
    }
  }
  
  return organizeColorPalette(colors)
}
```

### 3. API ドキュメント生成

#### 3.1 Supabase API 仕様書
```markdown
# API 仕様書

## 概要
このAPIはSupabaseを基盤とした認証・データベース・リアルタイム機能を提供します。

## 認証

### ログイン
```javascript
// エンドポイント: supabase.auth.signInWithPassword()
const login = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  })
  
  return { user: data.user, session: data.session, error }
}
```

**パラメータ:**
- `email` (string, required): ユーザーのメールアドレス
- `password` (string, required): パスワード

**レスポンス:**
```javascript
{
  user: User | null,
  session: Session | null,
  error: AuthError | null
}
```

### ユーザー登録
```javascript
const register = async (email, password, metadata = {}) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: metadata
    }
  })
  
  return { user: data.user, error }
}
```

## データベース操作

### Profiles テーブル

#### プロフィール取得
```javascript
// GET /profiles/:id
const getProfile = async (userId) => {
  const { data, error } = await supabase
    .from('profiles')
    .select(`
      id,
      user_id,
      display_name,
      avatar_url,
      bio,
      created_at,
      updated_at
    `)
    .eq('user_id', userId)
    .single()
  
  return { profile: data, error }
}
```

**RLS ポリシー:**
```sql
-- 全員が閲覧可能
CREATE POLICY "Profiles are viewable by everyone" 
  ON profiles FOR SELECT 
  USING (true);

-- 本人のみ更新可能
CREATE POLICY "Users can update own profile" 
  ON profiles FOR UPDATE 
  USING (auth.uid() = user_id);
```

#### プロフィール更新
```javascript
const updateProfile = async (userId, updates) => {
  const { data, error } = await supabase
    .from('profiles')
    .update(updates)
    .eq('user_id', userId)
    .select()
    .single()
  
  return { profile: data, error }
}
```

**バリデーション:**
- `display_name`: 最大50文字
- `bio`: 最大500文字
- `avatar_url`: 有効なURL形式

### Posts テーブル

#### 記事一覧取得
```javascript
const getPosts = async (filters = {}) => {
  let query = supabase
    .from('posts')
    .select(`
      id,
      title,
      content,
      status,
      created_at,
      updated_at,
      author:profiles(display_name, avatar_url),
      comments(count)
    `)
    .eq('status', 'published')
    .order('created_at', { ascending: false })
  
  // フィルター適用
  if (filters.category) {
    query = query.eq('category', filters.category)
  }
  
  if (filters.author) {
    query = query.eq('user_id', filters.author)
  }
  
  const { data, error } = await query
  return { posts: data, error }
}
```

## リアルタイム機能

### コメントのリアルタイム更新
```javascript
const subscribeToComments = (postId, callback) => {
  const channel = supabase
    .channel(`comments:${postId}`)
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'comments',
        filter: `post_id=eq.${postId}`
      },
      callback
    )
    .subscribe()
  
  return channel // クリーンアップ用
}

// 使用例
const channel = subscribeToComments('post-123', (payload) => {
  console.log('Comment change:', payload)
  // UIの更新処理
})

// クリーンアップ
onUnmounted(() => {
  supabase.removeChannel(channel)
})
```

## エラーハンドリング

### 共通エラーパターン
```javascript
const handleSupabaseError = (error) => {
  const errorMap = {
    // 認証エラー
    'invalid_credentials': 'メールアドレスまたはパスワードが正しくありません',
    'email_not_confirmed': 'メールアドレスの確認が必要です',
    'signup_disabled': '新規登録は現在無効になっています',
    
    // データベースエラー
    '23505': 'この値は既に使用されています（重複エラー）',
    '23503': '関連するデータが存在しません（外部キー制約）',
    'PGRST116': '指定されたデータが見つかりません',
    
    // RLSエラー
    'new row violates row-level security': 'このデータにアクセスする権限がありません',
    
    // ネットワークエラー
    'NetworkError': 'ネットワーク接続を確認してください',
    'timeout': 'リクエストがタイムアウトしました'
  }
  
  return errorMap[error.code] || 
         errorMap[error.message] || 
         '予期しないエラーが発生しました'
}
```

## レート制限

- **認証API**: 60リクエスト/分
- **データベースクエリ**: 100リクエスト/分
- **リアルタイム接続**: 100接続/分

## セキュリティ

### Row Level Security (RLS)
全てのテーブルでRLSが有効化されています。

### API キーの管理
```javascript
// 環境変数での管理
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// サービスキーは決してフロントエンドで使用しない
```
```

### 4. アーキテクチャドキュメント生成

#### 4.1 システム構成図の自動生成
```javascript
// アーキテクチャ図の自動生成
const generateArchitectureDiagram = async (projectStructure) => {
  const diagram = {
    frontend: {
      framework: 'Vue.js 3',
      buildTool: 'Vite',
      stateManagement: 'Pinia',
      routing: 'Vue Router',
      styling: 'Tailwind CSS + DaisyUI',
      testing: 'Vitest + Vue Test Utils'
    },
    
    backend: {
      database: 'PostgreSQL (Supabase)',
      auth: 'Supabase Auth',
      api: 'Supabase REST API',
      realtime: 'Supabase Realtime',
      storage: 'Supabase Storage'
    },
    
    deployment: {
      hosting: await detectHostingPlatform(),
      cdn: await detectCDN(),
      ci: await detectCI()
    },
    
    external: await detectExternalServices()
  }
  
  return generateMermaidDiagram(diagram)
}

// Mermaid 図の生成
const generateMermaidDiagram = (architecture) => {
  return `
graph TB
    subgraph "Frontend"
        A[Vue.js App]
        B[Vue Router]
        C[Pinia Store]
        D[Components]
        
        A --> B
        A --> C
        A --> D
    end
    
    subgraph "Supabase Backend"
        E[PostgreSQL DB]
        F[Auth Service]
        G[Realtime Engine]
        H[Storage]
        I[Edge Functions]
        
        E <--> F
        E <--> G
    end
    
    subgraph "External Services"
        J[Email Provider]
        K[File CDN]
        L[Analytics]
    end
    
    A <--> E
    A <--> F
    A <--> G
    A <--> H
    
    F --> J
    H --> K
    A --> L
  `
}
```

### 5. デプロイメントドキュメント生成

#### 5.1 自動デプロイガイド作成
```javascript
// デプロイメント設定の分析
const analyzeDeploymentConfig = async () => {
  const config = {
    buildCommand: await extractBuildCommand(),
    outputDirectory: await detectOutputDir(),
    environmentVariables: await extractEnvVars(),
    dependencies: await analyzeDependencies(),
    hostingPlatform: await detectHostingPlatform()
  }
  
  return generateDeploymentGuide(config)
}

// プラットform別のデプロイガイド生成
const generateDeploymentGuide = (config) => {
  const guides = {
    vercel: generateVercelGuide(config),
    netlify: generateNetlifyGuide(config),
    heroku: generateHerokuGuide(config)
  }
  
  return guides[config.hostingPlatform] || guides.vercel
}
```

## 出力形式

### ドキュメント構成（docs/）
```
docs/
├── README.md                    # プロジェクト概要
├── getting-started.md          # セットアップガイド
├── architecture/
│   ├── overview.md             # システム概要
│   ├── database-schema.md      # DB設計
│   ├── api-design.md          # API設計
│   └── security.md            # セキュリティ設計
├── components/
│   ├── README.md              # コンポーネント概要
│   ├── ui-components.md       # UIコンポーネント
│   ├── form-components.md     # フォームコンポーネント
│   └── layout-components.md   # レイアウトコンポーネント
├── api/
│   ├── authentication.md     # 認証API
│   ├── profiles.md           # プロフィールAPI
│   ├── posts.md              # 記事API
│   └── comments.md           # コメントAPI
├── development/
│   ├── setup.md              # 開発環境構築
│   ├── coding-standards.md   # コーディング規約
│   ├── testing.md            # テスト指針
│   └── deployment.md         # デプロイメント
└── user-guide/
    ├── user-manual.md        # ユーザーマニュアル
    ├── admin-guide.md        # 管理者ガイド
    └── troubleshooting.md    # トラブルシューティング
```

### 自動生成されるREADME.md
```markdown
# Vue.js + REST API アプリケーション

## 概要
このプロジェクトは Vue.js 3 と Supabase を使用したモダンなウェブアプリケーションです。

## 技術スタック

### フロントエンド
- **Framework**: Vue.js 3.4.21
- **Build Tool**: Vite 5.1.0
- **状態管理**: Pinia 2.1.7
- **ルーティング**: Vue Router 4.3.0
- **スタイリング**: Tailwind CSS 3.4.1 + DaisyUI 4.7.2
- **テスティング**: Vitest 1.3.1 + Vue Test Utils

### バックエンド
- **Database**: PostgreSQL (Supabase)
- **認証**: Supabase Auth
- **API**: Supabase REST API
- **リアルタイム**: Supabase Realtime
- **ストレージ**: Supabase Storage

### デプロイメント
- **ホスティング**: Vercel
- **CI/CD**: GitHub Actions
- **環境管理**: Vercel Environment Variables

## プロジェクト構造

```
src/
├── components/          # Vueコンポーネント
│   ├── ui/             # 再利用可能UIコンポーネント
│   ├── forms/          # フォームコンポーネント
│   └── layout/         # レイアウトコンポーネント
├── composables/        # Composition API ロジック
├── stores/             # Pinia ストア
├── views/              # ページコンポーネント
├── router/             # ルーティング設定
├── utils/              # ユーティリティ関数
├── types/              # JSDoc型定義
└── styles/             # グローバルスタイル
```

## セットアップ

### 前提条件
- Node.js 18.x以上
- npm または yarn
- Supabaseアカウント

### インストール

1. リポジトリのクローン
```bash
git clone <repository-url>
cd <project-name>
```

2. 依存関係のインストール
```bash
npm install
```

3. 環境変数の設定
```bash
cp .env.example .env.local
```

以下の環境変数を設定してください：
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. 開発サーバーの起動
```bash
npm run dev
```

## 主要機能

### 認証システム
- ユーザー登録・ログイン
- ソーシャルログイン (Google, GitHub)
- パスワードリセット
- プロフィール管理

### コンテンツ管理
- 記事の作成・編集・削除
- カテゴリ管理
- コメントシステム
- リアルタイム更新

### ユーザー体験
- レスポンシブデザイン
- ダークモード対応
- プログレッシブウェブアプリ (PWA)
- オフライン対応

## 開発ガイド

### コーディング規約
- [ESLint設定](.eslintrc.js) と [Prettier設定](.prettierrc) に従う
- Composition API を優先使用
- JSDoc での型安全性を重視
- コンポーネントは単一責任原則に従う

### テスト
```bash
# 単体テスト実行
npm run test

# カバレッジ付きテスト
npm run test:coverage

# E2Eテスト実行
npm run test:e2e
```

### ビルド・デプロイ
```bash
# プロダクションビルド
npm run build

# プレビュー
npm run preview

# デプロイ（Vercel）
vercel --prod
```

## ドキュメント

- [📖 コンポーネントガイド](docs/components/README.md)
- [🔌 API仕様書](docs/api/README.md)
- [🏗️ アーキテクチャ設計](docs/architecture/overview.md)
- [🚀 デプロイメントガイド](docs/development/deployment.md)
- [👥 ユーザーマニュアル](docs/user-guide/user-manual.md)

## ライセンス
MIT License

## 貢献
プルリクエスト歓迎！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## サポート
質問や問題がある場合は [Issues](../../issues) で報告してください。
```

## TodoWrite連携

ドキュメント作成のタスクを自動生成：

```javascript
const documentationTasks = [
  {
    id: 'doc-001',
    content: 'プロジェクト構造の分析と基本情報収集',
    status: 'completed',
    priority: 'high'
  },
  {
    id: 'doc-002',
    content: 'コンポーネントカタログの生成',
    status: 'in_progress',
    priority: 'high'
  },
  {
    id: 'doc-003',
    content: 'API仕様書の作成',
    status: 'pending',
    priority: 'high'
  },
  {
    id: 'doc-004',
    content: 'アーキテクチャドキュメントの生成',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'doc-005',
    content: 'デプロイメントガイドの作成',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'doc-006',
    content: 'ユーザーマニュアルの作成',
    status: 'pending',
    priority: 'medium'
  },
  {
    id: 'doc-007',
    content: '開発者ガイドの整備',
    status: 'pending',
    priority: 'low'
  },
  {
    id: 'doc-008',
    content: 'ドキュメントの校正と公開',
    status: 'pending',
    priority: 'low'
  }
]
```

## ドキュメント品質チェック

```javascript
// ドキュメント品質の自動チェック
const documentQualityCheck = {
  completeness: {
    components: 'カタログ化されたコンポーネントの割合',
    api: 'ドキュメント化されたAPIエンドポイントの割合',
    coverage: '全体的なドキュメント化カバレッジ'
  },
  
  accuracy: {
    codeSync: 'コードとドキュメントの同期状態',
    examples: '実行可能なコード例の検証',
    links: '内部リンクの有効性チェック'
  },
  
  usability: {
    navigation: 'ドキュメント間のナビゲーション',
    search: '検索機能の効果性',
    feedback: 'ユーザーフィードバックの仕組み'
  }
}
```

## 継続的ドキュメント更新

```javascript
// CI/CDでの自動ドキュメント更新
const automatedDocUpdate = {
  triggers: [
    'コンポーネントの追加・変更',
    'API エンドポイントの変更',
    '依存関係の更新',
    'デプロイメント設定の変更'
  ],
  
  actions: [
    'コンポーネントカタログの再生成',
    'API仕様書の更新',
    'チェンジログの自動生成',
    'ドキュメントのデプロイ'
  ]
}
```

## まとめ

このコマンドはVue.js + REST APIプロジェクトの包括的なドキュメント生成を支援します：

1. **自動生成**: コードベースから実際の実装に基づいたドキュメントを自動生成
2. **多角的視点**: 開発者・ユーザー・運用者それぞれに最適化されたドキュメント
3. **継続的更新**: コード変更に連動した自動ドキュメント更新
4. **品質保証**: ドキュメントの完全性・正確性・使いやすさの継続的改善

生成されたドキュメントは他のコマンド（analyze, enhance, fix, refactor）の基礎資料としても活用できます。