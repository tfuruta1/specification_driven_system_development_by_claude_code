# Tailwind CSS設定ガイド

## 概要

Vue.js + DaisyUI プロジェクト向けのTailwind CSS包括的設定ガイドです。カスタムテーマ、レスポンシブデザインパターン、最適化戦略について説明します。

## 目次

1. [基本設定](#基本設定)
2. [テーマカスタマイズ](#テーマカスタマイズ)
3. [カスタムユーティリティ](#カスタムユーティリティ)
4. [レスポンシブデザインパターン](#レスポンシブデザインパターン)
5. [パフォーマンス最適化](#パフォーマンス最適化)
6. [DaisyUI統合](#daisyui統合)
7. [ダークモード設定](#ダークモード設定)
8. [本番環境最適化](#本番環境最適化)

## 基本設定

### tailwind.config.js

```javascript
import typography from '@tailwindcss/typography'
import forms from '@tailwindcss/forms'
import aspectRatio from '@tailwindcss/aspect-ratio'
import daisyui from 'daisyui'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./node_modules/daisyui/dist/**/*.js"
  ],
  
  darkMode: ['class', '[data-theme="dark"]'],
  
  theme: {
    extend: {
      // カスタムスペーシングスケール
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      
      // カスタムフォントファミリー（日本語最適化）
      fontFamily: {
        'sans': [
          // 日本語フォント優先
          'Noto Sans JP',
          'Hiragino Kaku Gothic ProN', 
          'Hiragino Sans', 
          'Meiryo',
          // 英語フォントフォールバック
          'Inter', 
          'system-ui', 
          '-apple-system', 
          'BlinkMacSystemFont',
          'sans-serif'
        ],
        'display': [
          'Poppins', 
          'Noto Sans JP',
          'system-ui', 
          'sans-serif'
        ],
        'mono': [
          'JetBrains Mono', 
          'Fira Code',
          'Consolas',
          'Monaco',
          'monospace'
        ],
        // 日本語専用フォント
        'japanese': [
          'Noto Sans JP',
          'Hiragino Kaku Gothic ProN',
          'Hiragino Sans',
          'Yu Gothic UI',
          'Meiryo UI',
          'Meiryo',
          'MS PGothic',
          'sans-serif'
        ],
        // 英語専用フォント
        'english': [
          'Inter',
          'Roboto',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'sans-serif'
        ]
      },
      
      // 行間を含むカスタムフォントサイズ
      fontSize: {
        'xxs': ['0.625rem', { lineHeight: '0.75rem' }],
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
        '7xl': ['4.5rem', { lineHeight: '1' }],
        '8xl': ['6rem', { lineHeight: '1' }],
        '9xl': ['8rem', { lineHeight: '1' }],
      },
      
      // カスタムカラー（DaisyUIを補完）
      colors: {
        'brand': {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        'surface': {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        }
      },
      
      // カスタムアニメーション
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'fade-out': 'fadeOut 0.5s ease-in-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-up': 'slideInUp 0.3s ease-out',
        'slide-in-down': 'slideInDown 0.3s ease-out',
        'bounce-in': 'bounceIn 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'wiggle': 'wiggle 1s ease-in-out infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        slideInDown: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        bounceIn: {
          '0%': {
            transform: 'scale(0.3)',
            opacity: '0',
          },
          '50%': {
            transform: 'scale(1.05)',
          },
          '70%': {
            transform: 'scale(0.9)',
          },
          '100%': {
            transform: 'scale(1)',
            opacity: '1',
          },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        }
      },
      
      // カスタムブレークポイント
      screens: {
        'xs': '475px',
        '3xl': '1920px',
        '4xl': '2560px',
      },
      
      // カスタムz-indexスケール
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
      
      // カスタムbackdrop-blur
      backdropBlur: {
        xs: '2px',
      },
      
      // コンテナ設定
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '2rem',
          lg: '4rem',
          xl: '5rem',
          '2xl': '6rem',
        },
      },
    },
  },
  
  plugins: [
    typography({
      className: 'prose',
    }),
    forms({
      strategy: 'class',
    }),
    aspectRatio,
    daisyui,
    // カスタムユーティリティプラグイン
    function({ addUtilities, addComponents, addVariant, theme }) {
      // 日本語テキスト最適化ユーティリティ
      addUtilities({
        '.text-balance': {
          'text-wrap': 'balance',
        },
        // 日本語フォント最適化
        '.text-jp': {
          'font-family': theme('fontFamily.japanese'),
          'font-feature-settings': '"palt" 1',
          'letter-spacing': '0.05em',
          'line-break': 'strict',
          'word-break': 'break-all',
          'overflow-wrap': 'break-word'
        },
        // 英語フォント最適化
        '.text-en': {
          'font-family': theme('fontFamily.english'),
          'font-feature-settings': '"liga" 1, "kern" 1',
          'letter-spacing': '0.025em'
        },
        // コードテキスト
        '.text-code': {
          'font-variant-ligatures': 'none',
          'font-feature-settings': '"liga" 0, "calt" 0',
          'letter-spacing': '0'
        },
        // スクロールバー非表示
        '.scrollbar-hide': {
          /* Chrome、Safari、Opera用スクロールバー非表示 */
          '&::-webkit-scrollbar': {
            display: 'none',
          },
          /* IE、Edge、Firefox用スクロールバー非表示 */
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
        },
        // カスタムスクロールバー
        '.scrollbar-thin': {
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: theme('colors.gray.100'),
          },
          '&::-webkit-scrollbar-thumb': {
            background: theme('colors.gray.400'),
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: theme('colors.gray.500'),
          },
          '[data-theme="dark"] &::-webkit-scrollbar-track': {
            background: theme('colors.gray.800'),
          },
          '[data-theme="dark"] &::-webkit-scrollbar-thumb': {
            background: theme('colors.gray.600'),
          },
          '[data-theme="dark"] &::-webkit-scrollbar-thumb:hover': {
            background: theme('colors.gray.500'),
          },
        },
        // フォーカス管理
        '.focus-ring': {
          'outline': '2px solid transparent',
          'outline-offset': '2px',
          '&:focus': {
            'outline': `2px solid ${theme('colors.primary.500')}`,
            'outline-offset': '2px'
          }
        },
        '.focus-ring-inset': {
          '&:focus': {
            'outline': `2px solid ${theme('colors.primary.500')}`,
            'outline-offset': '-2px'
          }
        }
      })
      
      // カスタムコンポーネント
      addComponents({
        '.btn-gradient': {
          backgroundImage: `linear-gradient(to right, ${theme('colors.brand.500')}, ${theme('colors.brand.600')})`,
          color: 'white',
          transition: 'all 0.3s ease',
          border: 'none',
          '&:hover': {
            backgroundImage: `linear-gradient(to right, ${theme('colors.brand.600')}, ${theme('colors.brand.700')})`,
            transform: 'translateY(-1px)',
            boxShadow: theme('boxShadow.lg')
          },
          '&:active': {
            transform: 'translateY(0)',
            boxShadow: theme('boxShadow.md')
          }
        },
        '.card-elevated': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.lg'),
          boxShadow: theme('boxShadow.xl'),
          padding: theme('spacing.6'),
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: theme('boxShadow.2xl'),
            transform: 'translateY(-2px)'
          },
          '[data-theme="dark"] &': {
            backgroundColor: theme('colors.gray.800'),
            borderColor: theme('colors.gray.700')
          },
        },
        '.glass-effect': {
          backgroundColor: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)', // Safari対応
          border: '1px solid rgba(255, 255, 255, 0.3)',
          '[data-theme="dark"] &': {
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          },
        },
        // レスポンシブコンテナ
        '.container-fluid': {
          width: '100%',
          marginLeft: 'auto',
          marginRight: 'auto',
          paddingLeft: theme('spacing.4'),
          paddingRight: theme('spacing.4'),
          maxWidth: 'min(100% - 2rem, 1536px)',
          '@media (min-width: 640px)': {
            paddingLeft: theme('spacing.6'),
            paddingRight: theme('spacing.6'),
          },
          '@media (min-width: 1024px)': {
            paddingLeft: theme('spacing.8'),
            paddingRight: theme('spacing.8'),
          }
        }
      })

      // カスタムバリアント（日本語対応）
      addVariant('jp', '&.lang-jp')
      addVariant('en', '&.lang-en')
      addVariant('rtl', '&:dir(rtl)')
      addVariant('reduced-motion', '@media (prefers-reduced-motion: reduce)')
    }
  ],
  
  // DaisyUI設定
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          primary: "#3b82f6",
          secondary: "#8b5cf6",
          accent: "#f59e0b",
          neutral: "#1e293b",
          "base-100": "#ffffff",
          info: "#3abff8",
          success: "#36d399",
          warning: "#fbbd23",
          error: "#f87272",
          
          // カスタムCSS変数
          "--rounded-box": "1rem",
          "--rounded-btn": "0.5rem",
          "--rounded-badge": "1.9rem",
          "--animation-btn": "0.25s",
          "--animation-input": "0.2s",
          "--btn-focus-scale": "0.95",
          "--border-btn": "1px",
          "--tab-border": "1px",
          "--tab-radius": "0.5rem",
        },
        dark: {
          ...require("daisyui/src/theming/themes")["dark"],
          primary: "#60a5fa",
          secondary: "#a78bfa",
          accent: "#fbbf24",
          neutral: "#e2e8f0",
          "base-100": "#0f172a",
          "base-200": "#1e293b",
          "base-300": "#334155",
          info: "#93c5fd",
          success: "#86efac",
          warning: "#fde68a",
          error: "#fca5a5",
          
          // カスタムCSS変数
          "--rounded-box": "1rem",
          "--rounded-btn": "0.5rem",
          "--rounded-badge": "1.9rem",
          "--animation-btn": "0.25s",
          "--animation-input": "0.2s",
          "--btn-focus-scale": "0.95",
          "--border-btn": "1px",
          "--tab-border": "1px",
          "--tab-radius": "0.5rem",
        },
      },
      "cupcake",
      "bumblebee",
      "emerald",
      "corporate",
      "synthwave",
      "retro",
      "cyberpunk",
      "valentine",
      "halloween",
      "garden",
      "forest",
      "aqua",
      "lofi",
      "pastel",
      "fantasy",
      "wireframe",
      "black",
      "luxury",
      "dracula",
    ],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
    prefix: "",
    logs: false,
    themeRoot: ":root",
  },
}
```

## テーマカスタマイズ

### カスタムテーマの作成

```javascript
// tailwind.config.js内 - カスタムテーマ例
daisyui: {
  themes: [
    {
      myapp: {
        "primary": "#0ea5e9",
        "primary-focus": "#0284c7",
        "primary-content": "#ffffff",
        
        "secondary": "#8b5cf6",
        "secondary-focus": "#7c3aed",
        "secondary-content": "#ffffff",
        
        "accent": "#f59e0b",
        "accent-focus": "#d97706",
        "accent-content": "#ffffff",
        
        "neutral": "#2a2e37",
        "neutral-focus": "#16181d",
        "neutral-content": "#ffffff",
        
        "base-100": "#ffffff",
        "base-200": "#f3f4f6",
        "base-300": "#e5e7eb",
        "base-content": "#1f2937",
        
        "info": "#3abff8",
        "success": "#36d399",
        "warning": "#fbbd23",
        "error": "#f87272",
        
        "--rounded-box": "1rem",
        "--rounded-btn": "0.5rem",
        "--rounded-badge": "1.9rem",
        "--animation-btn": "0.25s",
        "--animation-input": "0.2s",
        "--btn-text-case": "uppercase",
        "--btn-focus-scale": "0.95",
        "--border-btn": "1px",
        "--tab-border": "1px",
        "--tab-radius": "0.5rem",
      },
    },
  ],
}
```

### テーマ切り替えコンポーネント

```vue
<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="btn btn-ghost btn-circle">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
    </div>
    <ul tabindex="0" class="dropdown-content z-[1] p-2 shadow-2xl bg-base-200 rounded-box w-52">
      <li v-for="theme in themes" :key="theme">
        <button
          @click="setTheme(theme)"
          class="btn btn-ghost btn-sm btn-block justify-start"
          :class="{ 'btn-active': currentTheme === theme }"
        >
          {{ theme }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const themes = [
  'light', 'dark', 'cupcake', 'bumblebee', 'emerald', 
  'corporate', 'synthwave', 'retro', 'cyberpunk', 'valentine'
]

const currentTheme = ref('light')

const setTheme = (theme) => {
  currentTheme.value = theme
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'light'
  setTheme(savedTheme)
})
</script>
```

## カスタムユーティリティ

### グラデーションテキスト

```css
/* CSSまたはTailwindプラグインとして */
.gradient-text {
  @apply bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent;
}

.gradient-text-hover {
  @apply bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent 
         transition-all duration-300 hover:from-secondary hover:to-primary;
}
```

### カスタムシャドウ

```javascript
// tailwind.config.js内
theme: {
  extend: {
    boxShadow: {
      'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
      'hard': '0 2px 15px -3px rgba(0, 0, 0, 0.2), 0 10px 20px -2px rgba(0, 0, 0, 0.1)',
      'inner-lg': 'inset 0 2px 8px 0 rgba(0, 0, 0, 0.1)',
      'glow': '0 0 30px rgba(59, 130, 246, 0.5)',
      'glow-lg': '0 0 60px rgba(59, 130, 246, 0.5)',
    }
  }
}
```

### レスポンシブタイポグラフィスケール

```javascript
// カスタムレスポンシブフォントサイズプラグイン
function({ addComponents, theme }) {
  addComponents({
    '.text-responsive-xs': {
      fontSize: theme('fontSize.xs'),
      '@media (min-width: 640px)': {
        fontSize: theme('fontSize.sm'),
      },
    },
    '.text-responsive-sm': {
      fontSize: theme('fontSize.sm'),
      '@media (min-width: 640px)': {
        fontSize: theme('fontSize.base'),
      },
    },
    '.text-responsive-base': {
      fontSize: theme('fontSize.base'),
      '@media (min-width: 640px)': {
        fontSize: theme('fontSize.lg'),
      },
    },
    '.text-responsive-lg': {
      fontSize: theme('fontSize.lg'),
      '@media (min-width: 640px)': {
        fontSize: theme('fontSize.xl'),
      },
      '@media (min-width: 1024px)': {
        fontSize: theme('fontSize.2xl'),
      },
    },
    '.text-responsive-xl': {
      fontSize: theme('fontSize.xl'),
      '@media (min-width: 640px)': {
        fontSize: theme('fontSize.2xl'),
      },
      '@media (min-width: 1024px)': {
        fontSize: theme('fontSize.3xl'),
      },
    },
  })
}
```

## レスポンシブデザインパターン

### フルードコンテナ

```vue
<template>
  <div class="container-fluid">
    <!-- コンテンツ -->
  </div>
</template>

<style>
.container-fluid {
  @apply w-full px-4 mx-auto;
  @apply sm:px-6 lg:px-8;
  max-width: min(100% - 2rem, 1536px);
}
</style>
```

### レスポンシブグリッドシステム

```vue
<template>
  <!-- 自動フィットグリッド -->
  <div class="grid-auto-fit">
    <div v-for="item in items" :key="item.id" class="card">
      <!-- カードコンテンツ -->
    </div>
  </div>
  
  <!-- レスポンシブカラム -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    <div v-for="item in items" :key="item.id">
      <!-- アイテムコンテンツ -->
    </div>
  </div>
</template>

<style>
.grid-auto-fit {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
</style>
```

### レスポンシブスペーシングスケール

```vue
<template>
  <div class="p-4 sm:p-6 lg:p-8 xl:p-10">
    <h1 class="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl mb-4 sm:mb-6 lg:mb-8">
      レスポンシブ見出し
    </h1>
    <div class="space-y-4 sm:space-y-6 lg:space-y-8">
      <!-- レスポンシブスペーシングを持つコンテンツ -->
    </div>
  </div>
</template>
```

## パフォーマンス最適化

### PurgeCSS設定

```javascript
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    // その他のテンプレートパスを含める
    "./src/**/*.{html,md}",
    // 動的クラスのセーフリスト
    {
      raw: '<div class="text-red-500 bg-blue-500"></div>',
      extension: 'html'
    }
  ],
  safelist: [
    // 動的クラスのセーフリスト
    'bg-red-500',
    'text-3xl',
    'lg:text-4xl',
    // パターンマッチング
    {
      pattern: /bg-(red|green|blue)-(100|200|300|400|500|600|700|800|900)/,
      variants: ['lg', 'hover', 'focus'],
    },
    {
      pattern: /text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl)/,
      variants: ['lg', 'md'],
    },
  ],
}
```

### JITモード最適化

```javascript
// vite.config.js
export default {
  css: {
    postcss: {
      plugins: [
        tailwindcss,
        autoprefixer,
        // 本番環境最適化
        ...(process.env.NODE_ENV === 'production'
          ? [
              cssnano({
                preset: ['default', {
                  discardComments: {
                    removeAll: true,
                  },
                }],
              }),
            ]
          : []),
      ],
    },
  },
}
```

## DaisyUI統合

### コンポーネントバリアント

```vue
<template>
  <!-- Tailwindユーティリティを持つボタンバリアント -->
  <button class="btn btn-primary hover:scale-105 transition-transform">
    プライマリ
  </button>
  
  <!-- カスタムスタイルのDaisyUIコンポーネント -->
  <div class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
    <div class="card-body">
      <h2 class="card-title text-gradient">
        カードタイトル
      </h2>
      <p class="text-base-content/70">
        Tailwind不透明度修飾子を使ったカードコンテンツ
      </p>
    </div>
  </div>
  
  <!-- カスタムバックドロップを持つモーダル -->
  <dialog class="modal" :class="{ 'modal-open': isOpen }">
    <div class="modal-box relative backdrop-blur-sm bg-base-100/95">
      <!-- モーダルコンテンツ -->
    </div>
    <form method="dialog" class="modal-backdrop bg-black/50">
      <button>閉じる</button>
    </form>
  </dialog>
</template>
```

### DaisyUIコンポーネント拡張

```css
/* カスタムDaisyUIコンポーネント拡張 */
.btn-gradient {
  @apply btn bg-gradient-to-r from-primary to-secondary text-primary-content;
  @apply hover:from-primary-focus hover:to-secondary-focus;
  @apply active:scale-95;
}

.card-hover {
  @apply card transition-all duration-300;
  @apply hover:shadow-2xl hover:-translate-y-1;
}

.input-bordered-primary {
  @apply input input-bordered;
  @apply focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20;
}
```

## ダークモード設定

### 自動ダークモード

```vue
<script setup>
import { onMounted, watch } from 'vue'
import { useDark, useToggle } from '@vueuse/core'

const isDark = useDark({
  selector: 'html',
  attribute: 'data-theme',
  valueDark: 'dark',
  valueLight: 'light',
})

const toggleDark = useToggle(isDark)

// システム設定と同期
onMounted(() => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  
  const handleChange = (e) => {
    if (!localStorage.getItem('theme')) {
      isDark.value = e.matches
    }
  }
  
  mediaQuery.addEventListener('change', handleChange)
  
  return () => mediaQuery.removeEventListener('change', handleChange)
})
</script>
```

### ダークモード専用ユーティリティ

```css
/* ダークモード専用ユーティリティ */
.dark-gradient {
  @apply bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900;
}

[data-theme="dark"] .dark-gradient {
  @apply bg-gradient-to-br from-gray-800 via-gray-700 to-gray-800;
}

.text-adaptive {
  @apply text-gray-900;
}

[data-theme="dark"] .text-adaptive {
  @apply text-gray-100;
}
```

## 本番環境最適化

### PostCSS設定

```javascript
// postcss.config.js
export default {
  plugins: {
    'tailwindcss/nesting': {},
    tailwindcss: {},
    autoprefixer: {},
    ...(process.env.NODE_ENV === 'production' ? {
      cssnano: {
        preset: ['default', {
          discardComments: {
            removeAll: true,
          },
          normalizeWhitespace: true,
          colormin: true,
          minifyFontValues: true,
        }]
      },
      '@fullhuman/postcss-purgecss': {
        content: [
          './src/**/*.vue',
          './src/**/*.js',
          './index.html',
        ],
        defaultExtractor: content => {
          const contentWithoutStyleBlocks = content.replace(/<style[^]+?<\/style>/gi, '')
          return contentWithoutStyleBlocks.match(/[A-Za-z0-9-_/:]*[A-Za-z0-9-_/]+/g) || []
        },
        safelist: [
          /-(leave|enter|appear)(|-(to|from|active))$/,
          /^(?!(|.*?:)cursor-move).+-move$/,
          /^router-link(|-exact)-active$/,
          /data-theme$/,
        ],
      }
    } : {})
  }
}
```

### ビルド最適化スクリプト

```json
// package.json
{
  "scripts": {
    "build": "vite build",
    "build:analyze": "vite build --mode analyze",
    "build:css": "tailwindcss -i ./src/assets/tailwind.css -o ./dist/output.css --minify",
    "optimize:css": "purgecss --css ./dist/**/*.css --content ./dist/**/*.html ./dist/**/*.js --output ./dist/assets/"
  }
}
```

## トラブルシューティング

### よくある問題

1. **本番環境でクラスが表示されない**
   - tailwind.config.jsのsafelistに追加
   - contentパスが正しいことを確認
   - 動的クラス生成をチェック

2. **テーマが切り替わらない**
   - data-theme属性が設定されているか確認
   - localStorage実装をチェック
   - DaisyUIテーマが設定されているか確認

3. **カスタムカラーが機能しない**
   - themeを置き換えるのではなく拡張する
   - 適切なカラー形式を使用（hex、rgb、hsl）
   - CSS変数の競合をチェック

4. **パフォーマンスの問題**
   - JITモードを有効化
   - 適切なパージを実装
   - 大きなリストにはCSS containmentを使用

### デバッグユーティリティ

```javascript
// Tailwindクラス用デバッグヘルパー
export function debugTailwind() {
  if (process.env.NODE_ENV === 'development') {
    console.log('アクティブテーマ:', document.documentElement.getAttribute('data-theme'))
    console.log('計算されたスタイル:', getComputedStyle(document.documentElement))
    console.log('CSS変数:', 
      Array.from(document.documentElement.style)
        .filter(prop => prop.startsWith('--'))
        .reduce((acc, prop) => {
          acc[prop] = document.documentElement.style.getPropertyValue(prop)
          return acc
        }, {})
    )
  }
}
```

## 📚 関連ドキュメント

このTailwind設定の活用方法については、以下のドキュメントを参照してください：

- **[🎨 デザインシステム概要](./00_design_overview.md)** - デザイントークンとブランドガイドライン
- **[🧩 DaisyUIコンポーネント活用ガイド](./02_daisyui_components.md)** - コンポーネント実装パターン
- **[🔧 Vueコンポーネント設計パターン](./03_vue_component_patterns.md)** - 高度な実装パターン
- **[🎨 デザイントークンリファレンス](./04_design_tokens.md)** - トークンの詳細仕様

### 実装順序の推奨

1. **この設定ファイルの導入** → 基盤となるCSS設定を構築
2. **[デザインシステム](./00_design_overview.md)の確認** → ブランドガイドラインを理解
3. **[DaisyUIコンポーネント](./02_daisyui_components.md)の実装** → 基本UIコンポーネントを作成
4. **[Vueパターン](./03_vue_component_patterns.md)の適用** → 高度な機能とパターンを実装

## 🎯 実用例

### 日本語最適化されたコンポーネント

```vue
<template>
  <div class="card-elevated">
    <!-- 日本語テキスト最適化 -->
    <h1 class="text-jp text-2xl font-bold mb-4">
      ユーザー管理システム
    </h1>
    
    <!-- 英語テキスト最適化 -->
    <p class="text-en text-sm text-gray-600 mb-6">
      User Management System v2.0
    </p>
    
    <!-- グラデーションボタン -->
    <button class="btn-gradient px-6 py-3 rounded-lg">
      新規ユーザー追加
    </button>
    
    <!-- ガラス効果カード -->
    <div class="glass-effect p-6 rounded-xl mt-6">
      <h3 class="text-jp text-lg font-medium">通知設定</h3>
      <p class="text-jp text-sm mt-2">
        システム通知の設定を変更できます。
      </p>
    </div>
  </div>
</template>
```

### レスポンシブグリッドシステム

```vue
<template>
  <div class="container-fluid">
    <!-- 自動調整グリッド -->
    <div class="grid-auto-fit gap-6 mb-8">
      <div v-for="item in items" :key="item.id" class="card-elevated">
        <h3 class="text-jp font-medium">{{ item.title }}</h3>
        <p class="text-jp text-sm text-gray-600">{{ item.description }}</p>
      </div>
    </div>
    
    <!-- レスポンシブカラム -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div v-for="stat in stats" :key="stat.id" class="stat-card">
        <div class="stat-value text-jp">{{ stat.value }}</div>
        <div class="stat-title text-jp">{{ stat.title }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid-auto-fit {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.stat-card {
  @apply card-elevated text-center;
}

.stat-value {
  @apply text-3xl font-bold text-primary mb-2;
}

.stat-title {
  @apply text-sm text-gray-600;
}
</style>
```

## ✅ 設定品質チェックリスト

### 基本設定
- [ ] **PurgeCSS**: 本番環境で不要なCSSが削除される
- [ ] **日本語フォント**: 適切なフォントファミリーが設定済み
- [ ] **ダークモード**: テーマ切り替えが正常に動作
- [ ] **レスポンシブ**: ブレークポイントが適切に設定

### パフォーマンス
- [ ] **JITモード**: 必要なスタイルのみ生成
- [ ] **最適化**: 本番ビルドでファイルサイズが最小化
- [ ] **フォント読み込み**: Webフォントが効率的に読み込まれる
- [ ] **キャッシュ**: CSS変更時に適切に更新

### 開発体験
- [ ] **IntelliSense**: エディタでクラス名補完が動作
- [ ] **ホットリロード**: 開発時の自動更新が正常
- [ ] **エラーハンドリング**: 設定エラーが分かりやすく表示
- [ ] **ドキュメント**: カスタム設定の使用方法が明確

### ブランド統一
- [ ] **カラーパレット**: ブランドカラーが正確に設定
- [ ] **タイポグラフィ**: フォントスケールが統一
- [ ] **スペーシング**: 一貫したスペーシングシステム
- [ ] **コンポーネント**: 再利用可能なスタイルパターン

## リソース

- [Tailwind CSS ドキュメント](https://tailwindcss.com/docs)
- [Tailwind UI コンポーネント](https://tailwindui.com)
- [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)
- [Heroicons](https://heroicons.com)
- [Tailwind CSS Forms](https://github.com/tailwindlabs/tailwindcss-forms)
- [Tailwind CSS Typography](https://github.com/tailwindlabs/tailwindcss-typography)