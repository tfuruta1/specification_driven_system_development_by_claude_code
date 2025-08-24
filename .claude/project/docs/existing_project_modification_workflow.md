# [NOTE]  - TDD

## [TARGET] 

### 
**REPORT**

1. **REPORT** - REPORT
2. **REPORT** - REPORT
3. **TDDREPORT** - ERROR

## [REPORT] ERROR

```mermaid
graph TD
    A[ERROR] --> B{ERROR}
    B -->|[ERROR] NO| C[ERROR]
    C --> D[ERROR]
    D --> E[ERROR]
    E --> F[ERROR]
    F --> G[TDD: Red - ]
    G --> H[TDD: Green - ]
    H --> I[TDD: Refactor - ]
    I --> J[]
    
    style B fill:#ff9999
    style C fill:#99ff99
    style D fill:#99ff99
    style E fill:#99ff99
```

## [SEARCH] Phase 1: 

### /modify-request 

#### 1. 
```markdown
## 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
```

#### 2. 
```markdown
## 
|  |  |  |  |
|------|----------|----------|--------------|
|  | [] | [] | High/Med/Low |
| API | [] | [] | High/Med/Low |
|  | [] | [] | High/Med/Low |
| UI/UX | [] | [] | High/Med/Low |
```

#### 3. 
```markdown
## 
### 
- 
- 
- 
- 

### 
- 
- 
- 
- 
```

## [INFO] Phase 2: 

### /modify-requirements - 

#### 
```markdown
# 

## 1. AS-IS
### 
[]

### 
[]

## 2. TO-BE
### 
[]

### 
[]

## 3. 
### 
- [ ] 1
- [ ] 2

### 
- [ ] 1
- [ ] 2

## 4. 
### 
- : []
- : []

### 
- []

## 5. 
- [ ] 1
- [ ] 2

## 6. 
- 
- 
- 
```

### /modify-design - 

#### 
```markdown
# 

## 1. 
### 
[/]

### 
[/]

### 
[]

## 2. 
### API
|  |  |  |  |
|---------------|--------|--------|--------|
| /api/xxx | [] | [] | Yes/No |

### 
| / |  |  |  |
|-------------------|--------|--------|-----------------|
| users.xxx | [] | [] | [] |

## 3. 
### 
[]

### 
[]

### 
[]

## 4. 
### 
- : []
- : [%]

### 
- : []

### E2E
- : []

## 5. 
|  |  |  |  |
|--------|--------|----------|------|
| [1] | High | Medium | [] |

## 6. 
- 
- 
- 
```

##  Phase 3: TDD

### /tdd-start - 

#### Red-Green-Refactor
```markdown
## TDD

###  Red Phase - 
1. 
2. 
3. 

###  Green Phase - 
1. 
2. 
3. 

###  Refactor Phase - 
1. 
2. 
3. 
4. 

### TEST
- TEST
- TEST
- TEST
```

#### TEST
```python
# Step 1: Red - TEST
def test_calculate_discount():
    assert calculate_discount(100, "GOLD") == 80  # 20%TEST
    assert calculate_discount(100, "SILVER") == 90  # 10%
    assert calculate_discount(100, "BRONZE") == 95  # 5%

# Step 2: Green - 
def calculate_discount(price, member_type):
    if member_type == "GOLD":
        return 80
    elif member_type == "SILVER":
        return 90
    elif member_type == "BRONZE":
        return 95
    return price

# Step 3: Refactor - 
DISCOUNT_RATES = {
    "GOLD": 0.2,
    "SILVER": 0.1,
    "BRONZE": 0.05
}

def calculate_discount(price, member_type):
    discount_rate = DISCOUNT_RATES.get(member_type, 0)
    return price * (1 - discount_rate)
```

##  

### 
|  |  |  |  |
|------|---------|--------|--------|
|  |  | -60% | 60% |
|  |  | -70% | 70% |
|  | 40-50% | 80-90% | 40% |
|  | 60% | 95% | 35% |

### 
|  |  |  | ROI |
|---------|----------|----------|-----|
|  | +30% | - | - |
|  | -20% | 20% | - |
|  | -40% | 40% | - |
| WARNING | -60% | 60%ERROR | - |
| **ERROR** | **-15%** | **15%ERROR** | **150%** |

## [WARNING] ERROR

### [ERROR] ERROR
1. **ERROR**
   - ERROR
   - ERROR

2. **ERROR**
   - ERROR
   - ERROR

3. ****
   - 
   - 

### [OK] 
1. ****
   - 15-20%

2. ****
   - 
   - 

3. ****
   - 
   - 

## [START] 

### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

### TDD
- [ ] Red: 
- [ ] Green: 
- [ ] Refactor: 
- [ ] 
- [ ] 

### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

---

**