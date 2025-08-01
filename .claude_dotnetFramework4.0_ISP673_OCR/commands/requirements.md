# /requirements - 要件定義書生成コマンド

**.NET Framework 4.0 デスクトップアプリ専用要件定義**

## 📋 コマンド概要

.NET Framework 4.0を使用したWindows Formsデスクトップアプリケーションの詳細な要件定義書を生成します。Windows XP/2003対応、レガシーシステム統合、企業環境特有の制約を考慮した包括的な仕様書を作成します。

## 🚀 使用方法

### 基本構文
```bash
/requirements "[project_description]" [options]
```

### 主要モード

#### 1. 業務管理システム
```bash
/requirements "顧客・売上・在庫管理システム" --type=business_management
```

#### 2. システム管理ツール
```bash
/requirements "サーバー監視・ログ解析ツール" --type=system_tool
```

#### 3. レガシー統合アプリ
```bash
/requirements "メインフレームデータ移行ツール" --type=legacy_integration
```

#### 4. データ処理アプリ
```bash
/requirements "Excelデータ変換・レポート生成" --type=data_processing
```

## 🎯 .NET Framework 4.0 特化要件

### 技術制約要件
```
● フレームワーク: .NET Framework 4.0 (ランタイムサイズ: 48MB)
● 言語: C# 4.0 (動的型、オプションパラメータのみ)
● UIフレームワーク: Windows Forms (メンテナンスモード)
● 非同期処理: BackgroundWorker / ThreadPool (✖️ async/await 使用不可)
● HTTP通信: WebClient / HttpWebRequest (✖️ HttpClient 使用不可)
● パッケージ管理: packages.config 手動管理 (✖️ 自動復元不可)
```

### 対応環境要件
```
● プライマリターゲット: Windows XP SP3 / Windows Server 2003 R2
● 推奨環境: Windows 7 SP1 / Windows Server 2008 R2 以降
● メモリ: 最低 512MB (推奨 1GB 以上)
● ストレージ: 最低 100MB (アプリ + ランタイム)
● ディスプレイ: 1024x768 以上 (スケーリング対応)
```

### 企業環境特有要件
```
● ドメイン認証: ActiveDirectory 統合認証
● グループポリシー: 企業セキュリティポリシー遵守
● ソフトウェア配布: ClickOnce / MSI インストーラー
● レガシー統合: COMコンポーネント・既存システム連携
● ネットワーク制約: ファイアウォール・プロキシサーバー対応
```

## 📊 要件定義テンプレート

### 1. プロジェクト概要
```markdown
# プロジェクト概要

## プロジェクト名
[Generated based on user input]

## 目的・背景
- 業務効率化のためのデスクトップアプリケーション開発
- レガシーシステムとの統合・データ移行
- Windows XP/2003 環境での安定稼働
- 企業セキュリティポリシー遵守

## ステークホルダー
- エンドユーザー: 企業の業務担当者
- IT管理者: システム管理・保守担当
- 経営陣: ROI追求・コスト削減要求
```

### 2. 機能要件 (.NET 4.0対応)
```markdown
# 機能要件

## コア機能
### F001. ユーザー認証
- **要件**: ActiveDirectory連携ドメイン認証
- **実装方式**: System.DirectoryServices (.NET 4.0対応)
- **フォールバック**: ローカル認証 (スタンドアロン環境)

### F002. データ管理
- **データベース**: SQL Server 2000/2005/2008 対応
- **ORM**: Entity Framework 4.0 (初期バージョン)
- **フォールバック**: ADO.NET 直接実装

### F003. レポート生成
- **フォーマット**: Excel (.xls/.xlsx)、PDF、CSV
- **実装**: Microsoft Office Interop (.NET 4.0対応)
- **プレビュー**: Windows Forms PrintPreviewControl
```

### 3. 非機能要件
```markdown
# 非機能要件

## パフォーマンス要件
- **起動時間**: 5秒以内 (Windows XP SP3 環境)
- **メモリ使用量**: 最大 256MB (アイドル時 64MB)
- **ファイルサイズ**: アプリケーション本体 50MB 以内
- **同時ユーザー**: 最大 100ユーザー (データベース同時アクセス)

## 信頼性要件
- **稼働率**: 99.5% (月内ダウンタイム 3.6時間以内)
- **エラーハンドリング**: 異常終了ゼロ、グレースフルデグラデーション
- **データ保全性**: 自動バックアップ、復旧機能

## セキュリティ要件
- **認証**: Windows統合認証 / ActiveDirectory
- **権限管理**: ロールベースアクセス制御 (RBAC)
- **データ暗号化**: AES 256bit (機密データ)
- **ログ管理**: 操作履歴、アクセスログ、エラーログ
```

### 4. 技術アーキテクチャ要件
```markdown
# 技術アーキテクチャ要件

## アーキテクチャパターン
- **UIアーキテクチャ**: MVP (Model-View-Presenter)
- **依存性注入**: Unity Container 2.1
- **データアクセス**: Repositoryパターン + Unit of Work
- **エラーハンドリング**: 一元化例外処理

## .NET Framework 4.0 制約対応
- **非同期処理**: BackgroundWorkerパターン
- **HTTP通信**: WebClient + HttpWebRequestパターン
- **スレッドセーフティ**: lock文 + ReaderWriterLockSlim
- **メモリ管理**: IDisposableパターン徹底

## パッケージ構成 (.NET 4.0対応)
```xml
<packages>
  <package id="Unity" version="2.1.505.0" targetFramework="net40" />
  <package id="EntityFramework" version="4.3.1" targetFramework="net40" />
  <package id="NUnit" version="2.6.4" targetFramework="net40" />
  <package id="log4net" version="1.2.15" targetFramework="net40" />
</packages>
```
```

## 🔧 詳細オプション

### 特定業界対応
```bash
/requirements "[description]" --industry=[industry_type]
```
**業界タイプ**:
- `manufacturing` - 製造業 (特殊機器連携、COM統合)
- `finance` - 金融業 (高セキュリティ、監査要件)
- `healthcare` - 医療業 (HIPAA準拠、個人情報保護)
- `retail` - 小売業 (POS連携、在庫管理)

### パフォーマンスレベル
```bash
/requirements "[description]" --performance=[level]
```
**レベル**:
- `basic` - 標準的なレスポンス性能
- `high` - 高パフォーマンス要求
- `real_time` - リアルタイム処理要求対応

### デプロイメントスコープ
```bash
/requirements "[description]" --deployment=[scope]
```
**スコープ**:
- `single_pc` - 単一PC環境
- `departmental` - 部署内ネットワーク
- `enterprise` - 全社統合システム

## 📊 品質保証要件

### テスト要件
```
● 単体テスト: カバレッジ 80% 以上
● 結合テスト: ユーザーシナリオベース
● UIテスト: White Frameworkによる自動化
● パフォーマンステスト: 負荷テスト・ストレステスト
● セキュリティテスト: ペネトレーションテスト
```

### ドキュメント要件
```
● ユーザーマニュアル: 操作手順書・トラブルシューティング
● 管理者ガイド: インストール・設定・バックアップ
● 開発者ドキュメント: API仕様書・設計書・コードコメント
● メンテナンスガイド: 更新手順・システム復旧手順
```

## 📝 生成ファイル

- `01_development_docs/requirements_specification.md` - 詳細要件定義書
- `01_development_docs/functional_requirements.md` - 機能要件一覧
- `01_development_docs/non_functional_requirements.md` - 非機能要件詳細
- `01_development_docs/technical_constraints.md` - .NET 4.0技術制約一覧
- `01_development_docs/deployment_requirements.md` - デプロイメント要件
- `00_project/user_stories.md` - ユーザーストーリー一覧

## 🔗 関連コマンド

- `/design` - 要件ベースの技術設計書作成
- `/tasks` - 要件をベースとしたタスク分割
- `/research` - 市場調査・競合調査ベースの要件分析
- `/analyze` - 要件分析・リスク評価
- `/winforms-patterns` - 要件ベースのUIパターン選定

---

**💡 重要**: .NET Framework 4.0の要件定義では、特にasync/await、HttpClientなどの新機能が使用できないことを明確に記載し、代替手段 (BackgroundWorker、WebClient) を明示することが重要です。