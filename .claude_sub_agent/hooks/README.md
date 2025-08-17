# Claude Code Hooks - 自動レビューシステム

## 🚀 クイックスタート

### 1. セットアップ実行
```bash
cd .claude_sub_agent/hooks
chmod +x setup_hooks.sh
./setup_hooks.sh
```

### 2. 環境変数の有効化
```bash
source ~/.claude_code_hooks
```

### 3. 動作確認
```bash
# フック動作テスト
./on_prompt.sh "実装を開始します"
./on_tool.sh "Write" "test.js"
./on_response.sh "実装完了しました"
```

## 📋 フック一覧

| フック名 | トリガー | 機能 |
|---------|---------|------|
| **on_prompt.sh** | ユーザー入力時 | 実装/テストキーワード検出、レビュー提案 |
| **on_tool.sh** | ツール使用時 | ファイル編集の追跡、バックアップ作成 |
| **on_response.sh** | 応答生成時 | 実装完了検出、レビュー必要ファイル表示 |

## 🔧 カスタマイズ

### レビュー基準の変更
```bash
# ~/.config/claude-code/settings.json
{
  "quality": {
    "review-threshold": 90,  // より厳格に
    "block-on-failure": true  // レビュー失敗時ブロック
  }
}
```

### 通知レベルの調整
- **レベル1（通知）**: デフォルト設定
- **レベル2（警告）**: `block-on-failure: false`
- **レベル3（ブロック）**: `block-on-failure: true`

## 📊 統計情報

### レビュー待ちファイル確認
```bash
cat ~/.claude_sub_agent/.pending_reviews
```

### ツール使用履歴
```bash
tail -20 ~/.claude_sub_agent/.stats/tool_usage.log
```

### バックアップ確認
```bash
ls -la ~/.claude_sub_agent/.backups/
```

## 🔍 トラブルシューティング

### フックが動作しない
```bash
# 権限確認
ls -la ~/.claude_sub_agent/hooks/*.sh

# 環境変数確認
env | grep CLAUDE_CODE_HOOK

# ログ確認
tail -f ~/.claude_sub_agent/logs/hooks.log
```

### バックアップ容量の管理
```bash
# 7日以上前のバックアップを削除
find ~/.claude_sub_agent/.backups -mtime +7 -delete
```

## 💡 ベストプラクティス

1. **定期的なレビュー実施**
   - 実装完了時は必ず `/code-review` を実行
   - レビュー待ちファイルを放置しない

2. **バックアップ管理**
   - 重要な変更前は手動バックアップも作成
   - 定期的に古いバックアップを削除

3. **チーム運用**
   - チーム全員が同じ設定を使用
   - レビュー基準を文書化

## 🎯 期待効果

- **レビュー漏れ**: 0件（100%防止）
- **品質問題の早期発見**: 80%向上
- **自動化率**: 95%達成
- **開発効率**: 30%向上

## 📝 更新履歴

- **v1.0.0** (2025-08-17): 初期リリース
  - 基本的なフック機能実装
  - 自動バックアップ機能
  - レビュー追跡機能

---

*階層型エージェントシステム v8.3 - Claude Code Hooks統合*