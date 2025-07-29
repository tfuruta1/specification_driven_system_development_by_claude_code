# DaisyUIコンポーネント活用ガイド

## 📚 関連ドキュメント

このガイドを最大限活用するために、以下のドキュメントと併せてご確認ください：

- **[🎨 デザインシステム概要](./00_design_overview.md)** - ブランドガイドラインとデザイントークン
- **[⚙️ Tailwind CSS設定ガイド](./01_tailwind_config.md)** - 基盤となるCSS設定とカスタマイズ
- **[🔧 Vueコンポーネント設計パターン](./03_vue_component_patterns.md)** - 高度な実装パターン
- **[🎨 デザイントークンリファレンス](./04_design_tokens.md)** - トークンの詳細仕様

## 概要

Supabase統合を含むVue.jsアプリケーション向けのDaisyUIコンポーネント活用パターン、カスタマイズ技法、ベストプラクティスの包括的ガイドです。

## 目次

1. [導入](#導入)
2. [フォームコンポーネント](#フォームコンポーネント)
3. [ナビゲーションコンポーネント](#ナビゲーションコンポーネント)
4. [データ表示](#データ表示)
5. [レイアウトコンポーネント](#レイアウトコンポーネント)
6. [フィードバックコンポーネント](#フィードバックコンポーネント)
7. [カスタムコンポーネント拡張](#カスタムコンポーネント拡張)
8. [Vue統合パターン](#vue統合パターン)
9. [アクセシビリティ強化](#アクセシビリティ強化)
10. [パフォーマンス最適化](#パフォーマンス最適化)

## 導入

### インストールとセットアップ

```bash
npm install daisyui
```

```javascript
// tailwind.config.js
import daisyui from 'daisyui'

export default {
  plugins: [daisyui],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
  },
}
```

### テーマ設定

```vue
<!-- App.vue -->
<template>
  <div class="min-h-screen" :data-theme="currentTheme">
    <ThemeController />
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ThemeController from '@/components/ThemeController.vue'

const currentTheme = ref('light')

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'light'
  currentTheme.value = savedTheme
  document.documentElement.setAttribute('data-theme', savedTheme)
})
</script>
```

## フォームコンポーネント

### 入力コンポーネント

```vue
<!-- InputField.vue -->
<template>
  <div class="form-control w-full max-w-xs">
    <label v-if="label" class="label">
      <span class="label-text">{{ label }}</span>
      <span v-if="required" class="label-text-alt text-error">*</span>
    </label>
    
    <input
      v-model="inputValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClasses"
      class="input input-bordered w-full max-w-xs"
      @blur="handleBlur"
      @focus="handleFocus"
    />
    
    <label v-if="error || helperText" class="label">
      <span v-if="error" class="label-text-alt text-error">{{ error }}</span>
      <span v-else-if="helperText" class="label-text-alt">{{ helperText }}</span>
    </label>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  placeholder: String,
  type: { type: String, default: 'text' },
  error: String,
  helperText: String,
  required: Boolean,
  disabled: Boolean,
  size: { type: String, default: 'md' },
  variant: { type: String, default: 'bordered' }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const isFocused = ref(false)

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const inputClasses = computed(() => {
  const classes = []
  
  // サイズバリアント
  if (props.size === 'xs') classes.push('input-xs')
  if (props.size === 'sm') classes.push('input-sm')
  if (props.size === 'lg') classes.push('input-lg')
  
  // バリアントスタイル
  if (props.variant === 'ghost') classes.push('input-ghost')
  if (props.variant === 'primary') classes.push('input-primary')
  if (props.variant === 'secondary') classes.push('input-secondary')
  if (props.variant === 'accent') classes.push('input-accent')
  
  // エラー状態
  if (props.error) classes.push('input-error')
  
  // フォーカス状態
  if (isFocused.value) classes.push('input-focus')
  
  return classes
})

const handleBlur = (event) => {
  isFocused.value = false
  emit('blur', event)
}

const handleFocus = (event) => {
  isFocused.value = true
  emit('focus', event)
}
</script>
```

### セレクトコンポーネント

```vue
<!-- SelectField.vue -->
<template>
  <div class="form-control w-full max-w-xs">
    <label v-if="label" class="label">
      <span class="label-text">{{ label }}</span>
      <span v-if="required" class="label-text-alt text-error">*</span>
    </label>
    
    <select
      v-model="selectedValue"
      :disabled="disabled"
      :class="selectClasses"
      class="select select-bordered w-full max-w-xs"
    >
      <option v-if="placeholder" disabled value="">{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    
    <label v-if="error || helperText" class="label">
      <span v-if="error" class="label-text-alt text-error">{{ error }}</span>
      <span v-else-if="helperText" class="label-text-alt">{{ helperText }}</span>
    </label>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  placeholder: String,
  options: { type: Array, required: true },
  error: String,
  helperText: String,
  required: Boolean,
  disabled: Boolean,
  size: { type: String, default: 'md' },
  variant: { type: String, default: 'bordered' }
})

const emit = defineEmits(['update:modelValue'])

const selectedValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const selectClasses = computed(() => {
  const classes = []
  
  if (props.size === 'xs') classes.push('select-xs')
  if (props.size === 'sm') classes.push('select-sm')
  if (props.size === 'lg') classes.push('select-lg')
  
  if (props.variant === 'ghost') classes.push('select-ghost')
  if (props.variant === 'primary') classes.push('select-primary')
  if (props.variant === 'secondary') classes.push('select-secondary')
  if (props.variant === 'accent') classes.push('select-accent')
  
  if (props.error) classes.push('select-error')
  
  return classes
})
</script>
```

### チェックボックスとラジオコンポーネント

```vue
<!-- CheckboxField.vue -->
<template>
  <div class="form-control">
    <label class="label cursor-pointer">
      <span class="label-text">{{ label }}</span>
      <input
        v-model="checkedValue"
        type="checkbox"
        :disabled="disabled"
        :class="checkboxClasses"
        class="checkbox"
      />
    </label>
    
    <div v-if="error" class="text-error text-sm mt-1">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  label: { type: String, required: true },
  error: String,
  disabled: Boolean,
  size: { type: String, default: 'md' },
  variant: { type: String, default: 'primary' }
})

const emit = defineEmits(['update:modelValue'])

const checkedValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const checkboxClasses = computed(() => {
  const classes = []
  
  if (props.size === 'xs') classes.push('checkbox-xs')
  if (props.size === 'sm') classes.push('checkbox-sm')
  if (props.size === 'lg') classes.push('checkbox-lg')
  
  if (props.variant === 'primary') classes.push('checkbox-primary')
  if (props.variant === 'secondary') classes.push('checkbox-secondary')
  if (props.variant === 'accent') classes.push('checkbox-accent')
  if (props.variant === 'success') classes.push('checkbox-success')
  if (props.variant === 'warning') classes.push('checkbox-warning')
  if (props.variant === 'error') classes.push('checkbox-error')
  
  return classes
})
</script>
```

### ファイルアップロードコンポーネント

```vue
<!-- FileUpload.vue -->
<template>
  <div class="form-control w-full max-w-xs">
    <label v-if="label" class="label">
      <span class="label-text">{{ label }}</span>
      <span v-if="required" class="label-text-alt text-error">*</span>
    </label>
    
    <div class="relative">
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled || uploading"
        class="file-input file-input-bordered w-full max-w-xs"
        :class="inputClasses"
        @change="handleFileChange"
      />
      
      <div v-if="uploading" class="absolute inset-0 flex items-center justify-center bg-base-100/80 rounded-lg">
        <span class="loading loading-spinner loading-sm"></span>
        <span class="ml-2 text-sm">アップロード中...</span>
      </div>
    </div>
    
    <!-- ファイルプレビュー -->
    <div v-if="files.length > 0" class="mt-2 space-y-2">
      <div
        v-for="(file, index) in files"
        :key="index"
        class="flex items-center justify-between p-2 bg-base-200 rounded-lg"
      >
        <div class="flex items-center space-x-2">
          <div class="avatar">
            <div class="w-8 h-8 rounded">
              <img v-if="file.preview" :src="file.preview" :alt="file.name" />
              <div v-else class="flex items-center justify-center bg-base-300">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
          <div>
            <div class="text-sm font-medium">{{ file.name }}</div>
            <div class="text-xs text-base-content/60">{{ formatFileSize(file.size) }}</div>
          </div>
        </div>
        
        <button
          type="button"
          class="btn btn-ghost btn-xs"
          @click="removeFile(index)"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    
    <label v-if="error || helperText" class="label">
      <span v-if="error" class="label-text-alt text-error">{{ error }}</span>
      <span v-else-if="helperText" class="label-text-alt">{{ helperText }}</span>
    </label>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSupabaseStorage } from '@/composables/useSupabaseStorage'

const props = defineProps({
  modelValue: Array,
  label: String,
  accept: String,
  multiple: Boolean,
  required: Boolean,
  disabled: Boolean,
  error: String,
  helperText: String,
  maxSize: { type: Number, default: 10 * 1024 * 1024 }, // 10MB
  bucket: { type: String, default: 'uploads' }
})

const emit = defineEmits(['update:modelValue', 'upload-complete', 'upload-error'])

const { uploadFile } = useSupabaseStorage()

const fileInput = ref(null)
const files = ref([])
const uploading = ref(false)

const inputClasses = computed(() => {
  const classes = []
  if (props.error) classes.push('file-input-error')
  if (uploading.value) classes.push('opacity-50')
  return classes
})

const handleFileChange = async (event) => {
  const selectedFiles = Array.from(event.target.files)
  
  // ファイル検証
  const validFiles = selectedFiles.filter(file => {
    if (file.size > props.maxSize) {
      emit('upload-error', `ファイル ${file.name} が大きすぎます`)
      return false
    }
    return true
  })
  
  // プレビュー付きファイルオブジェクトを作成
  const fileObjects = await Promise.all(
    validFiles.map(async (file) => {
      const preview = file.type.startsWith('image/') 
        ? URL.createObjectURL(file) 
        : null
      
      return {
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        preview
      }
    })
  )
  
  if (props.multiple) {
    files.value = [...files.value, ...fileObjects]
  } else {
    files.value = fileObjects
  }
  
  // 必要に応じて自動アップロード
  if (props.bucket) {
    await uploadFiles()
  }
  
  emit('update:modelValue', files.value)
}

const uploadFiles = async () => {
  uploading.value = true
  
  try {
    const uploadPromises = files.value
      .filter(f => !f.url)
      .map(async (fileObj) => {
        const result = await uploadFile(props.bucket, fileObj.file)
        fileObj.url = result.publicUrl
        return result
      })
    
    await Promise.all(uploadPromises)
    emit('upload-complete', files.value)
  } catch (error) {
    emit('upload-error', error.message)
  } finally {
    uploading.value = false
  }
}

const removeFile = (index) => {
  const file = files.value[index]
  if (file.preview) {
    URL.revokeObjectURL(file.preview)
  }
  files.value.splice(index, 1)
  emit('update:modelValue', files.value)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
```

## ナビゲーションコンポーネント

### ナビゲーションバーコンポーネント

```vue
<!-- Navbar.vue -->
<template>
  <div class="navbar bg-base-100 shadow-lg">
    <div class="navbar-start">
      <!-- モバイルメニューボタン -->
      <div class="dropdown lg:hidden">
        <div tabindex="0" role="button" class="btn btn-ghost">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        </div>
        <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
          <li v-for="item in menuItems" :key="item.path">
            <router-link :to="item.path" :class="{ active: isActive(item.path) }">
              {{ item.title }}
            </router-link>
          </li>
        </ul>
      </div>
      
      <!-- ロゴ -->
      <router-link to="/" class="btn btn-ghost text-xl">
        <img v-if="logo" :src="logo" :alt="appName" class="w-8 h-8" />
        {{ appName }}
      </router-link>
    </div>
    
    <!-- デスクトップメニュー -->
    <div class="navbar-center hidden lg:flex">
      <ul class="menu menu-horizontal px-1">
        <li v-for="item in menuItems" :key="item.path">
          <router-link :to="item.path" :class="{ active: isActive(item.path) }">
            {{ item.title }}
          </router-link>
        </li>
      </ul>
    </div>
    
    <div class="navbar-end">
      <!-- 検索 -->
      <div class="form-control mr-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="検索..."
          class="input input-bordered input-sm w-24 md:w-auto"
          @keyup.enter="handleSearch"
        />
      </div>
      
      <!-- テーマ切り替え -->
      <ThemeSwitcher class="mr-2" />
      
      <!-- ユーザーメニュー -->
      <div v-if="user" class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
          <div class="w-10 rounded-full">
            <img :src="user.avatar || '/default-avatar.png'" :alt="user.name" />
          </div>
        </div>
        <ul tabindex="0" class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52">
          <li><router-link to="/profile">プロフィール</router-link></li>
          <li><router-link to="/settings">設定</router-link></li>
          <li><a @click="handleLogout">ログアウト</a></li>
        </ul>
      </div>
      
      <!-- ログインボタン -->
      <router-link v-else to="/login" class="btn btn-primary">
        ログイン
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeSwitcher from './ThemeSwitcher.vue'

const props = defineProps({
  appName: { type: String, default: 'App' },
  logo: String,
  menuItems: { type: Array, default: () => [] }
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')

const user = computed(() => authStore.user)

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: 'search', query: { q: searchQuery.value } })
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>
```

### パンくずリストコンポーネント

```vue
<!-- Breadcrumbs.vue -->
<template>
  <div class="text-sm breadcrumbs">
    <ul>
      <li v-for="(item, index) in breadcrumbItems" :key="index">
        <router-link
          v-if="item.to && index < breadcrumbItems.length - 1"
          :to="item.to"
          class="link link-hover"
        >
          <component v-if="item.icon" :is="item.icon" class="w-4 h-4 mr-2" />
          {{ item.title }}
        </router-link>
        <span v-else class="flex items-center">
          <component v-if="item.icon" :is="item.icon" class="w-4 h-4 mr-2" />
          {{ item.title }}
        </span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  items: Array,
  showHome: { type: Boolean, default: true }
})

const route = useRoute()

const breadcrumbItems = computed(() => {
  if (props.items) {
    return props.showHome 
      ? [{ title: 'ホーム', to: '/' }, ...props.items]
      : props.items
  }
  
  // ルートから自動生成
  const segments = route.path.split('/').filter(Boolean)
  const items = []
  
  if (props.showHome) {
    items.push({ title: 'ホーム', to: '/' })
  }
  
  let path = ''
  segments.forEach((segment, index) => {
    path += `/${segment}`
    const title = segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' ')
    
    items.push({
      title,
      to: index === segments.length - 1 ? null : path
    })
  })
  
  return items
})
</script>
```

### サイドバーナビゲーション

```vue
<!-- Sidebar.vue -->
<template>
  <div class="drawer-side">
    <label for="drawer-toggle" class="drawer-overlay"></label>
    <aside class="w-64 min-h-full bg-base-200">
      <!-- ロゴ -->
      <div class="p-4 border-b border-base-300">
        <div class="flex items-center space-x-2">
          <img v-if="logo" :src="logo" :alt="appName" class="w-8 h-8" />
          <span class="text-lg font-semibold">{{ appName }}</span>
        </div>
      </div>
      
      <!-- ナビゲーションメニュー -->
      <ul class="menu p-4 space-y-2">
        <li v-for="section in menuSections" :key="section.title">
          <!-- セクションヘッダー -->
          <h3 v-if="section.title" class="menu-title text-base-content/60 text-xs uppercase tracking-wider font-semibold">
            {{ section.title }}
          </h3>
          
          <!-- メニューアイテム -->
          <template v-for="item in section.items" :key="item.path || item.title">
            <!-- 折りたたみメニュー -->
            <details v-if="item.children" :open="isParentActive(item)">
              <summary class="hover:bg-base-300 rounded-lg">
                <component v-if="item.icon" :is="item.icon" class="w-5 h-5" />
                {{ item.title }}
              </summary>
              <ul class="ml-4">
                <li v-for="child in item.children" :key="child.path">
                  <router-link
                    :to="child.path"
                    :class="{ active: isActive(child.path) }"
                    class="hover:bg-base-300 rounded-lg"
                  >
                    <component v-if="child.icon" :is="child.icon" class="w-4 h-4" />
                    {{ child.title }}
                  </router-link>
                </li>
              </ul>
            </details>
            
            <!-- 通常のメニューアイテム -->
            <li v-else>
              <router-link
                v-if="item.path"
                :to="item.path"
                :class="{ active: isActive(item.path) }"
                class="hover:bg-base-300 rounded-lg"
              >
                <component v-if="item.icon" :is="item.icon" class="w-5 h-5" />
                {{ item.title }}
                <span v-if="item.badge" class="badge badge-sm">{{ item.badge }}</span>
              </router-link>
              
              <button
                v-else
                @click="item.onClick"
                class="hover:bg-base-300 rounded-lg w-full text-left"
              >
                <component v-if="item.icon" :is="item.icon" class="w-5 h-5" />
                {{ item.title }}
                <span v-if="item.badge" class="badge badge-sm">{{ item.badge }}</span>
              </button>
            </li>
          </template>
        </li>
      </ul>
      
      <!-- 底部のユーザー情報 -->
      <div v-if="user" class="absolute bottom-0 left-0 right-0 p-4 border-t border-base-300">
        <div class="flex items-center space-x-3">
          <div class="avatar">
            <div class="w-10 h-10 rounded-full">
              <img :src="user.avatar || '/default-avatar.png'" :alt="user.name" />
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ user.name }}</p>
            <p class="text-xs text-base-content/60 truncate">{{ user.email }}</p>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  appName: { type: String, default: 'App' },
  logo: String,
  menuSections: { type: Array, required: true }
})

const route = useRoute()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const isParentActive = (item) => {
  return item.children?.some(child => isActive(child.path))
}
</script>
```

## データ表示

### テーブルコンポーネント

```vue
<!-- DataTable.vue -->
<template>
  <div class="w-full">
    <!-- テーブルコントロール -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
      <!-- 検索 -->
      <div class="form-control">
        <div class="input-group">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="検索..."
            class="input input-bordered input-sm"
          />
          <button class="btn btn-square btn-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- アクション -->
      <div class="flex gap-2">
        <button
          v-if="allowExport"
          @click="exportData"
          class="btn btn-outline btn-sm"
        >
          エクスポート
        </button>
        <button
          v-if="allowAdd"
          @click="$emit('add')"
          class="btn btn-primary btn-sm"
        >
          新規追加
        </button>
      </div>
    </div>
    
    <!-- テーブル -->
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <!-- テーブルヘッダー -->
        <thead>
          <tr>
            <th v-if="selectable" class="w-12">
              <label>
                <input
                  v-model="selectAll"
                  type="checkbox"
                  class="checkbox checkbox-sm"
                />
              </label>
            </th>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="column.headerClass"
              @click="handleSort(column)"
              class="cursor-pointer hover:bg-base-200"
            >
              <div class="flex items-center gap-2">
                {{ column.title }}
                <div v-if="column.sortable" class="flex flex-col">
                  <svg
                    class="w-3 h-3"
                    :class="{ 'text-primary': sortBy === column.key && sortOrder === 'asc' }"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
                  </svg>
                </div>
              </div>
            </th>
            <th v-if="actions.length > 0" class="w-24">アクション</th>
          </tr>
        </thead>
        
        <!-- テーブルボディ -->
        <tbody>
          <tr v-if="loading" class="animate-pulse">
            <td :colspan="totalColumns" class="text-center py-8">
              <span class="loading loading-spinner loading-md"></span>
              読み込み中...
            </td>
          </tr>
          
          <tr v-else-if="paginatedData.length === 0">
            <td :colspan="totalColumns" class="text-center py-8 text-base-content/60">
              {{ noDataMessage }}
            </td>
          </tr>
          
          <tr
            v-else
            v-for="(item, index) in paginatedData"
            :key="item.id || index"
            class="hover"
          >
            <td v-if="selectable">
              <label>
                <input
                  v-model="selectedItems"
                  :value="item.id"
                  type="checkbox"
                  class="checkbox checkbox-sm"
                />
              </label>
            </td>
            
            <td
              v-for="column in columns"
              :key="column.key"
              :class="column.cellClass"
            >
              <slot
                :name="`cell-${column.key}`"
                :item="item"
                :value="getNestedValue(item, column.key)"
                :column="column"
              >
                <component
                  v-if="column.component"
                  :is="column.component"
                  :value="getNestedValue(item, column.key)"
                  :item="item"
                />
                <span v-else>
                  {{ formatCellValue(item, column) }}
                </span>
              </slot>
            </td>
            
            <td v-if="actions.length > 0">
              <div class="flex gap-1">
                <button
                  v-for="action in actions"
                  :key="action.key"
                  @click="handleAction(action, item)"
                  :class="action.class || 'btn-ghost'"
                  class="btn btn-xs"
                  :title="action.title"
                >
                  <component v-if="action.icon" :is="action.icon" class="w-3 h-3" />
                  <span v-else>{{ action.label }}</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- ページネーション -->
    <div v-if="pagination && totalPages > 1" class="flex justify-center mt-4">
      <div class="btn-group">
        <button
          @click="currentPage = 1"
          :disabled="currentPage === 1"
          class="btn btn-sm"
        >
          最初
        </button>
        <button
          @click="currentPage--"
          :disabled="currentPage === 1"
          class="btn btn-sm"
        >
          «
        </button>
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="currentPage = page"
          :class="{ 'btn-active': page === currentPage }"
          class="btn btn-sm"
        >
          {{ page }}
        </button>
        <button
          @click="currentPage++"
          :disabled="currentPage === totalPages"
          class="btn btn-sm"
        >
          »
        </button>
        <button
          @click="currentPage = totalPages"
          :disabled="currentPage === totalPages"
          class="btn btn-sm"
        >
          最後
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  columns: { type: Array, required: true },
  actions: { type: Array, default: () => [] },
  loading: Boolean,
  selectable: Boolean,
  allowAdd: Boolean,
  allowExport: Boolean,
  pagination: { type: Boolean, default: true },
  pageSize: { type: Number, default: 10 },
  noDataMessage: { type: String, default: 'データがありません' }
})

const emit = defineEmits(['action', 'add', 'selection-change', 'export'])

const searchQuery = ref('')
const sortBy = ref('')
const sortOrder = ref('asc')
const currentPage = ref(1)
const selectedItems = ref([])

const totalColumns = computed(() => {
  let count = props.columns.length
  if (props.selectable) count++
  if (props.actions.length > 0) count++
  return count
})

const filteredData = computed(() => {
  let data = [...props.data]
  
  // 検索フィルター
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      props.columns.some(column => {
        const value = getNestedValue(item, column.key)
        return String(value).toLowerCase().includes(query)
      })
    )
  }
  
  // ソート
  if (sortBy.value) {
    data.sort((a, b) => {
      const aVal = getNestedValue(a, sortBy.value)
      const bVal = getNestedValue(b, sortBy.value)
      
      if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
      return 0
    })
  }
  
  return data
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / props.pageSize)
})

const paginatedData = computed(() => {
  if (!props.pagination) return filteredData.value
  
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return filteredData.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const selectAll = computed({
  get: () => {
    return selectedItems.value.length === paginatedData.value.length && paginatedData.value.length > 0
  },
  set: (value) => {
    if (value) {
      selectedItems.value = paginatedData.value.map(item => item.id)
    } else {
      selectedItems.value = []
    }
  }
})

const getNestedValue = (obj, path) => {
  return path.split('.').reduce((o, p) => o?.[p], obj)
}

const formatCellValue = (item, column) => {
  const value = getNestedValue(item, column.key)
  
  if (column.formatter) {
    return column.formatter(value, item)
  }
  
  if (column.type === 'date' && value) {
    return new Date(value).toLocaleDateString()
  }
  
  if (column.type === 'currency' && value) {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY'
    }).format(value)
  }
  
  return value
}

const handleSort = (column) => {
  if (!column.sortable) return
  
  if (sortBy.value === column.key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column.key
    sortOrder.value = 'asc'
  }
}

const handleAction = (action, item) => {
  emit('action', { action: action.key, item })
}

const exportData = () => {
  emit('export', filteredData.value)
}

watch(selectedItems, (newVal) => {
  emit('selection-change', newVal)
}, { deep: true })

watch(searchQuery, () => {
  currentPage.value = 1
})
</script>
```

### カードグリッドコンポーネント

```vue
<!-- CardGrid.vue -->
<template>
  <div class="w-full">
    <!-- グリッドコントロール -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <div class="flex items-center gap-4">
        <!-- 表示切り替え -->
        <div class="btn-group">
          <button
            @click="viewMode = 'grid'"
            :class="{ 'btn-active': viewMode === 'grid' }"
            class="btn btn-sm"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            @click="viewMode = 'list'"
            :class="{ 'btn-active': viewMode === 'list' }"
            class="btn btn-sm"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        
        <!-- フィルター -->
        <div class="dropdown">
          <div tabindex="0" role="button" class="btn btn-outline btn-sm">
            フィルター
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          <div tabindex="0" class="dropdown-content z-[1] card card-compact w-64 p-2 shadow bg-base-100">
            <div class="card-body">
              <h3 class="card-title text-sm">フィルターオプション</h3>
              <div class="form-control">
                <label class="label cursor-pointer">
                  <span class="label-text">お気に入りのみ表示</span>
                  <input v-model="filters.favorites" type="checkbox" class="checkbox checkbox-sm" />
                </label>
              </div>
              <!-- 必要に応じてフィルターを追加 -->
            </div>
          </div>
        </div>
      </div>
      
      <!-- 検索とソート -->
      <div class="flex items-center gap-2">
        <div class="form-control">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="検索..."
            class="input input-bordered input-sm w-48"
          />
        </div>
        
        <select v-model="sortBy" class="select select-bordered select-sm">
          <option value="">並び順</option>
          <option v-for="option in sortOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>
    
    <!-- ローディング状態 -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div
        v-for="n in 8"
        :key="n"
        class="card bg-base-100 shadow-xl animate-pulse"
      >
        <div class="h-48 bg-base-300 rounded-t-lg"></div>
        <div class="card-body">
          <div class="h-4 bg-base-300 rounded w-3/4 mb-2"></div>
          <div class="h-3 bg-base-300 rounded w-1/2"></div>
        </div>
      </div>
    </div>
    
    <!-- グリッド表示 -->
    <div
      v-else-if="viewMode === 'grid'"
      :class="gridClasses"
      class="grid gap-6"
    >
      <div
        v-for="item in paginatedItems"
        :key="item.id"
        class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer"
        @click="$emit('item-click', item)"
      >
        <slot name="card" :item="item">
          <!-- デフォルトカードコンテンツ -->
          <figure v-if="item.image" class="aspect-video">
            <img :src="item.image" :alt="item.title" class="w-full h-full object-cover" />
          </figure>
          
          <div class="card-body">
            <h2 class="card-title">
              {{ item.title }}
              <div v-if="item.isNew" class="badge badge-secondary">NEW</div>
            </h2>
            <p class="text-base-content/70">{{ item.description }}</p>
            
            <div class="card-actions justify-end">
              <button
                v-for="action in cardActions"
                :key="action.key"
                @click.stop="handleAction(action, item)"
                :class="action.class || 'btn-primary'"
                class="btn btn-sm"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
        </slot>
      </div>
    </div>
    
    <!-- リスト表示 -->
    <div v-else class="space-y-4">
      <div
        v-for="item in paginatedItems"
        :key="item.id"
        class="card card-side bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer"
        @click="$emit('item-click', item)"
      >
        <slot name="list-item" :item="item">
          <!-- デフォルトリストアイテムコンテンツ -->
          <figure v-if="item.image" class="w-24 h-24">
            <img :src="item.image" :alt="item.title" class="w-full h-full object-cover" />
          </figure>
          
          <div class="card-body flex-row justify-between">
            <div>
              <h2 class="card-title">{{ item.title }}</h2>
              <p class="text-base-content/70">{{ item.description }}</p>
            </div>
            
            <div class="card-actions">
              <button
                v-for="action in cardActions"
                :key="action.key"
                @click.stop="handleAction(action, item)"
                :class="action.class || 'btn-primary'"
                class="btn btn-sm"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
        </slot>
      </div>
    </div>
    
    <!-- 空の状態 -->
    <div v-if="!loading && filteredItems.length === 0" class="text-center py-12">
      <div class="text-6xl mb-4">📭</div>
      <h3 class="text-lg font-semibold mb-2">アイテムが見つかりません</h3>
      <p class="text-base-content/60">検索条件やフィルターを調整してみてください</p>
    </div>
    
    <!-- ページネーション -->
    <div v-if="pagination && totalPages > 1" class="flex justify-center mt-8">
      <div class="btn-group">
        <button
          @click="currentPage = 1"
          :disabled="currentPage === 1"
          class="btn"
        >
          «
        </button>
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="currentPage = page"
          :class="{ 'btn-active': page === currentPage }"
          class="btn"
        >
          {{ page }}
        </button>
        <button
          @click="currentPage = totalPages"
          :disabled="currentPage === totalPages"
          class="btn"
        >
          »
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: Boolean,
  cardActions: { type: Array, default: () => [] },
  sortOptions: { type: Array, default: () => [] },
  pagination: { type: Boolean, default: true },
  pageSize: { type: Number, default: 12 },
  gridCols: { type: String, default: '1 md:2 lg:3 xl:4' }
})

const emit = defineEmits(['item-click', 'action'])

const viewMode = ref('grid')
const searchQuery = ref('')
const sortBy = ref('')
const currentPage = ref(1)
const filters = ref({
  favorites: false
})

const gridClasses = computed(() => {
  return `grid-cols-${props.gridCols.replace(/:/g, ' grid-cols-')}`
})

const filteredItems = computed(() => {
  let items = [...props.items]
  
  // 検索フィルター
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    items = items.filter(item =>
      item.title?.toLowerCase().includes(query) ||
      item.description?.toLowerCase().includes(query)
    )
  }
  
  // その他のフィルター
  if (filters.value.favorites) {
    items = items.filter(item => item.isFavorite)
  }
  
  // ソート
  if (sortBy.value) {
    items.sort((a, b) => {
      const aVal = a[sortBy.value]
      const bVal = b[sortBy.value]
      
      if (aVal < bVal) return -1
      if (aVal > bVal) return 1
      return 0
    })
  }
  
  return items
})

const totalPages = computed(() => {
  return Math.ceil(filteredItems.value.length / props.pageSize)
})

const paginatedItems = computed(() => {
  if (!props.pagination) return filteredItems.value
  
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return filteredItems.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const handleAction = (action, item) => {
  emit('action', { action: action.key, item })
}
</script>
```

## レイアウトコンポーネント

### ヒーローセクション

```vue
<!-- HeroSection.vue -->
<template>
  <div class="hero min-h-screen" :class="heroClasses" :style="backgroundStyle">
    <div v-if="overlay" class="hero-overlay bg-opacity-60"></div>
    
    <div class="hero-content text-center">
      <div :class="contentClasses">
        <slot name="content">
          <h1 class="text-5xl font-bold" :class="titleClasses">
            {{ title }}
          </h1>
          
          <p v-if="subtitle" class="py-6" :class="subtitleClasses">
            {{ subtitle }}
          </p>
          
          <div v-if="$slots.actions || actions.length > 0" class="flex flex-wrap gap-4 justify-center">
            <slot name="actions">
              <button
                v-for="action in actions"
                :key="action.key"
                @click="handleAction(action)"
                :class="action.class || 'btn-primary'"
                class="btn"
              >
                {{ action.label }}
              </button>
            </slot>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  subtitle: String,
  backgroundImage: String,
  backgroundColor: String,
  gradient: String,
  overlay: { type: Boolean, default: true },
  variant: { type: String, default: 'default' },
  size: { type: String, default: 'full' },
  actions: { type: Array, default: () => [] }
})

const emit = defineEmits(['action'])

const backgroundStyle = computed(() => {
  const styles = {}
  
  if (props.backgroundImage) {
    styles.backgroundImage = `url(${props.backgroundImage})`
    styles.backgroundSize = 'cover'
    styles.backgroundPosition = 'center'
  } else if (props.gradient) {
    styles.background = props.gradient
  } else if (props.backgroundColor) {
    styles.backgroundColor = props.backgroundColor
  }
  
  return styles
})

const heroClasses = computed(() => {
  const classes = []
  
  if (props.size === 'small') classes.push('min-h-[50vh]')
  else if (props.size === 'medium') classes.push('min-h-[75vh]')
  else classes.push('min-h-screen')
  
  if (props.variant === 'centered') classes.push('text-center')
  
  return classes
})

const contentClasses = computed(() => {
  const classes = ['max-w-md']
  
  if (props.variant === 'wide') classes.push('max-w-4xl')
  
  return classes
})

const titleClasses = computed(() => {
  const classes = []
  
  if (props.backgroundImage || props.gradient) {
    classes.push('text-white')
  }
  
  return classes
})

const subtitleClasses = computed(() => {
  const classes = []
  
  if (props.backgroundImage || props.gradient) {
    classes.push('text-white/90')
  }
  
  return classes
})

const handleAction = (action) => {
  emit('action', action)
}
</script>
```

### 統計セクション

```vue
<!-- StatsSection.vue -->
<template>
  <div class="stats stats-vertical lg:stats-horizontal shadow w-full">
    <div
      v-for="stat in stats"
      :key="stat.id"
      class="stat"
      :class="stat.class"
    >
      <div v-if="stat.icon" class="stat-figure" :class="stat.iconColor">
        <component :is="stat.icon" class="w-8 h-8" />
      </div>
      
      <div class="stat-title" :class="stat.titleColor">
        {{ stat.title }}
      </div>
      
      <div class="stat-value" :class="stat.valueColor">
        <CountUp
          v-if="typeof stat.value === 'number'"
          :end-val="stat.value"
          :options="countUpOptions"
        />
        <span v-else>{{ stat.value }}</span>
      </div>
      
      <div v-if="stat.description" class="stat-desc" :class="stat.descColor">
        <span v-if="stat.trend" :class="getTrendClass(stat.trend)">
          <svg v-if="stat.trend > 0" class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
          <svg v-else-if="stat.trend < 0" class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          {{ Math.abs(stat.trend) }}%
        </span>
        {{ stat.description }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CountUp from 'vue-countup-v3'

const props = defineProps({
  stats: { type: Array, required: true },
  animated: { type: Boolean, default: true }
})

const countUpOptions = computed(() => ({
  useEasing: true,
  useGrouping: true,
  separator: ',',
  decimal: '.',
  duration: 2.5
}))

const getTrendClass = (trend) => {
  if (trend > 0) return 'text-success'
  if (trend < 0) return 'text-error'
  return 'text-warning'
}
</script>
```

## フィードバックコンポーネント

### アラートメッセージ

```vue
<!-- AlertMessage.vue -->
<template>
  <Transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="opacity-0 transform scale-90"
    enter-to-class="opacity-100 transform scale-100"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100 transform scale-100"
    leave-to-class="opacity-0 transform scale-90"
  >
    <div v-if="visible" :class="alertClasses" class="alert shadow-lg mb-4">
      <div class="flex-1 flex items-start">
        <component v-if="icon" :is="icon" class="w-6 h-6 mr-3 flex-shrink-0" />
        
        <div class="flex-1">
          <h4 v-if="title" class="font-semibold">{{ title }}</h4>
          <div class="text-sm">{{ message }}</div>
        </div>
      </div>
      
      <div v-if="dismissible" class="flex-shrink-0">
        <button @click="dismiss" class="btn btn-ghost btn-sm btn-circle">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  type: { type: String, default: 'info' },
  title: String,
  message: { type: String, required: true },
  dismissible: { type: Boolean, default: true },
  autoHide: { type: Boolean, default: false },
  duration: { type: Number, default: 5000 },
  icon: Object
})

const emit = defineEmits(['dismiss'])

const visible = ref(true)

const alertClasses = computed(() => {
  const classes = []
  
  switch (props.type) {
    case 'success':
      classes.push('alert-success')
      break
    case 'warning':
      classes.push('alert-warning')
      break
    case 'error':
      classes.push('alert-error')
      break
    default:
      classes.push('alert-info')
  }
  
  return classes
})

const dismiss = () => {
  visible.value = false
  emit('dismiss')
}

onMounted(() => {
  if (props.autoHide) {
    setTimeout(() => {
      dismiss()
    }, props.duration)
  }
})
</script>
```

### モーダルコンポーネント

```vue
<!-- ModalDialog.vue -->
<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <dialog
        v-if="modelValue"
        class="modal modal-open"
        @click="handleBackdropClick"
      >
        <Transition
          enter-active-class="transition ease-out duration-300"
          enter-from-class="opacity-0 transform scale-90"
          enter-to-class="opacity-100 transform scale-100"
          leave-active-class="transition ease-in duration-200"
          leave-from-class="opacity-100 transform scale-100"
          leave-to-class="opacity-0 transform scale-90"
        >
          <div v-if="modelValue" :class="modalBoxClasses" class="modal-box relative">
            <!-- 閉じるボタン -->
            <button
              v-if="closable"
              @click="close"
              class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"
            >
              ✕
            </button>
            
            <!-- ヘッダー -->
            <div v-if="$slots.header || title" class="modal-header mb-4">
              <slot name="header">
                <h3 class="font-bold text-lg">{{ title }}</h3>
              </slot>
            </div>
            
            <!-- コンテンツ -->
            <div class="modal-content">
              <slot />
            </div>
            
            <!-- フッター -->
            <div v-if="$slots.footer || actions.length > 0" class="modal-action">
              <slot name="footer">
                <button
                  v-for="action in actions"
                  :key="action.key"
                  @click="handleAction(action)"
                  :class="action.class || 'btn-primary'"
                  :disabled="action.disabled || loading"
                  class="btn"
                >
                  <span v-if="loading && action.key === 'confirm'" class="loading loading-spinner loading-sm mr-2"></span>
                  {{ action.label }}
                </button>
              </slot>
            </div>
          </div>
        </Transition>
      </dialog>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  title: String,
  size: { type: String, default: 'md' },
  closable: { type: Boolean, default: true },
  closeOnBackdrop: { type: Boolean, default: true },
  actions: { type: Array, default: () => [] },
  loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'action', 'close'])

const modalBoxClasses = computed(() => {
  const classes = []
  
  switch (props.size) {
    case 'xs':
      classes.push('max-w-xs')
      break
    case 'sm':
      classes.push('max-w-sm')
      break
    case 'lg':
      classes.push('max-w-2xl')
      break
    case 'xl':
      classes.push('max-w-4xl')
      break
    case 'full':
      classes.push('max-w-none w-11/12 h-5/6')
      break
    default:
      classes.push('max-w-lg')
  }
  
  return classes
})

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

const handleBackdropClick = (event) => {
  if (event.target === event.currentTarget && props.closeOnBackdrop) {
    close()
  }
}

const handleAction = (action) => {
  emit('action', action)
}

// Escキーで閉じる
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && props.closable) {
        close()
      }
    }
    
    document.addEventListener('keydown', handleEscape)
    
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }
})
</script>
```

### トースト通知

```vue
<!-- ToastContainer.vue -->
<template>
  <Teleport to="body">
    <div class="toast toast-top toast-end z-50">
      <TransitionGroup
        enter-active-class="transition ease-out duration-300"
        enter-from-class="opacity-0 transform translate-x-full"
        enter-to-class="opacity-100 transform translate-x-0"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100 transform translate-x-0"
        leave-to-class="opacity-0 transform translate-x-full"
        move-class="transition-transform duration-300"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="getToastClasses(toast)"
          class="alert shadow-lg max-w-sm"
        >
          <div class="flex-1 flex items-start">
            <component v-if="getToastIcon(toast)" :is="getToastIcon(toast)" class="w-6 h-6 mr-3 flex-shrink-0" />
            
            <div class="flex-1">
              <h4 v-if="toast.title" class="font-semibold">{{ toast.title }}</h4>
              <div class="text-sm">{{ toast.message }}</div>
            </div>
          </div>
          
          <button @click="removeToast(toast.id)" class="btn btn-ghost btn-sm btn-circle">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const toasts = computed(() => toastStore.toasts)

const getToastClasses = (toast) => {
  const classes = []
  
  switch (toast.type) {
    case 'success':
      classes.push('alert-success')
      break
    case 'warning':
      classes.push('alert-warning')
      break
    case 'error':
      classes.push('alert-error')
      break
    default:
      classes.push('alert-info')
  }
  
  return classes
}

const getToastIcon = (toast) => {
  // トーストタイプに基づいて適切なアイコンコンポーネントを返す
  // これはアイコンライブラリからインポートされる
  return null
}

const removeToast = (id) => {
  toastStore.removeToast(id)
}
</script>
```

## カスタムコンポーネント拡張

### ボタンバリアント

```css
/* カスタムボタン拡張 */
.btn-gradient {
  @apply bg-gradient-to-r from-primary to-secondary text-primary-content border-none;
  @apply hover:from-primary-focus hover:to-secondary-focus;
  @apply active:scale-95 transition-all duration-200;
}

.btn-glass {
  @apply bg-white/10 backdrop-blur-md border border-white/20 text-white;
  @apply hover:bg-white/20 hover:border-white/30;
}

.btn-loading {
  @apply relative overflow-hidden;
}

.btn-loading::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.btn-loading:hover::before {
  left: 100%;
}
```

### カード拡張

```css
/* 拡張カードスタイル */
.card-hover {
  @apply transition-all duration-300 cursor-pointer;
  @apply hover:shadow-2xl hover:-translate-y-2;
}

.card-glass {
  @apply bg-white/10 backdrop-blur-md border border-white/20;
}

.card-animated {
  @apply transition-all duration-500 ease-out;
}

.card-animated:hover {
  @apply scale-105 rotate-1;
}
```

## Vue統合パターン

### DaisyUIテーマ用コンポーザブル

```javascript
// composables/useDaisyTheme.js
import { ref, computed } from 'vue'

export function useDaisyTheme() {
  const currentTheme = ref('light')
  const availableThemes = ref([
    'light', 'dark', 'cupcake', 'bumblebee', 'emerald',
    'corporate', 'synthwave', 'retro', 'cyberpunk', 'valentine'
  ])

  const isDark = computed(() => {
    return ['dark', 'synthwave', 'halloween', 'forest', 'black', 'luxury', 'dracula'].includes(currentTheme.value)
  })

  const setTheme = (theme) => {
    currentTheme.value = theme
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }

  const toggleTheme = () => {
    const newTheme = currentTheme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    const theme = savedTheme || systemTheme
    setTheme(theme)
  }

  // システムテーマ変更の監視
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      setTheme(e.matches ? 'dark' : 'light')
    }
  })

  return {
    currentTheme,
    availableThemes,
    isDark,
    setTheme,
    toggleTheme,
    initTheme
  }
}
```

### フォームバリデーション用コンポーザブル

```javascript
// composables/useDaisyForm.js
import { ref, reactive, computed } from 'vue'

export function useDaisyForm(schema = {}) {
  const formData = reactive({})
  const errors = reactive({})
  const touched = reactive({})
  const isSubmitting = ref(false)

  const isValid = computed(() => {
    return Object.keys(errors).length === 0
  })

  const validateField = (field, value) => {
    const rules = schema[field]
    if (!rules) return

    delete errors[field]

    // 必須バリデーション
    if (rules.required && (!value || value.toString().trim() === '')) {
      errors[field] = rules.requiredMessage || `${field} は必須項目です`
      return
    }

    // 最小長バリデーション
    if (rules.minLength && value && value.length < rules.minLength) {
      errors[field] = rules.minLengthMessage || `${field} は ${rules.minLength} 文字以上で入力してください`
      return
    }

    // メールバリデーション
    if (rules.email && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(value)) {
        errors[field] = rules.emailMessage || '有効なメールアドレスを入力してください'
        return
      }
    }

    // カスタムバリデーション
    if (rules.validator && value) {
      const result = rules.validator(value, formData)
      if (result !== true) {
        errors[field] = result
        return
      }
    }
  }

  const validateForm = () => {
    Object.keys(schema).forEach(field => {
      validateField(field, formData[field])
      touched[field] = true
    })
    return isValid.value
  }

  const resetForm = () => {
    Object.keys(formData).forEach(key => {
      delete formData[key]
    })
    Object.keys(errors).forEach(key => {
      delete errors[key]
    })
    Object.keys(touched).forEach(key => {
      delete touched[key]
    })
    isSubmitting.value = false
  }

  const handleSubmit = async (submitFn) => {
    if (!validateForm()) return

    isSubmitting.value = true
    try {
      await submitFn(formData)
    } finally {
      isSubmitting.value = false
    }
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
    handleSubmit
  }
}
```

## アクセシビリティ強化

### ARIAラベルとロール

```vue
<!-- アクセシブルコンポーネント例 -->
<template>
  <div class="dropdown" @keydown="handleKeydown">
    <div
      tabindex="0"
      role="button"
      :aria-expanded="isOpen"
      :aria-haspopup="true"
      class="btn"
      @click="toggleDropdown"
    >
      {{ selectedOption?.label || placeholder }}
      <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>
    
    <ul
      v-if="isOpen"
      tabindex="0"
      role="listbox"
      :aria-labelledby="labelId"
      class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
    >
      <li
        v-for="(option, index) in options"
        :key="option.value"
        role="option"
        :aria-selected="selectedOption?.value === option.value"
        :class="{ 'bg-primary text-primary-content': focusedIndex === index }"
        @click="selectOption(option)"
        @mouseenter="focusedIndex = index"
      >
        <a>{{ option.label }}</a>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  options: { type: Array, required: true },
  modelValue: [String, Number, Object],
  placeholder: { type: String, default: 'オプションを選択' },
  labelId: String
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const focusedIndex = ref(-1)

const selectedOption = computed(() => {
  return props.options.find(option => option.value === props.modelValue)
})

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    focusedIndex.value = -1
  }
}

const selectOption = (option) => {
  emit('update:modelValue', option.value)
  isOpen.value = false
}

const handleKeydown = (event) => {
  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault()
      if (isOpen.value && focusedIndex.value >= 0) {
        selectOption(props.options[focusedIndex.value])
      } else {
        toggleDropdown()
      }
      break
    case 'Escape':
      isOpen.value = false
      break
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) {
        isOpen.value = true
      }
      focusedIndex.value = Math.min(focusedIndex.value + 1, props.options.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      focusedIndex.value = Math.max(focusedIndex.value - 1, 0)
      break
  }
}
</script>
```

## パフォーマンス最適化

### 遅延読み込みコンポーネント

```javascript
// DaisyUIコンポーネントの遅延読み込み
export const LazyDataTable = defineAsyncComponent(() => import('./DataTable.vue'))
export const LazyChart = defineAsyncComponent(() => import('./Chart.vue'))
export const LazyModal = defineAsyncComponent(() => import('./Modal.vue'))

// ローディングとエラー状態付き
export const LazyDataTable = defineAsyncComponent({
  loader: () => import('./DataTable.vue'),
  loadingComponent: () => h('div', { class: 'loading loading-spinner loading-lg' }),
  errorComponent: () => h('div', { class: 'alert alert-error' }, 'コンポーネントの読み込みに失敗しました'),
  delay: 200,
  timeout: 3000
})
```

### 大きなリスト用仮想スクロール

```vue
<!-- VirtualList.vue -->
<template>
  <div
    ref="containerRef"
    class="virtual-list-container overflow-auto"
### リソース効率化のベストプラクティス

```vue
<!-- PerformantCard.vue -->
<template>
  <div
    class="card bg-base-100 shadow-xl transition-all duration-200"
    :class="cardClasses"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- 画像の遅延読み込み -->
    <figure v-if="image" class="aspect-video">
      <LazyImage
        :src="image"
        :alt="title"
        :threshold="0.1"
        class="w-full h-full object-cover"
      />
    </figure>
    
    <div class="card-body">
      <!-- メモ化されたタイトル -->
      <h2 class="card-title">
        <MemoizedTitle :title="title" :highlight="searchQuery" />
        <div v-if="isNew" class="badge badge-secondary">NEW</div>
      </h2>
      
      <!-- 条件付きレンダリング -->
      <p v-if="description" class="text-base-content/70 line-clamp-3">
        {{ description }}
      </p>
      
      <!-- 遅延読み込みされるアクション -->
      <div v-if="showActions" class="card-actions justify-end">
        <Suspense>
          <template #default>
            <AsyncActionButtons
              :actions="actions"
              @action="handleAction"
            />
          </template>
          <template #fallback>
            <div class="flex gap-2">
              <div class="skeleton h-8 w-16"></div>
              <div class="skeleton h-8 w-16"></div>
            </div>
          </template>
        </Suspense>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, defineAsyncComponent } from 'vue'
import LazyImage from './LazyImage.vue'
import MemoizedTitle from './MemoizedTitle.vue'

// 遅延読み込みコンポーネント
const AsyncActionButtons = defineAsyncComponent(() =>
  import('./ActionButtons.vue')
)

const props = defineProps({
  title: { type: String, required: true },
  description: String,
  image: String,
  isNew: Boolean,
  actions: { type: Array, default: () => [] },
  searchQuery: String
})

const emit = defineEmits(['action', 'hover'])

const isHovered = ref(false)
const showActions = ref(false)

// メモ化された計算プロパティ
const cardClasses = computed(() => ({
  'hover:shadow-2xl hover:-translate-y-1': true,
  'scale-105': isHovered.value
}))

// パフォーマンス最適化されたイベントハンドラー
const handleMouseEnter = () => {
  isHovered.value = true
  // アクションボタンの遅延表示
  setTimeout(() => {
    showActions.value = true
  }, 150)
  emit('hover', { type: 'enter', item: props })
}

const handleMouseLeave = () => {
  isHovered.value = false
  emit('hover', { type: 'leave', item: props })
}

const handleAction = (action) => {
  emit('action', { action, item: props })
}
</script>
```

### メモ化コンポーネントの実装

```vue
<!-- MemoizedTitle.vue -->
<template>
  <span v-html="highlightedTitle"></span>
</template>

<script setup>
import { computed, memo } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  highlight: String
})

// 重い計算をメモ化
const highlightedTitle = computed(() => {
  if (!props.highlight) return props.title
  
  const regex = new RegExp(`(${props.highlight})`, 'gi')
  return props.title.replace(regex, '<mark class="bg-yellow-200">$1</mark>')
})
</script>

<script>
// コンポーネント全体をメモ化
export default memo(defineComponent({
  // ... コンポーネント定義
}))
</script>
```

### バンドル最適化設定

```javascript
// vite.config.js - パフォーマンス最適化
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue({
      // テンプレートコンパイル最適化
      template: {
        compilerOptions: {
          // 実行時ヘルパーの最適化
          hoistStatic: true,
          cacheHandlers: true,
        }
      }
    })
  ],
  
  build: {
    // チャンク分割戦略
    rollupOptions: {
      output: {
        manualChunks: {
          // ベンダーライブラリを分離
          vendor: ['vue', 'vue-router'],
          
          // DaisyUIコンポーネントを分離
          daisyui: ['daisyui'],
          
          // Supabaseライブラリを分離
          supabase: ['@supabase/supabase-js'],
          
          // 大きなライブラリを分離
          charts: ['chart.js', 'vue-chartjs'],
          
          // アイコンライブラリを分離
          icons: ['@heroicons/vue']
        }
      }
    },
    
    // 最適化設定
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    
    // ソースマップ設定
    sourcemap: process.env.NODE_ENV === 'development'
  },
  
  // 最適化オプション
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      '@supabase/supabase-js',
      'daisyui'
    ],
    exclude: [
      // 大きなライブラリは動的インポート
      'chart.js',
      '@heroicons/vue/24/solid'
    ]
  }
})
```

## ✅ パフォーマンスチェックリスト

### ランタイムパフォーマンス
- [ ] **仮想スクロール**: 1000+アイテムのリストで使用
- [ ] **遅延読み込み**: 画像とコンポーネントで実装
- [ ] **メモ化**: 重い計算とコンポーネントで適用
- [ ] **条件付きレンダリング**: 不要な要素を非表示

### バンドルサイズ
- [ ] **コード分割**: ルートレベルでチャンク分離
- [ ] **ツリーシェイキング**: 未使用コードを削除
- [ ] **動的インポート**: 大きなライブラリで適用
- [ ] **圧縮**: 本番ビルドで有効化

### メモリ使用量
- [ ] **イベントリスナー**: 適切にクリーンアップ
- [ ] **ウォッチャー**: 不要な監視を削除
- [ ] **参照**: 循環参照を避ける
- [ ] **キャッシュ**: 適切なサイズ制限

### ユーザー体験
- [ ] **ローディング**: 適切なスケルトン表示
- [ ] **エラーハンドリング**: ユーザーフレンドリーなメッセージ
- [ ] **レスポンシブ**: スムーズなアニメーション
- [ ] **アクセシビリティ**: パフォーマンス設定考慮

### メモ化とコンポーネント最適化

```vue
<!-- OptimizedDataTable.vue -->
<template>
  <div class="w-full">
    <!-- 検索とフィルター -->
    <div class="flex justify-between mb-4">
      <SearchInput
        v-model="searchQuery"
        @search="handleSearch"
        :debounce="300"
      />
      <FilterDropdown
        v-model="activeFilters"
        :options="filterOptions"
        @change="handleFilterChange"
      />
    </div>
    
    <!-- テーブル本体 -->
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <TableHeader
          :columns="columns"
          :sort-by="sortBy"
          :sort-order="sortOrder"
          @sort="handleSort"
        />
        <TableBody
          :items="paginatedItems"
          :columns="columns"
          @row-click="handleRowClick"
        />
      </table>
    </div>
    
    <!-- ページネーション -->
    <Pagination
      v-if="totalPages > 1"
      v-model="currentPage"
      :total-pages="totalPages"
      :visible-pages="5"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch, shallowRef } from 'vue'
import { debounce } from 'lodash-es'
import SearchInput from './components/SearchInput.vue'
import FilterDropdown from './components/FilterDropdown.vue'
import TableHeader from './components/TableHeader.vue'
import TableBody from './components/TableBody.vue'
import Pagination from './components/Pagination.vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  columns: { type: Array, required: true },
  pageSize: { type: Number, default: 20 },
  searchFields: { type: Array, default: () => [] },
  filterOptions: { type: Array, default: () => [] }
})

const emit = defineEmits(['row-click', 'selection-change'])

// リアクティブ状態
const searchQuery = ref('')
const activeFilters = ref({})
const sortBy = ref('')
const sortOrder = ref('asc')
const currentPage = ref(1)

// メモ化された計算プロパティ
const filteredItems = computed(() => {
  let items = props.data
  
  // 検索フィルター
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    items = items.filter(item => 
      props.searchFields.some(field => 
        String(item[field] || '').toLowerCase().includes(query)
      )
    )
  }
  
  // アクティブフィルター
  Object.entries(activeFilters.value).forEach(([key, value]) => {
    if (value) {
      items = items.filter(item => item[key] === value)
    }
  })
  
  return items
})

const sortedItems = computed(() => {
  if (!sortBy.value) return filteredItems.value
  
  return [...filteredItems.value].sort((a, b) => {
    const aVal = a[sortBy.value]
    const bVal = b[sortBy.value]
    
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})

const totalPages = computed(() => {
  return Math.ceil(sortedItems.value.length / props.pageSize)
})

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  return sortedItems.value.slice(start, start + props.pageSize)
})

// イベントハンドラー（デバウンス付き）
const handleSearch = debounce((query) => {
  searchQuery.value = query
  currentPage.value = 1
}, 300)

const handleFilterChange = (filters) => {
  activeFilters.value = filters
  currentPage.value = 1
}

const handleSort = (column) => {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'asc'
  }
  currentPage.value = 1
}

const handleRowClick = (item) => {
  emit('row-click', item)
}

// フィルター変更時のページリセット
watch([searchQuery, activeFilters], () => {
  currentPage.value = 1
}, { deep: true })
</script>
```

### Intersection Observer による遅延ローディング

```vue
<!-- LazyImage.vue -->
<template>
  <div
    ref="imageContainer"
    class="relative overflow-hidden bg-base-200"
    :class="containerClasses"
  >
    <Transition
      enter-active-class="transition-opacity duration-500"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
    >
      <img
        v-if="shouldLoad && imageLoaded"
        :src="src"
        :alt="alt"
        :class="imageClasses"
        class="w-full h-full object-cover"
        @load="handleImageLoad"
        @error="handleImageError"
      />
    </Transition>
    
    <!-- ローディングスケルトン -->
    <div
      v-if="!imageLoaded && shouldLoad"
      class="absolute inset-0 flex items-center justify-center"
    >
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    
    <!-- エラー状態 -->
    <div
      v-if="imageError"
      class="absolute inset-0 flex items-center justify-center bg-base-300"
    >
      <div class="text-center">
        <Icon name="photo" class="w-8 h-8 text-base-content/40 mx-auto mb-2" />
        <p class="text-xs text-base-content/60">画像を読み込めませんでした</p>
      </div>
    </div>
    
    <!-- プレースホルダー -->
    <div
      v-if="!shouldLoad"
      class="absolute inset-0 bg-gradient-to-br from-base-200 to-base-300"
    >
      <div class="absolute inset-0 animate-pulse bg-base-100/20"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps({
  src: { type: String, required: true },
  alt: { type: String, default: '' },
  aspectRatio: { type: String, default: '16/9' },
  threshold: { type: Number, default: 0.1 },
  rootMargin: { type: String, default: '50px' },
  eager: { type: Boolean, default: false }
})

const imageContainer = ref(null)
const shouldLoad = ref(props.eager)
const imageLoaded = ref(false)
const imageError = ref(false)

const containerClasses = computed(() => {
  const aspectRatioMap = {
    '1/1': 'aspect-square',
    '4/3': 'aspect-4/3',
    '16/9': 'aspect-video',
    '3/2': 'aspect-3/2'
  }
  
  return aspectRatioMap[props.aspectRatio] || 'aspect-video'
})

const imageClasses = computed(() => {
  return imageLoaded.value ? 'opacity-100' : 'opacity-0'
})

let observer = null

const handleImageLoad = () => {
  imageLoaded.value = true
  imageError.value = false
}

const handleImageError = () => {
  imageError.value = true
  imageLoaded.value = false
}

onMounted(() => {
  if (!props.eager && 'IntersectionObserver' in window) {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            shouldLoad.value = true
            observer?.disconnect()
          }
        })
      },
      {
        threshold: props.threshold,
        rootMargin: props.rootMargin
      }
    )
    
    if (imageContainer.value) {
      observer.observe(imageContainer.value)
    }
  } else {
    shouldLoad.value = true
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>
```
    :style="{ height: containerHeight + 'px' }"
    @scroll="handleScroll"
  >
    <div :style="{ height: totalHeight + 'px', position: 'relative' }">
      <div
        v-for="item in visibleItems"
        :key="item.index"
        :style="{ 
          position: 'absolute',
          top: item.top + 'px',
          left: 0,
          right: 0,
          height: itemHeight + 'px'
        }"
        class="virtual-list-item"
      >
        <slot :item="item.data" :index="item.index" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  itemHeight: { type: Number, default: 50 },
  containerHeight: { type: Number, default: 300 },
  overscan: { type: Number, default: 5 }
})

const containerRef = ref(null)
const scrollTop = ref(0)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleRange = computed(() => {
  const start = Math.floor(scrollTop.value / props.itemHeight)
  const end = Math.min(
    start + Math.ceil(props.containerHeight / props.itemHeight),
    props.items.length - 1
  )
  
  return {
    start: Math.max(0, start - props.overscan),
    end: Math.min(props.items.length - 1, end + props.overscan)
  }
})

const visibleItems = computed(() => {
  const items = []
  for (let i = visibleRange.value.start; i <= visibleRange.value.end; i++) {
    items.push({
      index: i,
      data: props.items[i],
      top: i * props.itemHeight
    })
  }
  return items
})

const handleScroll = (event) => {
  scrollTop.value = event.target.scrollTop
}

let resizeObserver

onMounted(() => {
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      // コンテナリサイズを処理
    })
    resizeObserver.observe(containerRef.value)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>
```

## 関連ドキュメント

- **[🎨 デザインシステム概要](./00_design_overview.md)** - デザイントークンとブランドガイドライン
- **[⚙️ Tailwind CSS設定](./01_tailwind_config.md)** - 基盤となるCSS設定
- **[🔧 Vueコンポーネントパターン](./03_vue_component_patterns.md)** - 高度な実装パターン
- **[🎨 デザイントークンリファレンス](./04_design_tokens.md)** - トークンの詳細仕様
- **[🔐 認証パターン](../01_authentication/03_vue_auth_patterns.md)** - 認証機能の実装
- **[📊 Supabase統合](../03_library_docs/02_supabase_integration.md)** - データベース連携

## リソース

- [DaisyUI ドキュメント](https://daisyui.com)
- [DaisyUI コンポーネント](https://daisyui.com/components/)
- [DaisyUI テーマ](https://daisyui.com/docs/themes/)
- [Vue アクセシビリティガイド](https://vue-a11y.com)
- [ARIA 作成実践](https://www.w3.org/WAI/ARIA/apg/)
- [ウェブコンテンツアクセシビリティガイドライン](https://www.w3.org/WAI/WCAG21/quickref/)