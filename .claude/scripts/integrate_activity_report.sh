#!/bin/bash
# ActivityReportを既存コマンドに統合するスクリプト

SCRIPTS_DIR="$(dirname "$0")"
ACTIVITY_TRACKER="$SCRIPTS_DIR/activity_tracker.sh"

# /spec コマンドへの統合
integrate_spec_command() {
    echo "📝 /spec コマンドにActivityReport機能を統合中..."
    
    # spec実行時のフック作成
    cat > "$SCRIPTS_DIR/spec_activity_hook.sh" << 'EOF'
#!/bin/bash
# /spec コマンド実行時のActivityReport更新

PHASE="$1"
ACTIVITY_TRACKER=".claude/scripts/activity_tracker.sh"

case "$PHASE" in
    "init")
        $ACTIVITY_TRACKER add "CTO" "プロジェクト初期化" "高"
        $ACTIVITY_TRACKER communicate "USER" "CTO" "新規プロジェクト開始"
        ;;
    "requirements")
        $ACTIVITY_TRACKER add "PLAN" "要件定義書作成" "高"
        $ACTIVITY_TRACKER communicate "CTO" "PLAN" "要件定義フェーズ開始"
        ;;
    "design")
        $ACTIVITY_TRACKER add "DEV" "技術設計書作成" "高"
        $ACTIVITY_TRACKER communicate "PLAN" "DEV" "要件定義完了、設計開始依頼"
        ;;
    "tasks")
        $ACTIVITY_TRACKER add "HR" "チーム編成" "中"
        $ACTIVITY_TRACKER communicate "CTO" "HR" "タスク分割とチーム編成依頼"
        ;;
    "implement")
        $ACTIVITY_TRACKER add "DEV" "実装開始" "高"
        $ACTIVITY_TRACKER add "QA" "コードレビュー準備" "中"
        $ACTIVITY_TRACKER communicate "DEV" "QA" "実装開始通知、レビュー準備依頼"
        ;;
esac
EOF
    chmod +x "$SCRIPTS_DIR/spec_activity_hook.sh"
}

# テスト実行時の統合
integrate_test_commands() {
    echo "🧪 テストコマンドにActivityReport機能を統合中..."
    
    cat > "$SCRIPTS_DIR/test_activity_hook.sh" << 'EOF'
#!/bin/bash
# テスト実行時のActivityReport更新

TEST_TYPE="$1"
RESULT="$2"
ACTIVITY_TRACKER=".claude/scripts/activity_tracker.sh"

# テスト開始時
$ACTIVITY_TRACKER add "QA" "テスト実行: $TEST_TYPE" "高"
$ACTIVITY_TRACKER communicate "QA" "DEV" "テスト開始: $TEST_TYPE"

# テスト完了時
if [ "$RESULT" = "success" ]; then
    $ACTIVITY_TRACKER update "*最新タスクID*" "完了"
    $ACTIVITY_TRACKER communicate "QA" "CTO" "テスト成功: $TEST_TYPE"
else
    $ACTIVITY_TRACKER communicate "QA" "DEV" "テスト失敗: $TEST_TYPE - 修正依頼"
fi
EOF
    chmod +x "$SCRIPTS_DIR/test_activity_hook.sh"
}

# コードレビュー時の統合
integrate_review_commands() {
    echo "🔍 レビューコマンドにActivityReport機能を統合中..."
    
    cat > "$SCRIPTS_DIR/review_activity_hook.sh" << 'EOF'
#!/bin/bash
# コードレビュー時のActivityReport更新

FILE="$1"
REVIEWER="$2"
RESULT="$3"
ACTIVITY_TRACKER=".claude/scripts/activity_tracker.sh"

# レビュー開始
$ACTIVITY_TRACKER add "QA" "コードレビュー: $(basename $FILE)" "中"
$ACTIVITY_TRACKER communicate "QA" "$REVIEWER" "レビュー開始: $FILE"

# レビュー結果記録
if [ "$RESULT" = "approved" ]; then
    $ACTIVITY_TRACKER communicate "QA" "DEV" "レビュー承認: $FILE"
else
    $ACTIVITY_TRACKER communicate "QA" "DEV" "レビュー要修正: $FILE"
fi
EOF
    chmod +x "$SCRIPTS_DIR/review_activity_hook.sh"
}

# 自動実行スケジューラー
setup_scheduler() {
    echo "⏰ 自動実行スケジューラーを設定中..."
    
    cat > "$SCRIPTS_DIR/activity_scheduler.sh" << 'EOF'
#!/bin/bash
# ActivityReport定期更新スケジューラー

ACTIVITY_DIR=".claude/.ActivityReport"
SCRIPTS_DIR=".claude/scripts"

# 10分ごとにメトリクス収集
while true; do
    # パフォーマンスメトリクス更新
    $SCRIPTS_DIR/collect_metrics.sh
    
    # 17:00になったら日次レポート生成
    if [ "$(date +%H:%M)" = "17:00" ]; then
        $SCRIPTS_DIR/daily_report_generator.sh
    fi
    
    # アクティブタスクの自動リマインド
    $SCRIPTS_DIR/send_reminders.sh
    
    sleep 600  # 10分待機
done &
EOF
    chmod +x "$SCRIPTS_DIR/activity_scheduler.sh"
}

# 既存プロジェクトへの適用
apply_to_existing_projects() {
    echo "📂 既存プロジェクトにActivityReportを適用中..."
    
    # test_projectsの結果をActivityReportに記録
    if [ -f ".claude/test_projects/results/integration_summary.md" ]; then
        $ACTIVITY_TRACKER add "QA" "統合テスト完了レポート作成" "完了"
        $ACTIVITY_TRACKER communicate "QA" "CTO" "全技術スタック統合検証完了"
    fi
}

# エイリアス設定
setup_aliases() {
    echo "🔗 エイリアス設定中..."
    
    cat > "$SCRIPTS_DIR/activity_aliases.sh" << 'EOF'
# ActivityReport用エイリアス
alias ar-add='~/.claude/scripts/activity_tracker.sh add'
alias ar-update='~/.claude/scripts/activity_tracker.sh update'
alias ar-comm='~/.claude/scripts/activity_tracker.sh communicate'
alias ar-dashboard='~/.claude/scripts/activity_dashboard.sh'
alias ar-report='~/.claude/scripts/daily_report_generator.sh'
EOF
    
    echo "source $SCRIPTS_DIR/activity_aliases.sh" >> ~/.bashrc
    echo "source $SCRIPTS_DIR/activity_aliases.sh" >> ~/.zshrc
}

# メイン処理
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ActivityReport統合開始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

integrate_spec_command
integrate_test_commands
integrate_review_commands
setup_scheduler
apply_to_existing_projects
setup_aliases

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ActivityReport統合完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 使用方法:"
echo "  • タスク追加: ar-add <部門> <タスク> <優先度>"
echo "  • ステータス更新: ar-update <タスクID> <ステータス>"
echo "  • 通信記録: ar-comm <送信元> <宛先> <メッセージ>"
echo "  • ダッシュボード: ar-dashboard"
echo "  • 日次レポート: ar-report"
echo ""
echo "🔄 自動更新:"
echo "  • /spec コマンド実行時に自動でActivityReport更新"
echo "  • テスト実行時に自動記録"
echo "  • コードレビュー時に自動記録"
echo "  • 17:00に日次レポート自動生成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"