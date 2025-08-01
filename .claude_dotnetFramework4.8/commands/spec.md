# Spec Command - .NET Framework エンタープライズ統合仕様駆動開発

## 概要

エンタープライズ要件定義から実装まで、.NET Framework 4.8 Windows Forms エンタープライズシステムプロジェクトの全工程を段階的に進行する統合コマンドです。エンタープライズ特有の複雑な業務要求・レガシーシステム統合・セキュリティ要求に対応した体系的開発プロセスを実現します。

## 使用方法

```
/spec [フェーズ名]
```

### エンタープライズフェーズ一覧
- `init` - エンタープライズプロジェクト初期化（マルチAI協調）
- `enterprise_requirements` - エンタープライズ要件定義・業務分析
- `enterprise_design` - エンタープライズ技術設計・アーキテクチャ
- `winforms_design` - Windows Forms UI/UX設計
- `legacy_integration` - レガシーシステム統合設計
- `enterprise_tasks` - エンタープライズタスク分割・実装計画
- `enterprise_implement` - エンタープライズ実装開始・品質管理
- `status` - エンタープライズプロジェクト状態確認
- `multiAI` - エンタープライズマルチAI協調管理

## エンタープライズマルチAI連携統合フロー

各フェーズでエンタープライズ専門AIチームメンバーと連携し、エンタープライズドメイン知識・技術専門性・既存システム統合を活かした開発を実現します。

### エンタープライズ拡張フェーズ構成

```mermaid
graph TB
    subgraph "Phase 1: エンタープライズ分析・戦略 (Gemini CLI)"
        A1[/research - ビジネスプロセス分析・業務調査]
        A2[/content-strategy - エンタープライズUI/UX戦略]
        A3[/product-plan - エンタープライズプロダクト管理・要件管理]
    end
    
    subgraph "Phase 2: エンタープライズ設計・実装 (Claude Code)"
        B1[/requirements - エンタープライズ要件定義]
        B2[/design - エンタープライズ技術設計]
        B3[/winforms-design - Windows Forms UI設計]
        B4[/tasks - エンタープライズタスク分割]
        B5[Enterprise Implementation - エンタープライズ実装]
    end
    
    subgraph "Phase 3: エンタープライズインフラ・統合 (o3 MCP)"
        C1[/architecture - エンタープライズシステム設計]
        C2[/legacy-integration - レガシーシステム統合]
        C3[/deployment - エンタープライズデプロイメント]
        C4[/security - エンタープライズセキュリティ]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    C1 --> C2
    B2 --> B4
    B4 --> B5
    C2 --> C3
    C3 --> C4
```

## フェーズ詳細説明

### Phase 0: プロジェクト初期化 (`init`)
**目的**: .NET Framework エンタープライズプロジェクトの基盤構築とAI環境準備

**実行内容**:
1. Visual Studio ソリューション構造の生成
2. プロジェクトテンプレートの適用（Clean Architecture）
3. 基本的なNuGetパッケージの設定
4. マルチAI連携環境の初期化
5. 既存システム連携用インターフェース定義

**出力**:
- `.sln` ソリューションファイル
- プロジェクト構造（Core, Infrastructure, Presentation）
- `CLAUDE.md`, `README.md` の配置
- AI共有フォルダ構造の生成

### Phase 1: エンタープライズ要件定義 (`enterprise_requirements`)
**目的**: ビジネス要件の明確化とシステム境界の定義

**Gemini CLI連携**:
- ビジネスプロセス分析
- 既存システムとの統合ポイント特定
- ユーザーストーリーの作成
- 非機能要件の洗い出し

**出力**:
- `requirements/business_requirements.md`
- `requirements/integration_requirements.md`
- `requirements/security_requirements.md`
- `requirements/user_stories.md`

### Phase 2: エンタープライズ設計 (`enterprise_design`)
**目的**: システムアーキテクチャとデータモデルの設計

**Claude Code主導**:
- Clean Architecture 設計
- エンティティ・DTOモデル設計
- サービスインターフェース定義
- リポジトリパターン設計

**o3 MCP連携**:
- データベーススキーマ設計
- 既存DBとのマッピング定義
- パフォーマンス考慮事項

**出力**:
- `design/architecture.md`
- `design/domain_models.cs`
- `design/database_schema.sql`
- `design/integration_mapping.md`

### Phase 3: Windows Forms UI設計 (`winforms_design`)
**目的**: ユーザーインターフェースの設計とユーザビリティ確保

**Gemini CLI連携**:
- UI/UXベストプラクティス適用
- 画面遷移フロー設計
- アクセシビリティ考慮

**Claude Code実装**:
- フォームレイアウト設計
- カスタムコントロール定義
- データバインディング設計
- イベントハンドリング設計

**出力**:
- `design/ui_mockups/`
- `design/screen_flow.md`
- `design/ui_components.md`
- `design/data_binding_map.md`

### Phase 4: レガシーシステム統合 (`legacy_integration`)
**目的**: 既存システムとのシームレスな統合実現

**o3 MCP主導**:
- レガシーDB接続設定
- ファイルフォーマット変換
- バッチ処理インターフェース
- データ同期戦略

**出力**:
- `integration/legacy_db_mapping.md`
- `integration/file_format_specs.md`
- `integration/batch_interface.md`
- `integration/sync_strategy.md`

### Phase 5: タスク分割 (`enterprise_tasks`)
**目的**: 実装可能な単位への分解とスケジューリング

**TodoWrite統合**:
- エピック・ストーリー・タスクへの分解
- 優先順位付け
- 依存関係の明確化
- 工数見積もり

**出力**:
- `tasks/epic_list.md`
- `tasks/sprint_plan.md`
- `tasks/task_dependencies.md`
- TodoWriteへの自動登録

### Phase 6: 実装 (`enterprise_implement`)
**目的**: 品質を保ちながらの段階的実装

**実装順序**:
1. ドメインモデル・ビジネスロジック
2. データアクセス層
3. 外部サービス統合
4. Windows Forms UI
5. テスト実装

**品質管理**:
- コードレビューチェックリスト
- 単体テストカバレッジ
- 統合テスト実施
- パフォーマンステスト

## Windows Forms 特有の考慮事項

### UI スレッド管理
```csharp
// 非同期処理での UI 更新パターン
private async void LoadDataButton_Click(object sender, EventArgs e)
{
    loadingPanel.Visible = true;
    
    try
    {
        var data = await Task.Run(() => _dataService.LoadDataAsync());
        
        // UI スレッドでの更新
        this.Invoke((Action)(() =>
        {
            dataGridView.DataSource = data;
            statusLabel.Text = $"{data.Count} 件のデータを読み込みました。";
        }));
    }
    catch (Exception ex)
    {
        MessageBox.Show($"エラー: {ex.Message}", "エラー", 
            MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
    finally
    {
        loadingPanel.Visible = false;
    }
}
```

### データバインディング
```csharp
// BindingSource を使用した双方向バインディング
private void SetupDataBinding()
{
    // ビジネスオブジェクトのバインディング
    customerBindingSource.DataSource = _customers;
    
    // DataGridView へのバインディング
    customerDataGridView.DataSource = customerBindingSource;
    
    // 個別コントロールへのバインディング
    nameTextBox.DataBindings.Add("Text", customerBindingSource, "Name");
    emailTextBox.DataBindings.Add("Text", customerBindingSource, "Email");
    
    // 検証イベントの設定
    nameTextBox.Validating += ValidateRequiredField;
}
```

## マルチAI協調のベストプラクティス

### 1. フェーズ間の成果物共有
- 各フェーズの出力は次フェーズの入力として活用
- マークダウン形式での統一的なドキュメント管理
- コード生成時のインターフェース定義優先

### 2. 専門性の活用
- **Gemini CLI**: ビジネス分析、UI/UX設計
- **Claude Code**: .NET実装、Windows Forms開発
- **o3 MCP**: インフラ、DB、レガシー統合

### 3. 品質チェックポイント
- 各フェーズ完了時のレビュー実施
- 成果物の相互検証
- 継続的な改善フィードバック

## 実行例

### 新規プロジェクト開始
```bash
/spec init --name "EnterprisePaymentSystem" --template "clean-architecture"
/spec enterprise_requirements
/spec enterprise_design
/spec winforms_design
/spec legacy_integration
/spec enterprise_tasks
/spec enterprise_implement
```

### 既存プロジェクトへの適用
```bash
/spec status  # 現状確認
/spec legacy_integration --analyze-existing
/spec enterprise_tasks --from-existing
```

## エラーハンドリング

### よくあるエラーと対処法
1. **ソリューション構造エラー**: プロジェクト参照の確認
2. **NuGetパッケージ競合**: パッケージバージョンの統一
3. **レガシーDB接続エラー**: 接続文字列と権限の確認
4. **UI フリーズ**: 非同期処理の適切な実装

## まとめ

このコマンドにより、.NET Framework 4.8 Windows Forms を使用したエンタープライズシステム開発において、マルチAI協調による効率的かつ高品質な開発プロセスを実現します。既存システムとの統合を重視し、段階的な移行と共存を可能にする柔軟なアーキテクチャを構築します。