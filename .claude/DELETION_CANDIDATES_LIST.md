# 階層型システム関連ファイル削除候補リスト

## [目標] 削除理由
v12.0でペアプログラミング体制（CTO+Alex）に移行したため、階層型システム（4部門体制）の関連ファイルは不要となりました。

## [警告] 削除対象ファイル

### 1. 階層型部門関連ファイル

#### agents/cto/ ディレクトリ内
- `quality_assurance_dept.md` - 品質保証部の定義（廃止済み）
- `file_access_permissions.md` - 部門別アクセス権限（簡素化済み）
- `realtime_logging.md` - 部門別ログ管理（ActivityReportに統合済み）
- `reporting_rules.md` - 部門別報告ルール（ペア報告に変更済み）
- `workflow.md` - 部門間ワークフロー（SDD+TDD単一フローに統合済み）

#### agents/ ディレクトリ内
- `hr_log_management.md` - 人事部ログ管理（廃止済み）

#### docs/ ディレクトリ内
- `cto_operations_guide.md` - CTO運用ガイド（cto.mdに統合済み）
- `hr_operations_guide.md` - 人事部運用ガイド（廃止済み）
- `qa_dept_operations_guide.md` - 品質保証部運用ガイド（廃止済み）
- `strategy_operations_guide.md` - 経営企画部運用ガイド（廃止済み）
- `sdd_tdd_role_assignment_matrix.md` - 部門別役割マトリクス（ペア役割に簡素化済み）

### 2. バックアップファイル

#### 絵文字削除バックアップ
- `.claude/CLAUDE.md.emoji_backup`
- `.claude/README.md.emoji_backup`
- `.claude/agents/cto/cto.md.emoji_backup`
- `.claude/docs/README.md.emoji_backup`

### 3. 旧システム関連

#### 不要なNoneファイル
- `docs/None_design.md`
- `docs/None_report.md`
- `docs/None_requirements.md`

#### 旧バージョン改善レポート
- `docs/improvement_report_v10.2.md` - v12.0で内容が陳腐化

## [OK] 保持するファイル

### 重要な技術ドキュメント
- `docs/sdd_existing_project_analysis.md` - 既存プロジェクト分析手法
- `docs/sdd_improvements_from_kiro.md` - SDD改善提案
- `docs/sdd_unified_specification.md` - 統一仕様
- `docs/existing_project_modification_workflow.md` - 既存プロジェクト修正ワークフロー

### 現行システムファイル
- `.claude/agents/cto/cto.md` - 修正済みCTO定義
- `.claude/agents/alex-sdd-tdd-engineer.md` - アレックス定義
- `.claude/docs/README.md` - 修正済みドキュメント管理
- `.claude/commands/README.md` - 修正済みコマンド体系

## [計画] 削除実行計画

### フェーズ1: 階層型部門ファイル削除
```bash
# 以下のファイルを削除
rm .claude/agents/cto/quality_assurance_dept.md
rm .claude/agents/cto/file_access_permissions.md
rm .claude/agents/cto/realtime_logging.md
rm .claude/agents/cto/reporting_rules.md
rm .claude/agents/cto/workflow.md
rm .claude/agents/hr_log_management.md
```

### フェーズ2: 部門別運用ガイド削除
```bash
# 以下のファイルを削除
rm .claude/docs/cto_operations_guide.md
rm .claude/docs/hr_operations_guide.md
rm .claude/docs/qa_dept_operations_guide.md
rm .claude/docs/strategy_operations_guide.md
rm .claude/docs/sdd_tdd_role_assignment_matrix.md
```

### フェーズ3: バックアップファイル削除
```bash
# 以下のファイルを削除
rm .claude/CLAUDE.md.emoji_backup
rm .claude/README.md.emoji_backup
rm .claude/agents/cto/cto.md.emoji_backup
rm .claude/docs/README.md.emoji_backup
```

### フェーズ4: 不要ファイル削除
```bash
# 以下のファイルを削除
rm .claude/docs/None_design.md
rm .claude/docs/None_report.md
rm .claude/docs/None_requirements.md
rm .claude/docs/improvement_report_v10.2.md
```

## [データ] 影響確認

### 削除しても問題ない理由
1. **階層型部門ファイル**: ペアプログラミング体制で不要
2. **部門別運用ガイド**: 単一CTO+Alex体制で不要
3. **バックアップファイル**: 既に修正済みで不要
4. **Noneファイル**: 空または無効な内容
5. **旧改善レポート**: v12.0で内容が陳腐化

### 削除による利点
- ファイル構造の簡素化
- 保守対象ファイル数の削減
- システムの理解しやすさ向上
- 不要な複雑性の排除

## [注意] 実行前確認事項

1. **重要ファイルの誤削除防止**: 保持リストのファイルに注意
2. **バックアップ**: 削除前にgitコミットで安全確保
3. **段階実行**: フェーズごとに削除して影響確認
4. **復元可能性**: gitで履歴管理されているため復元可能

---
*作成日: 2025-08-22*
*対象システム: v12.0 ペアプログラミング体制*