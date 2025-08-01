# Requirements Command - エンタープライズ要件定義

## 概要

エンタープライズシステムのビジネス要件と技術要件を体系的に定義し、既存システムとの統合ポイントを明確化するコマンドです。業務分析から非機能要件まで、包括的な要件定義を実現します。

## 使用方法

```
/requirements [オプション]
```

### オプション
- `--analyze` - 既存システム・業務プロセス分析
- `--business` - ビジネス要件定義
- `--technical` - 技術要件定義
- `--integration` - 既存システム統合要件
- `--security` - セキュリティ要件定義
- `--all` - 全要件定義プロセス実行（デフォルト）

## 実行フロー

### 1. 既存システム分析フェーズ
```mermaid
graph LR
    A[現行システム調査] --> B[業務フロー分析]
    B --> C[データフロー分析]
    C --> D[統合ポイント特定]
    D --> E[リスク評価]
```

### 2. ビジネス要件定義フェーズ
- 業務目標の明確化
- ユーザーストーリー作成
- 業務ルール定義
- KPI・メトリクス設定

### 3. 技術要件定義フェーズ
- システム構成要件
- パフォーマンス要件
- 可用性・信頼性要件
- 拡張性要件

## 出力成果物

### 要件定義書構成
```
requirements/
├── business_requirements.md      # ビジネス要件
├── technical_requirements.md     # 技術要件
├── integration_requirements.md   # 統合要件
├── security_requirements.md      # セキュリティ要件
├── user_stories/                # ユーザーストーリー
│   ├── epic_001_user_management.md
│   ├── epic_002_data_processing.md
│   └── epic_003_reporting.md
├── business_rules.md            # ビジネスルール
└── acceptance_criteria.md       # 受入基準
```

## ビジネス要件定義テンプレート

### 要件カテゴリ
1. **機能要件**
   - ユーザー管理
   - データ処理
   - レポート生成
   - ワークフロー管理
   - 通知・アラート

2. **非機能要件**
   - パフォーマンス（応答時間、処理能力）
   - 可用性（稼働率、計画停止）
   - セキュリティ（認証、認可、暗号化）
   - 保守性（ログ、監視、診断）
   - 互換性（OS、ブラウザ、既存システム）

### ユーザーストーリー形式
```markdown
## ユーザーストーリー: [タイトル]

**As a** [ユーザーロール]
**I want to** [実現したいこと]
**So that** [ビジネス価値]

### 受入基準
- [ ] 基準1
- [ ] 基準2
- [ ] 基準3

### 技術的考慮事項
- 既存システムとの連携方法
- データ移行要件
- パフォーマンス目標
```

## 既存システム統合要件

### 統合パターン分析
```csharp
// 統合パターンの例
public enum IntegrationPattern
{
    DirectDatabase,      // 直接DB接続
    FileTransfer,       // ファイル転送
    WebService,         // SOAP/REST API
    MessageQueue,       // メッセージキュー
    BatchProcess        // バッチ処理
}

// 統合要件定義
public class IntegrationRequirement
{
    public string SourceSystem { get; set; }
    public string TargetSystem { get; set; }
    public IntegrationPattern Pattern { get; set; }
    public string DataFormat { get; set; }
    public string Frequency { get; set; }
    public List<string> SecurityRequirements { get; set; }
}
```

### データマッピング仕様
```markdown
## データマッピング: [システム名]

### ソースシステム
- システム名: レガシー基幹システム
- データベース: Oracle 11g
- 文字コード: Shift-JIS

### マッピング定義
| ソーステーブル.カラム | データ型 | ターゲットテーブル.カラム | データ型 | 変換ルール |
|---------------------|---------|------------------------|---------|-----------|
| CUSTOMER.CUST_CD    | CHAR(8) | Customers.CustomerId   | INT     | 数値変換  |
| CUSTOMER.CUST_NAME  | VARCHAR2(40) | Customers.Name    | NVARCHAR(50) | 文字コード変換 |

### 変換ロジック
- 日付形式: YYYYMMDD → DateTime
- 金額: 整数型（円） → Decimal（小数点2桁）
- コード値: マスタ参照による変換
```

## セキュリティ要件定義

### 認証・認可要件
```csharp
// セキュリティ要件の例
public class SecurityRequirements
{
    // 認証要件
    public AuthenticationMethod AuthMethod { get; set; }
    public bool MultiFactorRequired { get; set; }
    public int PasswordComplexity { get; set; }
    
    // 認可要件
    public AuthorizationModel AuthzModel { get; set; }
    public List<Role> Roles { get; set; }
    public List<Permission> Permissions { get; set; }
    
    // 監査要件
    public List<AuditEvent> AuditEvents { get; set; }
    public int LogRetentionDays { get; set; }
    
    // 暗号化要件
    public EncryptionMethod DataEncryption { get; set; }
    public bool TransportEncryption { get; set; }
}
```

### コンプライアンス要件
- 個人情報保護法準拠
- 内部統制（J-SOX）対応
- 業界標準・ガイドライン準拠
- 社内セキュリティポリシー準拠

## マルチAI協調

### Gemini CLI連携
```bash
# ビジネスプロセス分析
gemini analyze-business-process --domain enterprise --output requirements/

# ユーザーインタビュー結果分析
gemini analyze-interviews --files interviews/*.md --extract requirements
```

### o3 MCP連携
```bash
# 既存システム調査
o3-mcp analyze-legacy --system mainframe --output requirements/legacy_analysis.md

# データベース構造分析
o3-mcp analyze-database --connection "legacy_db" --schema analysis
```

## 実行例

### 完全な要件定義プロセス
```bash
/requirements --all

# 実行結果
✓ 既存システム分析完了
✓ ビジネス要件定義完了
✓ 技術要件定義完了
✓ 統合要件定義完了
✓ セキュリティ要件定義完了

生成されたドキュメント:
- requirements/business_requirements.md
- requirements/technical_requirements.md
- requirements/integration_requirements.md
- requirements/security_requirements.md
- requirements/user_stories/ (15 files)
```

### 特定要件のみ定義
```bash
# 統合要件のみ定義
/requirements --integration

# セキュリティ要件のみ定義
/requirements --security
```

## ベストプラクティス

### 1. 要件の優先順位付け
- MoSCoW法（Must/Should/Could/Won't）
- ビジネス価値による順位付け
- 技術的リスクの考慮

### 2. 要件の検証
- ステークホルダーレビュー
- 実現可能性の確認
- 既存システムとの整合性チェック

### 3. 要件のトレーサビリティ
- 要件IDによる管理
- 設計・実装への紐付け
- 変更履歴の記録

## エラーハンドリング

### よくあるエラー
1. **既存システム接続エラー**
   - 接続情報の確認
   - アクセス権限の確認

2. **要件の矛盾**
   - ステークホルダー間の調整
   - 優先順位の明確化

3. **スコープクリープ**
   - 変更管理プロセスの適用
   - 影響分析の実施

## まとめ

このコマンドにより、エンタープライズシステムの要件を体系的に定義し、既存システムとの統合を考慮した包括的な要件定義書を作成できます。マルチAI協調により、ビジネス視点と技術視点の両面から質の高い要件定義を実現します。