# /database-optimize - データベース最適化コマンド

## 概要
プロジェクトのデータベースを包括的に最適化するコマンドです。SQLAlchemy、SQL Server、PostgreSQLなど、様々なデータベース技術に対応します。

## 使用方法
```bash
/database-optimize [optimization_type] [options]

# 使用例
/database-optimize performance --target=sqlalchemy
/database-optimize query --analyze-slow-queries
/database-optimize index --auto-create
/database-optimize migration --from=legacy --to=modern
```

## パラメータ

### 必須パラメータ
- `optimization_type`: 最適化タイプ
  - `performance` - パフォーマンス最適化
  - `query` - クエリ最適化
  - `index` - インデックス最適化
  - `migration` - データベース移行
  - `schema` - スキーマ最適化
  - `connection` - 接続プール最適化

### オプション
- `--target`: 対象技術（sqlalchemy, sql-server, postgresql, mysql）
- `--analyze-slow-queries`: 遅いクエリの分析
- `--auto-create`: 自動的に最適化を実施
- `--report`: 最適化レポート生成
- `--dry-run`: 実行せずに計画のみ表示

## 最適化内容

### 1. パフォーマンス最適化
```python
# SQLAlchemy最適化例
optimization_config = {
    "connection_pool": {
        "pool_size": 20,
        "max_overflow": 40,
        "pool_timeout": 30,
        "pool_recycle": 3600
    },
    "query_optimization": {
        "eager_loading": True,
        "batch_size": 1000,
        "query_cache": True
    }
}
```

### 2. インデックス最適化
```sql
-- 自動生成されるインデックス例
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_composite ON products(category_id, status);
```

### 3. クエリ最適化
```python
# N+1問題の解決
# Before
users = session.query(User).all()
for user in users:
    print(user.orders)  # N+1問題

# After（最適化後）
users = session.query(User).options(
    selectinload(User.orders)
).all()
```

### 4. スキーマ最適化
- 正規化/非正規化の判断
- パーティショニング戦略
- 適切なデータ型の選択
- 制約の最適化

## 対応データベース

| データベース | サポートレベル | 特記事項 |
|------------|--------------|---------|
| PostgreSQL | フル対応 | 推奨DB |
| SQL Server | フル対応 | エンタープライズ向け |
| MySQL | 基本対応 | 一般的な最適化 |
| SQLite | 限定対応 | 開発環境のみ |

## 実行プロセス

### 1. 現状分析フェーズ
```yaml
analysis:
  - slow_query_log分析
  - インデックス使用状況
  - テーブルサイズ確認
  - 接続プール状況
```

### 2. 最適化計画フェーズ
```yaml
planning:
  - 優先順位付け
  - 影響範囲評価
  - 実行計画作成
  - ロールバック計画
```

### 3. 実行フェーズ
```yaml
execution:
  - バックアップ作成
  - 最適化実行
  - 検証テスト
  - パフォーマンス測定
```

### 4. レポートフェーズ
```yaml
reporting:
  - 改善効果測定
  - ビフォーアフター比較
  - 推奨事項
  - 継続的改善提案
```

## 出力例

### 最適化レポート
```markdown
# データベース最適化レポート

## 実施内容
- インデックス追加: 5件
- クエリ最適化: 12件
- 接続プール調整: 完了

## 改善効果
- 平均レスポンス時間: 250ms → 80ms（68%改善）
- スロークエリ数: 45 → 3（93%削減）
- DB CPU使用率: 75% → 35%（53%削減）

## 推奨事項
1. 定期的なVACUUM実行
2. パーティショニングの検討
3. 読み取り専用レプリカの追加
```

## エラーハンドリング

### よくあるエラーと対処法
| エラー | 原因 | 対処法 |
|--------|------|--------|
| 接続エラー | DB接続情報不正 | 接続文字列確認 |
| 権限エラー | 権限不足 | DBA権限で実行 |
| タイムアウト | 大規模テーブル | バッチ処理に分割 |

## 管理責任
- **管理部門**: システム開発部
- **カスタマイズ**: プロジェクトのDB技術に応じて最適化

## 関連コマンド
- `/analyze` - データベース分析
- `/db-migration` - データベース移行
- `/performance-test` - パフォーマンステスト

---
*このコマンドはシステム開発部が管理します。*