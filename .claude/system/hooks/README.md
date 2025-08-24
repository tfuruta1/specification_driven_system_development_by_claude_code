# Claude Code Hooks - CONFIG

## [START] CONFIG

### 1. CONFIG
```bash
cd .claude/hooks
chmod +x setup_hooks.sh
./setup_hooks.sh
```

### 2. CONFIG
```bash
source ~/.claude_code_hooks
```

### 3. TEST
```bash
# TEST
./on_prompt.sh "TEST"
./on_tool.sh "Write" "test.js"
./on_response.sh "TEST"
```

## [INFO] TEST

| TEST | TEST | TEST |
|---------|---------|------|
| **on_prompt.sh** |  | / |
| **on_tool.sh** |  | CONFIG |
| **on_response.sh** | CONFIG | CONFIG |

## [TOOL] CONFIG

### CONFIG
```bash
# ~/.config/claude-code/settings.json
{
  "quality": {
    "review-threshold": 90,  // ERROR
    "block-on-failure": true  // ERROR
  }
}
```

### ERROR
- **ERROR1ERROR**: ERROR
- **ERROR2ERROR**: `block-on-failure: false`
- **ERROR3ERROR**: `block-on-failure: true`

## [REPORT] ERROR

### ERROR
```bash
cat ~/.claude/.pending_reviews
```

### ERROR
```bash
tail -20 ~/.claude/.stats/tool_usage.log
```

### 
```bash
ls -la ~/.claude/.backups/
```

## [SEARCH] 

### 
```bash
# 
ls -la ~/.claude/hooks/*.sh

# 
env | grep CLAUDE_CODE_HOOK

# 
tail -f ~/.claude/logs/hooks.log
```

### 
```bash
# 7
find ~/.claude/.backups -mtime +7 -delete
```

## [IDEA] 

1. ****
   -  `/code-review` 
   - 

2. ****
   - 
   - 

3. ****
   - 
   - 

## [TARGET] 

- ****: 0100%
- ****: 80%
- ****: 95%
- ****: 30%

## [NOTE] 

- **v1.0.0** (2025-08-17): 
  - 
  - 
  - 

---

* v8.3 - Claude Code Hooks*