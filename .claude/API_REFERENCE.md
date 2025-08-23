# Claude Code SDD+TDD システム APIリファレンス v12.0

## 目次

1. [統合システム (unified_system)](#統合システム)
2. [Auto Mode システム](#auto-mode-システム)
3. [Development Rules システム](#development-rules-システム)
4. [ユーティリティ](#ユーティリティ)

---

## 統合システム

### UnifiedSystem クラス

統合されたSDD+TDDシステムのメインクラス

```python
from claude.core.unified_system import UnifiedSystem

system = UnifiedSystem(project_name="MyProject")
```

#### メソッド

##### create_requirements_doc(project_name: str) -> str
要件定義書を作成します。

**パラメータ:**
- `project_name` (str): プロジェクト名

**戻り値:**
- str: 要件定義書の内容

**例:**
```python
req_doc = system.create_requirements_doc("MyProject")
```

##### create_design_doc(project_name: str) -> str
技術設計書を作成します。

**パラメータ:**
- `project_name` (str): プロジェクト名

**戻り値:**
- str: 技術設計書の内容

##### create_tasks_doc(project_name: str) -> str
実装計画書を作成します。

**パラメータ:**
- `project_name` (str): プロジェクト名

**戻り値:**
- str: 実装計画書の内容

##### create_failing_test(feature_name: str) -> str
TDD RED Phaseの失敗テストを作成します。

**パラメータ:**
- `feature_name` (str): 機能名

**戻り値:**
- str: テストコード

##### execute_new_project_flow(project_name: str) -> str
新規プロジェクトの完全なワークフローを実行します。

**パラメータ:**
- `project_name` (str): プロジェクト名

**戻り値:**
- str: 実行結果

##### execute_existing_project_flow(project_name: str) -> str
既存プロジェクトの修正フローを実行します。

**パラメータ:**
- `project_name` (str): プロジェクト名

**戻り値:**
- str: 実行結果

---

## Auto Mode システム

### AutoMode クラス

自動モードの管理を行うメインクラス

```python
from claude.core.auto_mode import AutoMode

auto_mode = AutoMode()
```

#### メソッド

##### start() -> None
Auto Modeを開始します。

```python
auto_mode.start()
```

##### stop() -> None
Auto Modeを停止します。

```python
auto_mode.stop()
```

##### is_active() -> bool
Auto Modeがアクティブかどうかを確認します。

**戻り値:**
- bool: アクティブな場合True

### AutoModeConfig クラス

Auto Modeの設定管理

```python
from claude.core.auto_mode_config import AutoModeConfig

config = AutoModeConfig()
```

#### メソッド

##### get(key: str, default=None) -> Any
設定値を取得します。

**パラメータ:**
- `key` (str): 設定キー
- `default`: デフォルト値

**戻り値:**
- Any: 設定値

##### set(key: str, value: Any) -> None
設定値を更新します。

**パラメータ:**
- `key` (str): 設定キー
- `value` (Any): 設定値

### AutoModeStateManager クラス

Auto Modeの状態管理

```python
from claude.core.auto_mode_state import AutoModeStateManager

state_manager = AutoModeStateManager()
```

#### メソッド

##### get_state() -> str
現在の状態を取得します。

**戻り値:**
- str: 状態 ('active', 'inactive', 'paused')

##### activate() -> None
状態をアクティブに変更します。

##### deactivate() -> None
状態を非アクティブに変更します。

---

## Development Rules システム

### DevelopmentRules クラス

開発ルールの管理と適用

```python
from claude.core.development_rules import DevelopmentRules

dev_rules = DevelopmentRules()
```

#### メソッド

##### apply_rules(project_name: str) -> dict
プロジェクトに開発ルールを適用します。

**パラメータ:**
- `project_name` (str): プロジェクト名

**戻り値:**
- dict: 適用結果

### ChecklistManager クラス

チェックリスト管理（教訓1）

```python
from claude.core.dev_rules_checklist import ChecklistManager

checklist_mgr = ChecklistManager()
```

#### メソッド

##### create_checklist(name: str) -> list
新しいチェックリストを作成します。

**パラメータ:**
- `name` (str): チェックリスト名

**戻り値:**
- list: チェックリスト

##### add_item(checklist_name: str, item: str) -> None
チェックリストに項目を追加します。

**パラメータ:**
- `checklist_name` (str): チェックリスト名
- `item` (str): 追加する項目

### TDDWorkflowManager クラス

TDDワークフロー管理（教訓2）

```python
from claude.core.dev_rules_tdd import TDDWorkflowManager

tdd_mgr = TDDWorkflowManager()
```

#### メソッド

##### start_red_phase(feature: str) -> str
RED Phaseを開始します。

**パラメータ:**
- `feature` (str): 機能名

**戻り値:**
- str: RED Phase結果

##### start_green_phase(feature: str) -> str
GREEN Phaseを開始します。

**パラメータ:**
- `feature` (str): 機能名

**戻り値:**
- str: GREEN Phase結果

##### start_refactor_phase(feature: str) -> str
REFACTOR Phaseを開始します。

**パラメータ:**
- `feature` (str): 機能名

**戻り値:**
- str: REFACTOR Phase結果

### TaskManager クラス

タスク管理（教訓3）

```python
from claude.core.dev_rules_tasks import TaskManager

task_mgr = TaskManager()
```

#### メソッド

##### create_task(description: str, status: str = "pending") -> str
新しいタスクを作成します。

**パラメータ:**
- `description` (str): タスクの説明
- `status` (str): 初期状態 ('pending', 'in_progress', 'completed')

**戻り値:**
- str: タスクID

##### update_task_status(task_id: str, status: str) -> None
タスクの状態を更新します。

**パラメータ:**
- `task_id` (str): タスクID
- `status` (str): 新しい状態

##### complete_task(task_id: str) -> None
タスクを完了状態にします。

**パラメータ:**
- `task_id` (str): タスクID

---

## ユーティリティ

### PathUtils クラス

クロスプラットフォーム対応のパスユーティリティ

```python
from claude.core.path_utils import PathUtils
```

#### 静的メソッド

##### normalize_path(path: Union[str, Path]) -> Path
パスを正規化します（OS依存の差異を吸収）。

**パラメータ:**
- `path` (Union[str, Path]): 正規化するパス

**戻り値:**
- Path: 正規化されたPathオブジェクト

**例:**
```python
normalized = PathUtils.normalize_path("C:\\Users\\test\\file.txt")
```

##### join_paths(*paths: Union[str, Path]) -> Path
複数のパスを結合します。

**パラメータ:**
- `*paths`: 結合するパス群

**戻り値:**
- Path: 結合されたパス

**例:**
```python
full_path = PathUtils.join_paths("base", "sub", "file.txt")
```

##### get_relative_path(path: Union[str, Path], base: Union[str, Path] = None) -> Path
相対パスを取得します。

**パラメータ:**
- `path`: 対象パス
- `base`: 基準パス（省略時は現在のディレクトリ）

**戻り値:**
- Path: 相対パス

##### ensure_dir(path: Union[str, Path]) -> Path
ディレクトリの存在を保証します（なければ作成）。

**パラメータ:**
- `path`: ディレクトリパス

**戻り値:**
- Path: 作成/確認されたディレクトリパス

##### list_files(directory: Union[str, Path], pattern: str = "*", recursive: bool = False) -> List[Path]
ディレクトリ内のファイルをリストします。

**パラメータ:**
- `directory`: 検索ディレクトリ
- `pattern`: ファイルパターン（glob形式）
- `recursive`: 再帰的に検索するか

**戻り値:**
- List[Path]: マッチしたファイルのリスト

##### get_project_root() -> Path
プロジェクトルートディレクトリを取得します。

**戻り値:**
- Path: プロジェクトルートパス

##### get_claude_dir() -> Path
.claudeディレクトリを取得します。

**戻り値:**
- Path: .claudeディレクトリパス

##### format_path_for_display(path: Union[str, Path], relative_to_project: bool = True) -> str
表示用にパスをフォーマットします。

**パラメータ:**
- `path`: フォーマットするパス
- `relative_to_project`: プロジェクトルートからの相対パスで表示

**戻り値:**
- str: 表示用のパス文字列

---

## 使用例

### 完全なワークフローの例

```python
from claude.core.unified_system import UnifiedSystem
from claude.core.auto_mode import AutoMode
from claude.core.development_rules import DevelopmentRules
from claude.core.path_utils import PathUtils

# プロジェクト初期化
project_name = "MyAwesomeProject"
project_root = PathUtils.get_project_root()

# システム初期化
system = UnifiedSystem(project_name)
auto_mode = AutoMode()
dev_rules = DevelopmentRules()

# Auto Mode開始
auto_mode.start()

# 開発ルール適用
rules_result = dev_rules.apply_rules(project_name)

# SDD+TDDワークフロー実行
if PathUtils.get_claude_dir().exists():
    # 新規プロジェクト
    result = system.execute_new_project_flow(project_name)
else:
    # 既存プロジェクト修正
    result = system.execute_existing_project_flow(project_name)

# Auto Mode停止
auto_mode.stop()

print(f"プロジェクト '{project_name}' の処理が完了しました")
```

### TDDサイクルの例

```python
from claude.core.dev_rules_tdd import TDDWorkflowManager

tdd = TDDWorkflowManager()
feature = "user_authentication"

# RED Phase - 失敗するテストを書く
red_result = tdd.start_red_phase(feature)
print(f"RED: {red_result}")

# GREEN Phase - テストを通す最小限の実装
green_result = tdd.start_green_phase(feature)
print(f"GREEN: {green_result}")

# REFACTOR Phase - コード品質改善
refactor_result = tdd.start_refactor_phase(feature)
print(f"REFACTOR: {refactor_result}")
```

---

## エラーハンドリング

すべてのAPIメソッドは適切なエラーハンドリングを実装しています：

```python
try:
    system = UnifiedSystem("MyProject")
    result = system.execute_new_project_flow("MyProject")
except ValueError as e:
    print(f"設定エラー: {e}")
except RuntimeError as e:
    print(f"実行時エラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

---

## バージョン情報

- **現在のバージョン**: 12.0.0
- **最終更新日**: 2025年8月23日
- **作成者**: アレックスチーム

## サポート

問題や質問がある場合は、プロジェクトのIssueトラッカーまでご連絡ください。

---

*このAPIリファレンスは、Claude Code SDD+TDDシステムのバージョン12.0.0に基づいています。*