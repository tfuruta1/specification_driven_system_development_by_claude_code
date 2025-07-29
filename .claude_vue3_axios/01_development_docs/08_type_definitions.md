# 型定義規約

## 1. JSDoc 型注釈規約

### 基本原則
1. **一貫性**: 全プロジェクトで統一された型注釈スタイル
2. **明確性**: 型の意図と使用方法を明確に記述
3. **保守性**: 変更に強い型定義設計
4. **IDE支援**: エディタの自動補完とエラーチェック最適化

### 基本的な型注釈
```javascript
/**
 * @typedef {Object} User
 * @property {string} id - ユーザーID (UUID)
 * @property {string} email - メールアドレス
 * @property {string|null} name - 表示名
 * @property {string|null} avatar_url - アバター画像URL
 * @property {string} created_at - 作成日時 (ISO 8601)
 * @property {string} updated_at - 更新日時 (ISO 8601)
 */

/**
 * @typedef {Object} Post
 * @property {string} id - 投稿ID (UUID)
 * @property {string} user_id - 投稿者ID
 * @property {string} title - タイトル
 * @property {string|null} content - 本文 (Markdown)
 * @property {string|null} excerpt - 抜粋
 * @property {'draft'|'published'|'archived'} status - 公開状態
 * @property {string[]} tags - タグ配列
 * @property {number} view_count - 閲覧数
 * @property {number} like_count - いいね数
 * @property {string|null} published_at - 公開日時
 * @property {string} created_at - 作成日時
 * @property {string} updated_at - 更新日時
 */

/**
 * @typedef {Object} Comment
 * @property {string} id - コメントID
 * @property {string} post_id - 投稿ID
 * @property {string} user_id - コメント投稿者ID
 * @property {string|null} parent_id - 親コメントID（返信の場合）
 * @property {string} content - コメント内容
 * @property {boolean} is_approved - 承認状態
 * @property {string} created_at - 作成日時
 */
```

## 2. 関数の型注釈

### 2.1 基本的な関数
```javascript
/**
 * ユーザー情報を取得する
 * @param {string} userId - ユーザーID
 * @returns {Promise<User|null>} ユーザー情報またはnull
 * @throws {Error} ユーザーが見つからない場合
 */
async function getUser(userId) {
  // 実装
}

/**
 * 投稿一覧を取得する
 * @param {Object} options - 取得オプション
 * @param {number} [options.page=1] - ページ番号
 * @param {number} [options.limit=10] - 取得件数
 * @param {'published'|'draft'|'archived'} [options.status] - ステータスフィルター
 * @param {string[]} [options.tags] - タグフィルター
 * @returns {Promise<{data: Post[], meta: PaginationMeta}>} 投稿一覧とメタ情報
 */
async function getPosts(options = {}) {
  // 実装
}

/**
 * フォームデータをバリデーションする
 * @param {Object} formData - フォームデータ
 * @param {ValidationRule[]} rules - バリデーションルール
 * @returns {ValidationResult} バリデーション結果
 */
function validateForm(formData, rules) {
  // 実装
}
```

### 2.2 イベントハンドラー
```javascript
/**
 * フォーム送信ハンドラー
 * @param {Event} event - フォームイベント
 * @returns {Promise<void>}
 */
async function handleSubmit(event) {
  // 実装
}

/**
 * ファイル選択ハンドラー
 * @param {Event} event - ファイル選択イベント
 * @param {(file: File) => void} onFileSelect - ファイル選択時のコールバック
 * @returns {void}
 */
function handleFileSelect(event, onFileSelect) {
  // 実装
}
```

## 3. Vue コンポーネントの型定義

### 3.1 Props定義
```javascript
/**
 * @typedef {Object} UserCardProps
 * @property {User} user - ユーザー情報
 * @property {boolean} [showActions=true] - アクションボタン表示フラグ
 * @property {'small'|'medium'|'large'} [size='medium'] - カードサイズ
 * @property {Function} [onEdit] - 編集ボタンクリック時のコールバック
 * @property {Function} [onDelete] - 削除ボタンクリック時のコールバック
 */

// コンポーネントでの使用
const props = defineProps({
  /** @type {User} */
  user: {
    type: Object,
    required: true
  },
  /** @type {boolean} */
  showActions: {
    type: Boolean,
    default: true
  },
  /** @type {'small'|'medium'|'large'} */
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})
```

### 3.2 Emit定義
```javascript
/**
 * @typedef {Object} PostFormEmits
 * @property {(post: Post) => void} save - 保存時のイベント
 * @property {() => void} cancel - キャンセル時のイベント
 * @property {(field: string, value: any) => void} change - フィールド変更時のイベント
 */

const emit = defineEmits(['save', 'cancel', 'change'])

/**
 * 保存ボタンクリック時の処理
 * @param {Post} postData - 投稿データ
 */
function handleSave(postData) {
  emit('save', postData)
}
```

### 3.3 Composable型定義
```javascript
/**
 * @typedef {Object} UseAuthReturn
 * @property {import('vue').ComputedRef<User|null>} user - 現在のユーザー
 * @property {import('vue').ComputedRef<boolean>} isLoggedIn - ログイン状態
 * @property {import('vue').ComputedRef<boolean>} loading - 読み込み状態
 * @property {(credentials: LoginCredentials) => Promise<AuthResult>} login - ログイン関数
 * @property {() => Promise<void>} logout - ログアウト関数
 * @property {() => Promise<void>} refresh - セッション更新関数
 */

/**
 * 認証機能を提供するコンポーザブル
 * @returns {UseAuthReturn} 認証関連の状態と関数
 */
export function useAuth() {
  // 実装
}
```

## 4. API レスポンス型定義

### 4.1 統一APIレスポンス
```javascript
/**
 * @template T
 * @typedef {Object} ApiResponse
 * @property {boolean} success - 成功フラグ
 * @property {T|null} data - レスポンスデータ
 * @property {string|null} error - エラーメッセージ
 * @property {ApiMeta|null} meta - メタ情報
 */

/**
 * @typedef {Object} ApiMeta
 * @property {number} [page] - 現在のページ
 * @property {number} [limit] - 1ページあたりの件数
 * @property {number} [total] - 総件数
 * @property {number} [totalPages] - 総ページ数
 * @property {string} [nextCursor] - 次のページのカーソル
 */

/**
 * @typedef {Object} PaginationMeta
 * @property {number} page - 現在のページ
 * @property {number} limit - 1ページあたりの件数
 * @property {number} total - 総件数
 * @property {number} totalPages - 総ページ数
 * @property {boolean} hasNext - 次のページの存在
 * @property {boolean} hasPrev - 前のページの存在
 */
```

### 4.2 Supabase型定義
```javascript
/**
 * @typedef {Object} SupabaseError
 * @property {string} message - エラーメッセージ
 * @property {string} [code] - PostgreSQLエラーコード
 * @property {string} [details] - 詳細情報
 * @property {string} [hint] - ヒント
 */

/**
 * @typedef {Object} SupabaseResponse
 * @property {any} data - レスポンスデータ
 * @property {SupabaseError|null} error - エラー情報
 * @property {number} count - 件数（countクエリの場合）
 * @property {number} status - HTTPステータスコード
 * @property {string} statusText - HTTPステータステキスト
 */

/**
 * @typedef {Object} RealtimePayload
 * @property {'INSERT'|'UPDATE'|'DELETE'} eventType - イベントタイプ
 * @property {Object} new - 新しいレコード
 * @property {Object} old - 古いレコード
 * @property {Object} errors - エラー情報
 */
```

## 5. フォームとバリデーション型定義

### 5.1 フォーム型定義
```javascript
/**
 * @typedef {Object} LoginForm
 * @property {string} email - メールアドレス
 * @property {string} password - パスワード
 * @property {boolean} [rememberMe=false] - ログイン状態を保持
 */

/**
 * @typedef {Object} PostForm
 * @property {string} title - タイトル
 * @property {string} content - 本文
 * @property {string} [excerpt] - 抜粋
 * @property {string[]} tags - タグ
 * @property {'draft'|'published'} status - 公開状態
 * @property {File|null} [featuredImage] - アイキャッチ画像
 */

/**
 * @typedef {Object} UserProfileForm
 * @property {string} name - 表示名
 * @property {string} [bio] - 自己紹介
 * @property {string} [website] - ウェブサイトURL
 * @property {string} [location] - 所在地
 * @property {File|null} [avatar] - アバター画像
 */
```

### 5.2 バリデーション型定義
```javascript
/**
 * @typedef {Object} ValidationRule
 * @property {string} name - ルール名
 * @property {Function} validator - バリデーター関数
 * @property {string} message - エラーメッセージ
 * @property {Object} [options] - オプション
 */

/**
 * @typedef {Object} ValidationResult
 * @property {boolean} isValid - バリデーション結果
 * @property {ValidationError[]} errors - エラー配列
 * @property {Object} validatedData - バリデーション済みデータ
 */

/**
 * @typedef {Object} ValidationError
 * @property {string} field - フィールド名
 * @property {string} message - エラーメッセージ
 * @property {string} code - エラーコード
 * @property {any} value - 入力値
 */

/**
 * バリデーションルール関数の型
 * @typedef {(value: any, options?: Object) => boolean|string|Promise<boolean|string>} ValidatorFunction
 */
```

## 6. ストア型定義

### 6.1 Pinia ストア型定義
```javascript
/**
 * @typedef {Object} AuthState
 * @property {User|null} user - 現在のユーザー
 * @property {boolean} loading - 読み込み状態
 * @property {string|null} error - エラーメッセージ
 * @property {boolean} initialized - 初期化済みフラグ
 */

/**
 * @typedef {Object} PostsState
 * @property {Post[]} posts - 投稿一覧
 * @property {Post|null} currentPost - 現在選択中の投稿
 * @property {boolean} loading - 読み込み状態
 * @property {string|null} error - エラーメッセージ
 * @property {PaginationMeta} pagination - ページネーション情報
 * @property {PostFilters} filters - フィルター条件
 */

/**
 * @typedef {Object} PostFilters
 * @property {string} [search] - 検索キーワード
 * @property {'published'|'draft'|'archived'} [status] - ステータス
 * @property {string[]} [tags] - タグ
 * @property {string} [authorId] - 投稿者ID
 * @property {string} [sortBy] - ソート項目
 * @property {'asc'|'desc'} [sortOrder] - ソート順
 */
```

### 6.2 ストアアクション型定義
```javascript
/**
 * @typedef {Object} AuthActions
 * @property {(credentials: LoginCredentials) => Promise<AuthResult>} login
 * @property {() => Promise<void>} logout
 * @property {(userData: SignupData) => Promise<AuthResult>} signup
 * @property {() => Promise<void>} initializeAuth
 * @property {() => Promise<void>} refreshToken
 */

/**
 * @typedef {Object} PostsActions
 * @property {(options?: PostsQueryOptions) => Promise<void>} fetchPosts
 * @property {(id: string) => Promise<void>} fetchPost
 * @property {(postData: PostForm) => Promise<Post>} createPost
 * @property {(id: string, updates: Partial<PostForm>) => Promise<Post>} updatePost
 * @property {(id: string) => Promise<void>} deletePost
 * @property {(filters: PostFilters) => void} setFilters
 * @property {() => void} clearError
 */
```

## 7. イベント型定義

### 7.1 カスタムイベント
```javascript
/**
 * @typedef {Object} PostEvent
 * @property {'created'|'updated'|'deleted'|'published'} type - イベントタイプ
 * @property {Post} post - 投稿データ
 * @property {string} timestamp - イベント発生時刻
 * @property {User} [actor] - アクションを実行したユーザー
 */

/**
 * @typedef {Object} UserEvent
 * @property {'login'|'logout'|'profile_updated'} type - イベントタイプ
 * @property {User} user - ユーザーデータ
 * @property {string} timestamp - イベント発生時刻
 * @property {Object} [metadata] - 追加メタデータ
 */

/**
 * @typedef {Object} NotificationEvent
 * @property {'info'|'success'|'warning'|'error'} type - 通知タイプ
 * @property {string} message - メッセージ
 * @property {string} [title] - タイトル
 * @property {NotificationAction[]} [actions] - アクション配列
 * @property {number} [timeout] - 自動非表示時間（ミリ秒）
 */

/**
 * @typedef {Object} NotificationAction
 * @property {string} text - アクションテキスト
 * @property {Function} handler - クリック時のハンドラー
 * @property {'primary'|'secondary'} [style] - スタイル
 */
```

## 8. ユーティリティ型定義

### 8.1 共通ユーティリティ型
```javascript
/**
 * オブジェクトのキーを部分的に必須にする
 * @template T
 * @template K
 * @typedef {T & Required<Pick<T, K>>} RequireKeys
 */

/**
 * オブジェクトのキーを部分的にオプショナルにする
 * @template T
 * @template K
 * @typedef {Omit<T, K> & Partial<Pick<T, K>>} OptionalKeys
 */

/**
 * ディープな部分型
 * @template T
 * @typedef {Partial<{[K in keyof T]: T[K] extends object ? DeepPartial<T[K]> : T[K]}>} DeepPartial
 */

/**
 * 配列の要素型を取得
 * @template T
 * @typedef {T extends (infer U)[] ? U : never} ArrayElement
 */
```

### 8.2 日付・時刻型定義
```javascript
/**
 * @typedef {string} ISO8601DateTime - ISO 8601形式の日時文字列
 * @example "2024-01-15T10:30:00.000Z"
 */

/**
 * @typedef {string} ISO8601Date - ISO 8601形式の日付文字列
 * @example "2024-01-15"
 */

/**
 * @typedef {Object} DateRange
 * @property {ISO8601DateTime} start - 開始日時
 * @property {ISO8601DateTime} end - 終了日時
 */

/**
 * @typedef {Object} TimeZoneInfo
 * @property {string} name - タイムゾーン名
 * @property {string} abbreviation - 略称
 * @property {number} offset - UTCからのオフセット（分）
 */
```

## 9. 設定とオプション型定義

### 9.1 アプリケーション設定
```javascript
/**
 * @typedef {Object} AppConfig
 * @property {string} appName - アプリケーション名
 * @property {string} version - バージョン
 * @property {EnvironmentConfig} environment - 環境設定
 * @property {DatabaseConfig} database - データベース設定
 * @property {AuthConfig} auth - 認証設定
 * @property {UIConfig} ui - UI設定
 */

/**
 * @typedef {Object} EnvironmentConfig
 * @property {'development'|'staging'|'production'} mode - 実行モード
 * @property {string} apiUrl - API URL
 * @property {boolean} debug - デバッグモード
 * @property {boolean} enableAnalytics - アナリティクス有効フラグ
 */

/**
 * @typedef {Object} DatabaseConfig
 * @property {string} url - Supabase URL
 * @property {string} anonKey - Supabase匿名キー
 * @property {number} [connectionTimeout] - 接続タイムアウト（ミリ秒）
 * @property {boolean} [enableRealtime] - リアルタイム機能有効フラグ
 */

/**
 * @typedef {Object} AuthConfig
 * @property {boolean} persistSession - セッション永続化
 * @property {number} sessionTimeout - セッションタイムアウト（秒）
 * @property {string[]} allowedDomains - 許可ドメイン一覧
 * @property {OAuthProvider[]} oauthProviders - OAuth プロバイダー
 */
```

### 9.2 コンポーネントオプション
```javascript
/**
 * @typedef {Object} DataTableOptions
 * @property {DataTableColumn[]} columns - カラム定義
 * @property {boolean} [sortable=true] - ソート可能フラグ
 * @property {boolean} [filterable=true] - フィルター可能フラグ
 * @property {boolean} [paginated=true] - ページネーション有効フラグ
 * @property {number} [pageSize=10] - 1ページあたりの件数
 * @property {boolean} [selectable=false] - 行選択可能フラグ
 * @property {boolean} [exportable=false] - エクスポート可能フラグ
 */

/**
 * @typedef {Object} DataTableColumn
 * @property {string} key - データキー
 * @property {string} label - 表示ラベル
 * @property {boolean} [sortable=true] - ソート可能フラグ
 * @property {boolean} [filterable=true] - フィルター可能フラグ
 * @property {Function} [formatter] - フォーマット関数
 * @property {string} [width] - カラム幅
 * @property {string} [align] - テキスト揃え
 */

/**
 * @typedef {Object} ModalOptions
 * @property {string} [title] - モーダルタイトル
 * @property {'small'|'medium'|'large'|'fullscreen'} [size='medium'] - サイズ
 * @property {boolean} [closable=true] - 閉じるボタン表示フラグ
 * @property {boolean} [maskClosable=true] - マスククリックで閉じる
 * @property {boolean} [keyboard=true] - ESCキーで閉じる
 * @property {Function} [onClose] - 閉じる時のコールバック
 */
```

## 10. エラー型定義

### 10.1 エラー分類
```javascript
/**
 * @typedef {Object} AppError
 * @property {string} name - エラー名
 * @property {string} message - エラーメッセージ
 * @property {string} code - エラーコード
 * @property {number} statusCode - HTTPステータスコード
 * @property {Object} [context] - コンテキスト情報
 * @property {string} timestamp - 発生時刻
 * @property {string} [stack] - スタックトレース
 */

/**
 * @typedef {Object} ValidationErrorDetail
 * @property {string} field - フィールド名
 * @property {string} message - エラーメッセージ
 * @property {string} code - エラーコード
 * @property {any} value - 入力値
 * @property {Object} [params] - バリデーションパラメータ
 */

/**
 * @typedef {Object} NetworkErrorDetail
 * @property {string} url - リクエストURL
 * @property {string} method - HTTPメソッド
 * @property {number} [status] - レスポンスステータス
 * @property {Object} [headers] - リクエストヘッダー
 * @property {Object} [response] - レスポンスデータ
 */
```

## 11. 型チェック関数

### 11.1 型ガード関数
```javascript
/**
 * オブジェクトがUser型かチェック
 * @param {any} obj - チェック対象
 * @returns {obj is User}
 */
function isUser(obj) {
  return obj && 
         typeof obj.id === 'string' &&
         typeof obj.email === 'string' &&
         (obj.name === null || typeof obj.name === 'string')
}

/**
 * 配列がPost配列かチェック
 * @param {any} arr - チェック対象
 * @returns {arr is Post[]}
 */
function isPostArray(arr) {
  return Array.isArray(arr) && arr.every(item => isPost(item))
}

/**
 * オブジェクトがPost型かチェック
 * @param {any} obj - チェック対象
 * @returns {obj is Post}
 */
function isPost(obj) {
  return obj &&
         typeof obj.id === 'string' &&
         typeof obj.title === 'string' &&
         ['draft', 'published', 'archived'].includes(obj.status)
}

/**
 * APIレスポンスの型チェック
 * @template T
 * @param {any} response - チェック対象
 * @param {(data: any) => data is T} dataValidator - データバリデーター
 * @returns {response is ApiResponse<T>}
 */
function isApiResponse(response, dataValidator) {
  return response &&
         typeof response.success === 'boolean' &&
         (response.data === null || dataValidator(response.data)) &&
         (response.error === null || typeof response.error === 'string')
}
```

## 12. まとめと使用例

### 12.1 実装例
```javascript
// types/index.js - 型定義のエクスポート
/**
 * @typedef {import('./user').User} User
 * @typedef {import('./post').Post} Post
 * @typedef {import('./api').ApiResponse} ApiResponse
 */

// 使用例
/**
 * ユーザー投稿を取得する
 * @param {string} userId - ユーザーID
 * @param {PostFilters} [filters] - フィルター条件
 * @returns {Promise<ApiResponse<Post[]>>} 投稿一覧のAPIレスポンス
 */
async function getUserPosts(userId, filters = {}) {
  try {
    const response = await api.posts.getByUserId(userId, filters)
    
    if (!isApiResponse(response, isPostArray)) {
      throw new Error('Invalid API response format')
    }
    
    return response
  } catch (error) {
    return {
      success: false,
      data: null,
      error: error.message,
      meta: null
    }
  }
}
```

### 12.2 型定義の利点
1. **開発効率**: IDE の自動補完とエラーチェック
2. **保守性**: 型変更時の影響範囲の把握
3. **ドキュメント**: コードが自己文書化される
4. **品質**: ランタイムエラーの早期発見

### 関連ドキュメント
- [アーキテクチャ設計](./01_architecture_design.md)
- [API設計](./03_api_design.md)
- [コンポーネント設計](./04_component_design.md)
- [エラーハンドリング設計](./07_error_handling_design.md)