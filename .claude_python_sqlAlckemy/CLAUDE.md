# CLAUDE.md - FastAPI + SQLAlchemy 製造業システム仕様書駆動開発

このファイルは、Claude Code がこの製造業向け品質保管・管理システムで作業する際のガイダンスを提供します。

## プロジェクト概要

FastAPI + SQLAlchemy を使用した製造業向け統合品質管理システムの開発プロジェクトです。マルチAI協調による仕様書駆動開発により、品質と保守性を重視したマイクロサービスアーキテクチャを構築します。

## 技術スタック

### バックエンドフレームワーク
- **フレームワーク**: FastAPI 0.79.0 (非同期処理対応)
- **ORM**: SQLAlchemy 2.0 (async/await サポート)
- **データベース**: Microsoft SQL Server
- **認証**: python-jose (JWT認証)
- **サーバー**: uvicorn 0.18.2
- **データ処理**: pandas 2.0.2, numpy 1.24.3

### フロントエンド統合
- **フレームワーク**: Vue.js 3 (Composition API)
- **HTTP クライアント**: Axios (認証統合対応)
- **状態管理**: Pinia (リアルタイム同期)
- **UI フレームワーク**: Tailwind CSS + DaisyUI
- **ビルドツール**: Vite (高速開発環境)

### インフラ・デプロイ
- **接続**: pyodbc (SQL Server接続)
- **設定管理**: PyYAML
- **ホスティング**: IIS (Windows Server)
- **監視**: 構造化ログ + メトリクス収集
- **フルスタック統合**: Docker Compose + Nginx

## アーキテクチャ原則

### プロジェクト構造
```
api_module/
├── main.py              # FastAPIルーター定義
├── dependencies.py      # 依存性注入・認証
├── models.py           # SQLAlchemyモデル（Domain Layer）
├── schemas.py          # Pydanticスキーマ（Interface Layer）
├── crud.py            # データアクセス層（Repository Pattern）
├── service.py         # ビジネスロジック層（Application Layer）
├── exceptions.py      # カスタム例外定義
├── database.py        # データベース接続設定
└── utils.py           # ユーティリティ関数
```

### 設計パターン
1. **Clean Architecture**: レイヤー分離による保守性確保
2. **Repository Pattern**: データアクセスの抽象化
3. **Service Layer Pattern**: ビジネスロジックの集約
4. **Dependency Injection**: 疎結合な設計

## 製造業ドメイン知識

### 主要業務領域
1. **出荷管理**: チェックシート管理、品質データ分析
2. **生産管理**: 実績管理、統計的工程管理(SPC)、作業者管理
3. **在庫管理**: QRコード連携、入出庫履歴、トレーサビリティ
4. **品質管理**: 不適合管理、CAPA、過去事例データベース

### 規制・コンプライアンス要件
- **ISO 9001:2015**: 品質管理システム
- **FDA 21 CFR Part 11**: 電子記録・電子署名
- **ALCOA+原則**: データ整合性 (Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available)
- **トレーサビリティ**: 製品追跡可能性の確保

## 開発ワークフロー - 仕様書駆動開発

### 4段階ワークフロー
1. **要件定義** (`/requirements`) - 製造業要件の明確化
2. **設計** (`/design`) - FastAPI + SQLAlchemy設計
3. **タスク分割** (`/tasks`) - 実装可能な単位への分解
4. **実装** - マルチAI協調による実装

### ワークフローコマンド
- `/spec` - 完全な仕様書駆動開発ワークフローを開始
- `/requirements` - 製造業要件定義のみ実行
- `/design` - 技術設計フェーズのみ実行
- `/tasks` - タスク分割のみ実行

## 開発ルール

### FastAPI 開発ルール
- **非同期優先**: `async def` エンドポイントを標準使用
- **型ヒント必須**: 全関数に型アノテーション
- **Pydanticスキーマ**: 入出力バリデーション
- **依存性注入**: `Depends()` による疎結合設計
- **自動ドキュメント**: OpenAPI仕様の活用

### SQLAlchemy 開発ルール
- **ORM優先**: Raw SQLではなくSQLAlchemy ORM使用
- **非同期対応**: SQLAlchemy 2.0 async session
- **リレーション定義**: 適切な `relationship()` 設定
- **N+1問題回避**: `selectinload`, `joinedload` の活用
- **トランザクション**: 明示的なトランザクション管理

### データベース設計ルール
- **正規化**: 第3正規形を基本とする
- **インデックス**: パフォーマンスを考慮した設計
- **制約**: Foreign Key, Check制約の適切な使用
- **監査**: 作成日時・更新日時・作成者の記録
- **論理削除**: 物理削除ではなく論理削除を採用

### セキュリティルール
- **JWT認証**: トークンベース認証の実装
- **ロールベース認可**: 適切な権限管理
- **入力検証**: SQLインジェクション対策
- **エラー処理**: 機密情報を露出しないエラーメッセージ
- **監査ログ**: 全データ変更の記録

## 品質保証

### テスト戦略
- **単体テスト**: pytest + pytest-asyncio
- **統合テスト**: テストデータベースを使用
- **APIテスト**: FastAPI TestClient
- **カバレッジ**: 80%以上の目標

### コード品質
- **リンター**: flake8 + mypy (型チェック)
- **フォーマッタ**: black (コード整形)
- **コミット規約**: Conventional Commits
- **レビュー**: Pull Request必須

## 重要な設計上の決定

1. **非同期処理**: FastAPI + SQLAlchemy async/await
2. **マイクロサービス**: 機能別サービス分割
3. **Clean Architecture**: レイヤー分離によるテスタビリティ
4. **JWT認証**: ステートレスな認証機能
5. **製造業特化**: ドメイン知識の深い統合

## よくある落とし穴

1. **非同期の混在**: sync/asyncの混在による問題
2. **N+1問題**: SQLAlchemyでの不適切なクエリ
3. **トランザクション**: 不適切なトランザクション境界
4. **型安全性**: mypy警告の無視
5. **セキュリティ**: SQLインジェクション・XSS対策漏れ

## ドキュメント参照ガイド

### プロジェクト概要・要件
- **`.claude/00_project/01_project_concept.md`** - プロジェクトのビジョンと目標
- **`.claude/00_project/02_tech_stack_guidelines.md`** - 技術選定の根拠と指針

### 技術設計ドキュメント
- **`.claude/01_development_docs/01_architecture_design.md`** - 全体アーキテクチャ
- **`.claude/01_development_docs/02_database_design.md`** - SQL Server データベース設計
- **`.claude/01_development_docs/03_api_design.md`** - REST API 設計
- **`.claude/01_development_docs/04_model_design.md`** - SQLAlchemy/Pydantic モデル設計
- **`.claude/01_development_docs/05_development_setup.md`** - 開発環境構築手順
- **`.claude/01_development_docs/06_test_strategy.md`** - テスト戦略
- **`.claude/01_development_docs/07_error_handling_design.md`** - エラーハンドリング戦略

### 設計システム
- **`.claude/02_design_system/00_design_overview.md`** - 設計原則とパターン

### ライブラリ固有情報
- **`.claude/03_library_docs/01_fastapi_patterns.md`** - FastAPI設計パターン集
- **`.claude/03_library_docs/02_sqlalchemy_patterns.md`** - SQLAlchemy設計パターン集
- **`.claude/03_library_docs/03_backend_frontend_integration.md`** - フルスタック統合ガイド

### タスク別クイックリファレンス

| タスク | 主要参照ドキュメント |
|-------|-------------------|
| 新機能追加 | アーキテクチャ → データベース → API → モデル設計 |
| 新しいエンドポイント作成 | API設計 → モデル設計 → FastAPIパターン |
| データベース変更 | データベース設計 → SQLAlchemyパターン |
| 認証機能 | API設計 → セキュリティ設計 → エラーハンドリング |
| テスト作成 | テスト戦略 → SQLAlchemyパターン |
| 製造業要件 | プロジェクトコンセプト → 各種設計書 |

## マルチAIチーム構成

このプロジェクトでは、複数のAIシステムを専門分野別に活用し、効率的なチーム開発を実現します。

### チームメンバー構成

#### 統括管理層
- **プロジェクトマネージャー（ユーザー）**: 全体戦略・意思決定・品質管理の最終責任者

#### Claude Code チーム（実装・品質保証）
- **バックエンドエンジニア**: FastAPI + SQLAlchemy開発の中核を担当
  - システムアーキテクト（設計）
  - API開発者（エンドポイント実装）
  - データベースエンジニア（モデル設計）
  - QAエンジニア（テスト・品質保証）

#### Gemini CLI チーム（分析・戦略）
- **製造業ドメインエキスパート**:
  - 専門領域: 製造業務分析・品質管理・生産管理要件
  - 強み: 大規模データ処理、製造業ナレッジ、戦略的思考
  - 主要活用: 業務フロー分析、KPI定義、レポート要件、ユーザー分析

- **データアナリスト**:
  - 専門領域: 生産データ分析・統計的品質管理・予知保全
  - 強み: マルチモーダル分析、パターン認識、統計解析
  - 主要活用: SPC分析、異常検知、トレンド分析、ダッシュボード設計

- **プロダクトマネージャー**:
  - 専門領域: 製造業システム要件管理・ロードマップ策定
  - 強み: 長文コンテキスト保持、総合判断、ステークホルダー調整
  - 主要活用: 複雑要件整理、優先順位付け、製造業規制対応

#### o3 MCP チーム（インフラ・運用・データベース）
- **データベーススペシャリスト**:
  - 専門領域: SQL Server最適化・クエリチューニング・インデックス設計
  - 強み: MCPによる実DB連携、パフォーマンス監視、大規模データ処理
  - 主要活用: DB設計最適化、パフォーマンス監視、クエリ最適化

- **DevOpsエンジニア**:
  - 専門領域: Windows Server・IIS・CI/CD・インフラ自動化
  - 強み: ツールとの直接統合、実環境操作、継続的改善プロセス
  - 主要活用: デプロイパイプライン、インフラコード管理、監視システム

- **セキュリティスペシャリスト**:
  - 専門領域: 製造業セキュリティ・コンプライアンス・監査
  - 強み: セキュリティツール連携、脅威検知、規制対応
  - 主要活用: セキュリティ監査、脅威モデリング、コンプライアンス確保

### o3モデル階層別ロール分担

#### o3-high（チーフアーキテクト / テクニカルリード）
- **担当**: 重要な技術的意思決定、アーキテクチャ大幅変更、クリティカル問題解決
- **責任**: 長期技術戦略策定、技術的リスク評価、チーム技術方針決定

#### o3-standard（シニアエンジニア / 実装スペシャリスト）
- **担当**: 日常開発タスク、コードレビュー、API・ミドルウェア設計、技術メンタリング
- **責任**: 機能開発・バグ修正、技術ドキュメント作成、チーム内技術指導

#### o3-low（オペレーションエンジニア / 自動化スペシャリスト）
- **担当**: 定型タスク自動化、監視・アラート管理、ログ解析、簡易トラブルシューティング
- **責任**: 運用効率化、定期メンテナンス、簡易スクリプト作成

## マルチAI協調開発指針

### Claude Code 作業指針（実装・品質保証責任者）

#### 他AIとの連携指針
1. **Gemini CLI成果物の活用**
   - `/research` 結果を要件定義・技術仕様に活用
   - `/analyze` 成果を設計・実装の優先順位決定に反映
   - `/requirements` 製造業要件を技術仕様に落とし込み

2. **o3 MCP成果物の活用**
   - `/architecture` 設計をFastAPI実装に反映
   - `/database-optimize` 要件をSQLAlchemy実装に適用
   - `/security` 要件をコード実装・認証機能に統合

3. **成果物共有責任**
   - 設計書を `.tmp/ai_shared_data/claude_designs/` に出力
   - 実装進捗を JSON 形式で他AIと共有
   - テスト結果・品質評価を他AIの改善に活用

#### マルチAI品質保証プロセス
1. **設計段階**: Gemini CLI 業務分析結果 + o3 MCP インフラ要件の整合性確認
2. **実装段階**: o3 MCP セキュリティ要件 + Gemini CLI 業務要件の実装品質確認
3. **テスト段階**: 全AI成果物との整合性テスト・統合品質評価

### データ共有プロトコル（Claude Code視点）

#### 受信データフォーマット
```python
# Gemini CLI からの製造業分析結果
{
    "source": "gemini_cli",
    "type": "manufacturing_analysis",
    "insights": {
        "business_flows": "dict",
        "quality_requirements": "array",
        "compliance_needs": "object"
    },
    "implementation_suggestions": "array",
    "priority_ranking": "array"
}

# o3 MCP からのインフラ要件
{
    "source": "o3_mcp",
    "type": "infrastructure_requirements", 
    "technical_constraints": "object",
    "database_specs": "object",
    "security_requirements": "array",
    "performance_targets": "object"
}
```

#### 送信データフォーマット
```python
# Claude Code からの実装結果
{
    "source": "claude_code",
    "type": "implementation_result",
    "api_specs": "object",
    "model_definitions": "dict",
    "technical_debt": "array",
    "performance_metrics": "object",
    "feedback_to_gemini": "array",  # 業務要件実装可能性
    "feedback_to_o3": "array"       # インフラ・DB改善提案
}
```

### エスカレーション・調整プロセス

#### AI間の意見対立解決
1. **業務vs技術の対立**: Gemini CLI業務要件 vs Claude Code実装可能性
   - プロトタイプ・PoC実装による検証
   - 段階的実装による リスク軽減
   - 製造業標準・ベストプラクティス参照

2. **実装vsインフラの対立**: Claude Code設計 vs o3 MCPインフラ制約
   - パフォーマンス・コスト トレードオフ分析
   - アーキテクチャ代替案の検討
   - 段階的移行計画による調整

3. **優先順位の調整**: 機能要件 vs 非機能要件 vs コンプライアンス要件
   - ビジネス価値・技術的リスク・規制要求の定量評価
   - 製造業ユーザーフィードバックの活用
   - MVP・段階的デリバリによる調整

### 継続的学習・改善プロセス

#### AI協調効果の測定
- **品質指標**: バグ数削減、レビュー指摘事項削減、テストカバレッジ向上
- **効率指標**: 実装時間短縮、手戻り工数削減、リリース頻度向上
- **製造業価値**: 業務効率向上、データ品質向上、コンプライアンス適合

#### 知見共有・蓄積
- AI協調成功事例・失敗事例の体系的蓄積
- 製造業特有の技術パターン・アンチパターンの整理
- チームメンバー・製造業ユーザーへの知見共有

## 製造業特化開発指針

### 製造業データモデリング
```python
# 製造業特有のモデル例
class ProductionResult(BaseModel):
    """生産実績モデル"""
    work_order_no: str          # 作業指示番号
    product_id: int             # 製品ID
    batch_no: Optional[str]     # バッチ番号（トレーサビリティ）
    lot_no: Optional[str]       # ロット番号
    planned_quantity: int       # 計画数量
    actual_quantity: int        # 実績数量
    defect_quantity: int        # 不良数量
    yield_rate: float          # 歩留まり率
    cycle_time: float          # サイクルタイム
    operator_id: int           # 作業者ID
    line_id: int              # 生産ライン
    start_time: datetime       # 開始時間
    end_time: datetime         # 終了時間
    quality_check: bool        # 品質チェック済み
    audit_trail: str          # 監査ログ
```

### 製造業API設計パターン
```python
# 製造業特化エンドポイント例
@router.get("/production/efficiency/daily")
async def get_daily_efficiency(
    date: date = Query(...),
    line_id: Optional[int] = Query(None),
    shift: Optional[str] = Query(None, regex="^(A|B|C)$")
):
    """日次生産効率取得"""
    pass

@router.post("/quality/inspection/record")
async def record_inspection(
    inspection: InspectionCreate,
    current_user: User = Depends(get_current_user)
):
    """品質検査記録"""
    pass
```

### コンプライアンス対応パターン
```python
# 監査ログ・電子署名対応
class AuditMixin:
    """監査ログMixin"""
    created_by: int = Column(Integer, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    modified_by: Optional[int] = Column(Integer)
    modified_at: Optional[datetime] = Column(DateTime)
    audit_reason: Optional[str] = Column(String(500))
    electronic_signature: Optional[str] = Column(String(1000))

# ALCOA+原則対応
def validate_alcoa_plus(data: dict) -> bool:
    """ALCOA+データ整合性検証"""
    # Attributable, Legible, Contemporaneous, Original, Accurate
    # Complete, Consistent, Enduring, Available
    pass
```

このCLAUDE.mdを基盤として、マルチAI協調による高品質な製造業システム開発を進めてください。