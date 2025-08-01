# .NET Framework 4.0 Windows Forms デスクトップアプリケーション

## 🎯 プロジェクト概要

.NET Framework 4.0に特化したWindows Formsデスクトップアプリケーション開発プロジェクトです。Windows XP SP3、Windows Server 2003 R2以降の環境をサポートし、レガシーシステムとの高い互換性を維持しながら、モダンなアーキテクチャパターンを適用します。

### 主要特徴

- **Windows XP/2003完全対応** - 企業の既存環境での安定稼働
- **.NET Framework 4.0最適化** - async/await非対応環境での非同期処理実装
- **Clean Architecture** - MVP + Repository + DI パターン
- **レガシーシステム統合** - COM+、ActiveDirectory、既存DB連携
- **マルチAI協調開発** - Claude Code + Gemini CLI + o3 MCPによる高品質実装

## 🚀 クイックスタート

### 前提条件
- Windows XP SP3 以降 / Windows Server 2003 R2 以降
- .NET Framework 4.0
- Visual Studio 2010 以降

### セットアップ
```bash
# プロジェクトディレクトリへ移動
cd .claude_dotnetFramework4.0

# Claude Codeで開始
claude .

# 開発フロー開始
/spec multiAI
```

## 📋 カスタムコマンド (18個)

### Claude Code コマンド (12個)
- `/spec` - 統合開発フロー管理
- `/requirements` - 要件定義書生成
- `/design` - 技術設計書作成
- `/tasks` - タスク分割・管理
- `/analyze` - プロジェクト分析
- `/enhance` - 機能追加・改善
- `/fix` - バグ修正
- `/refactor` - リファクタリング
- `/document` - ドキュメント生成
- `/standardize` - コード標準化
- `/winforms-patterns` - Windows Forms設計パターン
- `/legacy-integration` - レガシーシステム統合

### Gemini CLI コマンド (3個)
- `/research` - 市場分析・ユーザー調査
- `/content-strategy` - ブランディング・UX戦略
- `/product-plan` - ロードマップ策定

### o3 MCP コマンド (3個)
- `/architecture` - システムアーキテクチャ設計
- `/devops` - CI/CD・デプロイ自動化
- `/security` - セキュリティ設計・監査

## 🏗️ プロジェクト構造

```
.claude_dotnetFramework4.0/
├── src/                           # ソースコード
│   ├── BusinessManagementApp.sln  # ソリューションファイル
│   ├── BusinessManagementApp/     # メインアプリケーション
│   ├── BusinessManagementApp.Core/# ビジネスロジック
│   ├── BusinessManagementApp.Data/# データアクセス層
│   └── BusinessManagementApp.Tests/# テストプロジェクト
├── commands/                      # カスタムコマンド
├── docs/                         # プロジェクトドキュメント
└── deployment/                   # デプロイメント設定
```

## 💻 技術スタック

### フレームワーク・ライブラリ
- **.NET Framework 4.0** (C# 4.0)
- **Windows Forms** - UIフレームワーク
- **Unity Container 2.1** - 依存性注入
- **Entity Framework 5.0** - O/Rマッピング
- **log4net 2.0.3** - ロギング
- **Newtonsoft.Json 6.0.8** - JSON処理

### アーキテクチャパターン
- **MVP (Model-View-Presenter)** - UIアーキテクチャ
- **Repository Pattern** - データアクセス抽象化
- **Unit of Work** - トランザクション管理
- **Factory Pattern** - オブジェクト生成
- **Observer Pattern** - イベント駆動

## 🔧 .NET Framework 4.0 制限事項と対応

### 主要な制限
| 機能 | .NET 4.5以降 | .NET 4.0での代替 |
|------|--------------|------------------|
| 非同期処理 | async/await | BackgroundWorker, Task.Factory |
| HTTP通信 | HttpClient | WebClient, HttpWebRequest |
| 属性 | CallerMemberName | 手動指定, StackTrace |
| タスク実行 | Task.Run | ThreadPool.QueueUserWorkItem |
| NuGet | 自動復元 | packages.config手動管理 |

### 利点
- Windows XP SP3 サポート
- Windows Server 2003 R2 サポート
- 小さいランタイム (約48MB)
- レガシーシステムとの高い互換性
- 既存企業環境での簡単デプロイ

## 📊 パフォーマンス・品質指標

- **起動時間**: 2秒以内 (Windows XP環境)
- **メモリ使用量**: 100MB以下 (基本動作時)
- **応答時間**: 100ms以内 (UI操作)
- **コードカバレッジ**: 80%以上
- **静的解析**: FxCop違反ゼロ

## 🛡️ セキュリティ対策

- Windows認証 / カスタム認証
- データ暗号化 (AES 256bit)
- 通信暗号化 (TLS 1.0)
- SQLインジェクション対策
- 監査ログ・操作履歴

## 📦 デプロイメント

### 配布方法
1. **ClickOnce** - 自動更新対応
2. **MSI インストーラー** - 企業環境向け
3. **XCopy デプロイ** - 手動配布
4. **SCCM/WSUS** - 企業一括配布

### 対応環境
- Windows XP SP3 (x86/x64)
- Windows Server 2003 R2 SP2
- Windows Vista / 7 / 8 / 8.1 / 10 / 11
- Windows Server 2008 / 2012 / 2016 / 2019 / 2022

## 📚 ドキュメント

- [プロジェクトコンセプト](00_project/01_project_concept.md)
- [技術スタックガイドライン](00_project/02_tech_stack_guidelines.md)
- [アーキテクチャ設計](01_development_docs/01_architecture_design.md)
- [Windows XP/2003デプロイメントガイド](03_library_docs/08_windows_xp_2003_deployment_guide.md)
- [.NET 4.0制限事項と回避策](03_library_docs/09_dotnet40_limitations_guide.md)

## 🤝 サポート

- **技術サポート**: マルチAI統合技術サポート
- **コミュニティ**: エンタープライズ.NET開発者フォーラム
- **ドキュメント**: 包括的開発ガイド・ベストプラクティス

---

**🚀 Next Step**: `/spec multiAI` コマンドでマルチAI協調開発を開始