#  SDD

## [TARGET] 
KIROSDD

## [REFRESH] 

### 
1. **REPORTSingle Source of TruthREPORT**
2. **REPORT**
3. **REPORT**
4. **REPORT**

## [REPORT] REPORT

### REPORT
```mermaid
graph TD
    A[REPORT] --> B[/analyze REPORT]
    B --> C[REPORT]
    C --> D[ANALYSIS]
    C --> E[ANALYSIS]
    D --> F[.claude/specs/existing/]
    E --> F
    F --> G[ANALYSIS]
```

### 2ANALYSIS
```mermaid
graph TD
    A[ANALYSIS] --> B[/analyze ANALYSIS]
    B --> C{ANALYSIS}
    C -->|Yes| D[ANALYSIS]
    C -->|No| E[ANALYSIS]
    D --> F[]
    F --> G{}
    G -->|Yes| H[]
    G -->|No| I[]
    H --> J[]
    I --> K[]
    J --> K
```

##  

```
.claude/
 specs/
    existing/              # 
       [project-name]/
          requirements/  # 
             current.md     # 
      ANALYSIS   ANALYSIS   ANALYSIS history/       # ANALYSIS
ANALYSIS   ANALYSIS   ANALYSIS   ANALYSIS   ANALYSIS checksums.json # ANALYSIS
ANALYSIS   ANALYSIS   ANALYSIS   ANALYSIS design/        # ANALYSIS
ANALYSIS   ANALYSIS          current.md     # 
             architecture/  # 
      ANALYSIS   ANALYSIS   ANALYSIS history/       # ANALYSIS
ANALYSIS   ANALYSIS   ANALYSIS   ANALYSIS   ANALYSIS checksums.json # ANALYSIS
ANALYSIS   ANALYSIS   ANALYSIS   CONFIG metadata.json  # CONFIG
CONFIG   CONFIG new/                   # CONFIG
```

## [CONFIG] CONFIG

### /analyze - CONFIG
```bash
# CONFIG
/analyze [project-path] --generate-docs

# ANALYSIS
/analyze [project-path] --use-cache

# ANALYSIS
/analyze [project-path] --force-refresh

# ANALYSIS
/analyze [project-path] --diff-only
```

### /sync-docs - ANALYSIS
```bash
# ANALYSIS
/sync-docs [project-path]

# 
/sync-docs --auto --interval=on-change

# 
/sync-docs --status
```

### /validate-docs - 
```bash
# 
/validate-docs [project-path]

# 
/validate-docs --auto-fix
```

## [NOTE] 

### 
```markdown
#  - []

## 
- : [timestamp]
- : [timestamp]
- : [hash]
- : [version]

## 
[]

## 
### 
1. []: []
2. ...

## 
### 
[]

### 
[]

## API
[]

## 
[/]

## 
[/]
```

### 
```markdown
#  - []

## 
- : [timestamp]
- : [timestamp]
- : [hash]
- : [version]

## 
[/]

## 
### 
[]

### 
[]

## 
### 
[]

### 
[API]

## 
[]

## 
- : [version]
- : [version]
- : []

## 
- : []
- : [%]
- : []
```

## [REFRESH] SYSTEM

### SYSTEM
```json
{
  "project": "project-name",
  "files": {
    "src/main.js": {
      "hash": "sha256:abc123...",
      "lastModified": "2024-01-15T10:00:00Z",
      "analyzed": true
    }
  },
  "lastSync": "2024-01-15T10:30:00Z"
}
```

### ANALYSIS
1. ANALYSIS
2. ANALYSIS
3. 
4. 

##  AI

### Gemini-CLI
- 
- 
- 

### o3 MCP
- 
- 
- 

### Claude Code
- 
- 
- 

##  

### 
- ****: 100% ()
- **2**: 20-30% (70-80%)
- ****: 5-10% (90-95%WARNING)

### WARNING
- WARNING
- WARNING
- WARNING

### WARNING
- WARNING
- WARNING
- WARNING

## [WARNING] WARNING

### WARNING
1. **WARNING**
2. WARNING
3. WARNING

### WARNING
- WARNING
- WARNING
- 

### 
- .gitignoreANALYSIS
- ANALYSIS
- ANALYSIS

## [START] ANALYSIS

### Phase 1: ANALYSIS1ANALYSIS
- [ ] /analyzeANALYSIS
- [ ] ANALYSIS
- [ ] ANALYSIS

### Phase 2: ANALYSIS2ANALYSIS
- [ ] ANALYSIS
- [ ] ANALYSIS
- [ ] 

### Phase 3: 2
- [ ] 
- [ ] 
- [ ] Git hooks

### Phase 4: 1
- [ ] MCP
- [ ] 
- [ ] 

---

**