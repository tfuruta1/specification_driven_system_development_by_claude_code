#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合絵文字検証システム - Claude Code Core v11.0
分割されたモジュールを統合するメインインターフェース

CTOとアレックスの品質管理要件に対応
"""

from typing import List, Dict, Any
from .emoji_core import EmojiCoreValidator
from .emoji_file_scanner import EmojiFileScanner
from .emoji_patterns import get_replacement_suggestions
from .emoji_utils import (
    validate_text, clean_text, scan_file_for_emojis, 
    clean_file, scan_project, is_validation_enabled,
    get_emoji_suggestions
)

class EmojiValidator:
    """統合絵文字検証システム（メインインターフェース）"""
    
    def __init__(self):
        """バリデーターの初期化"""
        self.core_validator = EmojiCoreValidator()
        self.file_scanner = EmojiFileScanner()
    
    # コアバリデーション機能への委譲
    def is_validation_enabled(self) -> bool:
        """検証が有効かどうか"""
        return self.core_validator.is_validation_enabled()
    
    def detect_emojis(self, text: str) -> List[str]:
        """テキスト内の絵文字を検出"""
        return self.core_validator.detect_emojis(text)
    
    def remove_emojis(self, text: str) -> str:
        """テキストから絵文字を除去"""
        return self.core_validator.remove_emojis(text)
    
    def replace_emojis_with_text(self, text: str) -> str:
        """絵文字を対応するテキストに置換"""
        return self.core_validator.replace_emojis_with_text(text)
    
    def validate_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """コンテンツの絵文字検証"""
        return self.core_validator.validate_content(content, content_type)
    
    # ファイルスキャン機能への委譲
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """ファイルスキャン"""
        return self.file_scanner.scan_file(file_path)
    
    def clean_file(self, file_path: str, backup: bool = True) -> Dict[str, Any]:
        """ファイルクリーンアップ"""
        return self.file_scanner.clean_file(file_path, backup)
    
    def scan_project(self, project_path: str = None) -> Dict[str, Any]:
        """プロジェクト全体の絵文字スキャン"""
        return self.file_scanner.scan_project(project_path)
    
    def get_replacement_suggestions(self, emoji: str) -> List[str]:
        """絵文字の置換候補を提案"""
        return get_replacement_suggestions(emoji)

# シングルトンインスタンス（統合システム用）
emoji_validator = EmojiValidator()

# 後方互換性のための便利関数（emoji_utilsから再エクスポート）
from .emoji_utils import validate_text, clean_text, scan_file_for_emojis

# デモ・テスト実行
if __name__ == "__main__":
    from .emoji_utils import (
        validate_text as util_validate_text, 
        clean_text as util_clean_text, 
        is_validation_enabled
    )
    
    print("=== 統合絵文字検証システム v11.0（分割版） ===")
    
    # 基本テスト
    test_text = "CTOとアレックス 🤝 ペアプログラミング 💻 テスト完了 🎉"
    
    print(f"元のテキスト: {test_text}")
    print(f"検証結果: {'有効' if util_validate_text(test_text) else '無効'}")
    print(f"クリーンテキスト: {util_clean_text(test_text)}")
    print(f"検証有効: {is_validation_enabled()}")
    
    # モジュール分割確認
    print("\n=== 分割されたモジュール ===")
    print("- emoji_core.py: コアバリデーション")
    print("- emoji_patterns.py: パターンと置換マップ")
    print("- emoji_file_scanner.py: ファイルスキャン機能")
    print("- emoji_utils.py: ユーティリティ関数")