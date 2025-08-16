# 環境変数設定ガイド

## .envファイルの設定方法

このディレクトリには`.env`ファイルを配置して、MCPツールのAPIキーを管理します。

### 1. .envファイルの作成
`.claude_sub_agent/.env`ファイルが既に作成されています。

### 2. APIキーの設定

#### OpenAI API Key (o3 MCP用)
1. OpenAIのダッシュボードにアクセス
2. APIキーを生成またはコピー
3. `.env`ファイルの`OPENAI_API_KEY=`の後に貼り付け

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### 3. MCPツールの再登録（APIキーを更新した場合）

```bash
# 既存の登録を削除
claude mcp remove o3

# 新しいAPIキーで再登録
claude mcp add o3 -s user \
  -e OPENAI_API_KEY=your_actual_api_key_here \
  -e SEARCH_CONTEXT_SIZE=medium \
  -e REASONING_EFFORT=medium \
  -- npx o3-search-mcp

# 確認
claude mcp list
```

### セキュリティ注意事項
- `.env`ファイルは`.gitignore`に登録済みのため、GitHubにはアップロードされません
- APIキーは絶対に公開リポジトリにコミットしないでください
- 定期的にAPIキーをローテーションすることを推奨します