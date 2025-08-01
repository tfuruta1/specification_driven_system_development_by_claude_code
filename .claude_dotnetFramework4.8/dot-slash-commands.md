# .NET Framework 4.8 カスタムコマンド

このファイルは、Claudeが.NET Framework 4.8プロジェクトで使用できるカスタムコマンドを定義します。

## /spec - 仕様書駆動開発を開始
フルワークフローで仕様書駆動開発を実行します。
要件定義→設計→タスク分割→実装提案の順で進めます。

## /requirements - 要件定義フェーズ
企業要件を明確化し、ビジネスルールを文書化します。
出力: 00_requirements.md

## /design - 設計フェーズ
.NET Framework 4.8とWindows Formsでのアーキテクチャ設計を行います。
出力: 01_design.md

## /tasks - タスク分割フェーズ
実装タスクを管理可能な単位に分割します。
出力: 02_tasks.md

## /winforms-design - Windows Forms UI設計
Windows Formsの画面設計とUIフロー設計を行います。
- フォームレイアウト設計
- データバインディング設計
- イベントハンドリング設計
出力: 03_winforms_ui_design.md

## /database-design - データベース設計
SQL ServerまたはOracleでのデータベース設計を行います。
- ER図
- テーブル定義
- インデックス設計
- ストアドプロシージャ設計
出力: 04_database_design.md

## /security-design - セキュリティ設計
エンタープライズセキュリティ要件の設計を行います。
- 認証・認可設計
- データ暗号化設計
- 監査ログ設計
出力: 05_security_design.md

## /integration-design - 既存システム統合設計
レガシーシステムとの統合設計を行います。
- API連携設計
- ファイル連携設計
- データ同期設計
出力: 06_integration_design.md

## /entity-design - Entity Framework設計
Entity Framework 6のCode First設計を行います。
- エンティティクラス設計
- DbContext設計
- Migration戦略
出力: 07_entity_framework_design.md

## /di-setup - 依存性注入セットアップ
Unity ContainerまたはSimple Injectorの設定を行います。
- DIコンテナ設定
- サービス登録
- ライフサイクル管理
出力: 08_dependency_injection_setup.md

## /logging-setup - ロギングセットアップ
NLogまたはlog4netの設定を行います。
- ログレベル設定
- ログ出力先設定
- ログローテーション設定
出力: 09_logging_setup.md

## /deployment-plan - デプロイメント計画
エンタープライズ環境へのデプロイメント計画を作成します。
- ClickOnce設定
- MSI作成
- 更新戦略
出力: 10_deployment_plan.md

## /ci-setup - CI/CDパイプライン設定
継続的インテグレーション/デプロイメント環境を設定します。
- Azure DevOps Pipeline設定
- GitHub Actions設定
- Jenkins Pipeline設定
- ビルドエージェント要件
- 環境別デプロイメント設定
出力: CI/CD設定ファイル（azure-pipelines.yml、.github/workflows/ci-cd.yml、Jenkinsfile）

## /ci-guide - CI/CDガイド
CI/CD（継続的インテグレーション/デプロイメント）の詳細ガイドを提供します。
- DevOpsパイプライン構成
- ビルドサーバー設定
- Azure DevOps完全設定（マルチステージパイプライン）
- GitHub Actions詳細設定
- Jenkins Pipeline詳細設定
- ビルドとテストの自動化スクリプト
- 環境固有の設定管理
- 監視とアラート（Application Insights）
参照: 03_library_docs/07_ci_cd_guide.md

## /test-strategy - テスト戦略
包括的なテスト戦略を定義します。
- 単体テスト（MSTest/NUnit）
- UIテスト（Coded UI）
- 統合テスト
- パフォーマンステスト
出力: 11_test_strategy.md

## /tdd-start - TDD開発を開始
テスト駆動開発のサイクルを開始します。
- Red: 失敗するテストを先に書く
- Green: テストを通す最小限のコード実装
- Refactor: コードをリファクタリング
- テストコードの例を提供
- モックオブジェクトの使用例
出力: 実装対象機能のテストコードと実装コード

## /tdd-guide - TDDガイド
TDD（テスト駆動開発）の詳細ガイドを提供します。
- TDD開発フローの基本（Red-Green-Refactor）
- テストフレームワーク（MSTest v2、NUnit、xUnit）
- モックフレームワーク（Moq、NSubstitute）
- TDD実践パターン（AAA、Given-When-Then）
- テストデータビルダー、オブジェクトマザー
- 統合テストの実装
- テストカバレッジとメトリクス
参照: 03_library_docs/06_tdd_testing_guide.md

## /code-standards - コーディング規約
.NET Frameworkのコーディング規約を定義します。
- 命名規則
- コード構造
- ベストプラクティス
出力: 12_coding_standards.md

## /performance-optimization - パフォーマンス最適化
Windows Formsアプリケーションのパフォーマンス最適化指針を作成します。
- UI応答性向上
- メモリ管理
- データベースクエリ最適化
出力: 13_performance_optimization.md

## /batch-design - バッチ処理設計
Windowsサービスやタスクスケジューラ連携のバッチ処理設計を行います。
- バッチアーキテクチャ
- エラーハンドリング
- スケジューリング設計
出力: 14_batch_processing_design.md

## /reporting-design - レポート設計
Crystal ReportsまたはRDLCでのレポート設計を行います。
- レポートテンプレート設計
- データソース設計
- 出力形式（PDF/Excel）
出力: 15_reporting_design.md

## /project-setup - プロジェクトセットアップ
新規.NET Framework 4.8プロジェクトのセットアップ手順を提供します。
- ソリューション構造作成
- プロジェクト参照設定
- NuGetパッケージ設定
出力: project_setup_guide.md

## /migration-guide - マイグレーションガイド
既存システムからの移行ガイドを作成します。
- データ移行戦略
- 機能移行計画
- 並行稼働計画
出力: migration_guide.md

## /troubleshooting - トラブルシューティング
よくある問題と解決方法をまとめます。
- ビルドエラー対処
- 実行時エラー対処
- パフォーマンス問題対処
出力: troubleshooting_guide.md

## /files-guide - .NETファイル構造ガイド
.NET Framework固有のファイルの説明と使い方を提供します。
- .sln（ソリューションファイル）の構造と管理
- .csproj（プロジェクトファイル）の詳細設定
- packages.config vs PackageReference
- App.config の詳細設定
- appsettings.json の活用（.NET Framework 4.8での使用）
- Program.cs のベストプラクティス
- AssemblyInfo.cs の設定
- ビルド関連ファイル（Directory.Build.props等）
参照: 03_library_docs/04_dotnet_file_structure_guide.md

## /nuget-guide - NuGetパッケージガイド
.NET Framework 4.8で使用可能な便利なNuGetパッケージの詳細ガイドを提供します。
- データアクセス（Entity Framework 6、Dapper）
- 依存性注入（Unity、Autofac）
- ロギング（NLog、Serilog）
- JSONシリアライゼーション（Newtonsoft.Json）
- マッピング（AutoMapper）
- バリデーション（FluentValidation）
- HTTPクライアント（RestSharp、Refit）
- テスティング（Moq、FluentAssertions）
- ユーティリティ（Polly、Humanizer）
- Windows Forms拡張（MetroModernUI、MaterialSkin）
- セキュリティ（IdentityModel）
- パッケージ管理のベストプラクティス
参照: 03_library_docs/05_nuget_packages_guide.md

## 使用例
```
# フルワークフローの実行
/spec ユーザー管理システムを作成したい

# Windows Forms画面設計のみ
/winforms-design 顧客検索画面

# データベース設計のみ
/database-design 在庫管理テーブル

# .NETファイル構造の説明
/files-guide

# NuGetパッケージガイド
/nuget-guide

# TDD開発を開始
/tdd-start CustomerService.CreateCustomer

# TDDガイドを表示
/tdd-guide

# CI/CDパイプライン設定
/ci-setup Azure DevOps

# CI/CDガイドを表示
/ci-guide

# プロジェクトセットアップ
/project-setup EnterpriseInventorySystem
```

## 注意事項
- すべてのコマンドは.NET Framework 4.8とWindows Formsに特化しています
- エンタープライズ要件（セキュリティ、監査、既存システム統合）を考慮します
- 生成されるコードはC# 7.3の機能範囲内で記述されます
- TDD（テスト駆動開発）を標準の開発手法として採用しています
- CI/CD（継続的インテグレーション/デプロイメント）環境の構築を推奨します
- 依存性注入（DI）が適切に設定されていることを前提としています