# Issue #1: 型注釈の完全適用

## 概要
すべてのPythonコードに完全な型注釈を追加し、型安全性を向上させる

## 背景
現在、部分的にしか型注釈が適用されていないため、型関連のバグが発生する可能性がある

## タスク

### 1. mypy設定ファイルの作成
**ファイル**: `.claude/mypy.ini`
```ini
[mypy]
python_version = 3.13
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_uninitialized = True
check_untyped_defs = True
disallow_incomplete_defs = True
disallow_untyped_calls = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
```

### 2. core_system.pyへの型注釈追加
**ファイル**: `.claude/system/core/core_system.py`

**変更前**:
```python
def setup_paths():
    current = Path(__file__).resolve().parent
    # ...
    return claude_root
```

**変更後**:
```python
from pathlib import Path
from typing import Optional

def setup_paths() -> Path:
    """
    統一パス設定
    
    Returns:
        Path: .claudeルートディレクトリのパス
    """
    current: Path = Path(__file__).resolve().parent
    # ...
    return claude_root
```

### 3. Resultクラスの型注釈強化
**変更前**:
```python
@dataclass
class Result:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
```

**変更後**:
```python
from typing import TypeVar, Generic, Optional, Dict, Any

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
```

### 4. CoreSystemクラスのメソッド型注釈
**変更前**:
```python
def organize_files(self):
    return Result(True, f"Organized {moved_count} files")
```

**変更後**:
```python
def organize_files(self) -> Result[Dict[str, int]]:
    """
    ファイル整理を実行
    
    Returns:
        Result[Dict[str, int]]: 整理結果（moved_count含む）
    """
    return Result(True, f"Organized {moved_count} files", {"moved_count": moved_count})
```

## 受け入れ条件
- [ ] mypyがエラーなしで実行される
- [ ] すべての関数・メソッドに型注釈がある
- [ ] すべてのクラス属性に型注釈がある
- [ ] 型チェックがCIパイプラインに統合されている

## 実装手順
1. mypy.iniを作成
2. `pip install mypy`を実行
3. 各ファイルに型注釈を追加
4. `mypy .claude/system --config-file .claude/mypy.ini`で確認
5. テストを実行して動作確認

## 優先度
**高**

## 見積もり工数
2-3時間

## ラベル
- enhancement
- type-safety
- code-quality