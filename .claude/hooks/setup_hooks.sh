#!/bin/bash
# Claude Code Hooks セットアップスクリプト

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Claude Code Hooks セットアップ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HOOKS_DIR="$(dirname "$0")"
CLAUDE_CONFIG_DIR="$HOME/.config/claude-code"

# 実行権限付与
echo "📝 実行権限を設定中..."
chmod +x "$HOOKS_DIR"/*.sh

# 設定ディレクトリ作成
mkdir -p "$CLAUDE_CONFIG_DIR"

# settings.json作成/更新
SETTINGS_FILE="$CLAUDE_CONFIG_DIR/settings.json"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "📄 settings.json を作成中..."
    cat > "$SETTINGS_FILE" << 'EOF'
{
  "hooks": {
    "user-prompt-submit-hook": "~/.claude/hooks/on_prompt.sh",
    "tool-use-hook": "~/.claude/hooks/on_tool.sh",
    "response-hook": "~/.claude/hooks/on_response.sh"
  },
  "quality": {
    "auto-review": true,
    "review-threshold": 80,
    "block-on-failure": false
  },
  "backup": {
    "enabled": true,
    "retention-days": 7
  }
}
EOF
else
    echo "⚠️  settings.json は既に存在します"
    echo "    手動で hooks セクションを追加してください"
fi

# 環境変数設定スクリプト作成
ENV_SCRIPT="$HOME/.claude_code_hooks"
echo "🔧 環境変数設定を作成中..."
cat > "$ENV_SCRIPT" << 'EOF'
# Claude Code Hooks 環境変数
export CLAUDE_CODE_HOOK_USER_PROMPT="$HOME/.claude/hooks/on_prompt.sh"
export CLAUDE_CODE_HOOK_TOOL_USE="$HOME/.claude/hooks/on_tool.sh"
export CLAUDE_CODE_HOOK_RESPONSE="$HOME/.claude/hooks/on_response.sh"

# 品質設定
export CLAUDE_CODE_AUTO_REVIEW="true"
export CLAUDE_CODE_REVIEW_THRESHOLD="80"

# バックアップ設定
export CLAUDE_CODE_BACKUP_ENABLED="true"
export CLAUDE_CODE_BACKUP_RETENTION="7"
EOF

# .bashrc/.zshrc に追加
if [ -f "$HOME/.bashrc" ]; then
    if ! grep -q "claude_code_hooks" "$HOME/.bashrc"; then
        echo "" >> "$HOME/.bashrc"
        echo "# Claude Code Hooks" >> "$HOME/.bashrc"
        echo "[ -f ~/.claude_code_hooks ] && source ~/.claude_code_hooks" >> "$HOME/.bashrc"
        echo "✅ .bashrc に設定を追加しました"
    fi
fi

if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "claude_code_hooks" "$HOME/.zshrc"; then
        echo "" >> "$HOME/.zshrc"
        echo "# Claude Code Hooks" >> "$HOME/.zshrc"
        echo "[ -f ~/.claude_code_hooks ] && source ~/.claude_code_hooks" >> "$HOME/.zshrc"
        echo "✅ .zshrc に設定を追加しました"
    fi
fi

# 必要なディレクトリ作成
echo "📁 作業ディレクトリを作成中..."
mkdir -p "$HOME/.claude/.backups"
mkdir -p "$HOME/.claude/.stats"
mkdir -p "$HOME/.claude/logs"

# 初期ファイル作成
touch "$HOME/.claude/.pending_reviews"
touch "$HOME/.claude/.review_status"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ セットアップ完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 次のステップ:"
echo "  1. ターミナルを再起動するか、以下を実行:"
echo "     source ~/.claude_code_hooks"
echo ""
echo "  2. 設定を確認:"
echo "     echo \$CLAUDE_CODE_HOOK_USER_PROMPT"
echo ""
echo "  3. テスト実行:"
echo "     $HOOKS_DIR/on_prompt.sh 'test implementation'"
echo ""
echo "💡 ヒント:"
echo "  • ログ確認: tail -f ~/.claude/logs/*.log"
echo "  • 統計確認: cat ~/.claude/.stats/tool_usage.log"
echo "  • レビュー待ち: cat ~/.claude/.pending_reviews"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"