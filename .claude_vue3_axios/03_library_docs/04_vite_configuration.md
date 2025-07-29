# Vite設定ガイド

Vue.js + Tailwind CSS + DaisyUI + Supabaseアプリケーション向けの包括的なVite設定ガイド。最適化戦略、開発ワークフロー、本番デプロイ設定を網羅します。

## 📚 目次

1. [基本設定](#基本設定)
2. [開発環境設定](#開発環境設定)
3. [本番最適化](#本番最適化)
4. [プラグイン設定](#プラグイン設定)
5. [アセット処理](#アセット処理)
6. [環境変数](#環境変数)
7. [コード分割](#コード分割)
8. [PWA設定](#pwa設定)
9. [テスト設定](#テスト設定)
10. [デプロイ設定](#デプロイ設定)
11. [パフォーマンス監視](#パフォーマンス監視)
12. [トラブルシューティング](#トラブルシューティング)

## 基本設定

### コアVite設定

```javascript
// vite.config.js
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ command, mode }) => {
  // 現在の作業ディレクトリからmodeに基づいて環境ファイルを読み込み
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    // ベースパブリックパス
    base: mode === 'production' ? '/my-app/' : '/',
    
    // プラグイン
    plugins: [
      vue({
        // Vueプラグインオプション
        include: [/\.vue$/, /\.md$/],
        reactivityTransform: true,
        script: {
          defineModel: true,
          propsDestructure: true
        }
      })
    ],
    
    // パス解決
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '~': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@composables': resolve(__dirname, 'src/composables'),
        '@stores': resolve(__dirname, 'src/stores'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@assets': resolve(__dirname, 'src/assets'),
        '@types': resolve(__dirname, 'src/types'),
        '@styles': resolve(__dirname, 'src/styles')
      },
      extensions: ['.js', '.ts', '.jsx', '.tsx', '.json', '.vue', '.mjs']
    },
    
    // グローバル定数を定義
    define: {
      __VUE_OPTIONS_API__: true,
      __VUE_PROD_DEVTOOLS__: false,
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
      // カスタムアプリ定数
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      __COMMIT_HASH__: JSON.stringify(process.env.COMMIT_HASH || 'unknown')
    },
    
    // CSS設定
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @import "@/styles/variables.scss";
            @import "@/styles/mixins.scss";
          `,
          charset: false
        }
      },
      devSourcemap: mode === 'development',
      modules: {
        localsConvention: 'camelCase',
        generateScopedName: mode === 'production' 
          ? '[hash:base64:8]' 
          : '[name]__[local]___[hash:base64:5]'
      }
    },
    
    // サーバー設定
    server: {
      port: 3000,
      host: true,
      strictPort: false,
      open: true,
      cors: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, ''),
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log('プロキシエラー:', err.message)
              console.log(`  URL: ${req.method} ${req.url}`)
              console.log(`  Target: ${options.target}`)
            })
            proxy.on('proxyReq', (proxyReq, req, res) => {
              if (env.VITE_LOG_LEVEL === 'debug') {
                console.log(`プロキシリクエスト: ${req.method} ${req.url} -> ${options.target}${proxyReq.path}`)
              }
            })
            proxy.on('proxyRes', (proxyRes, req, res) => {
              if (env.VITE_LOG_LEVEL === 'debug') {
                console.log(`プロキシレスポンス: ${proxyRes.statusCode} ${req.method} ${req.url}`)
              }
            })
          }
        },
        // WebSocket プロキシ
        '/ws': {
          target: env.VITE_WS_URL || 'ws://localhost:8000',
          ws: true,
          changeOrigin: true
        }
      }
    },
    
    // ビルド設定
    build: {
      target: 'es2015',
      outDir: 'dist',
      assetsDir: 'assets',
      minify: 'terser',
      sourcemap: mode === 'development',
      cssCodeSplit: true,
      
      // Rollupオプション
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html')
        },
        output: {
          manualChunks: (id) => {
            // より精密なチャンク分割戦略
            if (id.includes('node_modules')) {
              // Vueコア（vue-routerを除く）
              if (id.includes('vue') && !id.includes('vue-router')) {
                return 'vue-core'
              }
              
              // Vue Router単体
              if (id.includes('vue-router')) {
                return 'vue-router'
              }
              
              // Pinia
              if (id.includes('pinia')) {
                return 'pinia'
              }
              
              // Supabase
              if (id.includes('@supabase')) {
                return 'supabase'
              }
              
              // UIライブラリ
              if (id.includes('@headlessui') || id.includes('daisyui') || id.includes('@heroicons')) {
                return 'ui-libs'
              }
              
              // チャートライブラリ
              if (id.includes('chart') || id.includes('d3') || id.includes('echarts')) {
                return 'charts'
              }
              
              // ユーティリティライブラリ
              if (id.includes('date-fns') || id.includes('lodash') || id.includes('@vueuse')) {
                return 'utils'
              }
              
              // その他のベンダー
              return 'vendor'
            }
            
            // アプリケーションコード
            if (id.includes('src/views/admin')) {
              return 'admin-pages'
            }
            
            if (id.includes('src/views/auth')) {
              return 'auth-pages'
            }
            
            if (id.includes('src/views/')) {
              return 'pages'
            }
            
            if (id.includes('src/components/forms')) {
              return 'form-components'
            }
            
            if (id.includes('src/components/charts')) {
              return 'chart-components'
            }
            
            if (id.includes('src/components/')) {
              return 'components'
            }
            
            if (id.includes('src/composables/') || id.includes('src/utils/')) {
              return 'composables-utils'
            }
            
            if (id.includes('src/stores/')) {
              return 'stores'
            }
            
            // デフォルトチャンクに任せる
            return undefined
          }
        }
      },
      
      // 本番用Terserオプション
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: mode === 'production'
        }
      }
    },
    
    // 最適化
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        '@supabase/supabase-js',
        'date-fns',
        'lodash-es'
      ],
      exclude: ['@vueuse/core']
    },
    
    // Worker設定
    worker: {
      format: 'es'
    }
  }
})
```

## 開発環境設定

### 開発専用設定

```javascript
// vite.config.dev.js
import { mergeConfig } from 'vite'
import baseConfig from './vite.config.js'

export default mergeConfig(baseConfig, {
  mode: 'development',
  
  server: {
    hmr: {
      overlay: true,
      clientPort: 3000
    },
    watch: {
      usePolling: true,
      interval: 100
    }
  },
  
  build: {
    sourcemap: true,
    minify: false,
    target: 'esnext'
  },
  
  optimizeDeps: {
    force: true
  },
  
  define: {
    __DEV__: true,
    'process.env.NODE_ENV': '"development"'
  },
  
  css: {
    devSourcemap: true
  }
})
```

### Hot Module Replacement (HMR)設定

```javascript
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// HMRサポート
if (import.meta.hot) {
  import.meta.hot.accept()
  
  // ストア用カスタムHMR処理
  import.meta.hot.accept('./stores/user.js', (newModule) => {
    if (newModule) {
      // ストア更新を処理
      console.log('ストアが更新されました')
    }
  })
  
  // コンポーネント更新を処理
  import.meta.hot.on('vue:update', (data) => {
    console.log('Vueコンポーネントが更新されました:', data)
  })
  
  // CSS更新を処理
  import.meta.hot.on('css-update', (data) => {
    console.log('CSSが更新されました:', data)
  })
}

app.mount('#app')
```

## 本番最適化

### 本番ビルド設定

```javascript
// vite.config.prod.js
import { mergeConfig } from 'vite'
import { visualizer } from 'rollup-plugin-visualizer'
import { compression } from 'vite-plugin-compression'
import { createHtmlPlugin } from 'vite-plugin-html'
import baseConfig from './vite.config.js'

export default mergeConfig(baseConfig, {
  mode: 'production',
  
  build: {
    target: 'es2015',
    minify: 'terser',
    sourcemap: false,
    cssCodeSplit: true,
    chunkSizeWarningLimit: 1000,
    
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // ベンダーチャンク
          if (id.includes('node_modules')) {
            if (id.includes('vue')) {
              return 'vendor-vue'
            }
            if (id.includes('@supabase')) {
              return 'vendor-supabase'
            }
            if (id.includes('date-fns') || id.includes('lodash')) {
              return 'vendor-utils'
            }
            return 'vendor'
          }
          
          // コンポーネントチャンク
          if (id.includes('src/components')) {
            return 'components'
          }
          
          // ページチャンク
          if (id.includes('src/views')) {
            return 'pages'
          }
        },
        
        // アセット命名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const extType = info[info.length - 1]
          
          if (/\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/i.test(assetInfo.name)) {
            return `assets/media/[name]-[hash].${extType}`
          }
          if (/\.(png|jpe?g|gif|svg|webp|avif)(\?.*)?$/i.test(assetInfo.name)) {
            return `assets/images/[name]-[hash].${extType}`
          }
          if (/\.(woff2?|eot|ttf|otf)(\?.*)?$/i.test(assetInfo.name)) {
            return `assets/fonts/[name]-[hash].${extType}`
          }
          return `assets/${extType}/[name]-[hash].${extType}`
        }
      }
    },
    
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn']
      },
      mangle: {
        safari10: true
      },
      format: {
        comments: false
      }
    }
  },
  
  plugins: [
    // HTMLテンプレート処理
    createHtmlPlugin({
      minify: true,
      inject: {
        data: {
          title: 'My App',
          description: 'SupabaseによるVue.jsアプリケーション',
          keywords: 'vue, vite, supabase, tailwind'
        }
      }
    }),
    
    // 圧縮
    compression({
      algorithm: 'gzip',
      ext: '.gz'
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br'
    }),
    
    // バンドル分析
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true
    })
  ],
  
  define: {
    __DEV__: false,
    'process.env.NODE_ENV': '"production"'
  }
})
```

### アセット最適化

```javascript
// vite.config.assets.js
import { defineConfig } from 'vite'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import legacy from '@vitejs/plugin-legacy'

export default defineConfig({
  plugins: [
    // SVGスプライト生成
    createSvgIconsPlugin({
      iconDirs: [resolve(process.cwd(), 'src/assets/icons')],
      symbolId: 'icon-[dir]-[name]',
      inject: 'body-last',
      customDomId: '__svg__icons__dom__'
    }),
    
    // レガシーブラウザサポート
    legacy({
      targets: ['defaults', 'not IE 11'],
      additionalLegacyPolyfills: ['regenerator-runtime/runtime'],
      renderLegacyChunks: true,
      polyfills: [
        'es.symbol',
        'es.array.filter',
        'es.promise',
        'es.promise.finally',
        'es/map',
        'es/set',
        'es.array.for-each',
        'es.object.define-properties',
        'es.object.define-property',
        'es.object.get-own-property-descriptor',
        'es.object.get-own-property-descriptors',
        'es.object.keys',
        'es.object.to-string',
        'web.dom-collections.for-each',
        'esnext.global-this',
        'esnext.string.match-all'
      ]
    })
  ],
  
  build: {
    rollupOptions: {
      output: {
        // アセット読み込み最適化
        assetFileNames: (assetInfo) => {
          // 小さなアセットをインライン化
          if (assetInfo.source && assetInfo.source.length < 4096) {
            return '[name].[ext]'
          }
          return 'assets/[name]-[hash].[ext]'
        }
      }
    }
  },
  
  // アセット処理
  assetsInclude: ['**/*.glb', '**/*.gltf', '**/*.hdr'],
  
  // パブリックディレクトリのアセット
  publicDir: 'public'
})
```

## プラグイン設定

### 必須プラグイン設定

```javascript
// plugins/index.js
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import WindiCSS from 'vite-plugin-windicss'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { VitePWA } from 'vite-plugin-pwa'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import Layouts from 'vite-plugin-vue-layouts'
import Pages from 'vite-plugin-pages'

export function createPlugins(env, isBuild) {
  const plugins = [
    // Vueサポート
    vue({
      include: [/\.vue$/, /\.md$/],
      reactivityTransform: true
    }),
    
    // API自動インポート
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia',
        '@vueuse/core',
        {
          '@supabase/supabase-js': ['createClient'],
          'date-fns': ['format', 'parseISO', 'isValid']
        }
      ],
      dirs: [
        'src/composables/**',
        'src/stores/**',
        'src/utils/**'
      ],
      vueTemplate: true,
      eslintrc: {
        enabled: true
      }
    }),
    
    // コンポーネント自動インポート
    Components({
      dirs: [
        'src/components',
        'src/layouts'
      ],
      extensions: ['vue', 'md'],
      deep: true,
      resolvers: []
    }),
    
    // ファイルベースルーティング
    Pages({
      dirs: [
        { dir: 'src/views', baseRoute: '' },
        { dir: 'src/views/admin', baseRoute: '/admin' }
      ],
      extensions: ['vue', 'md'],
      exclude: ['**/components/**/*.vue'],
      routeBlockLang: 'yaml',
      importMode: 'async'
    }),
    
    // レイアウトシステム
    Layouts({
      layoutsDirs: 'src/layouts',
      defaultLayout: 'default'
    }),
    
    // SVGアイコン
    createSvgIconsPlugin({
      iconDirs: [resolve(process.cwd(), 'src/assets/icons')],
      symbolId: 'icon-[dir]-[name]',
      customDomId: '__svg__icons__dom__'
    })
  ]
  
  // 開発専用プラグイン
  if (!isBuild) {
    // モックAPI
    plugins.push(
      mockPlugin({
        mockPath: 'mock',
        localEnabled: true
      })
    )
    
    // インスペクター
    plugins.push(
      inspectorPlugin()
    )
  }
  
  // 本番専用プラグイン
  if (isBuild) {
    // PWA
    plugins.push(
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/your-api-domain\.com\/api\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1年
                },
                cacheableResponse: {
                  statuses: [0, 200]
                }
              }
            }
          ]
        },
        manifest: {
          name: 'My Vue App',
          short_name: 'VueApp',
          description: 'SupabaseによるVue.jsアプリケーション',
          theme_color: '#ffffff',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            }
          ]
        }
      })
    )
    
    // バンドル分析
    plugins.push(
      bundleAnalyzer({
        analyzerMode: 'static',
        openAnalyzer: false,
        reportFilename: 'bundle-report.html'
      })
    )
  }
  
  return plugins
}
```

### カスタムプラグイン

```javascript
// plugins/supabase-types.js
import { readFileSync, writeFileSync } from 'fs'
import { resolve } from 'path'

export function supabaseTypesPlugin() {
  return {
    name: 'supabase-types',
    configResolved(config) {
      this.isProduction = config.command === 'build'
    },
    buildStart() {
      // SupabaseからTypeScript型を生成
      this.generateTypes()
    },
    async generateTypes() {
      try {
        // Supabaseインスタンスに接続して型を生成
        console.log('Supabase型を生成中...')
        
        // 型生成の例（実際の実装に置き換える）
        const types = `
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          created_at: string
        }
        Insert: {
          id?: string
          email: string
          created_at?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
        }
      }
    }
  }
}
        `
        
        writeFileSync(
          resolve(process.cwd(), 'src/types/database.ts'),
          types.trim()
        )
        
        console.log('Supabase型が正常に生成されました')
      } catch (error) {
        console.error('Supabase型の生成に失敗しました:', error)
      }
    }
  }
}

// plugins/env-vars.js
export function envVarsPlugin() {
  return {
    name: 'env-vars',
    config(config, { command }) {
      // 必要な環境変数を検証
      const requiredVars = [
        'VITE_SUPABASE_URL',
        'VITE_SUPABASE_ANON_KEY'
      ]
      
      const missing = requiredVars.filter(
        varName => !process.env[varName]
      )
      
      if (missing.length > 0) {
        throw new Error(
          `必要な環境変数が不足しています: ${missing.join(', ')}`
        )
      }
      
      // 環境固有の設定を追加
      if (command === 'serve') {
        config.define = config.define || {}
        config.define['__DEV_MODE__'] = true
      }
    }
  }
}
```

## アセット処理

### 静的アセット処理

```javascript
// vite.config.assets.js
export default defineConfig({
  // アセット処理
  assetsInclude: [
    '**/*.glb',
    '**/*.gltf', 
    '**/*.hdr',
    '**/*.pdf'
  ],
  
  build: {
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          const extType = assetInfo.name.split('.').at(-1)
          
          // 画像
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return `assets/images/[name]-[hash][extname]`
          }
          
          // フォント
          if (/woff|woff2|eot|ttf|otf/i.test(extType)) {
            return `assets/fonts/[name]-[hash][extname]`
          }
          
          // メディア
          if (/mp4|webm|ogg|mp3|wav|flac|aac/i.test(extType)) {
            return `assets/media/[name]-[hash][extname]`
          }
          
          // ドキュメント
          if (/pdf|doc|docx|xls|xlsx|ppt|pptx/i.test(extType)) {
            return `assets/documents/[name]-[hash][extname]`
          }
          
          return `assets/[name]-[hash][extname]`
        }
      }
    }
  },
  
  // CSSアセット処理
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @import "@/styles/variables.scss";
          @import "@/styles/mixins.scss";
          
          // アセットヘルパー関数
          @function asset-url($path) {
            @return url('/src/assets/' + $path);
          }
          
          @function image-url($path) {
            @return url('/src/assets/images/' + $path);
          }
        `
      }
    }
  }
})
```

### 動的インポートとコード分割

```javascript
// utils/dynamic-imports.js
// 適切なエラーハンドリング付き動的インポートのユーティリティ
export async function importComponent(componentPath) {
  try {
    const module = await import(`../components/${componentPath}.vue`)
    return module.default
  } catch (error) {
    console.error(`コンポーネントの読み込みに失敗しました: ${componentPath}`, error)
    
    // フォールバックコンポーネントを返す
    return {
      template: `
        <div class="alert alert-error">
          <span>コンポーネントの読み込みに失敗しました: ${componentPath}</span>
        </div>
      `
    }
  }
}

// ルートベースのコード分割
export const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import(
      /* webpackChunkName: "dashboard" */ 
      '@/views/Dashboard.vue'
    )
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import(
      /* webpackChunkName: "admin" */ 
      '@/views/admin/Index.vue'
    ),
    children: [
      {
        path: 'users',
        component: () => import(
          /* webpackChunkName: "admin-users" */ 
          '@/views/admin/Users.vue'
        )
      }
    ]
  }
]

// Suspense付きコンポーネント遅延読み込み
import { defineAsyncComponent } from 'vue'

export const LazyDataTable = defineAsyncComponent({
  loader: () => import('@/components/DataTable.vue'),
  loadingComponent: () => import('@/components/LoadingSpinner.vue'),
  errorComponent: () => import('@/components/ErrorFallback.vue'),
  delay: 200,
  timeout: 3000
})
```

## 環境変数

### 環境設定

```bash
# .env
VITE_APP_TITLE=My Vue App
VITE_APP_DESCRIPTION=SupabaseによるVue.jsアプリケーション

# .env.local（コミットしない）
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_LOG_LEVEL=debug
VITE_ENABLE_DEVTOOLS=true

# .env.staging
VITE_API_BASE_URL=https://staging-api.example.com
VITE_LOG_LEVEL=info
VITE_ENABLE_DEVTOOLS=false

# .env.production
VITE_API_BASE_URL=https://api.example.com
VITE_LOG_LEVEL=error
VITE_ENABLE_DEVTOOLS=false
```

```javascript
// utils/env.js
// 検証と型変換付き環境変数ユーティリティ
class EnvConfig {
  constructor() {
    this.validateRequired()
  }
  
  validateRequired() {
    const required = [
      'VITE_SUPABASE_URL',
      'VITE_SUPABASE_ANON_KEY'
    ]
    
    const missing = required.filter(key => !import.meta.env[key])
    
    if (missing.length > 0) {
      throw new Error(`必要な環境変数が不足しています: ${missing.join(', ')}`)
    }
  }
  
  get(key, defaultValue = undefined) {
    return import.meta.env[key] ?? defaultValue
  }
  
  getBoolean(key, defaultValue = false) {
    const value = this.get(key)
    if (value === undefined) return defaultValue
    return value === 'true' || value === '1'
  }
  
  getNumber(key, defaultValue = 0) {
    const value = this.get(key)
    if (value === undefined) return defaultValue
    const num = Number(value)
    return isNaN(num) ? defaultValue : num
  }
  
  getArray(key, defaultValue = [], separator = ',') {
    const value = this.get(key)
    if (!value) return defaultValue
    return value.split(separator).map(item => item.trim())
  }
  
  // よく使用される変数のゲッター
  get isDevelopment() {
    return import.meta.env.DEV
  }
  
  get isProduction() {
    return import.meta.env.PROD
  }
  
  get supabaseUrl() {
    return this.get('VITE_SUPABASE_URL')
  }
  
  get supabaseAnonKey() {
    return this.get('VITE_SUPABASE_ANON_KEY')
  }
  
  get apiBaseUrl() {
    return this.get('VITE_API_BASE_URL', 'http://localhost:3000')
  }
  
  get logLevel() {
    return this.get('VITE_LOG_LEVEL', 'info')
  }
  
  get enableDevtools() {
    return this.getBoolean('VITE_ENABLE_DEVTOOLS', this.isDevelopment)
  }
}

export const env = new EnvConfig()
```

## コード分割

### 高度なコード分割戦略

```javascript
// vite.config.splitting.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // ベンダーチャンク
          if (id.includes('node_modules')) {
            // コアVueエコシステム
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vendor-vue'
            }
            
            // Supabaseと認証
            if (id.includes('@supabase') || id.includes('auth')) {
              return 'vendor-auth'
            }
            
            // UIライブラリ
            if (id.includes('@headlessui') || id.includes('daisyui') || id.includes('@heroicons')) {
              return 'vendor-ui'
            }
            
            // ユーティリティ
            if (id.includes('date-fns') || id.includes('lodash') || id.includes('@vueuse')) {
              return 'vendor-utils'
            }
            
            // チャートライブラリ
            if (id.includes('chart') || id.includes('d3') || id.includes('echarts')) {
              return 'vendor-charts'
            }
            
            return 'vendor'
          }
          
          // ルート構造に基づくページチャンク
          if (id.includes('src/views/')) {
            if (id.includes('admin/')) {
              return 'pages-admin'
            }
            if (id.includes('auth/')) {
              return 'pages-auth'
            }
            if (id.includes('dashboard/')) {
              return 'pages-dashboard'
            }
            return 'pages'
          }
          
          // コンポーネントチャンク
          if (id.includes('src/components/')) {
            if (id.includes('forms/')) {
              return 'components-forms'
            }
            if (id.includes('charts/')) {
              return 'components-charts'
            }
            if (id.includes('tables/')) {
              return 'components-tables'
            }
            return 'components'
          }
          
          // ComposableとユーティリティI
          if (id.includes('src/composables/') || id.includes('src/utils/')) {
            return 'utils'
          }
          
          // ストア
          if (id.includes('src/stores/')) {
            return 'stores'
          }
        }
      }
    }
  }
})

// 動的チャンク読み込みユーティリティ
export class ChunkLoader {
  static loadedChunks = new Set()
  static loadingChunks = new Map()
  
  static async loadChunk(chunkName) {
    if (this.loadedChunks.has(chunkName)) {
      return true
    }
    
    if (this.loadingChunks.has(chunkName)) {
      return this.loadingChunks.get(chunkName)
    }
    
    const loadPromise = this.loadChunkImpl(chunkName)
    this.loadingChunks.set(chunkName, loadPromise)
    
    try {
      await loadPromise
      this.loadedChunks.add(chunkName)
      this.loadingChunks.delete(chunkName)
      return true
    } catch (error) {
      this.loadingChunks.delete(chunkName)
      throw error
    }
  }
  
  static async loadChunkImpl(chunkName) {
    // チャンク構造に基づいて実装される
    switch (chunkName) {
      case 'admin':
        return import('@/views/admin/Index.vue')
      case 'charts':
        return import('@/components/charts/index.js')
      default:
        throw new Error(`不明なチャンク: ${chunkName}`)
    }
  }
  
  static preloadChunk(chunkName) {
    // ブロックせずにチャンクをプリロード
    this.loadChunk(chunkName).catch(error => {
      console.warn(`チャンク${chunkName}のプリロードに失敗しました:`, error)
    })
  }
}
```

## PWA設定

### Progressive Web App設定

```javascript
// vite.config.pwa.js
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true
      },
      
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          // APIレスポンス
          {
            urlPattern: /^https:\/\/.*\.supabase\.co\/rest\/v1\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'supabase-api',
              networkTimeoutSeconds: 3,
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 5 * 60 // 5分
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          
          // 画像
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'images',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 30 * 24 * 60 * 60 // 30日
              }
            }
          },
          
          // Google Fonts
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1年
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ],
        
        // Skip waitingとclaim clients
        skipWaiting: true,
        clientsClaim: true,
        
        // 古いキャッシュをクリーンアップ
        cleanupOutdatedCaches: true
      },
      
      manifest: {
        name: 'My Vue App',
        short_name: 'VueApp',
        description: 'Supabaseバックエンド付きVue.jsアプリケーション',
        theme_color: '#3b82f6',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        
        icons: [
          {
            src: 'icons/pwa-64x64.png',
            sizes: '64x64',
            type: 'image/png'
          },
          {
            src: 'icons/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'icons/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'icons/maskable-icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ],
        
        shortcuts: [
          {
            name: 'ダッシュボード',
            short_name: 'ダッシュボード',
            description: 'ダッシュボードを開く',
            url: '/dashboard',
            icons: [{ src: 'icons/dashboard-96x96.png', sizes: '96x96' }]
          }
        ]
      }
    })
  ]
})

// Service Worker登録
// src/registerSW.js
import { registerSW } from 'virtual:pwa-register'

const updateSW = registerSW({
  onNeedRefresh() {
    // ユーザーに更新利用可能通知を表示
    console.log('新しいコンテンツが利用可能です。クリックして更新してください')
    
    // ここでトーストやモーダルを表示できます
    if (confirm('新しいコンテンツが利用可能です。リロードしますか？')) {
      updateSW(true)
    }
  },
  
  onOfflineReady() {
    console.log('アプリがオフラインで動作する準備ができました')
    // オフライン準備完了通知を表示
  },
  
  immediate: true
})

// 定期的SW更新
setInterval(() => {
  updateSW(true)
}, 60000) // 1分ごとに更新をチェック
```

## テスト設定

### Vitest設定

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    
    // カバレッジ設定
    coverage: {
      provider: 'c8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.test.{js,ts,vue}',
        '**/*.spec.{js,ts,vue}'
      ]
    },
    
    // テストファイルパターン
    include: [
      'src/**/*.{test,spec}.{js,ts,vue}',
      'tests/**/*.{test,spec}.{js,ts,vue}'
    ],
    
    // モック処理
    deps: {
      inline: ['@vue', '@vueuse']
    }
  },
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '~': resolve(__dirname, 'src')
    }
  },
  
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false
  }
})

// src/test/setup.js
import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Supabaseをモック
vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      signIn: vi.fn(),
      signOut: vi.fn(),
      getUser: vi.fn()
    },
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => Promise.resolve({ data: [], error: null }))
      }))
    }))
  }
}))

// グローバルテストユーティリティ
config.global.mocks = {
  $t: (key) => key, // i18nモック
  $route: {
    path: '/',
    params: {},
    query: {}
  },
  $router: {
    push: vi.fn(),
    replace: vi.fn()
  }
}

// DOMクリーンアップ
afterEach(() => {
  document.body.innerHTML = ''
})
```

### テストユーティリティ

```javascript
// src/test/utils.js
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// テストルーターを作成
export function createTestRouter(routes = []) {
  return createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
      ...routes
    ]
  })
}

// 共通プロバイダー付きでコンポーネントをマウント
export function mountWithProviders(component, options = {}) {
  const pinia = createPinia()
  const router = createTestRouter()
  
  return mount(component, {
    global: {
      plugins: [pinia, router],
      stubs: {
        RouterLink: true,
        RouterView: true,
        ...options.stubs
      },
      mocks: {
        $t: (key) => key,
        ...options.mocks
      }
    },
    ...options
  })
}

// APIレスポンスモック
export function mockApiResponse(data, error = null) {
  return {
    data,
    error,
    status: error ? 400 : 200,
    statusText: error ? 'Bad Request' : 'OK'
  }
}

// 次のティックとDOM更新を待機
export async function waitForUpdate() {
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 0))
}
```

## デプロイ設定

### Vercelデプロイ

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*\\.(js|css|ico|png|jpg|jpeg|svg|woff|woff2))",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_SUPABASE_URL": "@supabase-url",
    "VITE_SUPABASE_ANON_KEY": "@supabase-anon-key"
  }
}
```

### Netlifyデプロイ

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### Docker設定

```dockerfile
# Dockerfile
FROM node:18-alpine as build-stage

WORKDIR /app

# パッケージファイルをコピー
COPY package*.json ./
RUN npm ci --only=production

# ソースコードをコピー
COPY . .

# アプリケーションをビルド
RUN npm run build

# 本番ステージ
FROM nginx:alpine as production-stage

# ビルドされたアプリケーションをコピー
COPY --from=build-stage /app/dist /usr/share/nginx/html

# nginx設定をコピー
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Gzip圧縮
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    server {
        listen       80;
        server_name  localhost;
        
        root /usr/share/nginx/html;
        index index.html;
        
        # 静的アセットをキャッシュ
        location /assets/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # SPAルーティングを処理
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # セキュリティヘッダー
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
}
```

## パフォーマンス監視

### バンドル分析と監視

```javascript
// scripts/analyze-bundle.js
import { execSync } from 'child_process'
import { readFileSync, writeFileSync } from 'fs'
import { resolve } from 'path'

class BundleAnalyzer {
  constructor() {
    this.distPath = resolve(process.cwd(), 'dist')
    this.reportPath = resolve(process.cwd(), 'bundle-analysis.json')
  }
  
  analyze() {
    console.log('バンドルを分析中...')
    
    // バンドルレポートを生成
    execSync('npm run build -- --analyze', { stdio: 'inherit' })
    
    // バンドルサイズを解析
    const report = this.parseBundleReport()
    
    // 推奨事項を生成
    const recommendations = this.generateRecommendations(report)
    
    // 分析結果を保存
    const analysis = {
      timestamp: new Date().toISOString(),
      report,
      recommendations,
      summary: this.generateSummary(report)
    }
    
    writeFileSync(this.reportPath, JSON.stringify(analysis, null, 2))
    
    console.log('バンドル分析完了！')
    console.log(`総サイズ: ${analysis.summary.totalSize}`)
    console.log(`Gzipサイズ: ${analysis.summary.gzippedSize}`)
    
    return analysis
  }
  
  parseBundleReport() {
    // バンドル分析レポートを解析
    // バンドル分析ツールの出力形式に依存
    return {
      chunks: [],
      assets: [],
      modules: []
    }
  }
  
  generateRecommendations(report) {
    const recommendations = []
    
    // 大きなチャンクをチェック
    const largeChunks = report.chunks.filter(chunk => chunk.size > 500000)
    if (largeChunks.length > 0) {
      recommendations.push({
        type: 'warning',
        title: '大きなチャンクが検出されました',
        description: 'これらのチャンクをさらに分割することを検討してください',
        chunks: largeChunks.map(chunk => chunk.name)
      })
    }
    
    // 重複モジュールをチェック
    const duplicates = this.findDuplicateModules(report.modules)
    if (duplicates.length > 0) {
      recommendations.push({
        type: 'error',
        title: '重複モジュールが見つかりました',
        description: 'これらのモジュールが複数回含まれています',
        modules: duplicates
      })
    }
    
    return recommendations
  }
  
  generateSummary(report) {
    return {
      totalSize: this.formatBytes(report.assets.reduce((sum, asset) => sum + asset.size, 0)),
      gzippedSize: this.formatBytes(report.assets.reduce((sum, asset) => sum + (asset.gzipSize || 0), 0)),
      chunkCount: report.chunks.length,
      assetCount: report.assets.length
    }
  }
  
  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  
  findDuplicateModules(modules) {
    const moduleMap = new Map()
    const duplicates = []
    
    modules.forEach(module => {
      if (moduleMap.has(module.name)) {
        duplicates.push(module.name)
      } else {
        moduleMap.set(module.name, module)
      }
    })
    
    return [...new Set(duplicates)]
  }
}

// 分析を実行
if (import.meta.url === `file://${process.argv[1]}`) {
  const analyzer = new BundleAnalyzer()
  analyzer.analyze()
}
```

# 拡張パフォーマンス監視

```javascript
// utils/enhanced-performance-monitor.js
/**
 * 拡張パフォーマンス監視クラス
 */
export class EnhancedPerformanceMonitor {
  constructor() {
    this.metrics = new Map()
    this.thresholds = {
      lcp: 2500, // Large Contentful Paint
      fid: 100,  // First Input Delay  
      cls: 0.1,  // Cumulative Layout Shift
      fcp: 1800, // First Contentful Paint
      ttfb: 800  // Time to First Byte
    }
    this.observers = new Map()
    this.isEnabled = import.meta.env.DEV || import.meta.env.VITE_ENABLE_PERFORMANCE_MONITORING === 'true'
  }
  
  /**
   * パフォーマンス閾値をチェック
   * @returns {Array} アラート配列
   */
  checkThresholds() {
    const alerts = []
    
    for (const [metric, threshold] of Object.entries(this.thresholds)) {
      const value = this.metrics.get(metric)
      if (value && value > threshold) {
        alerts.push({
          metric,
          value: Math.round(value),
          threshold,
          severity: value > threshold * 1.5 ? 'high' : 'medium',
          impact: this.getMetricImpact(metric),
          suggestions: this.getSuggestions(metric, value)
        })
      }
    }
    
    return alerts
  }
  
  /**
   * メトリクスの影響度を取得
   * @param {string} metric - メトリクス名
   * @returns {string} 影響度説明
   */
  getMetricImpact(metric) {
    const impacts = {
      lcp: 'ページの主要コンテンツの表示が遅い',
      fid: 'ユーザーの最初の操作への反応が遅い',
      cls: 'レイアウトが予期せず移動している',
      fcp: '最初のコンテンツ表示が遅い',
      ttfb: 'サーバーの応答が遅い'
    }
    return impacts[metric] || '不明'
  }
  
  /**
   * 改善提案を取得
   * @param {string} metric - メトリクス名
   * @param {number} value - 測定値
   * @returns {Array} 改善提案
   */
  getSuggestions(metric, value) {
    const suggestions = {
      lcp: [
        '画像の最適化と遅延読み込み',
        'クリティカルCSSのインライン化',
        'サーバーレスポンス時間の改善'
      ],
      fid: [
        'JavaScriptバンドルサイズの削減',
        'メインスレッドのブロック処理の最適化',
        'Web Workersの活用'
      ],
      cls: [
        '画像・広告のサイズ指定',
        'フォント読み込みの最適化',
        'ダイナミックコンテンツの高さ確保'
      ],
      fcp: [
        'クリティカルリソースの優先読み込み',
        'レンダリングブロック要素の削減',
        'CDNの活用'
      ],
      ttfb: [
        'サーバーサイドの最適化',
        'CDNの活用',
        'データベースクエリの最適化'
      ]
    }
    
    return suggestions[metric] || ['一般的な最適化手法を確認してください']
  }
  
  /**
   * パフォーマンススコアを計算
   * @returns {number} 0-100のスコア
   */
  calculateScore() {
    const weights = {
      lcp: 0.25,
      fid: 0.25,
      cls: 0.25,
      fcp: 0.15,
      ttfb: 0.10
    }
    
    let totalScore = 0
    let totalWeight = 0
    
    for (const [metric, weight] of Object.entries(weights)) {
      const value = this.metrics.get(metric)
      const threshold = this.thresholds[metric]
      
      if (value !== undefined && threshold) {
        // スコア計算（100点満点、閾値以下なら満点）
        const score = value <= threshold ? 100 : Math.max(0, 100 - ((value - threshold) / threshold) * 50)
        totalScore += score * weight
        totalWeight += weight
      }
    }
    
    return totalWeight > 0 ? Math.round(totalScore / totalWeight) : 0
  }
  
  /**
   * 詳細レポートを生成
   * @returns {Object} パフォーマンスレポート
   */
  generateReport() {
    const alerts = this.checkThresholds()
    const score = this.calculateScore()
    
    return {
      score,
      grade: score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F',
      metrics: Object.fromEntries(this.metrics),
      alerts,
      summary: {
        total_metrics: this.metrics.size,
        alerts_count: alerts.length,
        high_priority_alerts: alerts.filter(a => a.severity === 'high').length
      },
      recommendations: this.generateRecommendations(alerts),
      timestamp: new Date().toISOString()
    }
  }
  
  /**
   * 全体的な推奨事項を生成
   * @param {Array} alerts - アラート配列
   * @returns {Array} 推奨事項
   */
  generateRecommendations(alerts) {
    const recommendations = []
    
    if (alerts.length === 0) {
      recommendations.push({
        priority: 'maintenance',
        title: '良好なパフォーマンス',
        description: '現在のパフォーマンスは良好です。定期的な監視を継続してください。'
      })
    } else {
      const highPriorityAlerts = alerts.filter(a => a.severity === 'high')
      
      if (highPriorityAlerts.length > 0) {
        recommendations.push({
          priority: 'high',
          title: '緊急改善が必要',
          description: `${highPriorityAlerts.length}件の重要なパフォーマンス問題があります。`,
          actions: highPriorityAlerts.flatMap(alert => alert.suggestions)
        })
      }
      
      const mediumPriorityAlerts = alerts.filter(a => a.severity === 'medium')
      if (mediumPriorityAlerts.length > 0) {
        recommendations.push({
          priority: 'medium',
          title: '改善推奨',
          description: `${mediumPriorityAlerts.length}件のパフォーマンス改善余地があります。`,
          actions: mediumPriorityAlerts.flatMap(alert => alert.suggestions)
        })
      }
    }
    
    return recommendations
  }
  
  /**
   * 監視を開始
   */
  startMonitoring() {
    if (!this.isEnabled) return
    
    this.observeWebVitals()
    this.observeCustomMetrics()
    
    // 定期レポート（本番環境のみ）
    if (import.meta.env.PROD) {
      setInterval(() => {
        this.sendReport()
      }, 60000) // 1分ごと
    }
    
    // ページアンロード時のレポート送信
    window.addEventListener('beforeunload', () => {
      this.sendReport()
    })
  }
  
  /**
   * Web Vitalsを監視
   */
  observeWebVitals() {
    // LCP観測
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const lastEntry = entries[entries.length - 1]
      this.metrics.set('lcp', lastEntry.startTime)
    })
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })
    this.observers.set('lcp', lcpObserver)
    
    // FID観測
    const fidObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        this.metrics.set('fid', entry.processingStart - entry.startTime)
      }
    })
    fidObserver.observe({ entryTypes: ['first-input'] })
    this.observers.set('fid', fidObserver)
    
    // CLS観測
    let clsValue = 0
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value
        }
      }
      this.metrics.set('cls', clsValue)
    })
    clsObserver.observe({ entryTypes: ['layout-shift'] })
    this.observers.set('cls', clsObserver)
  }
  
  /**
   * カスタムメトリクスを監視
   */
  observeCustomMetrics() {
    // ナビゲーション詳細
    const navObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'navigation') {
          this.metrics.set('ttfb', entry.responseStart - entry.requestStart)
          this.metrics.set('fcp', entry.responseEnd - entry.responseStart)
        }
      }
    })
    navObserver.observe({ entryTypes: ['navigation'] })
    this.observers.set('navigation', navObserver)
  }
  
  /**
   * レポートを外部サービスに送信
   */
  sendReport() {
    if (!import.meta.env.PROD) return
    
    const report = this.generateReport()
    
    // Analytics送信（例：Google Analytics）
    if (typeof gtag !== 'undefined') {
      gtag('event', 'performance_report', {
        score: report.score,
        grade: report.grade,
        alerts_count: report.summary.alerts_count
      })
    }
    
    // カスタムAPI送信
    if (import.meta.env.VITE_PERFORMANCE_API) {
      fetch(import.meta.env.VITE_PERFORMANCE_API, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(report)
      }).catch(error => {
        console.warn('パフォーマンスレポート送信失敗:', error)
      })
    }
  }
  
  /**
   * 監視を停止してクリーンアップ
   */
  stopMonitoring() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers.clear()
    this.metrics.clear()
  }
}

// シングルトンインスタンス
export const performanceMonitor = new EnhancedPerformanceMonitor()

// 自動開始
if (typeof window !== 'undefined') {
  performanceMonitor.startMonitoring()
}
```

## トラブルシューティング

### よくある問題と解決法

```javascript
// utils/diagnostics.js
export class ViteDiagnostics {
  static async runDiagnostics() {
    const results = {
      timestamp: new Date().toISOString(),
      environment: this.checkEnvironment(),
      dependencies: await this.checkDependencies(),
      configuration: this.checkConfiguration(),
      build: await this.checkBuild(),
      network: await this.checkNetwork()
    }
    
    console.log('Vite診断結果:', results)
    return results
  }
  
  static checkEnvironment() {
    return {
      nodeVersion: process.version,
      platform: process.platform,
      arch: process.arch,
      viteVersion: this.getPackageVersion('vite'),
      vueVersion: this.getPackageVersion('vue'),
      isDev: import.meta.env.DEV,
      isProd: import.meta.env.PROD,
      mode: import.meta.env.MODE
    }
  }
  
  static async checkDependencies() {
    const issues = []
    
    // 一般的な依存関係の競合をチェック
    const conflicts = [
      ['vue', '^3.0.0'],
      ['@vitejs/plugin-vue', '^4.0.0'],
      ['vite', '^4.0.0']
    ]
    
    conflicts.forEach(([pkg, expectedVersion]) => {
      const version = this.getPackageVersion(pkg)
      if (!version) {
        issues.push(`必要な依存関係が不足しています: ${pkg}`)
      } else if (!this.satisfiesVersion(version, expectedVersion)) {
        issues.push(`バージョンの不一致: ${pkg}@${version} (期待値 ${expectedVersion})`)
      }
    })
    
    return {
      issues,
      packageVersions: this.getAllPackageVersions()
    }
  }
  
  static checkConfiguration() {
    const issues = []
    
    // 環境変数をチェック
    const requiredEnvVars = [
      'VITE_SUPABASE_URL',
      'VITE_SUPABASE_ANON_KEY'
    ]
    
    requiredEnvVars.forEach(varName => {
      if (!import.meta.env[varName]) {
        issues.push(`環境変数が不足しています: ${varName}`)
      }
    })
    
    return {
      issues,
      envVars: Object.keys(import.meta.env).filter(key => key.startsWith('VITE_'))
    }
  }
  
  static async checkBuild() {
    const issues = []
    
    try {
      // ビルドディレクトリが存在し、期待されるファイルがあるかチェック
      const buildFiles = ['index.html', 'assets']
      // これは実際の環境ではファイルシステムをチェックする
      
      return {
        issues,
        buildExists: true,
        buildFiles: buildFiles
      }
    } catch (error) {
      issues.push(`ビルドチェックに失敗しました: ${error.message}`)
      return { issues, buildExists: false }
    }
  }
  
  static async checkNetwork() {
    const issues = []
    const checks = []
    
    // Supabase接続をチェック
    try {
      const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
      if (supabaseUrl) {
        const response = await fetch(`${supabaseUrl}/rest/v1/`, {
          method: 'HEAD',
          headers: {
            'apikey': import.meta.env.VITE_SUPABASE_ANON_KEY
          }
        })
        
        checks.push({
          service: 'Supabase',
          status: response.ok ? 'ok' : 'error',
          statusCode: response.status
        })
      }
    } catch (error) {
      issues.push(`Supabase接続に失敗しました: ${error.message}`)
    }
    
    return { issues, checks }
  }
  
  static getPackageVersion(packageName) {
    try {
      // 実際の実装ではpackage.jsonから読み取り
      return '1.0.0' // プレースホルダー
    } catch {
      return null
    }
  }
  
  static getAllPackageVersions() {
    // package.jsonから全パッケージバージョンを返す
    return {}
  }
  
  static satisfiesVersion(actual, expected) {
    // 簡単なバージョンチェック - 実際の実装ではsemverを使用
    return true
  }
}

// デバッグユーティリティ
export const debugUtils = {
  logHMRUpdates() {
    if (import.meta.hot) {
      import.meta.hot.on('vite:beforeUpdate', (payload) => {
        console.log('HMR更新:', payload)
      })
      
      import.meta.hot.on('vite:error', (payload) => {
        console.error('HMRエラー:', payload)
      })
    }
  },
  
  logPerformanceMetrics() {
    if (window.performance) {
      const navigation = performance.getEntriesByType('navigation')[0]
      console.table({
        'DNS検索': navigation.domainLookupEnd - navigation.domainLookupStart,
        'TCP接続': navigation.connectEnd - navigation.connectStart,
        'リクエスト': navigation.responseStart - navigation.requestStart,
        'レスポンス': navigation.responseEnd - navigation.responseStart,
        'DOM処理': navigation.domComplete - navigation.responseEnd,
        '総読み込み時間': navigation.loadEventEnd - navigation.navigationStart
      })
    }
  },
  
  async analyzeBundle() {
    // 現在のバンドルを分析
    console.log('ランタイムではバンドル分析は利用できません')
  }
}

// 開発用エラーバウンダリ
export function createErrorHandler() {
  return (error, instance, info) => {
    console.error('Vueエラー:', error)
    console.error('コンポーネント:', instance)
    console.error('情報:', info)
    
    // 本番環境ではエラー報告サービスに送信
    if (import.meta.env.PROD) {
      // Sentry等のサービスにエラーを報告
    }
  }
}
```

### パフォーマンスデバッグ

```javascript
// パフォーマンスデバッグユーティリティ
export const perfDebug = {
  measureComponentRender(componentName) {
    if (!import.meta.env.DEV) return
    
    return {
      beforeCreate() {
        performance.mark(`${componentName}-create-start`)
      },
      created() {
        performance.mark(`${componentName}-create-end`)
        performance.measure(
          `${componentName}-create`,
          `${componentName}-create-start`,
          `${componentName}-create-end`
        )
      },
      beforeMount() {
        performance.mark(`${componentName}-mount-start`)
      },
      mounted() {
        performance.mark(`${componentName}-mount-end`)
        performance.measure(
          `${componentName}-mount`,
          `${componentName}-mount-start`,
          `${componentName}-mount-end`
        )
        
        const createTime = performance.getEntriesByName(`${componentName}-create`)[0]?.duration
        const mountTime = performance.getEntriesByName(`${componentName}-mount`)[0]?.duration
        
        console.log(`${componentName} パフォーマンス:`, {
          create: `${createTime?.toFixed(2)}ms`,
          mount: `${mountTime?.toFixed(2)}ms`,
          total: `${(createTime + mountTime)?.toFixed(2)}ms`
        })
      }
    }
  },
  
  watchReactivity(target, label = 'Reactive Object') {
    if (!import.meta.env.DEV) return target
    
    return new Proxy(target, {
      get(obj, prop) {
        console.log(`${label}: ${String(prop)}を取得中`)
        return obj[prop]
      },
      set(obj, prop, value) {
        console.log(`${label}: ${String(prop)}を設定中`, value)
        obj[prop] = value
        return true
      }
    })
  },
  
  logRenderCount(componentName) {
    let renderCount = 0
    
    return {
      beforeUpdate() {
        renderCount++
        console.log(`${componentName} レンダー #${renderCount}`)
      }
    }
  }
}
```

## ✅ 開発品質チェックリスト

### Vite設定
- [ ] **基本設定**: 適切なエイリアスとパス解決
- [ ] **環境変数**: セキュアな環境変数管理
- [ ] **プラグイン**: 必要なプラグインの適切な設定
- [ ] **最適化**: 本番ビルドの最適化設定
- [ ] **JSDoc**: 関数とオブジェクトの適切なドキュメント化

### パフォーマンス
- [ ] **バンドル分割**: 効率的なコード分割戦略
- [ ] **キャッシュ**: 適切なキャッシュ戦略の実装
- [ ] **圧縮**: Gzip/Brotli圧縮の有効化
- [ ] **レガシー**: 古いブラウザサポート（必要に応じて）
- [ ] **プリロード**: 重要リソースのプリロード

### 開発体験
- [ ] **HMR**: Hot Module Replacementの適切な設定
- [ ] **ソースマップ**: 開発時のソースマップ生成
- [ ] **エラーハンドリング**: 開発時の適切なエラー表示
- [ ] **デバッグ**: デバッグツールとユーティリティ
- [ ] **テスト**: テスト環境の適切な設定

### セキュリティ
- [ ] **環境変数**: 機密情報の適切な管理
- [ ] **CSP**: Content Security Policyの設定
- [ ] **HTTPS**: 本番環境でのHTTPS使用
- [ ] **依存関係**: セキュリティ監査と更新
- [ ] **ビルド**: セキュアなビルドプロセス

### デプロイ
- [ ] **CI/CD**: 自動化されたビルドとデプロイ
- [ ] **環境管理**: 環境別の適切な設定
- [ ] **モニタリング**: エラーとパフォーマンスの監視
- [ ] **ロールバック**: デプロイの迅速なロールバック機能
- [ ] **スケーリング**: トラフィック増加への対応

## 📚 関連ドキュメント

- **[Vue Compositionパターン](./01_vue_composition_patterns.md)** - Vue 3 Composition APIパターン
- **[Pinia状態管理パターン](./02_pinia_store_patterns.md)** - 状態管理との統合
- **[Supabase連携パターン](./03_supabase_integration.md)** - データベース操作との連携

## リソース

- [Vite Documentation](https://vitejs.dev)
- [Vite Plugin Directory](https://github.com/vitejs/awesome-vite)
- [Rollup Configuration](https://rollupjs.org/configuration-options/)
- [esbuild Documentation](https://esbuild.github.io)
- [Vitest Testing Framework](https://vitest.dev)
- [PWA Builder](https://www.pwabuilder.com)
- [Web Vitals](https://web.dev/vitals/)
- [Bundle Analyzer Tools](https://github.com/webpack-contrib/webpack-bundle-analyzer)