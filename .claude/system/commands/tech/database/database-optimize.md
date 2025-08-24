# /database-optimize - 

## 
SQLAlchemySQL ServerPostgreSQL

## 
```bash
/database-optimize [optimization_type] [options]

# ANALYSIS
/database-optimize performance --target=sqlalchemy
/database-optimize query --analyze-slow-queries
/database-optimize index --auto-create
/database-optimize migration --from=legacy --to=modern
```

## 

### 
- `optimization_type`: 
  - `performance` - 
  - `query` - 
  - `index` - 
  - `migration` - 
  - `schema` - 
  - `connection` - ANALYSIS

### ANALYSIS
- `--target`: ANALYSISsqlalchemy, sql-server, postgresql, mysqlREPORT
- `--analyze-slow-queries`: REPORT
- `--auto-create`: REPORT
- `--report`: REPORT
- `--dry-run`: CONFIG

## CONFIG

### 1. CONFIG
```python
# SQLAlchemyCONFIG
optimization_config = {
    "connection_pool": {
        "pool_size": 20,
        "max_overflow": 40,
        "pool_timeout": 30,
        "pool_recycle": 3600
    },
    "query_optimization": {
        "eager_loading": True,
        "batch_size": 1000,
        "query_cache": True
    }
}
```

### 2. 
```sql
-- 
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_composite ON products(category_id, status);
```

### 3. 
```python
# N+1
# Before
users = session.query(User).all()
for user in users:
    print(user.orders)  # N+1

# After
users = session.query(User).options(
    selectinload(User.orders)
).all()
```

### 4. 
- /
- 
- 
- 

## 

|  |  |  |
|------------|--------------|---------|
| PostgreSQL |  | DB |
| SQL Server |  |  |
| MySQL | ANALYSIS | ANALYSIS |
| SQLite | ANALYSIS | ANALYSIS |

## ANALYSIS

### 1. ANALYSIS
```yaml
analysis:
  - slow_query_logANALYSIS
  - ANALYSIS
  - ANALYSIS
  - ANALYSIS
```

### 2. ANALYSIS
```yaml
planning:
  - 
  - 
  - 
  - 
```

### 3. 
```yaml
execution:
  - REPORT
  - REPORT
  - REPORT
  - REPORT
```

### 4. REPORT
```yaml
reporting:
  - REPORT
  - REPORT
  - REPORT
  - REPORT
```

## REPORT

### REPORT
```markdown
# 

## 
- : 5
- : 12
- : 

## 
- : 250ms -> 80ms68%
- : 45 -> 393%
- DB CPU: 75% -> 35%53%

## 
1. VACUUM
2. 
3. 
```

## 

### 
|  |  |  |
|--------|------|--------|
|  | DB |  |
|  |  | DBA |
|  |  | ANALYSIS |

## ANALYSIS
- **ANALYSIS**: ANALYSIS
- **ANALYSIS**: TESTDBTEST

## TEST
- `/analyze` - TEST
- `/db-migration` - TEST
- `/performance-test` - TEST

---
*TEST*