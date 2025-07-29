# 開発環境セットアップガイド - マルチAI協調対応

## 概要

このドキュメントでは、Vue.js + Supabase + マルチAI協調開発システムの開発環境をセットアップする手順を説明します。**Claude Code + Gemini CLI + o3 MCP**の3階AI連携システムを活用し、新しいメンバー（人間でもAIでも）が素早く協調開発を開始できるよう、必要なツールのインストールから環境設定まで、ステップバイステップで解説します。

### マルチAI協調開発システムの特徴
- **3階AI連携**: 各AIが専門分野で力を発揮し、相互連携で品質向上
- **データ駆動意思決定**: AI間データ共有で透明性と客観性を確保
- **継続改善**: AIフィードバックループで品質と効率の持続的向上
- **リスク分散**: 単一AIの限界を他AIが補完する安全性設計

## 前提条件

### 必須環境
- **OS**: Windows 10/11、macOS 10.15以上、Ubuntu 20.04以上
- **メモリ**: 8GB以上推奨（**マルチAI協調用は16GB強く推奨**）
- **ストレージ**: 15GB以上の空き容量（AIモデルと共有データ用）
- **ネットワーク**: 安定したインターネット接続（AI API通信用）

### AIシステム要件
- **Claude Code**: Anthropicアカウント（無料プラン可）
- **Gemini CLI**: Google AI Studio APIキー（無料枠あり）
- **OpenAI o3 MCP**: OpenAI Platform APIキー（有料、初回クレジットあり）

## 1. 基本開発ツールのインストール

### 1.1 Node.js環境
```bash
# Node.js v18.x LTS または v20.x LTS
# 公式サイト: https://nodejs.org/

# インストール確認
node --version  # v18.0.0以上
npm --version   # v9.0.0以上

# pnpm（推奨パッケージマネージャー）
npm install -g pnpm
pnpm --version  # v8.0.0以上
```

### 1.2 Git
```bash
# Git v2.30以上
# 公式サイト: https://git-scm.com/

# インストール確認
git --version

# グローバル設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.autocrlf input  # macOS/Linux
git config --global core.autocrlf true   # Windows
```

### 1.3 コードエディタ
```bash
# VS Code（推奨）
# 公式サイト: https://code.visualstudio.com/

# 必須拡張機能
- Vue Language Features (Volar)
- JavaScript Vue Plugin (Volar)
- ESLint
- Prettier - Code formatter
- Tailwind CSS IntelliSense
- Claude Code (AI開発支援)
```

## 2. マルチAI開発システムのセットアップ

### 2.1 Claude Code
```bash
# Claude Code CLIのインストール
# 公式サイト: https://claude.ai/code

# macOS/Linux
curl -fsSL https://claude.ai/install.sh | sh

# Windows (PowerShell管理者権限)
iwr -useb https://claude.ai/install.ps1 | iex

# 動作確認
claude --version
```

### 2.2 Gemini CLI
```bash
# Gemini CLIのインストール
npm install -g @google/gemini-cli

# 動作確認
gemini --version

# API認証設定
# 1. Google AI Studio (https://ai.google.dev/) でAPIキーを取得
# 2. 環境変数の設定
export GEMINI_API_KEY="your_gemini_api_key_here"

# Windows PowerShell
$env:GEMINI_API_KEY = "your_gemini_api_key_here"

# 永続化（.bashrc/.zshrc または .env ファイルに追加）
echo 'export GEMINI_API_KEY="your_gemini_api_key_here"' >> ~/.bashrc
```

### 2.3 OpenAI o3 MCP
```bash
# OpenAI SDKのインストール
npm install -g openai @openai/agents

# API認証設定
# 1. OpenAI Platform (https://platform.openai.com/) でAPIキーを取得
# 2. 環境変数の設定
export OPENAI_API_KEY="your_openai_api_key_here"

# Windows PowerShell
$env:OPENAI_API_KEY = "your_openai_api_key_here"

# 永続化
echo 'export OPENAI_API_KEY="your_openai_api_key_here"' >> ~/.bashrc
```

### 2.4 マルチAI協調確認・初期設定
```bash
# プロジェクトディレクトリで実行
claude .

# マルチAI連携テスト
/modeltest comprehensive

# 期待される結果:
# ✅ Claude Code: 正常稼働 (実装・品質保証担当)
# ✅ Gemini CLI: 正常稼働 (分析・戦略策定担当)
# ✅ OpenAI o3 MCP: 正常稼働 (インフラ・運用担当)
# ✅ AI協調データ交換: 正常動作
# ✅ 統合品質評価: 正常動作

# AI協調ワークスペースの初期化
/multiAI project_init --ai_priority="balanced" --scope="all"

# 共有データ領域の作成
mkdir -p .tmp/ai_shared_data/{gemini_analysis,claude_designs,o3_infrastructure}
mkdir -p .tmp/{integration_reports,collaboration_logs}
```

## 3. プロジェクトのセットアップ

### 3.1 リポジトリのクローン
```bash
# プロジェクトのクローン
git clone https://github.com/tfuruta1/specification_driven_system_development_by_claude_code.git
cd specification_driven_system_development_by_claude_code

# 依存関係のインストール
pnpm install
```

### 3.2 環境変数の設定
```bash
# .env.localファイルを作成
cp .env.example .env.local

# .env.localを編集
# エディタで開いて以下の値を設定
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_APP_URL=http://localhost:5173

# AI関連（既に設定済みの場合は省略可）
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 4. Supabase開発環境

### 4.1 Supabase CLIのインストール
```bash
# macOS (Homebrew)
brew install supabase/tap/supabase

# Windows (Scoop)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# その他のOS
npm install -g supabase

# 動作確認
supabase --version
```

### 4.2 ローカルSupabaseの起動
```bash
# Docker Desktopが必要（事前にインストール）
# https://www.docker.com/products/docker-desktop/

# Supabaseプロジェクトの初期化
supabase init

# ローカルデータベースの起動
supabase start

# 起動確認（以下のURLが表示される）
# Studio URL: http://localhost:54323
# API URL: http://localhost:54321
# DB URL: postgresql://postgres:postgres@localhost:54322/postgres
```

### 4.3 マイグレーションの実行
```bash
# 既存のマイグレーションを実行
supabase db reset

# 新しいマイグレーションの作成
supabase migration new create_users_table

# マイグレーションファイルを編集後、適用
supabase db push
```

## 5. 開発サーバーの起動

### 5.1 フロントエンド開発サーバー
```bash
# 開発サーバーの起動
pnpm dev

# ブラウザで開く
# http://localhost:5173

# その他のコマンド
pnpm build      # プロダクションビルド
pnpm preview    # ビルドのプレビュー
pnpm lint       # ESLintチェック
pnpm format     # Prettierフォーマット
pnpm type-check # JSDoc型チェック
```

### 5.2 開発ツールの確認
```bash
# Vue.js DevTools
# Chrome/Firefox拡張機能をインストール

# Supabase Studio
# http://localhost:54323 でデータベース管理UI

# ネットワークタブ
# Supabase APIリクエストの確認
```

## 6. IDEの設定

### 6.1 VS Code設定
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "js/ts.implicitProjectConfig.checkJs": true,
  "tailwindCSS.includeLanguages": {
    "vue": "html"
  },
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "emmet.triggerExpansionOnTab": true
}
```

### 6.2 推奨拡張機能
```json
// .vscode/extensions.json
{
  "recommendations": [
    "Vue.volar",
    "Vue.vscode-vue-plugin",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "antfu.iconify",
    "formulahendry.auto-rename-tag",
    "steoates.autoimport"
  ]
}
```

## 7. トラブルシューティング

### 7.1 よくある問題と解決方法

#### Node.jsバージョンの問題
```bash
# nvm（Node Version Manager）を使用
# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Windows (nvm-windows)
# https://github.com/coreybutler/nvm-windows
nvm install 18.19.0
nvm use 18.19.0
```

#### pnpm関連のエラー
```bash
# キャッシュのクリア
pnpm store prune

# node_modulesの再インストール
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### Supabase接続エラー
```bash
# ローカルSupabaseの再起動
supabase stop
supabase start

# ログの確認
supabase logs
```

#### AI認証エラー
```bash
# APIキーの確認
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY

# 環境変数の再読み込み
source ~/.bashrc  # または source ~/.zshrc
```

### 7.2 デバッグ設定
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Vue.js デバッグ",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src",
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    }
  ]
}
```

## 8. マルチAI協調開発の開始

### 8.1 AI協調ワークフローの開始
```bash
# マルチAI協調開発フローの開始
claude .

# 統合AI協調フロー (推奨)
/spec multiAI

# フェーズ別AI協調コマンド
/research            # Gemini CLI主導 - 市場・ユーザー分析
/content-strategy    # Gemini CLI主導 - コンテンツ戦略策定
/product-plan        # Gemini CLI主導 - プロダクト計画
/design              # Claude Code主導 - 技術設計
/implement           # Claude Code主導 - 実装・品質保証
/architecture        # o3 MCP主導 - システムアーキテクチャ
/devops              # o3 MCP主導 - CI/CD・運用自動化
/security            # o3 MCP主導 - セキュリティ設計

# AI協調管理コマンド
/multiAI cross_analysis      # 横断分析・多角的評価
/multiAI integrated_design   # 統合設計・整合性確認
/multiAI quality_assurance   # 統合品質保証・相互レビュー
```

### 8.2 AI協調効果のモニタリング
```bash
# AI協調効果の測定・可視化
/analyze collaboration_metrics

# 継続改善サイクルの実行
/multiAI continuous_improvement

# AI協調ログの分析
ls .tmp/collaboration_logs/
cat .tmp/integration_reports/latest_quality_assessment.md
```

### 8.3 マルチAI協調ドキュメントの参照
#### コアドキュメント
- [CLAUDE.md](../CLAUDE.md) - マルチAI協調ガイドライン
- [アーキテクチャ設計](./01_architecture_design.md) - マルチAI協調アーキテクチャ
- [プロジェクト概念](../00_project/01_project_concept.md) - マルチAIビジョン

#### 技術ドキュメント
- [フロントエンド設計](./11_frontend_design.md)
- [E2Eテスト設計](./12_e2e_test_design.md)
- [セキュリティ設計](./13_security_design.md)
- [パフォーマンス最適化](./14_performance_optimization.md)
- [パフォーマンス監視](./15_performance_monitoring.md)

### 8.4 コミュニティ・サポート
- GitHub Issues: バグ報告・機能要望
- Discord: リアルタイムサポート（予定）
- ドキュメント: 最新情報の確認

## まとめ

これで**マルチAI協調開発環境**のセットアップは完了です。**Claude Code + Gemini CLI + o3 MCP**の3階AI連携システムを活用して、今までにない高品質・高効率な協調開発を始めることができます。

### マルチAI協調開発のメリット
🤖 **専門性の結集**: 各AIが得意分野で最大限の力を発揮  
🔍 **品質の多重化**: 複数観点からのレビューで見落しを最小化  
📊 **データ駆動意思決定**: 客観的データに基づく透明性の高いプロセス  
♾️ **継続改善**: AIフィードバックループで絶え間ない品質向上  
🛡️ **リスク分散**: 単一障害点の排除で安定した開発品質  

問題が発生した場合は、トラブルシューティングセクションを参照するか、プロジェクトのIssuesで質問してください。

Happy Collaborative AI Development! 🚀🤖✨