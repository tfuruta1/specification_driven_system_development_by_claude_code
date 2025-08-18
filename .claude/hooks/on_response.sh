#!/bin/bash
# Claude Code Hook: 応答生成時の自動提案

RESPONSE="$1"
PENDING_REVIEWS=".claude/.pending_reviews"

# 実装完了を検出
if echo "$RESPONSE" | grep -qiE "(実装完了|implementation complete|コーディング完了|coding done)"; then
    if [ -f "$PENDING_REVIEWS" ] && [ -s "$PENDING_REVIEWS" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔍 品質保証部からの自動提案"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "実装が完了しました。"
        echo "以下のファイルのレビューが必要です:"
        echo ""
        cat "$PENDING_REVIEWS" | while read file; do
            echo "  📄 $file"
        done
        echo ""
        echo "推奨アクション:"
        echo "  1. /code-review - コードレビュー実施"
        echo "  2. /test-create - テストケース作成"
        echo "  3. /test-execute - テスト実行"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
fi

# テスト完了を検出
if echo "$RESPONSE" | grep -qiE "(テスト完了|test complete|all tests pass)"; then
    echo ""
    echo "✅ 品質保証完了チェックリスト:"
    echo "  □ コードレビュー実施済み"
    echo "  □ セキュリティスキャン完了"
    echo "  □ パフォーマンステスト完了"
    echo "  □ ドキュメント更新済み"
    echo ""
    
    # レビュー済みファイルをクリア
    > "$PENDING_REVIEWS"
    echo ".review_status" > ".claude/.review_status"
    echo "completed" >> ".claude/.review_status"
fi

# エラー検出時の自動サポート
if echo "$RESPONSE" | grep -qiE "(error|エラー|failed|失敗|exception)"; then
    echo ""
    echo "💡 トラブルシューティングのヒント:"
    echo "  • エラーログを確認: tail -f .claude/logs/error.log"
    echo "  • 最近の変更を確認: git diff HEAD~1"
    echo "  • バックアップから復元: ls .claude/.backups/"
    echo ""
fi