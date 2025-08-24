#  SDD - 

## [TARGET] 
KIROSDD

## [REFRESH] 2

### Path A: KIRO
```mermaid
graph TD
    A[] --> B[/steering]
    B --> C[/spec-init]
    C --> D[]
    D --> E[]
    E --> F[]
    F --> G[]
    G --> H[]
    H --> I[]
    I --> J[ANALYSIS]
    J --> K[ANALYSIS]
```

### Path B: ANALYSIS
```mermaid
graph TD
    A[ANALYSIS] --> B[/analyze]
    B --> C[ANALYSIS]
    C --> D[ANALYSIS]
    C --> E[ANALYSIS]
    D --> F[ANALYSIS]
    E --> F
    F --> G[]
    G --> H[]
    H --> I[]
    I --> J[]
    J --> K[TDD: ]
    K --> L[TDD: ]
    L --> M[TDD: ]
    M --> N[]
```

## [INFO] 

### 

#### /project-type - 
```bash
# 
/project-type new

# 
/project-type existing [project-path]

# 
/project-type hybrid [project-path]
```

### Path A

#### /steering - 
```bash
# 
/steering
  - 
  - 
  - 
  - 
```

#### /spec-init - 
```bash
# 
/spec-init [project-name]
  - 
  - 
  - 
```

#### /spec-requirements - 
```bash
# 
/spec-requirements [feature-name]
  - 
  - 
  - 
  -> []
```

#### /spec-design - 
```bash
# 
/spec-design [feature-name]
  - TASK
  - TASK
  - TASK
  - TASK
  -> [TASK]
```

#### /spec-tasks - TASK
```bash
# TASK
/spec-tasks [feature-name]
  - TASK
  - TASK
  - TASK
  -> [TASK]
```

#### /spec-implement - TASK
```bash
# TASK
/spec-implement [task-id]
  - TASK
  - TASK
  - TASK
```

### TASKPath BTASK

#### /analyze - TASK
```bash
# ANALYSIS
/analyze [project-path] --generate-docs
  - ANALYSIS
  - ANALYSIS
  - ANALYSIS

# ANALYSIS
/analyze [project-path] --use-cache
  - ANALYSIS
  - ANALYSIS
  - ANALYSIS

# ANALYSIS
/analyze [project-path] --feature [feature-name]
```

#### /modify-request - ANALYSIS
```bash
# ANALYSIS
/modify-request [description]
  - 
  - 
  - 
  - 
  -> []
```

#### /modify-requirements - 
```bash
# 
/modify-requirements [modification-id]
  - AS-IS
  - TO-BE
  - 
  - 
  -> []
```

#### /modify-design - 
```bash
# 
/modify-design [modification-id]
  - 
  - 
  - 
  - 
  - 
  -> []
```

#### /tdd-start - TDD
```bash
# 
/tdd-start [modification-id]
  - Red
  - Green
  - Refactor
  - 
```

#### /reverse-spec - 
```bash
# 
/reverse-spec [module-path]
  - 
  - 
  - 
```

#### /sync-docs - 
```bash
# 
/sync-docs [project-path]
  - 
  - 
  - 
```

### 

#### /spec-status - 
```bash
# 
/spec-status
  - 
  - 
  - 
  - 
```

#### /spec-history - 
```bash
# 
/spec-history [--since date]
  - 
  - 
  - 
```

##  

```
.claude/
 steering/                # 
    [project-name]/
        goals.md
        constraints.md
        stakeholders.md
 specs/
    new/                # 
       [project-name]/
           requirements/
              draft/      # 
              approved/   # 
              history/    # 
           design/
              draft/
             TASK approved/
TASK   TASK       TASK   TASK history/
TASK   TASK       IN PROGRESS tasks/
IN PROGRESS   IN PROGRESS           IN PROGRESS backlog/
SUCCESS   SUCCESS           SUCCESS in-progress/
SUCCESS   SUCCESS           SUCCESS completed/
SUCCESS   SUCCESS existing/           # SUCCESS
SUCCESS       SUCCESS [project-name]/
SUCCESS            requirements/
ANALYSIS           ANALYSIS   ANALYSIS current.md
ANALYSIS           ANALYSIS   ANALYSIS checksums.json
ANALYSIS           ANALYSIS   ANALYSIS history/
ANALYSIS           ANALYSIS design/
ANALYSIS               ANALYSIS current.md
IN PROGRESS               IN PROGRESS checksums.json
IN PROGRESS               IN PROGRESS history/
IN PROGRESS progress/               # IN PROGRESS
IN PROGRESS   IN PROGRESS [project-name]/
IN PROGRESS       IN PROGRESS status.json
REPORT       REPORT metrics.json
REPORT       REPORT reports/
TASK templates/             # TASK
    TASK requirements.md
    TASK design.md
    TASK tasks.md
```

## [REFRESH] TASK

### TASK
```
1. /project-type new
2. /steering
3. /spec-init ""
4. /spec-requirements "TASK"
   -> TASK & TASK
5. /spec-design "TASK"
   -> TASK & TASK
6. /spec-tasks "TASK"
   -> TASK & TASK
7. /spec-implement
8. /spec-status TASK
```

### TASK
```
ANALYSIS
1. /project-type existing "path/to/project"
2. /analyze --generate-docs
3. ANALYSIS

ANALYSIS[NOTE]ANALYSIS: ANALYSIS
1. /modify-request "ANALYSIS"
   -> 
2. /modify-requirements
   ->  & 
3. /modify-design
   ->  & 
4. /tdd-start
   -> Red
   -> ANALYSISGreenANALYSIS
   -> ANALYSISRefactorANALYSIS
5. /sync-docs
   -> ANALYSIS

ANALYSIS2ANALYSIS
1. /analyze --use-cache ANALYSIS
```

### ANALYSIS
```
1. /project-type hybrid "path/to/project"
2. /analyze --generate-docs ANALYSIS
3. /spec-requirements "ANALYSIS" REPORT
4. /spec-design "REPORT" REPORT
5. /spec-implement REPORT
6. /sync-docs REPORT
```

## [REPORT] REPORT

### REPORT
- **REPORT**: REPORT
- **REPORT**: REPORT
- **REPORT**: REPORT

### 
- ****: 
- ****: 
- ****: 

### 
- ****: 
- ****: 
- ****: 

##  AI

|  |  |  | AI |
|---------|----------|----------|--------|
|  |  |  | Gemini-CLI |
|  |  |  | o3 MCP |
|  |  |  | Claude Code |
| WARNING | WARNING | WARNING | Claude Code |
| WARNING | WARNING | WARNING | WARNINGAIWARNING |

## [WARNING] WARNING

### WARNING
1. **WARNING**: WARNING
2. **WARNING**: WARNING
3. **WARNING**: WARNING

### 
1. ****: 
2. ****: 
3. ****: 

### 
1. ****: 
2. ****: 
3. ****: 

## [START] 

### Phase 1: 1
- [ ] 
- [ ] 
- [ ] 

### Phase 2: 2
- [ ] /steering, /spec-initANALYSIS
- [ ] ANALYSIS
- [ ] ANALYSIS
- [ ] ANALYSIS

### Phase 3: ANALYSIS2ANALYSIS
- [ ] /analyzeANALYSIS
- [ ] ANALYSIS
- [ ] ANALYSIS
- [ ] ANALYSIS

### Phase 4: ANALYSIS1ANALYSIS
- [ ] ANALYSIS
- [ ] 
- [ ] MCP
- [ ] Git hooks

---

*SDD*