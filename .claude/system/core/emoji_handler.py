#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合Emojiハンドラー - YAGNI原則適用リファクタリング版
5つの分離されたemojiモジュールを統合して、本当に必要な機能だけを提供

YAGNI: 現在使用されている機能のみ実装
DRY: 重複機能を統合
KISS: 複雑な抽象化を削除してシンプル化
TDD: 100%テストカバレッジ維持
"""

import re
from typing import Dict, List, Optional, Set
from pathlib import Path

# 共通基盤を使用してDRY原則適用
from .common_base import BaseManager, BaseResult, create_result

class EmojiHandler(BaseManager):
    """統合emoji処理クラス - 全emoji機能を一箇所に集約"""
    
    # 基本的なemoji置換パターン（実際に使用されているもののみ）
    BASIC_REPLACEMENTS = {
        # 実行状態系
        ':check:': '✅',
        ':cross:': '❌', 
        ':warning:': '⚠️',
        ':info:': 'ℹ️',
        ':success:': '🎉',
        ':error:': '🚨',
        ':fire:': '🔥',
        ':rocket:': '🚀',
        ':star:': '⭐',
        ':thumbs_up:': '👍',
        ':thumbs_down:': '👎',
        
        # プロジェクト系
        ':folder:': '📁',
        ':file:': '📄',
        ':gear:': '⚙️',
        ':wrench:': '🔧',
        ':hammer:': '🔨',
        ':mag:': '🔍',
        ':chart:': '📊',
        ':trophy:': '🏆',
        ':target:': '🎯',
        ':bulb:': '💡'
    }
    
    # Unicode emoji検出パターン（より正確な範囲）
    EMOJI_PATTERN = re.compile(
        r'[\U0001F600-\U0001F64F]|'  # 顔文字
        r'[\U0001F300-\U0001F5FF]|'  # その他のシンボル
        r'[\U0001F680-\U0001F6FF]|'  # 交通・地図
        r'[\U0001F1E0-\U0001F1FF]|'  # 国旗
        r'[\U00002600-\U000026FF]|'  # その他記号（範囲修正）
        r'[\U0001F900-\U0001F9FF]|'  # 追加記号
        r'[\U00002700-\U000027BF]'   # 装飾記号
    )
    
    def __init__(self, enabled: bool = True):
        """
        Args:
            enabled: emoji処理の有効/無効フラグ
        """
        super().__init__("EmojiHandler", {"enabled": enabled})
        self.enabled = enabled
        self.replacement_cache: Dict[str, str] = {}
        self.stats = {
            "replacements_made": 0,
            "emojis_detected": 0,
            "files_processed": 0,
            "cache_hits": 0
        }
    
    def initialize(self) -> BaseResult:
        """初期化処理"""
        try:
            # 置換キャッシュをプリロード
            self.replacement_cache = self.BASIC_REPLACEMENTS.copy()
            self._initialized = True
            return create_result(True, f"EmojiHandler initialized with {len(self.replacement_cache)} patterns")
        except Exception as e:
            return create_result(False, f"Initialization failed: {e}")
    
    def cleanup(self) -> BaseResult:
        """クリーンアップ処理"""
        self.replacement_cache.clear()
        self.stats = {key: 0 for key in self.stats.keys()}
        self._initialized = False
        return create_result(True, "EmojiHandler cleaned up")
    
    def replace_emoji_codes(self, text: str) -> str:
        """
        テキスト内のemojiコードを実際のemojiに置換
        
        Args:
            text: 置換対象のテキスト
            
        Returns:
            置換後のテキスト
        """
        if not self.enabled or not text:
            return text
        
        # キャッシュチェック
        if text in self.replacement_cache:
            self.stats["cache_hits"] += 1
            return self.replacement_cache[text]
        
        result = text
        replacements_made = 0
        
        for code, emoji in self.BASIC_REPLACEMENTS.items():
            if code in result:
                result = result.replace(code, emoji)
                replacements_made += 1
        
        if replacements_made > 0:
            self.stats["replacements_made"] += replacements_made
            # 頻繁に使用されるパターンをキャッシュ
            if len(self.replacement_cache) < 100:
                self.replacement_cache[text] = result
        
        return result
    
    def detect_emojis(self, text: str) -> List[str]:
        """
        テキスト内のUnicode emojiを検出
        
        Args:
            text: 検出対象のテキスト
            
        Returns:
            検出されたemojiのリスト
        """
        if not self.enabled or not text:
            return []
        
        emojis = self.EMOJI_PATTERN.findall(text)
        if emojis:
            self.stats["emojis_detected"] += len(emojis)
        
        return emojis
    
    def has_emojis(self, text: str) -> bool:
        """
        テキストにemojiが含まれているかチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            emojiが含まれている場合True
        """
        return len(self.detect_emojis(text)) > 0
    
    def process_file(self, file_path: Path, replace_codes: bool = True) -> BaseResult:
        """
        ファイル内のemoji処理
        
        Args:
            file_path: 処理対象のファイルパス
            replace_codes: emojiコードを置換するかどうか
            
        Returns:
            処理結果
        """
        if not self.enabled:
            return create_result(False, "Emoji processing is disabled")
        
        try:
            if not file_path.exists():
                return create_result(False, f"File not found: {file_path}")
            
            # テキストファイルのみ処理
            if file_path.suffix not in {'.txt', '.md', '.py', '.json', '.yaml', '.yml'}:
                return create_result(False, f"Unsupported file type: {file_path.suffix}")
            
            # ファイル読み込み
            original_content = file_path.read_text(encoding='utf-8')
            
            # emoji処理
            processed_content = original_content
            if replace_codes:
                processed_content = self.replace_emoji_codes(original_content)
            
            # 検出統計
            detected_emojis = self.detect_emojis(processed_content)
            
            # 変更があった場合のみファイル更新
            if processed_content != original_content:
                file_path.write_text(processed_content, encoding='utf-8')
                changed = True
            else:
                changed = False
            
            self.stats["files_processed"] += 1
            
            return create_result(
                True, 
                f"Processed {file_path.name}",
                {
                    "file_path": str(file_path),
                    "emojis_detected": len(detected_emojis),
                    "content_changed": changed,
                    "detected_emojis": detected_emojis[:10]  # 最初の10個のみ
                }
            )
            
        except Exception as e:
            return create_result(False, f"Failed to process {file_path}: {e}")
    
    def scan_directory(self, directory: Path, pattern: str = "*.md") -> BaseResult:
        """
        ディレクトリ内のファイルをスキャンしてemoji処理
        
        Args:
            directory: スキャン対象ディレクトリ
            pattern: ファイルパターン
            
        Returns:
            スキャン結果
        """
        if not self.enabled:
            return create_result(False, "Emoji processing is disabled")
        
        try:
            if not directory.exists() or not directory.is_dir():
                return create_result(False, f"Directory not found: {directory}")
            
            files_processed = 0
            total_emojis = 0
            errors = []
            
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    result = self.process_file(file_path)
                    if result.success:
                        files_processed += 1
                        if result.data:
                            total_emojis += result.data.get("emojis_detected", 0)
                    else:
                        errors.append(result.message)
            
            return create_result(
                True,
                f"Scanned {files_processed} files in {directory}",
                {
                    "directory": str(directory),
                    "files_processed": files_processed,
                    "total_emojis_detected": total_emojis,
                    "errors": errors
                }
            )
            
        except Exception as e:
            return create_result(False, f"Failed to scan directory {directory}: {e}")
    
    def get_suggestions(self, emoji_code: str) -> List[str]:
        """
        未知のemojiコードに対する候補を提案
        
        Args:
            emoji_code: 候補を求めるemojiコード
            
        Returns:
            候補のリスト
        """
        if not self.enabled or not emoji_code:
            return []
        
        suggestions = []
        code_lower = emoji_code.lower()
        
        # 部分マッチで候補を検索
        for known_code in self.BASIC_REPLACEMENTS.keys():
            if code_lower in known_code.lower() or known_code.lower() in code_lower:
                suggestions.append(known_code)
        
        return suggestions[:5]  # 最大5個まで
    
    def add_custom_replacement(self, code: str, emoji: str) -> bool:
        """
        カスタムemoji置換を追加
        
        Args:
            code: emojiコード（例: ":custom:"）
            emoji: 実際のemoji
            
        Returns:
            追加に成功した場合True
        """
        if not self.enabled or not code or not emoji:
            return False
        
        # コードの正規化
        if not code.startswith(':') or not code.endswith(':'):
            code = f":{code.strip(':')}:"
        
        self.BASIC_REPLACEMENTS[code] = emoji
        # キャッシュクリア（新しい置換を反映するため）
        self.replacement_cache.clear()
        
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """処理統計を取得"""
        return self.stats.copy()
    
    def reset_stats(self):
        """統計をリセット"""
        self.stats = {key: 0 for key in self.stats.keys()}


# モジュールレベルのシングルトンインスタンス（KISS原則）
_default_handler: Optional[EmojiHandler] = None

def get_emoji_handler() -> EmojiHandler:
    """デフォルトのEmojiHandlerインスタンスを取得"""
    global _default_handler
    if _default_handler is None:
        _default_handler = EmojiHandler()
        _default_handler.initialize()
    return _default_handler

# 便利な関数（既存コードとの互換性のため）
def replace_emojis(text: str) -> str:
    """emoji置換の簡便関数"""
    return get_emoji_handler().replace_emoji_codes(text)

def detect_emojis_in_text(text: str) -> List[str]:
    """emoji検出の簡便関数"""
    return get_emoji_handler().detect_emojis(text)

def has_emojis_in_text(text: str) -> bool:
    """emoji存在確認の簡便関数"""
    return get_emoji_handler().has_emojis(text)


if __name__ == "__main__":
    # 基本テスト実行
    handler = EmojiHandler()
    result = handler.initialize()
    print(f"Emoji Handler: {result.message}")
    
    # テスト用文字列
    test_text = "Test :check: and :rocket: emojis! 🎉"
    processed = handler.replace_emoji_codes(test_text)
    detected = handler.detect_emojis(processed)
    
    print(f"Original: {test_text}")
    print(f"Processed: {processed}")
    print(f"Detected emojis: {detected}")
    print(f"Stats: {handler.get_stats()}")