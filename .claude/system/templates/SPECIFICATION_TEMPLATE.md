# 機能仕様書テンプレート - AI往復最適化版

## 📋 基本情報
- **機能名**: [機能の正確な名称]
- **担当エンジニア**: [EngineerRole - ALEX_LEAD/OPTIMIZER/QA_DOC/TDD_TEST]
- **優先度**: [HIGH/MEDIUM/LOW]
- **作業見積**: [Small/Medium/Large]
- **関連モジュール**: [影響を受けるコアモジュール]

## 🎯 仕様詳細

### 目的・背景
```
[なぜこの機能が必要なのか？解決したい課題は何か？]
```

### 機能要件
```
✅ [具体的な要件1] 
✅ [具体的な要件2]
✅ [具体的な要件3]
```

### 技術要件
- **対象モジュール**: `system/core/[module_name].py`
- **依存関係**: [既存モジュールとの依存]
- **パフォーマンス要件**: [レスポンス時間/メモリ使用量]
- **互換性要件**: [後方互換性の考慮]

## 🏗️ 実装仕様

### アーキテクチャ設計
```python
# 期待されるクラス構造
class [ClassName](BaseManager):
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def [main_method](self, input: InputType) -> BaseResult:
        pass
```

### インターフェース定義
```python
# 入力パラメータ
@dataclass
class [InputClass]:
    field1: str
    field2: Optional[int] = None

# 出力結果
@dataclass  
class [OutputClass]:
    success: bool
    result: Any
    message: str
```

## 🧪 テスト仕様 (TDD)

### RED Phase - 失敗テスト
```python
def test_[function_name]_invalid_input():
    """無効な入力でエラーが発生することを確認"""
    pass

def test_[function_name]_edge_cases():
    """境界値テストが適切に動作することを確認"""
    pass
```

### GREEN Phase - 成功テスト
```python
def test_[function_name]_valid_input():
    """正常な入力で期待される結果が返ることを確認"""
    pass

def test_[function_name]_integration():
    """他のモジュールとの統合が正常動作することを確認"""
    pass
```

### テストカバレッジ目標
- **目標**: 100% (YAGNI原則に基づく必要最小限の実装)
- **重要パス**: [重要な実行パスの特定]

## 🔄 AI往復最適化情報

### バッチ処理要求
```
1回のAIとのやり取りで以下を一括処理:
☐ インターフェース実装
☐ メインロジック実装  
☐ エラーハンドリング実装
☐ テストコード実装
☐ ドキュメント更新
```

### コンテキスト情報
- **既存コード参照**: `system/core/common_base.py` (BaseManager, BaseResult)
- **コーディング規約**: CLAUDE.md準拠
- **インポートパターン**: 相対import with fallback
- **エラーハンドリング**: try-except with logging

### 自動検証チェックリスト
```bash
# AIに自動実行を依頼する検証コマンド
cd .claude
python -m pytest project/tests/test_[module_name].py -v
python -m coverage report --include="system/core/[module_name].py"
python system/core/[module_name].py  # 単体実行テスト
```

## 📝 実装後チェックリスト

### YAGNI原則確認
- [ ] 現在必要な機能のみ実装されているか
- [ ] 将来のための過剰な抽象化がないか
- [ ] 使われていない引数・メソッドがないか

### DRY原則確認
- [ ] 既存の`common_base.py`の機能を活用しているか
- [ ] 重複するロジックが他モジュールにないか
- [ ] 共通設定は`config.py`を使用しているか

### KISS原則確認
- [ ] メソッドが50行以下に収まっているか
- [ ] クラス責任が単一で明確か
- [ ] 複雑な条件分岐がシンプル化されているか

### TDD原則確認
- [ ] RED→GREEN→REFACTORサイクルが守られているか
- [ ] テストカバレッジが95%以上か
- [ ] テストが仕様を正確に表現しているか

## 🚀 デプロイメント仕様

### 統合テスト
```bash
# AI往復最適化: 一括実行コマンド
python system/core/dependency_checker.py  # 循環依存チェック
python -m pytest project/tests/ --cov=system/core -v  # 全体テスト
```

### パフォーマンス検証
- **実行時間**: [許容できる最大実行時間]
- **メモリ使用量**: [許容できる最大メモリ使用量]
- **同時実行**: [並行実行時の動作確認]

---

## 💡 AI協力指示

この仕様書に基づいて、以下を**1回の往復で一括実装**してください:

1. **実装**: 上記仕様に基づく完全なコード実装
2. **テスト**: RED/GREEN両フェーズのテストコード
3. **統合**: 既存システムとの統合確認
4. **検証**: 自動テスト実行とカバレッジ確認
5. **文書**: 実装結果の簡潔なサマリー

**重要**: エラーが発生した場合は、自動的に修正を試行し、最終的な動作する状態まで完成させてください。