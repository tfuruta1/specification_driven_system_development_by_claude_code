# /frontend-optimize - 

## 
Vue3ReactTASKAngularTASKREST APITASKSupabaseTASK

## TASK
```bash
/frontend-optimize [framework] [connection] [options]

# TASK
/frontend-optimize vue3 rest-api --performance
/frontend-optimize vue3 supabase --realtime
/frontend-optimize vue3 hybrid --offline-first
/frontend-optimize react api --bundle-size
```

## TASK

### TASK
- `framework`: TASKvue3, react, angularTASK
- `connection`: TASKrest-api, supabase, hybrid, graphqlTASK

### 
- `--performance`: 
- `--bundle-size`: 
- `--realtime`: 
- `--offline-first`: 
- `--seo`: SEO
- `--lazy-loading`: 

## CONFIG

### 1. REST APICONFIGAxiosCONFIG
```javascript
// CONFIG Axios CONFIG
const apiConfig = {
  // CONFIG
  request: {
    timeout: 5000,
    retry: 3,
    cache: true,
    compression: true
  },
  
  // ERROR
  response: {
    interceptors: true,
    errorHandling: 'centralized',
    dataTransform: true
  },
  
  // ERROR
  auth: {
    tokenRefresh: 'automatic',
    headerInjection: true,
    sessionManagement: true
  }
}
```

### 2. Supabase
```javascript
// Supabase 
const supabaseOptimization = {
  // 
  connection: {
    poolSize: 10,
    keepAlive: true,
    compression: true
  },
  
  // 
  realtime: {
    channels: 'selective',
    debounce: 300,
    presence: true
  },
  
  // 
  storage: {
    cdn: true,
    caching: 'aggressive',
    lazyLoad: true
  }
}
```

### 3. 
```javascript
// 3
const hybridStrategy = {
  // 
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
  
  // ANALYSIS
  fallback: {
    automatic: true,
    healthCheck: 30000,
    syncOnReconnect: true
  }
}
```

## ANALYSIS

### Vue3ANALYSIS
```javascript
// Composition API
import { ref, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'

// CONFIG
export default {
  setup() {
    // ReactiveCONFIG
    const data = shallowRef(largeDataset)
    
    // CONFIG
    const filtered = computed(() => {
      return data.value.filter(/* ... */)
    }, { cache: true })
    
    // Watcher
    watchEffect(() => {
      // 
    }, { flush: 'post' })
    
    return { data, filtered }
  }
}
```

### 

#### 1. 
```javascript
// 
const AdminPanel = () => import('./components/AdminPanel.vue')
const Analytics = () => import('./components/Analytics.vue')
```

#### 2. 
```javascript
// 
import { VirtualList } from '@tanstack/vue-virtual'

// 10000
<VirtualList :items="largeDataset" :height="400" />
```

#### 3. 
```javascript
// 
const imageOptimization = {
  lazy: true,
  webp: true,
  responsive: true,
  placeholder: 'blur'
}
```

## CONFIG

### ViteCONFIG
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
    // 
    treeShaking: true,
    // 
    minify: 'terser',
    // gzip
    compression: true
  }
}
```

## SEOCONFIG

### CONFIG
```javascript
// Vue3 + Vite SSG
export const seoConfig = {
  meta: {
    defaultTitle: 'CONFIG',
    titleTemplate: '%s | CONFIG',
    description: 'REPORT'
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

## CONFIG

### Service WorkerCONFIG
```javascript
// PWACONFIG
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

## 

### 
```markdown
# 

## 
[OK] : 2.1MB -> 680KB (67%)
[OK] : 3.2 -> 1.1 (66%)
[OK] Lighthouse : 65 -> 95
[OK] : 15

## 
- First Contentful Paint: 1.2s
- Time to Interactive: 2.1s
- Cumulative Layout Shift: 0.02

## 
1. CDN
2. WebP
3. Critical CSS
```

## 
|  |  |  |
|--------|------|--------|
| CONFIG | CONFIG | npm install --force |
| CONFIG | TypeScriptCONFIG | tsconfig.jsonCONFIG |
| CORS CONFIG | APICONFIG | CONFIG |

## CONFIG
- **CONFIG**: CONFIG
- **CONFIG**: 

## 
- `/backend-sync` - 
- `/rest-api-optimize` - REST API
- `/supabase-optimize` - Supabase
- `/hybrid-optimize` - 

---
**