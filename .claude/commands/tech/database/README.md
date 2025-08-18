# 📚 データベース技術専用コマンド

## 概要
データベース技術ごとに特化した高品質な最適化コマンド群です。各コマンドは特定のデータベース技術とその高度な機能に深く特化しています。

## データベース専用コマンド一覧

| コマンド | 説明 | 対象技術 | エンタープライズ機能 |
|---------|------|----------|---------------------|
| `/sqlalchemy-optimize` | SQLAlchemy最適化 | SQLAlchemy 2.0+ | 非同期、N+1自動検出、監査 |
| `/sqlserver-optimize` | SQL Server最適化 | SQL Server 2019+ | Always On、インメモリOLTP、列ストア |
| `/postgresql-optimize` | PostgreSQL最適化 | PostgreSQL 14+ | パーティション、VACUUM、並列処理 |
| `/database-optimize` | 汎用DB最適化 | 全般 | 基本的な最適化 |

## なぜ分割管理するのか

### 技術的理由
1. **データベース固有機能**
   - SQL Server: Always On、インメモリOLTP、列ストア
   - PostgreSQL: VACUUM、MVCC、パーティション継承
   - SQLAlchemy: ORM特有のN+1問題、遅延読み込み

2. **最適化戦略の違い**
   - SQL Server: クエリストア、実行プラン
   - PostgreSQL: EXPLAIN ANALYZE、pg_stat
   - SQLAlchemy: Python側の最適化

3. **エンタープライズ要件**
   - 監査・コンプライアンス対応
   - 高可用性構成
   - 大規模データ処理

## 使用ガイドライン

### プロジェクトに応じた選択
```yaml
SQLAlchemy + FastAPIプロジェクト:
  推奨: /sqlalchemy-optimize
  理由: ORM特有の最適化、非同期対応

.NET + SQL Serverプロジェクト:
  推奨: /sqlserver-optimize
  理由: SQL Server固有機能の活用

Node.js + PostgreSQLプロジェクト:
  推奨: /postgresql-optimize
  理由: PostgreSQL特有の最適化

複数DB対応プロジェクト:
  推奨: /database-optimize
  理由: 汎用的な最適化
```

## コマンド詳細

### /sqlalchemy-optimize
**特徴**:
- N+1問題の自動検出と修正
- 非同期SQLAlchemy完全対応
- エンタープライズ監査機能
- 分散トランザクション管理
- マルチAI協調分析

**使用例**:
```bash
/sqlalchemy-optimize n-plus-one --auto-fix
/sqlalchemy-optimize async-patterns --convert
/sqlalchemy-optimize enterprise-transactions --with-audit
```

### /sqlserver-optimize
**特徴**:
- クエリストアと自動チューニング
- Always On可用性グループ
- インメモリOLTP
- 列ストアインデックス
- パーティション自動管理

**使用例**:
```bash
/sqlserver-optimize alwayson configure --availability-group
/sqlserver-optimize inmemory enable --hot-tables
/sqlserver-optimize columnstore create --fact-tables
```

### /postgresql-optimize（予定）
**特徴**:
- VACUUM戦略最適化
- パーティション継承
- 並列クエリ最適化
- JSONBインデックス
- 論理レプリケーション

## パフォーマンス比較

| 最適化項目 | 汎用版 | 専用版 | 改善率 |
|-----------|--------|--------|--------|
| クエリ実行時間 | 30%改善 | 80%改善 | 2.7倍 |
| N+1問題検出 | 手動 | 自動 | ∞ |
| エンタープライズ機能 | 基本 | 完全対応 | - |
| 監査・コンプライアンス | なし | 完全対応 | - |

## ベストプラクティス

### 1. 初期分析
```bash
# まず現状分析
/sqlalchemy-optimize analyze --full-report

# 問題箇所の特定
/sqlalchemy-optimize n-plus-one --detect

# 最適化実行
/sqlalchemy-optimize n-plus-one --auto-fix
```

### 2. 段階的最適化
1. **Phase 1**: 基本的な最適化（インデックス、クエリ）
2. **Phase 2**: 高度な最適化（パーティション、キャッシュ）
3. **Phase 3**: エンタープライズ機能（監査、高可用性）

### 3. 継続的改善
- 定期的なパフォーマンス分析
- 自動最適化の設定
- 監視とアラート

## トラブルシューティング

| 問題 | 原因 | 解決策 |
|------|------|--------|
| 最適化後も遅い | 根本原因が違う | プロファイリング実施 |
| メモリ使用増加 | キャッシュ過多 | キャッシュ戦略見直し |
| ロック競合 | トランザクション長い | 分離レベル調整 |

## 管理責任
- **管理部門**: システム開発部
- **方針**: データベース技術ごとの専門性を最大限活用
- **品質基準**: エンタープライズレベルの最適化を提供

---
*データベース技術コマンドは、各技術の高度な機能を最大限活用するため個別に管理されています。*