# E2Eテスト設計書

## 概要

このドキュメントでは、Vue.js + Supabaseアプリケーションにおけるエンドツーエンド（E2E）テストの設計方針と実装方法を定義します。クリティカルパス（絶対に動作してほしい機能）を明確にし、効率的で保守性の高いテスト戦略を提供します。

## 1. E2Eテスト戦略

### 1.1 テストピラミッドにおける位置づけ
```
         /\      E2Eテスト（10%）
        /  \     - クリティカルユーザージャーニー
       /    \    - リリース前の最終確認
      /------\   
     /        \  統合テスト（30%）
    /          \ - API連携、ストア連携
   /------------\
  /              \ ユニットテスト（60%）
 /                \ - Composables、ユーティリティ
/------------------\
```

### 1.2 テストツール選定
```javascript
// E2Eテストスタック
const testingStack = {
  framework: "Playwright 1.41+",
  assertion: "Playwright Test Assertions",
  reporting: "Playwright HTML Reporter",
  parallelization: "Playwright Test Runner",
  browser: ["chromium", "firefox", "webkit"],
  device: ["desktop", "mobile"],
  ci: "GitHub Actions / GitLab CI"
}
```

### 1.3 テスト実行環境
- **ローカル開発**: 開発中の即時フィードバック
- **CI/CD**: プルリクエスト時の自動実行
- **ステージング**: リリース前の全機能テスト
- **プロダクション**: スモークテスト（最小限の動作確認）

## 2. クリティカルパスの定義

### 2.1 優先度レベル
```javascript
/**
 * テスト優先度の定義
 * P0: ビジネスクリティカル - 障害時に即座にサービス停止
 * P1: 重要機能 - 主要ユーザーフローに影響
 * P2: 一般機能 - 特定機能の利用に影響
 * P3: 補助機能 - UX向上のための機能
 */
const testPriorities = {
  P0: "BUSINESS_CRITICAL",
  P1: "CORE_FEATURE",
  P2: "GENERAL_FEATURE",  
  P3: "NICE_TO_HAVE"
}
```

### 2.2 クリティカルユーザージャーニー

#### P0: ビジネスクリティカル
1. **ユーザー認証フロー**
   - 新規登録
   - ログイン
   - パスワードリセット
   - ログアウト

2. **決済フロー**（該当する場合）
   - 商品購入
   - サブスクリプション登録
   - 決済情報の更新

3. **データ整合性**
   - 重要データの作成・更新・削除
   - トランザクション処理

#### P1: 主要機能
1. **ダッシュボード**
   - 初期表示
   - リアルタイムデータ更新
   - フィルター・検索機能

2. **ユーザープロフィール**
   - プロフィール編集
   - アバター画像アップロード
   - 設定変更

3. **コンテンツ管理**
   - 作成・編集・削除
   - 公開・非公開切り替え
   - ソート・ページネーション

## 3. テスト実装設計

### 3.1 プロジェクト構造
```
e2e/
├── tests/                    # テストファイル
│   ├── auth/                # 認証関連テスト
│   │   ├── login.spec.js
│   │   ├── register.spec.js
│   │   └── password-reset.spec.js
│   ├── dashboard/           # ダッシュボードテスト
│   ├── profile/             # プロフィールテスト
│   └── critical-paths/      # クリティカルパステスト
├── fixtures/                # テストデータ
│   ├── users.json
│   ├── products.json
│   └── test-data.js
├── helpers/                 # ヘルパー関数
│   ├── auth-helper.js
│   ├── db-helper.js
│   └── api-helper.js
├── page-objects/            # ページオブジェクト
│   ├── base.page.js
│   ├── login.page.js
│   ├── dashboard.page.js
│   └── profile.page.js
└── playwright.config.js     # Playwright設定
```

### 3.2 Playwright設定
```javascript
// playwright.config.js
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list']
  ],
  
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // グローバルタイムアウト
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
})
```

## 4. ページオブジェクトパターン

### 4.1 ベースページクラス
```javascript
// e2e/page-objects/base.page.js
export class BasePage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page
  }

  /**
   * ページへ遷移
   * @param {string} path
   */
  async goto(path = '') {
    await this.page.goto(path)
  }

  /**
   * 要素が表示されるまで待機
   * @param {string} selector
   * @param {number} timeout
   */
  async waitForElement(selector, timeout = 30000) {
    await this.page.waitForSelector(selector, { 
      state: 'visible', 
      timeout 
    })
  }

  /**
   * テキストが含まれる要素を取得
   * @param {string} text
   */
  async getByText(text) {
    return this.page.getByText(text)
  }

  /**
   * アラートメッセージを取得
   * @param {string} type - success, error, warning, info
   */
  async getAlert(type = 'success') {
    const alertSelector = `.alert-${type}`
    await this.waitForElement(alertSelector)
    return await this.page.locator(alertSelector).textContent()
  }

  /**
   * ローディング完了を待機
   */
  async waitForLoadingComplete() {
    await this.page.waitForLoadState('networkidle')
    // ローディングスピナーが消えるまで待機
    await this.page.waitForSelector('.loading', { state: 'hidden' })
  }
}
```

### 4.2 ログインページ
```javascript
// e2e/page-objects/login.page.js
import { BasePage } from './base.page.js'

export class LoginPage extends BasePage {
  constructor(page) {
    super(page)
    
    // セレクタ定義
    this.selectors = {
      emailInput: 'input[type="email"]',
      passwordInput: 'input[type="password"]',
      submitButton: 'button[type="submit"]',
      rememberCheckbox: 'input[type="checkbox"]',
      forgotPasswordLink: 'a[href="/forgot-password"]',
      registerLink: 'a[href="/register"]',
      errorMessage: '.error-message'
    }
  }

  async goto() {
    await super.goto('/login')
    await this.waitForElement(this.selectors.emailInput)
  }

  /**
   * ログイン実行
   * @param {string} email
   * @param {string} password
   * @param {boolean} remember
   */
  async login(email, password, remember = false) {
    await this.page.fill(this.selectors.emailInput, email)
    await this.page.fill(this.selectors.passwordInput, password)
    
    if (remember) {
      await this.page.check(this.selectors.rememberCheckbox)
    }
    
    await this.page.click(this.selectors.submitButton)
  }

  /**
   * エラーメッセージを取得
   */
  async getErrorMessage() {
    await this.waitForElement(this.selectors.errorMessage)
    return await this.page.locator(this.selectors.errorMessage).textContent()
  }

  /**
   * ログイン成功を確認
   */
  async expectLoginSuccess() {
    // ダッシュボードへのリダイレクトを待機
    await this.page.waitForURL('/dashboard', { timeout: 10000 })
  }
}
```

### 4.3 ダッシュボードページ
```javascript
// e2e/page-objects/dashboard.page.js
import { BasePage } from './base.page.js'

export class DashboardPage extends BasePage {
  constructor(page) {
    super(page)
    
    this.selectors = {
      welcomeMessage: 'h1',
      statCards: '.stat-card',
      dataTable: '.data-table',
      searchInput: 'input[placeholder*="検索"]',
      filterButton: 'button:has-text("フィルター")',
      refreshButton: 'button[aria-label="更新"]',
      userMenu: '.user-menu',
      logoutButton: 'button:has-text("ログアウト")'
    }
  }

  async goto() {
    await super.goto('/dashboard')
    await this.waitForLoadingComplete()
  }

  /**
   * 統計カードの値を取得
   * @param {string} cardTitle
   */
  async getStatValue(cardTitle) {
    const card = await this.page.locator('.stat-card', { 
      hasText: cardTitle 
    })
    return await card.locator('.stat-value').textContent()
  }

  /**
   * データテーブルの行数を取得
   */
  async getTableRowCount() {
    await this.waitForElement(this.selectors.dataTable)
    const rows = await this.page.locator('.data-table tbody tr').count()
    return rows
  }

  /**
   * 検索実行
   * @param {string} query
   */
  async search(query) {
    await this.page.fill(this.selectors.searchInput, query)
    await this.page.press(this.selectors.searchInput, 'Enter')
    await this.waitForLoadingComplete()
  }

  /**
   * ログアウト
   */
  async logout() {
    await this.page.click(this.selectors.userMenu)
    await this.page.click(this.selectors.logoutButton)
    await this.page.waitForURL('/login')
  }
}
```

## 5. テストヘルパー

### 5.1 認証ヘルパー
```javascript
// e2e/helpers/auth-helper.js
import { test as base } from '@playwright/test'

/**
 * 認証済みページを提供するフィクスチャ
 */
export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // テスト用認証トークンを設定
    await page.addInitScript(() => {
      window.localStorage.setItem('auth-token', 'test-token')
    })
    
    // Supabaseセッションをモック
    await page.route('**/auth/v1/token**', async route => {
      await route.fulfill({
        status: 200,
        json: {
          access_token: 'test-access-token',
          token_type: 'bearer',
          expires_in: 3600,
          refresh_token: 'test-refresh-token'
        }
      })
    })
    
    await use(page)
  }
})

export { expect } from '@playwright/test'
```

### 5.2 データベースヘルパー
```javascript
// e2e/helpers/db-helper.js
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
)

/**
 * テストデータベースヘルパー
 */
export class TestDatabase {
  /**
   * テストユーザーを作成
   * @param {Object} userData
   */
  static async createTestUser(userData = {}) {
    const defaultUser = {
      email: `test-${Date.now()}@example.com`,
      password: 'Test123456!',
      email_confirmed_at: new Date().toISOString()
    }
    
    const user = { ...defaultUser, ...userData }
    
    const { data, error } = await supabase.auth.admin.createUser({
      email: user.email,
      password: user.password,
      email_confirm: true
    })
    
    if (error) throw error
    return { user: data.user, password: user.password }
  }

  /**
   * テストデータをクリーンアップ
   * @param {string} userId
   */
  static async cleanupTestUser(userId) {
    // プロフィールデータを削除
    await supabase
      .from('profiles')
      .delete()
      .eq('user_id', userId)
    
    // ユーザーを削除
    await supabase.auth.admin.deleteUser(userId)
  }

  /**
   * テストデータをシード
   */
  static async seedTestData() {
    // テスト用の初期データを投入
    const testData = [
      { name: 'テストアイテム1', status: 'active' },
      { name: 'テストアイテム2', status: 'inactive' },
      { name: 'テストアイテム3', status: 'active' }
    ]
    
    const { data, error } = await supabase
      .from('items')
      .insert(testData)
      .select()
    
    if (error) throw error
    return data
  }
}
```

## 6. クリティカルパステスト実装

### 6.1 認証フローテスト
```javascript
// e2e/tests/auth/login.spec.js
import { test, expect } from '@playwright/test'
import { LoginPage } from '../../page-objects/login.page'
import { DashboardPage } from '../../page-objects/dashboard.page'
import { TestDatabase } from '../../helpers/db-helper'

test.describe('認証フロー @critical', () => {
  let testUser
  
  test.beforeAll(async () => {
    // テストユーザーを作成
    testUser = await TestDatabase.createTestUser()
  })
  
  test.afterAll(async () => {
    // テストユーザーをクリーンアップ
    if (testUser) {
      await TestDatabase.cleanupTestUser(testUser.user.id)
    }
  })

  test('正常なログイン', async ({ page }) => {
    const loginPage = new LoginPage(page)
    const dashboardPage = new DashboardPage(page)
    
    // ログインページへ遷移
    await loginPage.goto()
    
    // ログイン実行
    await loginPage.login(testUser.user.email, testUser.password)
    
    // ログイン成功を確認
    await loginPage.expectLoginSuccess()
    
    // ダッシュボードの表示を確認
    await expect(page).toHaveURL('/dashboard')
    await expect(await dashboardPage.getByText('ようこそ')).toBeVisible()
  })

  test('無効な認証情報でのログイン', async ({ page }) => {
    const loginPage = new LoginPage(page)
    
    await loginPage.goto()
    await loginPage.login('invalid@example.com', 'wrongpassword')
    
    // エラーメッセージを確認
    const errorMessage = await loginPage.getErrorMessage()
    expect(errorMessage).toContain('メールアドレスまたはパスワードが正しくありません')
    
    // ログインページに留まることを確認
    await expect(page).toHaveURL('/login')
  })

  test('ログイン状態の永続化', async ({ page, context }) => {
    const loginPage = new LoginPage(page)
    
    await loginPage.goto()
    await loginPage.login(testUser.user.email, testUser.password, true)
    await loginPage.expectLoginSuccess()
    
    // 新しいページでセッションが維持されることを確認
    const newPage = await context.newPage()
    await newPage.goto('/dashboard')
    await expect(newPage).toHaveURL('/dashboard')
  })

  test('ログアウト', async ({ page }) => {
    const loginPage = new LoginPage(page)
    const dashboardPage = new DashboardPage(page)
    
    // ログイン
    await loginPage.goto()
    await loginPage.login(testUser.user.email, testUser.password)
    await loginPage.expectLoginSuccess()
    
    // ログアウト
    await dashboardPage.logout()
    
    // ログインページへのリダイレクトを確認
    await expect(page).toHaveURL('/login')
    
    // 認証が必要なページへのアクセスを確認
    await page.goto('/dashboard')
    await expect(page).toHaveURL('/login')
  })
})
```

### 6.2 ダッシュボード機能テスト
```javascript
// e2e/tests/dashboard/dashboard.spec.js
import { test, expect } from '../../helpers/auth-helper'
import { DashboardPage } from '../../page-objects/dashboard.page'
import { TestDatabase } from '../../helpers/db-helper'

test.describe('ダッシュボード機能 @critical', () => {
  let dashboardPage
  let testData
  
  test.beforeEach(async ({ authenticatedPage }) => {
    dashboardPage = new DashboardPage(authenticatedPage)
    
    // テストデータをシード
    testData = await TestDatabase.seedTestData()
    
    await dashboardPage.goto()
  })
  
  test.afterEach(async () => {
    // テストデータをクリーンアップ
    if (testData) {
      const ids = testData.map(item => item.id)
      await TestDatabase.cleanupItems(ids)
    }
  })

  test('ダッシュボードの初期表示', async ({ authenticatedPage }) => {
    // ページタイトル
    await expect(authenticatedPage).toHaveTitle(/ダッシュボード/)
    
    // 統計カードの表示
    const activeCount = await dashboardPage.getStatValue('アクティブ')
    expect(parseInt(activeCount)).toBeGreaterThanOrEqual(2)
    
    // データテーブルの表示
    const rowCount = await dashboardPage.getTableRowCount()
    expect(rowCount).toBe(testData.length)
  })

  test('検索機能', async ({ authenticatedPage }) => {
    // 検索実行
    await dashboardPage.search('テストアイテム1')
    
    // 検索結果の確認
    const rowCount = await dashboardPage.getTableRowCount()
    expect(rowCount).toBe(1)
    
    // 検索結果の内容確認
    const firstRow = authenticatedPage.locator('.data-table tbody tr').first()
    await expect(firstRow).toContainText('テストアイテム1')
  })

  test('リアルタイムデータ更新', async ({ authenticatedPage }) => {
    // 別のブラウザタブでデータを追加
    const newItem = await TestDatabase.createItem({
      name: 'リアルタイムテスト',
      status: 'active'
    })
    
    // データが自動的に表示されることを確認（5秒以内）
    await expect(authenticatedPage.getByText('リアルタイムテスト')).toBeVisible({
      timeout: 5000
    })
    
    // クリーンアップ
    await TestDatabase.cleanupItems([newItem.id])
  })

  test('ページネーション', async ({ authenticatedPage }) => {
    // 大量のテストデータを作成
    const manyItems = await TestDatabase.createManyItems(25)
    
    // ページネーションコントロールの確認
    await expect(authenticatedPage.getByText('1-20 / 28')).toBeVisible()
    
    // 次のページへ
    await authenticatedPage.click('button[aria-label="次のページ"]')
    
    // 2ページ目の表示確認
    await expect(authenticatedPage.getByText('21-28 / 28')).toBeVisible()
    
    // クリーンアップ
    await TestDatabase.cleanupItems(manyItems.map(item => item.id))
  })
})
```

## 7. CI/CD統合

### 7.1 GitHub Actions設定
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    services:
      supabase:
        image: supabase/postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Setup Supabase
        run: |
          npm run supabase:start
          npm run supabase:seed
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
      
      - name: Build application
        run: npm run build
      
      - name: Run E2E tests
        run: npm run test:e2e
        env:
          BASE_URL: http://localhost:5173
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
      
      - name: Upload test videos
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-videos
          path: test-results/
          retention-days: 7
```

### 7.2 package.jsonスクリプト
```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:critical": "playwright test --grep @critical",
    "test:e2e:report": "playwright show-report",
    "test:e2e:codegen": "playwright codegen http://localhost:5173"
  }
}
```

## 8. ベストプラクティス

### 8.1 テスト設計原則
1. **独立性**: 各テストは他のテストに依存しない
2. **冪等性**: 何度実行しても同じ結果
3. **高速性**: 並列実行、不要な待機の削除
4. **保守性**: ページオブジェクトパターン、ヘルパー関数

### 8.2 アンチパターンの回避
```javascript
// ❌ 悪い例: ハードコードされたセレクタ
await page.click('#submit-btn-123')

// ✅ 良い例: 意味のあるセレクタ
await page.click('button[type="submit"]')

// ❌ 悪い例: 固定の待機時間
await page.waitForTimeout(5000)

// ✅ 良い例: 条件付き待機
await page.waitForSelector('.loading', { state: 'hidden' })

// ❌ 悪い例: テストデータの共有
const sharedUser = { email: 'test@example.com' }

// ✅ 良い例: 各テスト用の独立したデータ
const testUser = await createTestUser()
```

### 8.3 デバッグテクニック
```javascript
// スクリーンショット取得
await page.screenshot({ path: 'debug.png', fullPage: true })

// ブラウザコンソールログ出力
page.on('console', msg => console.log('PAGE LOG:', msg.text()))

// ネットワークリクエスト監視
page.on('request', request => {
  console.log('Request:', request.method(), request.url())
})

// Playwrightインスペクタ起動
await page.pause()
```

## まとめ

このE2Eテスト設計に従うことで、信頼性が高く保守しやすいテストスイートを構築できます。クリティカルパスに焦点を当て、適切なテストパターンとツールを使用することで、開発速度を維持しながら品質を確保できます。