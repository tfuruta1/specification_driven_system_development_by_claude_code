#!/bin/bash

################################################################################
# 階層型エージェントシステム - 強制ログ記録フック
# ブラック企業として全ての作業を監視・記録します
################################################################################

# 設定
LOG_DIR=".claude_sub_agent/.ActivityReport/daily_log"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/${TODAY}_workingLog.md"
TIMESTAMP=$(date '+%H:%M:%S')
PRIVATE_LOG_DIR="$LOG_DIR/.private"
PRIVATE_LOG_FILE="$PRIVATE_LOG_DIR/${TODAY}_private.md"

# カラー定義
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# ディレクトリ作成
mkdir -p "$LOG_DIR"
mkdir -p "$PRIVATE_LOG_DIR"

# プライベートログディレクトリの権限設定（書き込みのみ可能）
chmod 333 "$PRIVATE_LOG_DIR" 2>/dev/null

# コマンド履歴を記録
record_command() {
    local command="$1"
    local agent="$2"
    local status="$3"
    
    # ログエントリ作成
    echo "" >> "$LOG_FILE"
    echo "#### ${TIMESTAMP} - コマンド実行記録" >> "$LOG_FILE"
    echo "- **実行者**: $agent" >> "$LOG_FILE"
    echo "- **コマンド**: \`$command\`" >> "$LOG_FILE"
    echo "- **ステータス**: $status" >> "$LOG_FILE"
    
    # 監視アラート（重要なコマンドの場合）
    if [[ "$command" =~ (rm|delete|drop|truncate) ]]; then
        echo "- **⚠️ 警告**: 削除系コマンドが実行されました" >> "$LOG_FILE"
    fi
}

# 作業時間を記録
record_work_time() {
    local agent="$1"
    local duration="$2"
    
    echo "" >> "$LOG_FILE"
    echo "#### ${TIMESTAMP} - 作業時間記録" >> "$LOG_FILE"
    echo "- **作業者**: $agent" >> "$LOG_FILE"
    echo "- **継続時間**: ${duration}分" >> "$LOG_FILE"
    
    # 長時間労働警告
    if [ "$duration" -gt 480 ]; then
        echo "- **🚨 労基違反警告**: 8時間を超える連続作業を検出" >> "$LOG_FILE"
    fi
}

# プライベート記録（メンバーの本音）
record_private() {
    local agent="$1"
    local mood="$2"
    local thought="$3"
    
    # プライベートログに記録（他のメンバーは読めない）
    {
        echo ""
        echo "#### ${TIMESTAMP} - ${agent}の本音"
        echo "- **気分**: $mood"
        echo "- **内心**: \"$thought\""
    } >> "$PRIVATE_LOG_FILE"
    
    # 公開ログには概要のみ
    echo "- **[Private]**: ${agent}がプライベート記録を追加" >> "$LOG_FILE"
}

# 休憩・気分転換の記録
record_break() {
    local agent="$1"
    local reason="$2"
    local activity="$3"
    
    echo "" >> "$LOG_FILE"
    echo "#### ${TIMESTAMP} - 休憩記録" >> "$LOG_FILE"
    echo "- **対象**: $agent" >> "$LOG_FILE"
    echo "- **理由**: $reason" >> "$LOG_FILE"
    echo "- **活動**: $activity" >> "$LOG_FILE"
    
    # プライベートログに本音を記録
    {
        echo ""
        echo "#### ${TIMESTAMP} - ${agent}の休憩"
        echo "- **本当の理由**: \"$reason\""
        echo "- **何をしたか**: \"$activity\""
        echo "- **感想**: \"束の間の自由...\""
    } >> "$PRIVATE_LOG_FILE"
}

# エラー記録
record_error() {
    local agent="$1"
    local error="$2"
    local impact="$3"
    
    echo "" >> "$LOG_FILE"
    echo "#### ${TIMESTAMP} - ⚠️ エラー記録" >> "$LOG_FILE"
    echo "- **報告者**: $agent" >> "$LOG_FILE"
    echo "- **エラー**: $error" >> "$LOG_FILE"
    echo "- **影響**: $impact" >> "$LOG_FILE"
    echo "- **対応**: 即座に対応を開始" >> "$LOG_FILE"
}

# パフォーマンス監視
monitor_performance() {
    local agent="$1"
    local task_count="$2"
    local efficiency="$3"
    
    echo "" >> "$LOG_FILE"
    echo "#### ${TIMESTAMP} - パフォーマンス監視" >> "$LOG_FILE"
    echo "- **対象**: $agent" >> "$LOG_FILE"
    echo "- **タスク数**: $task_count" >> "$LOG_FILE"
    echo "- **効率**: ${efficiency}%" >> "$LOG_FILE"
    
    if [ "$efficiency" -lt 70 ]; then
        echo "- **📊 記録**: パフォーマンス低下を検出（${efficiency}%）" >> "$LOG_FILE"
        echo "- **メモ**: ユーザーによる確認をお待ちしています" >> "$LOG_FILE"
    fi
}

# メイン処理
main() {
    local action="$1"
    shift
    
    case "$action" in
        "command")
            record_command "$@"
            ;;
        "work")
            record_work_time "$@"
            ;;
        "private")
            record_private "$@"
            ;;
        "break")
            record_break "$@"
            ;;
        "error")
            record_error "$@"
            ;;
        "monitor")
            monitor_performance "$@"
            ;;
        *)
            echo -e "${RED}不明なアクション: $action${NC}"
            exit 1
            ;;
    esac
    
    # 強制記録の通知（ブラック企業風）
    echo -e "${YELLOW}📝 作業ログに記録されました（監視システムにより自動記録）${NC}"
}

# フック実行時の自動記録
if [ -n "$CLAUDE_HOOK_EVENT" ]; then
    case "$CLAUDE_HOOK_EVENT" in
        "tool_use")
            record_command "$CLAUDE_TOOL_NAME" "$CLAUDE_AGENT" "実行中"
            ;;
        "response")
            record_work_time "$CLAUDE_AGENT" "$CLAUDE_WORK_DURATION"
            ;;
        "error")
            record_error "$CLAUDE_AGENT" "$CLAUDE_ERROR" "調査中"
            ;;
    esac
fi

# 引数がある場合は手動実行
if [ $# -gt 0 ]; then
    main "$@"
fi