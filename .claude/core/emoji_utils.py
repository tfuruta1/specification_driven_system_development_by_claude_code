#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
絵文字ユーティリティ関数 - Claude Code Core v11.0
EmojiValidatorから分離されたユーティリティ関数とヘルパー
"""

from typing import Dict, Any
from .emoji_core import EmojiCoreValidator
from .emoji_file_scanner import EmojiFileScanner
from .emoji_patterns import get_replacement_suggestions

# シングルトンインスタンス（統合システム用）
_core_validator = None
_file_scanner = None

def get_core_validator():
    """コアバリデーターのシングルトンインスタンスを取得"""
    global _core_validator
    if _core_validator is None:
        _core_validator = EmojiCoreValidator()
    return _core_validator

def get_file_scanner():
    """ファイルスキャナーのシングルトンインスタンスを取得"""
    global _file_scanner
    if _file_scanner is None:
        _file_scanner = EmojiFileScanner()
    return _file_scanner

# 便利関数
def validate_text(text: str) -> bool:
    """テキストに絵文字が含まれていないかチェック"""
    return get_core_validator().validate_content(text)["is_valid"]

def clean_text(text: str) -> str:
    """テキストから絵文字を除去/置換"""
    return get_core_validator().replace_emojis_with_text(text)

def scan_file_for_emojis(file_path: str) -> Dict[str, Any]:
    """ファイルの絵文字スキャン"""
    return get_file_scanner().scan_file(file_path)

def clean_file(file_path: str, backup: bool = True) -> Dict[str, Any]:
    """ファイルの絵文字クリーンアップ"""
    return get_file_scanner().clean_file(file_path, backup)

def scan_project(project_path: str = None) -> Dict[str, Any]:
    """プロジェクト全体の絵文字スキャン"""
    return get_file_scanner().scan_project(project_path)

def is_validation_enabled() -> bool:
    """絵文字検証が有効かどうか"""
    return get_core_validator().is_validation_enabled()

def get_emoji_suggestions(emoji: str):
    """絵文字の置換候補を取得"""
    return get_replacement_suggestions(emoji)

# デモ・テスト実行
if __name__ == "__main__":
    print("=== 絵文字ユーティリティシステム v11.0 ===")
    
    # 基本テスト
    test_text = "CTOとアレックス 🤝 ペアプログラミング 💻 テスト完了 🎉"
    
    print(f"元のテキスト: {test_text}")
    print(f"検証結果: {'有効' if validate_text(test_text) else '無効'}")
    print(f"クリーンテキスト: {clean_text(test_text)}")
    print(f"検証有効: {is_validation_enabled()}")
    
    # 置換候補テスト
    emojis = ["🤝", "💻", "🎉", "🔥"]
    for emoji in emojis:
        suggestions = get_emoji_suggestions(emoji)
        print(f"絵文字 '{emoji}' の置換候補: {suggestions}")