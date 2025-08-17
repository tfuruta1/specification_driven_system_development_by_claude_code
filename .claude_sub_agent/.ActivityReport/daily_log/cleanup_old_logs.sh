#!/bin/bash

################################################################################
# 階層型エージェントシステム - 作業日誌自動削除スクリプト
# 1ヶ月以上経過した作業日誌を自動削除します
################################################################################

# デフォルト設定
RETENTION_DAYS=30
DRY_RUN=false
LOG_DIR="."

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルプ表示
show_help() {
    cat << EOF
使用方法: $0 [オプション]

階層型エージェントシステムの作業日誌を自動削除します。

オプション:
    -d, --days DAYS      ログ保持日数（デフォルト: 30日）
    -n, --dry-run        実際には削除せず、削除対象のみ表示
    -p, --path PATH      ログディレクトリのパス（デフォルト: 現在のディレクトリ）
    -h, --help           このヘルプを表示

例:
    $0                   # 30日以上経過したログを削除
    $0 --days 60         # 60日以上経過したログを削除
    $0 --dry-run         # 削除対象を確認（実際には削除しない）
    $0 --path /path/to/logs --days 7  # 指定ディレクトリの7日以上のログを削除

EOF
}

# 引数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--days)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -p|--path)
            LOG_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "不明なオプション: $1"
            show_help
            exit 1
            ;;
    esac
done

# ディレクトリ存在確認
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${RED}エラー: ディレクトリが存在しません: $LOG_DIR${NC}"
    exit 1
fi

# 変数初期化
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIMESTAMP=$(date +%s)
CUTOFF_TIMESTAMP=$((CURRENT_TIMESTAMP - RETENTION_DAYS * 86400))
FOUND_COUNT=0
DELETED_COUNT=0
TOTAL_SIZE=0
REPORT_FILE="$LOG_DIR/cleanup_report_$(date +%Y%m%d_%H%M%S).md"

# レポートヘッダー作成
create_report_header() {
    cat << EOF
# 作業日誌クリーンアップレポート

**実行日時**: $(date '+%Y-%m-%d %H:%M:%S')  
**保持期間**: ${RETENTION_DAYS}日  
**削除基準日**: $(date -d "-$RETENTION_DAYS days" +%Y-%m-%d)  
**実行モード**: $([ "$DRY_RUN" = true ] && echo "ドライラン" || echo "実行")  

## 削除対象ファイル

| ファイル名 | 作成日 | 経過日数 | サイズ | 状態 |
|-----------|--------|---------|--------|------|
EOF
}

# バナー表示
echo "=============================================================="
echo -e "${BLUE}階層型エージェントシステム - 作業日誌クリーンアップ${NC}"
echo "=============================================================="
echo -e "保持期間: ${GREEN}${RETENTION_DAYS}日${NC}"
echo -e "モード: $([ "$DRY_RUN" = true ] && echo -e "${YELLOW}ドライラン${NC}" || echo -e "${GREEN}実行${NC}")"
echo -e "対象ディレクトリ: ${BLUE}$LOG_DIR${NC}"
echo "=============================================================="
echo

# レポート開始
REPORT_CONTENT=$(create_report_header)

# ログファイル処理
echo -e "${BLUE}検索中...${NC}"
echo

# ファイル検索と処理
for log_file in "$LOG_DIR"/*_workingLog.md; do
    # ファイルが存在しない場合はスキップ
    [ ! -f "$log_file" ] && continue
    
    # ファイル名取得
    filename=$(basename "$log_file")
    
    # テンプレートファイルはスキップ
    if [ "$filename" = "TEMPLATE_workingLog.md" ]; then
        continue
    fi
    
    # 日付抽出（YYYY-MM-DD形式）
    if [[ $filename =~ ([0-9]{4})-([0-9]{2})-([0-9]{2})_workingLog\.md ]]; then
        file_date="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}"
        
        # 日付の妥当性チェック
        if date -d "$file_date" >/dev/null 2>&1; then
            # ファイルの経過日数計算
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                file_timestamp=$(date -j -f "%Y-%m-%d" "$file_date" +%s 2>/dev/null)
            else
                # Linux
                file_timestamp=$(date -d "$file_date" +%s 2>/dev/null)
            fi
            
            if [ -n "$file_timestamp" ]; then
                age_days=$(( (CURRENT_TIMESTAMP - file_timestamp) / 86400 ))
                
                # 保持期間を超えているかチェック
                if [ $age_days -gt $RETENTION_DAYS ]; then
                    FOUND_COUNT=$((FOUND_COUNT + 1))
                    
                    # ファイルサイズ取得
                    if [[ "$OSTYPE" == "darwin"* ]]; then
                        # macOS
                        file_size=$(stat -f%z "$log_file" 2>/dev/null)
                    else
                        # Linux
                        file_size=$(stat -c%s "$log_file" 2>/dev/null)
                    fi
                    file_size_kb=$((file_size / 1024))
                    TOTAL_SIZE=$((TOTAL_SIZE + file_size))
                    
                    # 削除処理
                    if [ "$DRY_RUN" = false ]; then
                        if rm "$log_file" 2>/dev/null; then
                            DELETED_COUNT=$((DELETED_COUNT + 1))
                            status="削除済"
                            echo -e "${GREEN}削除: $filename (${age_days}日経過)${NC}"
                        else
                            status="削除失敗"
                            echo -e "${RED}エラー: $filename の削除に失敗しました${NC}"
                        fi
                    else
                        status="削除予定"
                        echo -e "${YELLOW}削除予定: $filename (${age_days}日経過)${NC}"
                    fi
                    
                    # レポートに追加
                    REPORT_CONTENT+="
| $filename | $file_date | ${age_days}日 | ${file_size_kb}KB | $status |"
                fi
            fi
        fi
    fi
done

# 結果サマリー
echo
echo "=============================================================="
echo -e "${BLUE}実行結果:${NC}"
echo -e "  検出: ${YELLOW}${FOUND_COUNT}件${NC}"
echo -e "  削除: ${GREEN}${DELETED_COUNT}件${NC}"
echo -e "  合計サイズ: ${BLUE}$((TOTAL_SIZE / 1024))KB${NC}"
echo "=============================================================="

# レポート完成
if [ $FOUND_COUNT -eq 0 ]; then
    REPORT_CONTENT+="

削除対象のファイルはありませんでした。"
else
    REPORT_CONTENT+="

## サマリー

- **検出ファイル数**: ${FOUND_COUNT}件
- **削除ファイル数**: ${DELETED_COUNT}件
- **削除データ量**: $((TOTAL_SIZE / 1024))KB"
fi

REPORT_CONTENT+="

---
*このレポートは自動生成されました*"

# レポート保存
echo "$REPORT_CONTENT" > "$REPORT_FILE"
echo
echo -e "${GREEN}レポート保存: $(basename "$REPORT_FILE")${NC}"

# ドライラン時の注意表示
if [ "$DRY_RUN" = true ] && [ $FOUND_COUNT -gt 0 ]; then
    echo
    echo -e "${YELLOW}※ ドライランモードのため、実際の削除は行われていません${NC}"
    echo -e "${YELLOW}  実際に削除するには --dry-run オプションを外して実行してください${NC}"
fi

exit 0