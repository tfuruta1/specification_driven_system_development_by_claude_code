# Vue Router 設計パターン

## 1. ルーティング設計概要

### 基本構成
```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { navigationGuards } from './guards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // パブリックルート
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomeView.vue'),
      meta: {
        title: 'ホーム',
        description: 'ホームページ',
        requiresAuth: false
      }
    },
    
    // 認証ルート
    {
      path: '/auth',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        {
          path: 'login',
          name: 'Login',
          component: () => import('@/views/auth/LoginView.vue'),
          meta: {
            title: 'ログイン',
            requiresGuest: true
          }
        },
        {
          path: 'signup',
          name: 'Signup',
          component: () => import('@/views/auth/SignupView.vue'),
          meta: {
            title: '会員登録',
            requiresGuest: true
          }
        },
        {
          path: 'forgot-password',
          name: 'ForgotPassword',
          component: () => import('@/views/auth/ForgotPasswordView.vue'),
          meta: {
            title: 'パスワードリセット',
            requiresGuest: true
          }
        }
      ]
    },

    // 保護されたルート
    {
      path: '/dashboard',
      component: () => import('@/layouts/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: {
            title: 'ダッシュボード',
            breadcrumb: [
              { name: 'ダッシュボード', path: '/dashboard' }
            ]
          }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/dashboard/ProfileView.vue'),
          meta: {
            title: 'プロフィール',
            breadcrumb: [
              { name: 'ダッシュボード', path: '/dashboard' },
              { name: 'プロフィール', path: '/dashboard/profile' }
            ]
          }
        },
        {
          path: 'posts',
          children: [
            {
              path: '',
              name: 'Posts',
              component: () => import('@/views/dashboard/PostsView.vue'),
              meta: {
                title: '投稿管理',
                breadcrumb: [
                  { name: 'ダッシュボード', path: '/dashboard' },
                  { name: '投稿管理', path: '/dashboard/posts' }
                ]
              }
            },
            {
              path: 'create',
              name: 'CreatePost',
              component: () => import('@/views/dashboard/CreatePostView.vue'),
              meta: {
                title: '新規投稿',
                breadcrumb: [
                  { name: 'ダッシュボード', path: '/dashboard' },
                  { name: '投稿管理', path: '/dashboard/posts' },
                  { name: '新規投稿', path: '/dashboard/posts/create' }
                ]
              }
            },
            {
              path: ':id/edit',
              name: 'EditPost',
              component: () => import('@/views/dashboard/EditPostView.vue'),
              props: true,
              meta: {
                title: '投稿編集',
                breadcrumb: [
                  { name: 'ダッシュボード', path: '/dashboard' },
                  { name: '投稿管理', path: '/dashboard/posts' },
                  { name: '投稿編集', path: null }
                ]
              }
            }
          ]
        }
      ]
    },

    // パブリック投稿ルート
    {
      path: '/posts',
      children: [
        {
          path: '',
          name: 'PostsList',
          component: () => import('@/views/posts/PostsListView.vue'),
          meta: {
            title: '投稿一覧',
            description: '最新の投稿をお楽しみください'
          }
        },
        {
          path: ':slug',
          name: 'PostDetail',
          component: () => import('@/views/posts/PostDetailView.vue'),
          props: true,
          meta: {
            title: '投稿詳細',
            dynamicTitle: true // 動的にタイトルを設定
          }
        }
      ]
    },

    // エラーページ
    {
      path: '/404',
      name: 'NotFound',
      component: () => import('@/views/errors/NotFoundView.vue'),
      meta: {
        title: 'ページが見つかりません'
      }
    },

    // 全てのルートにマッチしない場合
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ],
  
  scrollBehavior(to, from, savedPosition) {
    // 保存された位置があれば復元
    if (savedPosition) {
      return savedPosition
    }
    
    // ハッシュがあればその位置にスクロール
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    }
    
    // 新しいページでは先頭にスクロール
    return { top: 0 }
  }
})

// ナビゲーションガードを適用
navigationGuards(router)

export default router
```

## 2. ナビゲーションガード

### 2.1 認証ガード
```javascript
// router/guards.js
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

export function navigationGuards(router) {
  // グローバル beforeEach ガード
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    // 認証状態の確認（必要に応じて）
    if (!authStore.initialized) {
      await authStore.initializeAuth()
    }

    // 認証が必要なルート
    if (to.meta.requiresAuth && !authStore.isLoggedIn) {
      notificationStore.showError('ログインが必要です')
      return next({
        name: 'Login',
        query: { redirect: to.fullPath }
      })
    }

    // ゲスト専用ルート（ログイン済みの場合はリダイレクト）
    if (to.meta.requiresGuest && authStore.isLoggedIn) {
      return next({ name: 'Dashboard' })
    }

    // 管理者権限が必要なルート
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      notificationStore.showError('管理者権限が必要です')
      return next({ name: 'Dashboard' })
    }

    // 権限チェック
    if (to.meta.permissions) {
      const hasPermission = authStore.hasPermissions(to.meta.permissions)
      if (!hasPermission) {
        notificationStore.showError('このページにアクセスする権限がありません')
        return next({ name: 'Dashboard' })
      }
    }

    next()
  })

  // グローバル afterEach ガード
  router.afterEach((to, from) => {
    // ページタイトルの設定
    updatePageTitle(to)
    
    // メタタグの更新
    updateMetaTags(to)
    
    // ページビュー追跡
    trackPageView(to)
  })
}

/**
 * ページタイトルを更新
 * @param {Object} route - ルートオブジェクト
 */
function updatePageTitle(route) {
  const baseTitle = 'MyApp'
  
  if (route.meta.dynamicTitle) {
    // 動的タイトルは後でコンポーネント内で設定
    return
  }
  
  if (route.meta.title) {
    document.title = `${route.meta.title} | ${baseTitle}`
  } else {
    document.title = baseTitle
  }
}

/**
 * メタタグを更新
 * @param {Object} route - ルートオブジェクト
 */
function updateMetaTags(route) {
  // 既存のメタタグを削除
  const existingMeta = document.querySelectorAll('meta[data-dynamic]')
  existingMeta.forEach(tag => tag.remove())

  // 新しいメタタグを追加
  if (route.meta.description) {
    const descriptionMeta = document.createElement('meta')
    descriptionMeta.setAttribute('name', 'description')
    descriptionMeta.setAttribute('content', route.meta.description)
    descriptionMeta.setAttribute('data-dynamic', 'true')
    document.head.appendChild(descriptionMeta)
  }

  // OGタグの設定
  if (route.meta.ogImage) {
    const ogImageMeta = document.createElement('meta')
    ogImageMeta.setAttribute('property', 'og:image')
    ogImageMeta.setAttribute('content', route.meta.ogImage)
    ogImageMeta.setAttribute('data-dynamic', 'true')
    document.head.appendChild(ogImageMeta)
  }
}

/**
 * ページビューを追跡
 * @param {Object} route - ルートオブジェクト
 */
function trackPageView(route) {
  // Googleアナリティクス等での追跡
  if (typeof gtag !== 'undefined') {
    gtag('config', 'GA_TRACKING_ID', {
      page_path: route.fullPath
    })
  }
}
```

### 2.2 権限ベースのガード
```javascript
// router/permissions.js
import { useAuthStore } from '@/stores/auth'

/**
 * 権限チェック関数
 * @param {string|string[]} permissions - 必要な権限
 * @param {string} mode - チェックモード ('any' | 'all')
 * @returns {boolean}
 */
export function checkPermissions(permissions, mode = 'any') {
  const authStore = useAuthStore()
  
  if (!authStore.user) return false
  
  const userPermissions = authStore.user.permissions || []
  const requiredPermissions = Array.isArray(permissions) ? permissions : [permissions]
  
  if (mode === 'all') {
    return requiredPermissions.every(permission => 
      userPermissions.includes(permission)
    )
  } else {
    return requiredPermissions.some(permission => 
      userPermissions.includes(permission)
    )
  }
}

/**
 * ルート定義での権限指定例
 */
export const protectedRoutes = [
  {
    path: '/admin',
    meta: {
      requiresAuth: true,
      permissions: ['admin.access'],
      permissionMode: 'all'
    }
  },
  {
    path: '/posts/manage',
    meta: {
      requiresAuth: true,
      permissions: ['posts.create', 'posts.edit'],
      permissionMode: 'any'
    }
  }
]
```

## 3. 動的ルート管理

### 3.1 動的ルート生成
```javascript
// router/dynamic.js
import { postsApi } from '@/lib/supabase/posts'

/**
 * 動的ルートローダー
 */
export class DynamicRouteLoader {
  constructor(router) {
    this.router = router
    this.cache = new Map()
  }

  /**
   * 投稿スラッグからルートを解決
   * @param {string} slug - 投稿スラッグ
   * @returns {Promise<Object|null>}
   */
  async resolvePostRoute(slug) {
    // キャッシュから確認
    if (this.cache.has(slug)) {
      const cached = this.cache.get(slug)
      if (Date.now() - cached.timestamp < 5 * 60 * 1000) { // 5分キャッシュ
        return cached.data
      }
    }

    try {
      const response = await postsApi.getBySlug(slug)
      
      if (response.success && response.data) {
        const routeData = {
          name: 'PostDetail',
          params: { slug },
          meta: {
            title: response.data.title,
            description: response.data.excerpt,
            ogImage: response.data.featured_image,
            post: response.data
          }
        }

        // キャッシュに保存
        this.cache.set(slug, {
          data: routeData,
          timestamp: Date.now()
        })

        return routeData
      }
    } catch (error) {
      console.error('動的ルート解決エラー:', error)
    }

    return null
  }

  /**
   * カテゴリスラッグからルートを解決
   * @param {string} categorySlug - カテゴリスラッグ
   * @returns {Promise<Object|null>}
   */
  async resolveCategoryRoute(categorySlug) {
    // 実装は投稿と同様
  }

  /**
   * キャッシュをクリア
   */
  clearCache() {
    this.cache.clear()
  }
}
```

### 3.2 プリフェッチング
```javascript
// composables/useRoutePrefetch.js
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export function useRoutePrefetch() {
  const router = useRouter()
  const prefetchedRoutes = ref(new Set())

  /**
   * ルートをプリフェッチ
   * @param {string} routeName - ルート名
   * @param {Object} params - パラメータ
   */
  const prefetchRoute = async (routeName, params = {}) => {
    const routeKey = `${routeName}:${JSON.stringify(params)}`
    
    if (prefetchedRoutes.value.has(routeKey)) {
      return
    }

    try {
      const route = router.resolve({ name: routeName, params })
      
      // コンポーネントを事前読み込み
      if (route.matched.length > 0) {
        const component = route.matched[route.matched.length - 1].components?.default
        if (typeof component === 'function') {
          await component()
          prefetchedRoutes.value.add(routeKey)
        }
      }
    } catch (error) {
      console.error('プリフェッチエラー:', error)
    }
  }

  /**
   * リンクホバー時のプリフェッチ
   */
  const setupHoverPrefetch = () => {
    const handleMouseEnter = (event) => {
      const link = event.target.closest('a[href]')
      if (link) {
        const href = link.getAttribute('href')
        const route = router.resolve(href)
        if (route.name) {
          prefetchRoute(route.name, route.params)
        }
      }
    }

    document.addEventListener('mouseenter', handleMouseEnter, true)

    return () => {
      document.removeEventListener('mouseenter', handleMouseEnter, true)
    }
  }

  let cleanup = null

  onMounted(() => {
    cleanup = setupHoverPrefetch()
  })

  onUnmounted(() => {
    if (cleanup) cleanup()
  })

  return {
    prefetchRoute,
    prefetchedRoutes: prefetchedRoutes.value
  }
}
```

## 4. SEO最適化

### 4.1 メタタグ管理
```javascript
// composables/useMeta.js
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

export function useMeta() {
  const route = useRoute()
  const metaTags = ref([])

  /**
   * メタタグを設定
   * @param {Object} meta - メタタグ情報
   */
  const setMeta = (meta) => {
    // タイトル設定
    if (meta.title) {
      document.title = `${meta.title} | MyApp`
    }

    // 既存の動的メタタグを削除
    const existingMeta = document.querySelectorAll('meta[data-vue-meta]')
    existingMeta.forEach(tag => tag.remove())

    // 新しいメタタグを追加
    const metaMap = {
      description: { name: 'description' },
      keywords: { name: 'keywords' },
      author: { name: 'author' },
      'og:title': { property: 'og:title' },
      'og:description': { property: 'og:description' },
      'og:image': { property: 'og:image' },
      'og:url': { property: 'og:url' },
      'og:type': { property: 'og:type' },
      'twitter:card': { name: 'twitter:card' },
      'twitter:title': { name: 'twitter:title' },
      'twitter:description': { name: 'twitter:description' },
      'twitter:image': { name: 'twitter:image' }
    }

    const createdTags = []

    Object.entries(meta).forEach(([key, value]) => {
      if (metaMap[key] && value) {
        const tag = document.createElement('meta')
        const attr = metaMap[key]
        
        if (attr.name) tag.setAttribute('name', attr.name)
        if (attr.property) tag.setAttribute('property', attr.property)
        
        tag.setAttribute('content', value)
        tag.setAttribute('data-vue-meta', 'true')
        
        document.head.appendChild(tag)
        createdTags.push(tag)
      }
    })

    metaTags.value = createdTags
  }

  /**
   * 投稿詳細のメタタグを設定
   * @param {Object} post - 投稿データ
   */
  const setPostMeta = (post) => {
    const currentUrl = window.location.href

    setMeta({
      title: post.title,
      description: post.excerpt || post.title,
      keywords: post.tags?.join(', '),
      author: post.author?.name,
      'og:title': post.title,
      'og:description': post.excerpt || post.title,
      'og:image': post.featured_image || '/og-default.jpg',
      'og:url': currentUrl,
      'og:type': 'article',
      'twitter:card': 'summary_large_image',
      'twitter:title': post.title,
      'twitter:description': post.excerpt || post.title,
      'twitter:image': post.featured_image || '/og-default.jpg'
    })
  }

  /**
   * 構造化データを設定
   * @param {Object} data - 構造化データ
   */
  const setStructuredData = (data) => {
    // 既存の構造化データを削除
    const existingScript = document.querySelector('script[type="application/ld+json"][data-vue-meta]')
    if (existingScript) {
      existingScript.remove()
    }

    // 新しい構造化データを追加
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.setAttribute('data-vue-meta', 'true')
    script.textContent = JSON.stringify(data)
    document.head.appendChild(script)
  }

  /**
   * 投稿の構造化データを設定
   * @param {Object} post - 投稿データ
   */
  const setPostStructuredData = (post) => {
    const structuredData = {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: post.title,
      description: post.excerpt,
      image: post.featured_image,
      datePublished: post.published_at,
      dateModified: post.updated_at,
      author: {
        '@type': 'Person',
        name: post.author?.name || '不明'
      },
      publisher: {
        '@type': 'Organization',
        name: 'MyApp',
        logo: {
          '@type': 'ImageObject',
          url: '/logo.png'
        }
      }
    }

    setStructuredData(structuredData)
  }

  // クリーンアップ
  onUnmounted(() => {
    metaTags.value.forEach(tag => {
      if (tag.parentNode) {
        tag.parentNode.removeChild(tag)
      }
    })
  })

  return {
    setMeta,
    setPostMeta,
    setStructuredData,
    setPostStructuredData
  }
}
```

## 5. ルート遷移アニメーション

### 5.1 ページ遷移アニメーション
```vue
<!-- App.vue -->
<template>
  <div id="app">
    <router-view v-slot="{ Component, route }">
      <transition
        :name="getTransitionName(route)"
        mode="out-in"
        @enter="onEnter"
        @leave="onLeave"
      >
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

/**
 * ルートに応じた遷移名を取得
 * @param {Object} route - ルートオブジェクト
 * @returns {string}
 */
const getTransitionName = (route) => {
  // ルートレベルに基づいた遷移
  const level = route.path.split('/').length - 1
  
  if (route.meta.transition) {
    return route.meta.transition
  }
  
  if (level <= 1) {
    return 'page-slide'
  } else {
    return 'page-fade'
  }
}

/**
 * 遷移開始時の処理
 */
const onEnter = (el) => {
  // ローディング状態の終了
  document.body.classList.remove('page-loading')
}

/**
 * 遷移終了時の処理
 */
const onLeave = (el) => {
  // ローディング状態の開始
  document.body.classList.add('page-loading')
}
</script>

<style>
/* ページスライド遷移 */
.page-slide-enter-active,
.page-slide-leave-active {
  transition: all 0.3s ease;
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* ページフェード遷移 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* ローディング状態 */
.page-loading {
  cursor: wait;
}
</style>
```

## 6. エラーハンドリング

### 6.1 ルートエラー処理
```javascript
// router/errorHandler.js
import { useNotificationStore } from '@/stores/notification'

export function setupRouterErrorHandler(router) {
  router.onError((error, to, from) => {
    const notificationStore = useNotificationStore()
    
    console.error('Router Error:', error)
    
    if (error.name === 'ChunkLoadError') {
      // チャンクロードエラー（アプリ更新時など）
      notificationStore.showError(
        'アプリケーションが更新されました。ページをリロードしてください。',
        {
          action: {
            text: 'リロード',
            handler: () => window.location.reload()
          }
        }
      )
    } else if (error.message.includes('Loading chunk')) {
      // 動的インポートエラー
      notificationStore.showError('ページの読み込みに失敗しました')
      router.push('/404')
    } else {
      // その他のエラー
      notificationStore.showError('ページの読み込み中にエラーが発生しました')
    }
  })
}
```

## 7. パフォーマンス最適化

### 7.1 ルート遅延読み込み
```javascript
// router/lazy.js

/**
 * コンポーネントを遅延読み込み（エラーハンドリング付き）
 * @param {Function} importFn - インポート関数
 * @param {string} fallbackRoute - フォールバックルート
 * @returns {Function}
 */
export function lazyLoadComponent(importFn, fallbackRoute = '/404') {
  return () => 
    importFn()
      .catch(error => {
        console.error('コンポーネント読み込みエラー:', error)
        return import('@/views/errors/ComponentLoadError.vue')
      })
}

/**
 * ルート定義での使用例
 */
export const routes = [
  {
    path: '/dashboard',
    component: lazyLoadComponent(
      () => import('@/views/DashboardView.vue'),
      '/404'
    )
  }
]
```

### 7.2 ルートベースのコード分割
```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 認証関連
          if (id.includes('/views/auth/')) {
            return 'auth'
          }
          
          // ダッシュボード関連
          if (id.includes('/views/dashboard/')) {
            return 'dashboard'
          }
          
          // 投稿関連
          if (id.includes('/views/posts/')) {
            return 'posts'
          }
          
          // ベンダー
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        }
      }
    }
  }
})
```

## 8. まとめ

このVue Router設計の特徴：

1. **セキュリティ**: 認証・権限ベースのガード
2. **SEO対応**: メタタグと構造化データの動的設定
3. **UX最適化**: スムーズな遷移アニメーション
4. **パフォーマンス**: 遅延読み込みとコード分割
5. **エラーハンドリング**: 堅牢なエラー処理

### 関連ドキュメント
- [アーキテクチャ設計](./01_architecture_design.md)
- [認証システム](../03_library_docs/03_supabase_integration.md)
- [状態管理設計](./05_state_management_design.md)