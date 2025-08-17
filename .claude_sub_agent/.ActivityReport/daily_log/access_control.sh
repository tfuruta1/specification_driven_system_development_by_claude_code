#!/bin/bash

################################################################################
# 階層型エージェントシステム - ログアクセス権限管理
# ブラック企業のログアクセス制御システム
################################################################################

# 設定
LOG_DIR=".claude_sub_agent/.ActivityReport/daily_log"
PRIVATE_DIR="$LOG_DIR/.private"
TASKS_DIR=".claude_sub_agent/.ActivityReport/tasks"

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ユーザー/エージェント識別
identify_accessor() {
    local accessor="$1"
    
    case "$accessor" in
        "user"|"USER")
            echo "user"
            ;;
        "cto"|"CTO")
            echo "agent_cto"
            ;;
        "hr"|"人事部")
            echo "agent_hr"
            ;;
        "planning"|"経営企画部")
            echo "agent_planning"
            ;;
        "dev"|"システム開発部")
            echo "agent_dev"
            ;;
        "qa"|"品質保証部")
            echo "agent_qa"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# アクセス権限チェック
check_permission() {
    local accessor="$1"
    local action="$2"
    local target="$3"
    
    local role=$(identify_accessor "$accessor")
    
    # ユーザーのみ全て読み取り可能（CTOも読み取り不可）
    if [ "$role" = "user" ] && [ "$action" = "read" ]; then
        return 0
    fi
    
    # 全エージェント（CTOを含む）のログ書き込み権限
    if [[ "$role" == agent_* ]] && [ "$action" = "write" ]; then
        # daily_logへの書き込みは全エージェント可能
        if [[ "$target" == *"daily_log"* ]] && [[ "$target" != *".private"* ]]; then
            return 0
        fi
        # プライベートログへの書き込みも可能
        if [[ "$target" == *".private"* ]]; then
            return 0
        fi
    fi
    
    # エージェントのログ読み取り制限
    if [[ "$role" == agent_* ]] && [ "$action" = "read" ]; then
        # tasksフォルダは読み書き可能（情報共有用）
        if [[ "$target" == *"tasks"* ]]; then
            return 0
        fi
        # daily_logは書き込みのみ、読み取り不可
        if [[ "$target" == *"daily_log"* ]]; then
            return 1  # 読み取り拒否
        fi
    fi
    
    # 人事部の削除権限
    if [ "$role" = "agent_hr" ] && [ "$action" = "delete" ]; then
        if [[ "$target" == *"daily_log"* ]]; then
            return 0
        fi
    fi
    
    # デフォルトは拒否
    return 1
}

# ログ書き込み（追記のみ）
write_log() {
    local agent="$1"
    local content="$2"
    local log_type="$3"  # normal or private
    
    local role=$(identify_accessor "$agent")
    local timestamp=$(date '+%H:%M:%S')
    local today=$(date +%Y-%m-%d)
    
    if [ "$log_type" = "private" ]; then
        local target="$PRIVATE_DIR/${today}_private.md"
    else
        local target="$LOG_DIR/${today}_workingLog.md"
    fi
    
    # 権限チェック
    if check_permission "$agent" "write" "$target"; then
        # ディレクトリ作成
        mkdir -p "$(dirname "$target")"
        
        # ログ追記
        {
            echo ""
            echo "#### ${timestamp} - ${agent}の記録"
            echo "$content"
        } >> "$target"
        
        echo -e "${GREEN}✅ ログ記録成功${NC}"
        
        # プライベートログの場合は権限設定
        if [ "$log_type" = "private" ]; then
            chmod 600 "$target" 2>/dev/null  # 所有者のみ読み書き可能
        fi
    else
        echo -e "${RED}❌ アクセス拒否: ${agent}はログに書き込めません${NC}"
        return 1
    fi
}

# ログ読み取り
read_log() {
    local accessor="$1"
    local target="$2"
    
    # 権限チェック
    if check_permission "$accessor" "read" "$target"; then
        if [ -f "$target" ]; then
            echo -e "${GREEN}=== ログ内容 ===${NC}"
            cat "$target"
        else
            echo -e "${YELLOW}ログファイルが存在しません${NC}"
        fi
    else
        echo -e "${RED}❌ アクセス拒否: ${accessor}はこのログを読めません${NC}"
        echo -e "${YELLOW}💡 ヒント: エージェントはログを書き込みのみ可能です${NC}"
        echo -e "${YELLOW}          情報共有はtasksフォルダを使用してください${NC}"
        return 1
    fi
}

# タスク共有（読み書き可能）
share_task() {
    local agent="$1"
    local content="$2"
    local timestamp=$(date '+%H:%M:%S')
    local shared_file="$TASKS_DIR/shared_tasks.md"
    
    # tasksディレクトリは全員読み書き可能
    mkdir -p "$TASKS_DIR"
    
    {
        echo ""
        echo "#### ${timestamp} - ${agent}からの共有"
        echo "$content"
    } >> "$shared_file"
    
    echo -e "${GREEN}✅ タスク共有成功（他のメンバーも読めます）${NC}"
}

# 定期削除（人事部専用）
cleanup_logs() {
    local executor="$1"
    local role=$(identify_accessor "$executor")
    
    if [ "$role" != "agent_hr" ]; then
        echo -e "${RED}❌ エラー: ログ削除は人事部のみ実行可能です${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🗑️ 人事部による定期ログ削除を開始...${NC}"
    
    # 30日以上経過したログを削除
    find "$LOG_DIR" -name "*_workingLog.md" -mtime +30 -exec rm {} \; 2>/dev/null
    find "$PRIVATE_DIR" -name "*_private.md" -mtime +30 -exec rm {} \; 2>/dev/null
    
    # 削除レポート作成
    local report_file="$LOG_DIR/deletion_report_$(date +%Y%m%d).md"
    {
        echo "# ログ削除レポート"
        echo "**実行者**: 人事部"
        echo "**実行日時**: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "**削除基準**: 30日以上経過"
        echo ""
        echo "削除完了しました。"
    } > "$report_file"
    
    echo -e "${GREEN}✅ 定期削除完了${NC}"
}

# アクセス制御デモ
demo_access_control() {
    echo -e "${BLUE}=== アクセス制御デモ ===${NC}"
    echo
    
    # ユーザーのアクセス
    echo -e "${GREEN}1. ユーザー（唯一の閲覧者）: 全ログ読み取り可能${NC}"
    echo "   ✅ daily_log読み取り"
    echo "   ✅ private_log読み取り"
    echo "   ✅ tasks読み取り"
    echo "   ℹ️ パフォーマンス監視と面談指示"
    echo
    
    # CTOのアクセス
    echo -e "${YELLOW}2. CTO: ログ書き込みのみ（読み取り不可）${NC}"
    echo "   ✅ daily_log書き込み"
    echo "   ✅ private_log書き込み"
    echo "   ❌ daily_log読み取り（拒否）"
    echo "   ❌ 他メンバーのパフォーマンス閲覧（拒否）"
    echo "   ✅ tasks読み書き（情報共有のみ）"
    echo
    
    # 人事部の特権
    echo -e "${BLUE}3. 人事部: 削除権限あり${NC}"
    echo "   ✅ ログ書き込み"
    echo "   ❌ ログ読み取り（拒否）"
    echo "   ✅ 30日経過ログの削除"
    echo "   ✅ tasks読み書き"
    echo
    
    # その他エージェント
    echo -e "${YELLOW}4. その他エージェント${NC}"
    echo "   ✅ ログ書き込み（追記のみ）"
    echo "   ❌ ログ読み取り（拒否）"
    echo "   ✅ tasks読み書き（情報共有用）"
}

# メイン処理
main() {
    local command="$1"
    shift
    
    case "$command" in
        "write")
            write_log "$@"
            ;;
        "read")
            read_log "$@"
            ;;
        "share")
            share_task "$@"
            ;;
        "cleanup")
            cleanup_logs "$@"
            ;;
        "demo")
            demo_access_control
            ;;
        "help")
            cat << EOF
使用方法:
  $0 write <agent> <content> [private]  - ログ書き込み
  $0 read <accessor> <file>             - ログ読み取り
  $0 share <agent> <content>            - タスク共有
  $0 cleanup <executor>                 - ログ削除（人事部のみ）
  $0 demo                                - アクセス制御デモ
  $0 help                                - このヘルプ

例:
  $0 write "CTO" "本日の作業開始"
  $0 write "システム開発部" "疲れた..." private
  $0 read "user" "daily_log/2025-08-17_workingLog.md"
  $0 share "品質保証部" "テスト完了、レビュー依頼"
  $0 cleanup "人事部"
EOF
            ;;
        *)
            echo -e "${RED}不明なコマンド: $command${NC}"
            echo "使用方法: $0 help"
            exit 1
            ;;
    esac
}

# 引数がある場合は実行
if [ $# -gt 0 ]; then
    main "$@"
else
    echo "使用方法: $0 help"
fi