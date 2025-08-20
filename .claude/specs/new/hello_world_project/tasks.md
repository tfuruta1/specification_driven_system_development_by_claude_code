# 実装計画書 - Hello World Python System

## 📋 Step 3: Implementation Plan（SDD+TDD統合）

### 1. TDD実装フロー

| フェーズ | タスク | 担当 | 見積時間 | TDDステップ |
|----------|--------|------|----------|-------------|
| PHASE-1 | プロジェクト環境準備 | アレックス | 5分 | 準備 |
| PHASE-2 | テスト作成（RED） | アレックス | 10分 | Red |
| PHASE-3 | 実装（GREEN） | アレックス | 10分 | Green |
| PHASE-4 | リファクタリング | アレックス | 5分 | Refactor |
| PHASE-5 | 最終レビュー | CTO + アレックス | 5分 | 完了 |

**総所要時間**: 約35分

### 2. 詳細フェーズ定義

#### PHASE-1: プロジェクト環境準備
**担当**: アレックス  
**TDDステップ**: 準備フェーズ

**作業内容**:
1. プロジェクトディレクトリ作成
2. 仮想環境セットアップ
3. 基本ファイル構成作成

```bash
mkdir hello_world_project
cd hello_world_project
python -m venv venv
venv\Scripts\activate  # Windows
mkdir tests
```

**成果物**:
- hello_world_project/ディレクトリ
- venv仮想環境
- tests/ディレクトリ

**完了条件**: 開発環境が整備されること

#### PHASE-2: テスト作成（TDD Red Phase）
**担当**: アレックス  
**TDDステップ**: Red（失敗するテストを先に作成）

**作業内容**:
1. test_main.py作成
2. main()関数のテスト記述
3. テスト実行して失敗確認

```python
# tests/test_main.py
import unittest
import sys
import os
from io import StringIO

# プロジェクトルートを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestMain(unittest.TestCase):
    def test_main_returns_zero(self):
        """main()が0を返すことを確認"""
        from main import main
        result = main()
        self.assertEqual(result, 0)
        
    def test_main_prints_hello_world(self):
        """main()が"Hello world"を出力することを確認"""
        from main import main
        captured_output = StringIO()
        sys.stdout = captured_output
        main()
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue().strip(), "Hello world")

if __name__ == '__main__':
    unittest.main()
```

**成果物**:
- tests/test_main.py

**完了条件**: テストが作成され、実行して失敗することを確認

#### PHASE-3: 実装（TDD Green Phase）
**担当**: アレックス  
**TDDステップ**: Green（テストを成功させる最小限の実装）

**作業内容**:
1. main.py作成
2. テストが成功する最小実装
3. テスト実行して成功確認

```python
# main.py
import sys

def main() -> int:
    """
    Hello Worldメッセージを表示するメイン関数
    
    Returns:
        int: 実行結果（0: 正常終了, 1: エラー）
    """
    try:
        print("Hello world")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
```

**成果物**:
- main.py

**完了条件**: 全テストが成功すること

#### PHASE-4: リファクタリング（TDD Refactor Phase）
**担当**: アレックス  
**TDDステップ**: Refactor（品質向上、テスト成功維持）

**作業内容**:
1. コード品質向上
2. エラーハンドリング改善
3. ドキュメント作成
4. 最終テスト実行

```python
# requirements.txt
# No external dependencies - using standard library only

# README.md
# Hello World Python System

Simple Hello World implementation following SDD+TDD methodology.

## Setup
1. Activate virtual environment:
   ```
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   ```

2. Run the program:
   ```
   python main.py
   ```

## Expected Output
```
Hello world
```
```

**成果物**:
- requirements.txt
- README.md
- 改良されたmain.py

**完了条件**: テスト成功維持 + コード品質向上

#### PHASE-5: 最終レビュー
**担当**: CTO + アレックス  
**TDDステップ**: 完了

**作業内容**:
1. 要件適合性確認
2. テストカバレッジ確認
3. 実行テスト
4. ドキュメント確認

**成果物**:
- 最終レビューレポート

**完了条件**: CTO承認

### 3. TDD実行順序

```
PHASE-1 (環境準備)
    ↓
PHASE-2 (Red: テスト作成)
    ↓
PHASE-3 (Green: 実装)
    ↓
PHASE-4 (Refactor: 品質向上)
    ↓
PHASE-5 (レビュー: 完了)
```

### 4. チェックポイント

| フェーズ | チェック項目 | 確認方法 |
|----------|-------------|----------|
| PHASE-1 | 環境準備完了 | ディレクトリ・venv確認 |
| PHASE-2 | テスト失敗確認 | `python -m pytest tests/` |
| PHASE-3 | テスト成功確認 | `python -m pytest tests/` |
| PHASE-4 | 品質向上確認 | コードレビュー + テスト |
| PHASE-5 | 要件適合確認 | 受入テスト実行 |

### 5. 品質基準

- **テストカバレッジ**: 100%（main関数）
- **PEP8準拠**: flake8チェック通過
- **型ヒント**: 関数戻り値に必須
- **エラーハンドリング**: 想定例外に対応

### 6. 最終成果物

1. **プロダクションコード**
   - hello_world_project/main.py
   - hello_world_project/requirements.txt
   - hello_world_project/README.md

2. **テストコード**
   - hello_world_project/tests/test_main.py

3. **実行環境**
   - hello_world_project/venv/

4. **設計ドキュメント**
   - requirements.md（要件定義）
   - design.md（技術設計）
   - tasks.md（実装計画）

### 7. CTO承認事項

**承認が必要なタイミング**:
- Step 4: 設計レビュー（現在のステップ）
- PHASE-2完了: テスト設計承認
- PHASE-5完了: 最終成果物承認

---
*アレックス作成 - SDD+TDD統合開発手法*
*CTO承認待ち: 設計レビューと実装開始許可*