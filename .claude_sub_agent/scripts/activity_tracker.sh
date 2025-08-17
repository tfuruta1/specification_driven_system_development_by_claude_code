#!/bin/bash
# ActivityReport自動更新スクリプト

ACTIVITY_DIR=".claude_sub_agent/.ActivityReport"
TASKS_FILE="$ACTIVITY_DIR/tasks/shared_tasks.md"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# ディレクトリ作成
mkdir -p "$ACTIVITY_DIR/tasks"
mkdir -p "$ACTIVITY_DIR/communications/requests"
mkdir -p "$ACTIVITY_DIR/communications/responses"
mkdir -p "$ACTIVITY_DIR/communications/decisions"
mkdir -p "$ACTIVITY_DIR/daily_report"
mkdir -p "$ACTIVITY_DIR/metrics"

# タスク追加関数
add_task() {
    local department="$1"
    local task="$2"
    local priority="$3"
    local task_id="$(date +%Y%m%d)-${department}-$(printf '%03d' $RANDOM)"
    
    # 優先度に応じてセクション選択
    case "$priority" in
        "高")
            section="### 🔴 緊急度：高"
            ;;
        "中")
            section="### 🟡 緊急度：中"
            ;;
        *)
            section="### 🟢 緊急度：低"
            ;;
    esac
    
    # タスクを適切なセクションに追加
    awk -v section="$section" -v task="| $task_id | $department | $task | 未着手 | $(date -d '+3 days' +%Y-%m-%d) | - |" '
        $0 ~ section {
            print
            getline
            print
            getline
            print
            print task
            next
        }
        {print}
    ' "$TASKS_FILE" > "$TASKS_FILE.tmp" && mv "$TASKS_FILE.tmp" "$TASKS_FILE"
    
    echo "✅ タスク追加: $task_id - $task"
    
    # 通信ログに記録
    log_communication "SYSTEM" "$department" "新規タスク割り当て: $task_id"
}

# 部門間通信記録関数
log_communication() {
    local from="$1"
    local to="$2"
    local message="$3"
    local comm_file="$ACTIVITY_DIR/communications/$(date +%Y%m%d).log"
    
    {
        echo "[$TIMESTAMP] $from → $to"
        echo "内容: $message"
        echo "---"
    } >> "$comm_file"
    
    # shared_tasks.mdの通信セクションも更新
    update_communication_section "$from" "$to" "$message"
}

# 通信セクション更新
update_communication_section() {
    local from="$1"
    local to="$2"
    local message="$3"
    
    # 依頼事項セクションに追加
    awk -v timestamp="$TIMESTAMP" -v from="$from" -v to="$to" -v msg="$message" '
        /### 依頼事項/ {
            print
            getline
            print
            print "[" timestamp "] " from " → " to
            print "内容：" msg
            print "期限：" strftime("%Y-%m-%d", systime() + 86400)
            print ""
            next
        }
        {print}
    ' "$TASKS_FILE" > "$TASKS_FILE.tmp" && mv "$TASKS_FILE.tmp" "$TASKS_FILE"
}

# ステータス更新関数
update_status() {
    local task_id="$1"
    local new_status="$2"
    
    # タスクのステータスを更新
    sed -i "s/| $task_id | \([^|]*\) | \([^|]*\) | [^|]* |/| $task_id | \1 | \2 | $new_status |/" "$TASKS_FILE"
    
    echo "📝 ステータス更新: $task_id → $new_status"
    
    # 進捗サマリーも更新
    update_progress_summary "$task_id" "$new_status"
}

# 進捗サマリー更新
update_progress_summary() {
    local task_id="$1"
    local status="$2"
    local department=$(grep "$task_id" "$TASKS_FILE" | cut -d'|' -f3 | tr -d ' ')
    
    # 部門別進捗を更新
    case "$status" in
        "完了")
            mark_task_complete "$department"
            ;;
        "進行中")
            mark_task_in_progress "$department"
            ;;
    esac
}

# タスク完了マーク
mark_task_complete() {
    local dept="$1"
    local dept_section=$(get_dept_section "$dept")
    
    # 該当部門のチェックボックスを更新
    sed -i "/$dept_section/,/^###/ s/- \[ \] 完了タスク/- [x] 完了タスク/" "$TASKS_FILE"
}

# 部門セクション取得
get_dept_section() {
    case "$1" in
        "CTO") echo "### 🎯 CTO" ;;
        "DEV") echo "### 💻 システム開発部" ;;
        "QA") echo "### 🛡️ 品質保証部" ;;
        "HR") echo "### 🏢 人事部" ;;
        "PLAN") echo "### 💡 経営企画部" ;;
    esac
}

# メイン処理
case "$1" in
    "add")
        add_task "$2" "$3" "$4"
        ;;
    "update")
        update_status "$2" "$3"
        ;;
    "communicate")
        log_communication "$2" "$3" "$4"
        ;;
    "init")
        # 初期化処理
        echo "📊 ActivityReport初期化中..."
        cp "$ACTIVITY_DIR/tasks/shared_tasks.md.template" "$TASKS_FILE" 2>/dev/null || echo "テンプレートなし、既存ファイル使用"
        ;;
    *)
        echo "使用方法:"
        echo "  $0 add <部門> <タスク> <優先度>"
        echo "  $0 update <タスクID> <ステータス>"
        echo "  $0 communicate <送信元> <宛先> <メッセージ>"
        echo "  $0 init"
        ;;
esac