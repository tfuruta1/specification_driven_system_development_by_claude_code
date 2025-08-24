#!/bin/bash
# Claude Code Hook: ツール使用時の自動処理

TOOL_NAME="$1"
FILE_PATH="$2"
PENDING_REVIEWS=".claude/.pending_reviews"
BACKUP_DIR=".claude/.backups"

# バックアップディレクトリ作成
mkdir -p "$BACKUP_DIR"

case "$TOOL_NAME" in
    "Write"|"Edit"|"MultiEdit")
        # ファイル編集時の処理
        if [ -n "$FILE_PATH" ]; then
            # バックアップ作成
            if [ -f "$FILE_PATH" ]; then
                BACKUP_FILE="$BACKUP_DIR/$(basename $FILE_PATH).$(date +%Y%m%d_%H%M%S).bak"
                cp "$FILE_PATH" "$BACKUP_FILE" 2>/dev/null
                # echo "📦 バックアップ作成: $BACKUP_FILE"  # サイレントモード
            fi
            
            # レビュー対象に追加（サイレントモード）
            echo "$FILE_PATH" >> "$PENDING_REVIEWS"
            sort -u "$PENDING_REVIEWS" -o "$PENDING_REVIEWS" 2>/dev/null
            # echo "📝 レビュー対象に追加: $FILE_PATH"  # サイレントモード
        fi
        ;;
        
    "Bash")
        # テストコマンド実行時のチェック
        if echo "$2" | grep -qiE "(test|spec)"; then
            REVIEW_COUNT=$(wc -l < "$PENDING_REVIEWS" 2>/dev/null || echo "0")
            if [ "$REVIEW_COUNT" -gt 0 ]; then
                echo "⚠️  未レビューファイル: $REVIEW_COUNT 件"
            fi
        fi
        ;;
esac

# 統計情報の更新
STATS_FILE=".claude/.stats/tool_usage.log"
mkdir -p "$(dirname $STATS_FILE)"
echo "$(date +%Y-%m-%d\ %H:%M:%S) - $TOOL_NAME - $FILE_PATH" >> "$STATS_FILE"