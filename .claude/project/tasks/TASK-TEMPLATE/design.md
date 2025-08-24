#  

##  

### 
```
[] <--> [] <--> []
     v                    v                      v
[Vue.js Components]  [Service Classes]    [Supabase Tables]
```

### 
- ****: []
- ****: []
- ****: []
- ****: []

### 
- []

##  

### 

#### 
```sql
-- [1]
CREATE TABLE [table_name] (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    [column1] [type] [constraints],
    [column2] [type] [constraints],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 
```sql
-- []
ALTER TABLE [existing_table] 
ADD COLUMN [new_column] [type] [constraints];
```

### 
```typescript
// 
interface [DataType] {
  id: string;
  [property1]: [type];
  [property2]: [type];
  createdAt: Date;
  updatedAt: Date;
}
```

##  API

### 

#### 
```
GET    /api/[resource]         - []
POST   /api/[resource]         - []
PUT    /api/[resource]/:id     - []
DELETE /api/[resource]/:id     - []
```

#### 
```typescript
// POST /api/[resource] 
interface CreateRequest {
  [property1]: [type];
  [property2]: [type];
}

// SUCCESS
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}
```

## SUCCESS SUCCESS

### SUCCESS

#### ERROR
```
src/components/[device]/[FeatureName]/
SYSTEM [MainComponent].vue          # SYSTEM
SYSTEM [SubComponent1].vue          # SYSTEM1
SYSTEM [SubComponent2].vue          # 2
 index.js                     # 
```

#### CONFIG
```vue
<!-- [ComponentName].vue -->
<template>
  <!-- UICONFIG -->
</template>

<script setup>
// PropsCONFIG
interface Props {
  [prop1]: [type];
  [prop2]: [type];
}

// EmitsCONFIG
interface Emits {
  [event1]: [payload_type];
  [event2]: [payload_type];
}
</script>
```

### 

#### Pinia
```typescript
// stores/[storeName].js
export const use[StoreName]Store = defineStore('[storeName]', () => {
  // State
  const [state1] = ref([initial_value]);
  const [state2] = ref([initial_value]);
  
  // Getters
  const [getter1] = computed(() => [computation]);
  
  // Actions
  const [action1] = async ([params]) => {
    // [action implementation]
  };
  
  return {
    // States
    [state1],
    [state2],
    // Getters
    [getter1],
    // Actions
    [action1]
  };
});
```

### 
```javascript
// router
{
  path: '/[path]',
  name: '[routeName]',
  component: () => import('@/views/[device]/[ViewName].vue'),
  meta: {
    requiresAuth: [true/false],
    roles: ['[role1]', '[role2]'],
    device: '[tablet/desktop]'
  }
}
```

##  

### 
- ****: []
- ****: []
- ****: []

### WARNING
- **WARNING**: [WARNING]
- **WARNING**: [WARNING]
- **SQLWARNING**: [WARNING]

## [WARNING] WARNING

### WARNING
1. **WARNING**: [WARNING]
2. **WARNING**: [ERROR]
3. **ERROR**: [ERROR]
4. **ERROR**: [ERROR]

### ERROR
```typescript
interface ErrorMessage {
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  action?: {
    label: string;
    handler: () => void;
  };
}
```

##  

### 
- ****: []
- ****: []
- **E2E**: []

### 
#### 
1. [1]: []
2. [2]: []
3. [3]: []

#### 
1. [1]: []
2. [2]: []

##  

### 
- ****: []
- **API**: []
- ****: []

### 
- [1]
- [2]
- [3]

## [REFRESH] 

### Phase 1: [1]
1. [1]
2. [2]
3. [3]

### Phase 2: [2]
1. [1]
2. [2]
3. [3]

### Phase 3: [3]
1. [1]
2. [2]
3. [3]

## [NOTE] 

### 
1. **[1]**: [] -> []
2. **[2]**: [] -> []
3. **[3]**: [] -> []

### 
- ****: []
- ****: []
- ****: []

---
**CTO**