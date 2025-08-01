# /architecture - デスクトップアプリアーキテクチャ・レガシー統合設計コマンド

**OpenAI o3 MCP 専用 - 高度推論・システム設計特化**

## 📋 コマンド概要

.NET Framework 4.0デスクトップアプリケーションのシステムアーキテクチャ設計、レガシーシステム統合アーキテクチャ、スケーラビリティ設計、パフォーマンス最適化をOpenAI o3 MCPの高度な推論能力で実現します。Windows XP/2003環境での制約と企業級エンタープライズ要求を統合した最適アーキテクチャを設計します。

## 🚀 使用方法

### 基本構文
```bash
/architecture [architecture_type] [options]
```

### 主要アーキテクチャタイプ

#### 1. デスクトップアプリケーション設計
```bash
/architecture desktop_design [complexity_level]
```
**複雑性レベル**:
- `simple` - 単一機能ツール型アーキテクチャ
- `business` - 業務管理システム型アーキテクチャ
- `enterprise` - エンタープライズ級統合アーキテクチャ

#### 2. レガシーシステム統合設計
```bash
/architecture legacy_integration [integration_scope]
```
**統合範囲**:
- `com_components` - COMコンポーネント統合アーキテクチャ
- `mainframe_bridge` - メインフレームブリッジアーキテクチャ
- `hybrid_systems` - ハイブリッドシステム統合アーキテクチャ

#### 3. スケーラビリティ設計
```bash
/architecture scalability_design [scale_target]
```
**スケールターゲット**:
- `concurrent_users` - 同時ユーザー数スケーリング
- `data_volume` - 大量データ処理スケーリング
- `geographic_distribution` - 地理的分散対応アーキテクチャ

#### 4. パフォーマンス最適化設計
```bash
/architecture performance_optimization [optimization_focus]
```
**最適化焦点**:
- `memory_efficiency` - メモリ効率最適化 (Windows XP対応)
- `response_time` - レスポンス時間最適化
- `throughput` - スループット最適化

## 🎯 .NET Framework 4.0 アーキテクチャ設計

### レイヤードアーキテクチャ (MVP + Clean Architecture)
```
┌──────────────────────────────────────────────────┐
│                 Presentation Layer                 │
│  ┌────────────────────────────────────────────┐  │
│  │          Windows Forms (Views)          │  │
│  │    - IMainView, ICustomerView, etc.     │  │
│  │    - Windows Forms Controls           │  │
│  │    - UI Event Handlers                │  │
│  └────────────────────────────────────────────┘  │
│                        │                        │
│  ┌────────────────────────────────────────────┐  │
│  │           Presenters (MVP)           │  │
│  │   - MainPresenter, CustomerPresenter   │  │
│  │   - BackgroundWorker Management      │  │
│  │   - UI Logic & Event Coordination    │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
                        │
┌──────────────────────────────────────────────────┐
│                Business Layer                  │
│  ┌────────────────────────────────────────────┐  │
│  │          Business Services          │  │
│  │  - ICustomerService, IOrderService    │  │
│  │  - Business Logic Implementation     │  │
│  │  - Validation & Business Rules       │  │
│  └────────────────────────────────────────────┘  │
│                        │                        │
│  ┌────────────────────────────────────────────┐  │
│  │             Domain Models            │  │
│  │     - Customer, Order, Product        │  │
│  │     - Domain Entities & Value Objects │  │
│  │     - Domain Logic                   │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
                        │
┌──────────────────────────────────────────────────┐
│              Data Access Layer               │
│  ┌────────────────────────────────────────────┐  │
│  │       Repository Pattern (.NET 4.0)     │  │
│  │  - ICustomerRepository, IOrderRepo    │  │
│  │  - Entity Framework 4.0 / ADO.NET    │  │
│  │  - Unit of Work Pattern              │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
                        │
┌──────────────────────────────────────────────────┐
│             Infrastructure Layer             │
│  ┌────────────────────────────────────────────┐  │
│  │    Legacy Systems Integration       │  │
│  │  - COM Interop Wrappers             │  │
│  │  - ActiveDirectory Services         │  │
│  │  - External API Clients (WebClient) │  │
│  │  - File System Operations           │  │
│  └────────────────────────────────────────────┘  │
│                        │                        │
│  ┌────────────────────────────────────────────┐  │
│  │        Cross-Cutting Concerns        │  │
│  │  - Logging (log4net)               │  │
│  │  - Exception Handling               │  │
│  │  - Security & Authentication       │  │
│  │  - Configuration Management        │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

### 依存性注入アーキテクチャ (Unity Container 2.1)
```csharp
// .NET Framework 4.0 対応 DI コンテナ設計
public class ArchitectureBootstrapper
{
    private static IUnityContainer _container;
    
    public static IUnityContainer Container
    {
        get
        {
            if (_container == null)
            {
                _container = new UnityContainer();
                RegisterDependencies(_container);
            }
            return _container;
        }
    }
    
    private static void RegisterDependencies(IUnityContainer container)
    {
        // プレゼンテーション層
        container.RegisterType<IMainView, MainForm>(new ContainerControlledLifetimeManager());
        container.RegisterType<MainPresenter>(new ContainerControlledLifetimeManager());
        
        // ビジネス層
        container.RegisterType<ICustomerService, CustomerService>();
        container.RegisterType<IOrderService, OrderService>();
        
        // データアクセス層
        container.RegisterType<ICustomerRepository, CustomerRepository>();
        container.RegisterType<IUnitOfWork, UnitOfWork>();
        
        // インフラストラクチャ層
        container.RegisterType<ILegacySystemService, LegacySystemService>();
        container.RegisterType<IActiveDirectoryService, ActiveDirectoryService>();
        
        // 横断的関心事
        container.RegisterInstance<ILogger>(LogManager.GetLogger("Application"));
        container.RegisterType<IExceptionHandler, GlobalExceptionHandler>();
    }
}
```

### レガシーシステム統合アーキテクチャ
```
┌──────────────────────────────────────────────────┐
│            .NET Framework 4.0 Desktop App           │
└──────────────────────────────────────────────────┘
                        │
        ┌─────────────────────┬──────────────────────┐
        │ COM Interop Layer  │  Web Services Layer  │
        │                    │                     │
        │ ┌──────────────────┐ │ ┌───────────────────┐ │
        │ │  COM Wrappers   │ │ │  WebClient API   │ │
        │ │  Type Libraries │ │ │  SOAP Services   │ │
        │ │  OLE Automation │ │ │  REST APIs       │ │
        │ └──────────────────┘ │ └───────────────────┘ │
        └─────────────────────┴──────────────────────┘
                        │
        ┌─────────────────────┬──────────────────────┐
        │    Legacy DBs      │    Active Directory   │
        │                    │                     │
        │ ┌──────────────────┐ │ ┌───────────────────┐ │
        │ │ SQL Server 2000 │ │ │  Domain Users    │ │
        │ │ Oracle 10g      │ │ │  Groups/OUs      │ │
        │ │ Access MDB      │ │ │  Group Policies  │ │
        │ │ Mainframe DB2   │ │ │  LDAP Queries    │ │
        │ └──────────────────┘ │ └───────────────────┘ │
        └─────────────────────┴──────────────────────┘
```

## 🔧 詳細オプション

### パフォーマンス最適化オプション
```bash
/architecture performance_optimization --target=[target] --constraints=[constraints]
```
**ターゲット**:
- `memory_limited` - メモリ制約環境 (512MB-1GB)
- `cpu_limited` - CPU制約環境 (シングルコア)
- `network_limited` - ネットワーク制約環境
- `storage_limited` - ストレージ制約環境

### スケーラビリティ設計オプション
```bash
/architecture scalability --users=[count] --data_volume=[size]
```
**ユーザー数**:
- `1-10` - 小規模シングルユーザー
- `10-100` - 中規模チームユーザー
- `100-1000` - 大規模企業ユーザー
- `1000+` - エンタープライズレベル

### セキュリティレベル設定
```bash
/architecture security_design --level=[security_level]
```
**セキュリティレベル**:
- `basic` - 基本的な認証・許可
- `enterprise` - 企業レベルセキュリティ
- `government` - 政府機関レベルセキュリティ
- `financial` - 金融業特化セキュリティ

## 📊 アーキテクチャ品質評価

### アーキテクチャ評価指標
```
● 保守性: SOLID原則適用度、結合度・凝集度評価
● スケーラビリティ: 同時ユーザー数、データ量、レスポンス時間
● パフォーマンス: CPU/メモリ使用率、スループット
● セキュリティ: 脆弱性評価、コンプライアンス遙守状況
● テスタビリティ: ユニットテストカバレッジ、モック可能性
```

### アーキテクチャレビューチェックリスト
```
□ .NET Framework 4.0 制約事項対応状況
□ MVPパターンの正しい実装
□ Unity Container DI設定の最適化
□ Repositoryパターン + Unit of Work実装
□ COM統合アーキテクチャの安全性
□ メモリ管理・リソース解放パターン
□ スレッドセーフティ設計
□ エラーハンドリング戦略
□ ログ戦略・監視ポイント
□ デプロイメント・更新戦略
```

## 📝 生成アーキテクチャドキュメント

- `.tmp/ai_shared_data/architecture_design.json` - アーキテクチャ設計データ
- `01_development_docs/system_architecture.md` - システムアーキテクチャ書
- `01_development_docs/legacy_integration_architecture.md` - レガシー統合アーキテクチャ
- `01_development_docs/performance_design.md` - パフォーマンス設計書
- `01_development_docs/scalability_design.md` - スケーラビリティ設計書
- `docs/architecture/` - 詳細アーキテクチャ図・シーケンス図

## 🤖 マルチAI連携ポイント

### o3 MCP → Claude Code 設計連携
```json
{
  "architecture_specifications": {
    "patterns": ["MVP", "Repository", "Unity DI", "COM Interop"],
    "constraints": [".NET 4.0", "Windows XP/2003", "BackgroundWorker only"],
    "performance_targets": {"memory": "<256MB", "startup": "<5s"},
    "integration_requirements": ["COM compatibility", "AD authentication"]
  }
}
```

### o3 MCP → Gemini CLI 戦略連携
```json
{
  "technical_feasibility": {
    "complexity_score": 7.5,
    "risk_factors": ["COM interop complexity", "Legacy OS support"],
    "success_probability": 0.85,
    "recommended_approach": "Incremental legacy migration"
  }
}
```

## 🔗 関連コマンド

- `/security` - アーキテクチャベースのセキュリティ設計
- `/devops` - アーキテクチャに基づいたCI/CD設計
- `/design` - アーキテクチャを踏まえた詳細設計
- `/winforms-patterns` - アーキテクチャパターンの実装
- `/legacy-integration` - アーキテクチャベースの統合実装

---

**💡 重要**: .NET Framework 4.0環境では、アーキテクチャの選択が特に重要です。async/awaitやHttpClientなどのモダンな機能が使用できないため、MVP + Unity DI + Repositoryパターンの組み合わせで、保守性とテスタビリティを確保した堅牢なアーキテクチャを構築することが最重要です。