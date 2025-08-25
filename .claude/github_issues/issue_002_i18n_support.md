# Issue #2: 国際化(i18n)対応の実装

## 概要
ハードコーディングされた日本語メッセージを国際化対応に変更

## 背景
現在、エラーメッセージや通知が日本語でハードコーディングされており、他言語への対応が困難

## タスク

### 1. メッセージ管理モジュールの作成
**新規ファイル**: `.claude/system/core/i18n.py`
```python
from typing import Dict, Any
from pathlib import Path
import json

class I18n:
    """国際化対応メッセージ管理"""
    
    def __init__(self, lang: str = 'ja'):
        self.lang = lang
        self.messages: Dict[str, Dict[str, str]] = {}
        self._load_messages()
    
    def _load_messages(self) -> None:
        """メッセージファイルを読み込み"""
        messages_dir = Path(__file__).parent / 'messages'
        for lang_file in messages_dir.glob('*.json'):
            lang_code = lang_file.stem
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.messages[lang_code] = json.load(f)
    
    def get(self, key: str, **kwargs: Any) -> str:
        """メッセージを取得"""
        message = self.messages.get(self.lang, {}).get(key, key)
        return message.format(**kwargs) if kwargs else message
    
    def set_language(self, lang: str) -> None:
        """言語を設定"""
        self.lang = lang

# グローバルインスタンス
i18n = I18n()
```

### 2. メッセージファイルの作成
**新規ファイル**: `.claude/system/core/messages/ja.json`
```json
{
  "file_organized": "{count}個のファイルを整理しました",
  "cleanup_complete": "{count}個のアイテムをクリーンアップしました",
  "test_passed": "テストが成功しました",
  "test_failed": "テストが失敗しました",
  "quality_check_passed": "コード品質チェックに合格しました",
  "quality_check_failed": "{count}個の問題が見つかりました",
  "status_ok": "ステータス取得成功",
  "unknown_command": "不明なコマンド: {command}",
  "file_not_found": "ファイルが見つかりません: {file}",
  "permission_denied": "アクセス権限がありません: {file}"
}
```

**新規ファイル**: `.claude/system/core/messages/en.json`
```json
{
  "file_organized": "Organized {count} files",
  "cleanup_complete": "Cleaned {count} items",
  "test_passed": "Tests passed",
  "test_failed": "Tests failed",
  "quality_check_passed": "Code quality check passed",
  "quality_check_failed": "Found {count} issues",
  "status_ok": "Status retrieved",
  "unknown_command": "Unknown command: {command}",
  "file_not_found": "File not found: {file}",
  "permission_denied": "Permission denied: {file}"
}
```

### 3. CoreSystemクラスの修正
**ファイル**: `.claude/system/core/core_system.py`

**変更前**:
```python
def organize_files(self) -> Result:
    # ...
    return Result(True, f"Organized {moved_count} files")
```

**変更後**:
```python
from .i18n import i18n

def organize_files(self) -> Result:
    # ...
    message = i18n.get("file_organized", count=moved_count)
    return Result(True, message)
```

### 4. 設定ファイルに言語設定を追加
**ファイル**: `.claude/config/system_config.json`
```json
{
  "language": "ja",
  "temp_max_age_hours": 24,
  "auto_cleanup": true,
  "test_coverage_target": 100.0
}
```

### 5. CLIコマンドに言語切り替えオプションを追加
**ファイル**: `.claude/claude`
```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('--lang', default='ja', choices=['ja', 'en'], 
                       help='Language (ja/en)')
    args = parser.parse_args()
    
    # 言語設定
    i18n.set_language(args.lang)
    
    # コマンド実行
    # ...
```

## 受け入れ条件
- [ ] 日本語と英語のメッセージファイルが存在する
- [ ] すべてのハードコーディングされたメッセージが置き換えられている
- [ ] 言語切り替えが正常に動作する
- [ ] テストが全て通る

## 実装手順
1. i18n.pyモジュールを作成
2. messagesディレクトリとJSONファイルを作成
3. CoreSystemクラスのメッセージをi18n化
4. CLIに言語オプションを追加
5. テストを実行して動作確認

## 優先度
**高**

## 見積もり工数
3-4時間

## ラベル
- enhancement
- i18n
- user-experience