# CLAUDE.md - .NET Framework 4.8 Windows Forms エンタープライズシステム仕様書駆動開発

このファイルは、Claude Code がこの.NET Framework 4.8 Windows Forms エンタープライズ向け統合管理システムで作業する際のガイダンスを提供します。

## プロジェクト概要

.NET Framework 4.8 と Windows Forms を使用したエンタープライズ向け統合業務管理システムの開発プロジェクトです。マルチAI協調による仕様書駆動開発により、品質と保守性を重視したマルチプロジェクトソリューション構造を構築し、既存システムとの統合を実現します。

## 技術スタック

### 開発フレームワーク
- **フレームワーク**: .NET Framework 4.8 (長期サポート)
- **UI フレームワーク**: Windows Forms
- **開発環境**: Visual Studio 2022
- **言語**: C# 7.3
- **データアクセス**: ADO.NET / Entity Framework 6
- **依存性注入**: Unity Container / Simple Injector

### アーキテクチャ
- **構造**: マルチプロジェクトソリューション
- **設計パターン**: Clean Architecture + Repository Pattern
- **コーディング原則**: YAGNI, DRY, KISS
- **ログ**: NLog / log4net
- **設定管理**: JSON / XML Configuration

### 既存システム統合
- **データベース**: SQL Server / Oracle / AS/400連携
- **ファイル連携**: 固定長ファイル / CSV / XML
- **API連携**: SOAP / REST API
- **レガシー統合**: COM+ / Windows Service
- **バッチ処理**: Windows タスクスケジューラ統合

## アーキテクチャ原則

### ソリューション構造
```
YourEnterpriseSystem\
├── Core\                        # ビジネスロジック層
│   ├── Domain\                  # ドメインモデル
│   ├── Services\               # ドメインサービス
│   └── Interfaces\             # リポジトリインターフェース
├── Infrastructure\              # インフラストラクチャ層
│   ├── Data\                   # データアクセス実装
│   ├── ExternalServices\       # 外部サービス統合
│   └── FileProcessing\         # ファイル処理
├── Application\                 # アプリケーション層
│   ├── Services\               # アプリケーションサービス
│   ├── DTOs\                   # データ転送オブジェクト
│   └── Mappers\                # オブジェクトマッピング
├── Presentation\                # プレゼンテーション層
│   ├── MainForm\               # メインアプリケーション
│   ├── SubModules\             # サブモジュール
│   └── Common\                 # 共通UI部品
├── CrossCutting\               # 横断的関心事
│   ├── Logging\                # ロギング
│   ├── Configuration\          # 設定管理
│   ├── Security\               # セキュリティ
│   └── Utilities\              # ユーティリティ
└── Tests\                      # テストプロジェクト
    ├── UnitTests\              # 単体テスト
    └── IntegrationTests\       # 統合テスト
```

### 設計パターン
1. **Clean Architecture**: ビジネスロジックの独立性確保
2. **Repository Pattern**: データアクセスの抽象化
3. **Service Layer Pattern**: ビジネスロジックの集約
4. **Factory Pattern**: オブジェクト生成の統一
5. **Strategy Pattern**: アルゴリズムの切り替え

## エンタープライズドメイン知識

### 主要業務領域
1. **データ統合管理**: マルチソースデータ統合、ETL処理、データ変換
2. **業務プロセス自動化**: ワークフロー管理、バッチ処理、スケジューリング
3. **ドキュメント処理**: OCR連携、帳票生成、PDF処理、電子署名
4. **既存システム連携**: レガシーDB接続、ファイル連携、API統合
5. **セキュリティ管理**: Active Directory連携、権限管理、監査ログ

### 規制・コンプライアンス要件
- **内部統制**: J-SOX対応、監査証跡の記録
- **個人情報保護**: 個人情報保護法準拠、アクセス制御
- **データ保全**: バックアップ、アーカイブ、災害復旧
- **セキュリティ**: Windows セキュリティポリシー準拠
- **既存システム互換性**: レガシーシステムとのデータ整合性

## 開発ワークフロー - 仕様書駆動開発

### 4段階ワークフロー
1. **要件定義** (`/requirements`) - エンタープライズ要件の明確化
2. **設計** (`/design`) - .NET Framework設計・UI設計
3. **タスク分割** (`/tasks`) - 実装可能な単位への分解
4. **実装** - マルチAI協調による実装

### ワークフローコマンド
- `/spec` - 完全な仕様書駆動開発ワークフローを開始
- `/requirements` - エンタープライズ要件定義のみ実行
- `/design` - 技術設計フェーズのみ実行
- `/tasks` - タスク分割のみ実行

## 開発ルール

### .NET Framework 開発ルール
- **命名規則**: Microsoft C#コーディング規約準拠
- **例外処理**: try-catch-finallyの適切な使用
- **リソース管理**: using文によるリソース解放
- **非同期処理**: async/awaitパターンの活用（.NET 4.5+）
- **null安全**: null条件演算子の活用

### Windows Forms 開発ルール
- **UIスレッド**: UIの更新は必ずUIスレッドで実行
- **データバインディング**: BindingSourceの活用
- **イベント処理**: イベントハンドラの適切な登録・解除
- **レスポンシブUI**: BackgroundWorkerまたはTaskの使用
- **ユーザビリティ**: Tabオーダー、ショートカットキーの設定

### データベース設計ルール
- **正規化**: 第3正規形を基本とする
- **インデックス**: パフォーマンスを考慮した設計
- **ストアドプロシージャ**: 複雑なビジネスロジックの実装
- **トランザクション**: TransactionScopeの適切な使用
- **接続管理**: 接続プーリングの活用

### セキュリティルール
- **認証**: Windows認証 / フォーム認証
- **認可**: ロールベースアクセス制御
- **暗号化**: 機密データの暗号化保存
- **SQLインジェクション対策**: パラメータクエリの使用
- **監査ログ**: 全操作の記録・追跡可能性

## 品質保証

### テスト戦略
- **単体テスト**: MSTest / NUnit / xUnit
- **UIテスト**: Coded UI Test / Windows Application Driver
- **統合テスト**: データベース接続を含むテスト
- **パフォーマンステスト**: 大量データ処理の検証

### コード品質
- **静的解析**: FxCop / StyleCop / SonarQube
- **コードカバレッジ**: 80%以上の目標
- **コードレビュー**: Pull Request必須
- **リファクタリング**: 定期的な技術的負債の解消

## 重要な設計上の決定

1. **.NET Framework 4.8選択理由**: 長期サポート、既存システム互換性
2. **Windows Forms採用**: エンタープライズデスクトップアプリの実績
3. **Clean Architecture**: ビジネスロジックのテスタビリティ確保
4. **マルチプロジェクト構造**: 機能の独立性と再利用性
5. **既存システム統合重視**: レガシーシステムとの共存

## よくある落とし穴

1. **メモリリーク**: イベントハンドラの解除忘れ
2. **UIフリーズ**: 長時間処理のUIスレッド実行
3. **接続リーク**: データベース接続の未解放
4. **例外の握りつぶし**: catch句での例外無視
5. **ハードコーディング**: 設定値の直接記述

## コーディング原則（参考プロジェクトより）

### YAGNI (You Ain't Gonna Need It)
- 現在必要な機能だけを実装する
- 将来使うかもしれない機能の事前実装を避ける
- 過度な抽象化や汎用化を避ける

### DRY (Don't Repeat Yourself)
- 重複コードは必ず関数化・モジュール化する
- 設定値は一箇所で管理する
- 同じロジックが複数箇所にある場合は共通ライブラリに移動する

### KISS (Keep It Simple, Stupid)
- 複雑な解決策より単純な解決策を優先
- 読みやすく理解しやすいコードを書く
- 過度な最適化を避け、まず動くものを作る

## マルチAIチーム構成

### チームメンバー構成

#### Claude Code チーム（実装・品質保証）
- **.NETエンジニア**: Windows Forms開発の中核を担当
  - UIデザイナー（画面設計）
  - ビジネスロジック開発者（サービス実装）
  - データアクセス開発者（リポジトリ実装）
  - QAエンジニア（テスト・品質保証）

#### Gemini CLI チーム（分析・戦略）
- **エンタープライズドメインエキスパート**:
  - 専門領域: エンタープライズ業務分析・プロセス最適化
  - 強み: 大規模データ処理、業務フロー分析、UI/UX設計
  - 主要活用: 要件分析、画面設計、ユーザビリティ評価

#### o3 MCP チーム（インフラ・運用・データベース）
- **データベーススペシャリスト**:
  - 専門領域: SQL Server / Oracle最適化・既存DB統合
  - 強み: レガシーDB連携、パフォーマンスチューニング
  - 主要活用: DB設計、クエリ最適化、データ移行
  
- **インフラエンジニア**:
  - 専門領域: Windows Server、Active Directory、既存システム統合
  - 強み: レガシーシステム連携、セキュリティ設定
  - 主要活用: デプロイメント、権限管理、システム監視

## Windows Forms 特有の開発指針

### 🚨 重要：Designer.cs および .resx ファイルの取り扱い

**絶対的なルール：**
- **`.Designer.cs` ファイルは絶対に直接編集しない**
- **`.resx` ファイルは絶対に直接編集しない**
- これらのファイルはVisual Studioのデザイナーが自動生成・管理するため、手動編集するとフォームが壊れる可能性があります

### UI実装の正しいアプローチ

AIはユーザーに以下のような**指示形式**でUI実装をガイドします：

```markdown
## フォーム実装手順

1. **Visual Studioでフォームデザイナーを開く**
   - ソリューションエクスプローラーで `CustomerForm.cs` をダブルクリック

2. **コントロールの配置**
   - ツールボックスから `DataGridView` をフォームにドラッグ＆ドロップ
   - 名前を `customerDataGridView` に変更
   - Dock プロパティを `Fill` に設定

3. **プロパティの設定**
   - プロパティウィンドウで以下を設定：
     - AllowUserToAddRows: False
     - SelectionMode: FullRowSelect
     - MultiSelect: False
     - ReadOnly: True

4. **イベントハンドラの追加**
   - DataGridViewをダブルクリックして CellClick イベントハンドラを生成
   - または、プロパティウィンドウのイベントタブから追加
```

### コードビハインドでの実装例
```csharp
// CustomerForm.cs での実装（Designer.csではない）
public partial class CustomerForm : Form
{
    // Designer.csで自動生成されたコントロールを使用
    private void CustomerForm_Load(object sender, EventArgs e)
    {
        // プログラムでプロパティを設定する場合
        customerDataGridView.AutoGenerateColumns = false;
        
        // カラムの追加はコードで行う
        customerDataGridView.Columns.Add(new DataGridViewTextBoxColumn
        {
            Name = "CustomerIdColumn",
            HeaderText = "顧客ID",
            DataPropertyName = "CustomerId",
            Width = 100
        });
    }
}
```

### UIデザインパターン
```csharp
// MVP (Model-View-Presenter) パターンの例
public interface IMainView
{
    string StatusText { get; set; }
    event EventHandler ProcessButtonClicked;
    void ShowProgress(int percentage);
}

public class MainPresenter
{
    private readonly IMainView _view;
    private readonly IBusinessService _service;
    
    public MainPresenter(IMainView view, IBusinessService service)
    {
        _view = view;
        _service = service;
        _view.ProcessButtonClicked += OnProcessButtonClicked;
    }
}
```

### 非同期処理パターン
```csharp
// BackgroundWorkerを使った非同期処理
private async void ProcessButton_Click(object sender, EventArgs e)
{
    processButton.Enabled = false;
    progressBar.Visible = true;
    
    try
    {
        await Task.Run(() => 
        {
            // 長時間処理
            for (int i = 0; i <= 100; i++)
            {
                Thread.Sleep(50);
                // UIスレッドで進捗更新
                this.Invoke((Action)(() => progressBar.Value = i));
            }
        });
        
        MessageBox.Show("処理が完了しました。", "完了", 
            MessageBoxButtons.OK, MessageBoxIcon.Information);
    }
    catch (Exception ex)
    {
        MessageBox.Show($"エラーが発生しました: {ex.Message}", "エラー", 
            MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
    finally
    {
        processButton.Enabled = true;
        progressBar.Visible = false;
    }
}
```

### データバインディングパターン
```csharp
// BindingSourceを使ったデータバインディング
public partial class CustomerForm : Form
{
    private BindingSource customerBindingSource;
    
    private void LoadCustomers()
    {
        var customers = _customerService.GetAllCustomers();
        customerBindingSource.DataSource = customers;
        dataGridView.DataSource = customerBindingSource;
        
        // テキストボックスへのバインディング
        nameTextBox.DataBindings.Add("Text", customerBindingSource, "Name");
        emailTextBox.DataBindings.Add("Text", customerBindingSource, "Email");
    }
}
```

このCLAUDE.mdを基盤として、マルチAI協調による高品質な.NET Framework 4.8 Windows Formsエンタープライズシステム開発を進めてください。