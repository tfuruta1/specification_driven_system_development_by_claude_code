# /frontend-optimize - フロントエンド最適化統合コマンド

## 概要
Vue3、React、Angularなど様々なフロントエンドフレームワークとその接続方法（REST API、Supabase、ハイブリッド）を最適化する統合コマンドです。

## 使用方法
```bash
/frontend-optimize [framework] [connection] [options]

# 使用例
/frontend-optimize vue3 rest-api --performance
/frontend-optimize vue3 supabase --realtime
/frontend-optimize vue3 hybrid --offline-first
/frontend-optimize react api --bundle-size
```

## パラメータ

### 必須パラメータ
- `framework`: フレームワーク（vue3, react, angular）
- `connection`: 接続方式（rest-api, supabase, hybrid, graphql）

### オプション
- `--performance`: パフォーマンス最適化
- `--bundle-size`: バンドルサイズ最適化
- `--realtime`: リアルタイム機能最適化
- `--offline-first`: オフラインファースト最適化
- `--seo`: SEO最適化
- `--lazy-loading`: 遅延読み込み実装

## 最適化戦略

### 1. REST API最適化（Axios）
```javascript
// 最適化された Axios 設定
const apiConfig = {
  // リクエスト最適化
  request: {
    timeout: 5000,
    retry: 3,
    cache: true,
    compression: true
  },
  
  // レスポンス最適化
  response: {
    interceptors: true,
    errorHandling: 'centralized',
    dataTransform: true
  },
  
  // 認証最適化
  auth: {
    tokenRefresh: 'automatic',
    headerInjection: true,
    sessionManagement: true
  }
}
```

### 2. Supabase最適化
```javascript
// Supabase リアルタイム最適化
const supabaseOptimization = {
  // 接続最適化
  connection: {
    poolSize: 10,
    keepAlive: true,
    compression: true
  },
  
  // リアルタイム最適化
  realtime: {
    channels: 'selective',
    debounce: 300,
    presence: true
  },
  
  // ストレージ最適化
  storage: {
    cdn: true,
    caching: 'aggressive',
    lazyLoad: true
  }
}
```

### 3. ハイブリッド接続最適化
```javascript
// 3層フォールバック最適化
const hybridStrategy = {
  // 優先順位設定
  layers: [
    {
      type: 'rest-api',
      priority: 1,
      timeout: 3000,
      cache: 'memory'
    },
    {
      type: 'supabase',
      priority: 2,
      timeout: 5000,
      cache: 'indexed-db'
    },
    {
      type: 'local-json',
      priority: 3,
      timeout: 100,
      cache: 'persistent'
    }
  ],
  
  // 自動切り替え
  fallback: {
    automatic: true,
    healthCheck: 30000,
    syncOnReconnect: true
  }
}
```

## フレームワーク別最適化

### Vue3最適化
```javascript
// Composition API最適化
import { ref, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'

// 最適化されたコンポーネント
export default {
  setup() {
    // Reactive参照の最適化
    const data = shallowRef(largeDataset)
    
    // 計算プロパティのメモ化
    const filtered = computed(() => {
      return data.value.filter(/* ... */)
    }, { cache: true })
    
    // Watcherの最適化
    watchEffect(() => {
      // 依存関係を最小限に
    }, { flush: 'post' })
    
    return { data, filtered }
  }
}
```

### パフォーマンス最適化テクニック

#### 1. コード分割
```javascript
// 動的インポート
const AdminPanel = () => import('./components/AdminPanel.vue')
const Analytics = () => import('./components/Analytics.vue')
```

#### 2. 仮想スクロール
```javascript
// 大量データの表示最適化
import { VirtualList } from '@tanstack/vue-virtual'

// 10000件のデータも高速表示
<VirtualList :items="largeDataset" :height="400" />
```

#### 3. 画像最適化
```javascript
// 遅延読み込みと最適化
const imageOptimization = {
  lazy: true,
  webp: true,
  responsive: true,
  placeholder: 'blur'
}
```

## バンドルサイズ最適化

### Vite設定例
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'pinia'],
          'ui': ['@headlessui/vue', 'tailwindcss'],
          'utils': ['lodash', 'dayjs']
        }
      }
    },
    // ツリーシェイキング
    treeShaking: true,
    // 圧縮
    minify: 'terser',
    // gzip圧縮
    compression: true
  }
}
```

## SEO最適化

### メタタグ管理
```javascript
// Vue3 + Vite SSG
export const seoConfig = {
  meta: {
    defaultTitle: 'サイトタイトル',
    titleTemplate: '%s | サイト名',
    description: 'サイト説明'
  },
  og: {
    type: 'website',
    image: '/og-image.jpg'
  },
  twitter: {
    card: 'summary_large_image'
  }
}
```

## オフラインファースト戦略

### Service Worker設定
```javascript
// PWA対応
const pwaConfig = {
  strategies: {
    api: 'NetworkFirst',
    assets: 'CacheFirst',
    pages: 'StaleWhileRevalidate'
  },
  cache: {
    maxAge: 86400,
    maxEntries: 100
  }
}
```

## 出力例

### 最適化レポート
```markdown
# フロントエンド最適化レポート

## 実施項目
✅ バンドルサイズ: 2.1MB → 680KB (67%削減)
✅ 初期表示時間: 3.2秒 → 1.1秒 (66%改善)
✅ Lighthouse スコア: 65 → 95
✅ コード分割: 15チャンク生成

## パフォーマンス改善
- First Contentful Paint: 1.2s
- Time to Interactive: 2.1s
- Cumulative Layout Shift: 0.02

## 推奨事項
1. CDNの導入
2. 画像フォーマットをWebPに統一
3. Critical CSSのインライン化
```

## エラーハンドリング
| エラー | 原因 | 対処法 |
|--------|------|--------|
| ビルドエラー | 依存関係の問題 | npm install --force |
| 型エラー | TypeScript設定 | tsconfig.json確認 |
| CORS エラー | API設定 | プロキシ設定追加 |

## 管理責任
- **管理部門**: システム開発部
- **カスタマイズ**: プロジェクトのフロントエンド技術に応じて最適化

## 関連コマンド
- `/backend-sync` - バックエンド連携
- `/rest-api-optimize` - REST API専門最適化
- `/supabase-optimize` - Supabase専門最適化
- `/hybrid-optimize` - ハイブリッド接続専門最適化

---
*このコマンドはシステム開発部が管理します。*