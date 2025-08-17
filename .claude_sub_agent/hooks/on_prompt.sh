#!/bin/bash
# Claude Code Hook: ユーザー入力時の自動チェック

# 実装関連のキーワードを検出
if echo "$1" | grep -qiE "(implement|実装|coding|コーディング|/spec implement)"; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  品質保証部からの通知"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "実装作業が検出されました。"
    echo "実装完了後は必ずコードレビューを実施してください。"
    echo ""
    echo "📋 品質チェックリスト:"
    echo "  □ コードレビュー実施"
    echo "  □ セキュリティチェック"
    echo "  □ パフォーマンス確認"
    echo "  □ テストカバレッジ確認"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# テスト実行前のレビューチェック
if echo "$1" | grep -qiE "(test|テスト|pytest|npm test|dotnet test)"; then
    REVIEW_STATUS=".claude_sub_agent/.review_status"
    
    if [ ! -f "$REVIEW_STATUS" ] || [ "$(cat $REVIEW_STATUS 2>/dev/null)" != "completed" ]; then
        echo ""
        echo "❌ 警告: コードレビューが未完了です"
        echo "テスト実行前に必ずコードレビューを実施してください。"
        echo "実行コマンド: /code-review"
        echo ""
    fi
fi

# プロジェクト完了時のチェック
if echo "$1" | grep -qiE "(完了|complete|finish|done|merge|push)"; then
    echo ""
    echo "✅ プロジェクト完了前チェックリスト:"
    echo "  • コードレビュー完了"
    echo "  • テスト実行完了"
    echo "  • ドキュメント更新"
    echo "  • 品質基準達成"
    echo ""
fi