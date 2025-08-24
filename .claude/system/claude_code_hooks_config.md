# Claude Code Hooks - 

## [INFO] 
Claude Code Hooks

## [TOOL] Hooks

### 1. user-prompt-submit-hook

```json
{
  "user-prompt-submit-hook": [
    {
      "description": "",
      "condition": "contains('/spec implement') || contains('WARNING') || contains('WARNING')",
      "action": "echo '[WARNING] WARNING'"
    },
    {
      "description": "WARNING",
      "condition": "contains('test') || contains('TEST')",
      "action": "check_review_status.sh"
    }
  ]
}
```

### 2. tool-use-hookANALYSIS

```json
{
  "tool-use-hook": {
    "Write": {
      "description": "",
      "pre-hook": "backup_before_write.sh",
      "post-hook": "mark_for_review.sh"
    },
    "Edit": {
      "description": "",
      "post-hook": "add_review_flag.sh"
    },
    "MultiEdit": {
      "description": "ANALYSIS",
      "post-hook": "quality_check_batch.sh"
    }
  }
}
```

### 3. response-hookANALYSIS

```json
{
  "response-hook": [
    {
      "description": "SUCCESS",
      "condition": "response_contains('SUCCESS') || response_contains('implementation complete')",
      "action": "suggest_code_review.sh"
    }
  ]
}
```

## SUCCESS SUCCESS

### check_review_status.sh
```bash
#!/bin/bash
# ANALYSIS

REVIEW_FLAG=".claude/.review_status"

if [ ! -f "$REVIEW_FLAG" ] || [ "$(cat $REVIEW_FLAG)" != "completed" ]; then
    echo "[ERROR] SUCCESS: SUCCESS"
    echo "[INFO] SUCCESS:"
    echo "  /code-review"
    exit 1
fi

echo "[OK] "
```

### mark_for_review.sh
```bash
#!/bin/bash
# /

FILE_PATH="$1"
REVIEW_LIST=".claude/.pending_reviews"

# 
echo "$FILE_PATH" >> "$REVIEW_LIST"

# 
sort -u "$REVIEW_LIST" -o "$REVIEW_LIST"

echo "[NOTE] : $FILE_PATH"
```

### suggest_code_review.sh
```bash
#!/bin/bash
# 

PENDING_REVIEWS=".claude/.pending_reviews"

if [ -f "$PENDING_REVIEWS" ] && [ -s "$PENDING_REVIEWS" ]; then
    echo ""
    echo ""
    echo "[SEARCH] :"
    echo "SUCCESS"
    cat "$PENDING_REVIEWS" | while read file; do
        echo "  • $file"
    done
    echo ""
    echo "[IDEA] SUCCESS: /code-review SUCCESS"
    echo "SUCCESS"
fi
```

### quality_check_batch.sh
```bash
#!/bin/bash
# ANALYSIS

echo "[SEARCH] WARNING..."

# LintWARNING
if [ -f "package.json" ]; then
    npm run lint 2>/dev/null || echo "[WARNING] LintWARNING"
fi

if [ -f "pyproject.toml" ]; then
    ruff check . 2>/dev/null || echo "[WARNING] Python lintWARNING"
fi

if [ -f "*.csproj" ]; then
    dotnet format --verify-no-changes 2>/dev/null || echo "[WARNING] .NET formatWARNING"
fi

echo "[OK] WARNING"
```

## [TARGET] HooksWARNING

### WARNING1: WARNING
- 
- 

### 2: CONFIG
- CONFIG
- CONFIG

### CONFIG3: CONFIG
- CONFIG
- CONFIG

## [INFO] CONFIG

### 1. settings.jsonCONFIG
```json
{
  "hooks": {
    "user-prompt-submit-hook": "~/.claude/hooks/on_prompt.sh",
    "tool-use-hook": "~/.claude/hooks/on_tool.sh",
    "response-hook": "~/.claude/hooks/on_response.sh"
  }
}
```

### 2. 
```bash
export CLAUDE_CODE_HOOK_USER_PROMPT="~/.claude/hooks/on_prompt.sh"
export CLAUDE_CODE_HOOK_TOOL_USE="~/.claude/hooks/on_tool.sh"
export CLAUDE_CODE_HOOK_RESPONSE="~/.claude/hooks/on_response.sh"
```

## [REFRESH] 

```mermaid
graph TB
    A[/] --> B{Hooks: mark_for_review}
    B --> C[]
    C --> D[]
    D --> E{Hooks: suggest_review}
    E --> F[ANALYSIS]
    F --> G{ANALYSIS?}
    G -->|Yes| H[ERROR]
    G -->|No| I[ERROR]
    I --> J{Hooks: check_review}
    J -->|ERROR| K[[ERROR] ERROR]
    J -->|ERROR| L[[OK] ERROR]
    H --> M[ERROR]
    M --> L
```

## [REPORT] REPORT

### REPORT
- **REPORT**: 100%REPORT
- **REPORT**: 80%REPORT
- **REPORT**: 60%REPORT
- ****: 95%

### 
- 
- 
- 
- 

## [START] 

### 1. AI
```bash
#!/bin/bash
# AI

echo " AI..."
for file in $(cat .pending_reviews); do
    echo "SYSTEM: $file"
    # Claude APISUCCESS
    claude review "$file" --security --performance --maintainability
done
```

### 2. SUCCESS
```bash
#!/bin/bash
# SUCCESS

{
    echo "date: $(date +%Y-%m-%d)"
    echo "files_reviewed: $(wc -l < .reviewed_files)"
    echo "issues_found: $(grep -c 'issue' .review_log)"
    echo "review_time: $(cat .review_time)"
} >> .metrics/review_metrics.yaml
```

### 3. ERROR
```bash
#!/bin/bash
# Slack/TeamsERROR

if [ "$(cat .review_status)" = "failed" ]; then
    curl -X POST $SLACK_WEBHOOK_URL \
        -H 'Content-Type: application/json' \
        -d '{"text":"[WARNING] WARNING"}'
fi
```

## [TOOL] WARNING

### Q: HooksWARNING
A: WARNING
```bash
chmod +x ~/.claude/hooks/*.sh
```

### Q: Hooks
A: 
```bash
tail -f ~/.claude/logs/hooks.log
```

### Q: 
A: 
```bash
# 
nohup ./review_hook.sh &
```

##  

1. ****: 
2. ****: 
3. ****: 
4. ****: Hooks
5. ****: Hooks

---

*Claude Code Hooks*