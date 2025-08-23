#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
絵文字コアバリデーションシステム - Claude Code Core v11.0
EmojiValidatorから分離されたコアバリデーション機能
"""

import re
from typing import List, Dict, Any
from .config import get_config
from .logger import logger
from .emoji_patterns import EMOJI_REPLACEMENTS, EMOJI_PATTERN

class EmojiCoreValidator:
    """絵文字コアバリデーションシステム"""
    
    def __init__(self):
        """バリデーターの初期化"""
        self.config = get_config()
        
        # 設定から品質管理設定を取得
        self.quality_config = self.config.get_quality_config()
        self.validation_enabled = self.quality_config.get('emoji_validation', True)
        
        # パターンと置換マップの参照
        self.emoji_replacements = EMOJI_REPLACEMENTS
        self.emoji_pattern = EMOJI_PATTERN
    
    def is_validation_enabled(self) -> bool:
        """検証が有効かどうか"""
        return self.validation_enabled
    
    def detect_emojis(self, text: str) -> List[str]:
        """
        テキスト内の絵文字を検出
        
        Args:
            text: 検索対象テキスト
            
        Returns:
            検出された絵文字のリスト
        """
        if not text or not self.is_validation_enabled():
            return []
        
        try:
            # 正規表現で絵文字を検出
            emoji_matches = self.emoji_pattern.findall(text)
            
            # 重複を除去
            unique_emojis = list(set(emoji_matches))
            
            if unique_emojis:
                logger.debug(f"絵文字検出: {unique_emojis}", "EMOJI")
            
            return unique_emojis
            
        except Exception as e:
            logger.error(f"絵文字検出エラー: {e}", "EMOJI")
            return []
    
    def remove_emojis(self, text: str) -> str:
        """
        テキストから絵文字を除去
        
        Args:
            text: 対象テキスト
            
        Returns:
            絵文字が除去されたテキスト
        """
        if not text:
            return text
        
        if not self.is_validation_enabled():
            return text
        
        try:
            # 絵文字を空文字で置換
            cleaned_text = self.emoji_pattern.sub('', text)
            
            # 連続する空白を整理
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            logger.debug(f"絵文字除去: '{text[:50]}...' -> '{cleaned_text[:50]}...'", "EMOJI")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"絵文字除去エラー: {e}", "EMOJI")
            return text
    
    def replace_emojis_with_text(self, text: str) -> str:
        """
        絵文字を対応するテキストに置換
        
        Args:
            text: 対象テキスト
            
        Returns:
            絵文字がテキストに置換されたテキスト
        """
        if not text:
            return text
        
        if not self.is_validation_enabled():
            return text
        
        try:
            result_text = text
            replaced_count = 0
            
            # 定義済み絵文字を対応テキストに置換
            for emoji, replacement in self.emoji_replacements.items():
                if emoji in result_text:
                    result_text = result_text.replace(emoji, replacement)
                    replaced_count += 1
            
            # 残りの未定義絵文字を除去
            result_text = self.remove_emojis(result_text)
            
            if replaced_count > 0:
                logger.info(f"絵文字置換完了: {replaced_count}個の絵文字を置換", "EMOJI")
            
            return result_text
            
        except Exception as e:
            logger.error(f"絵文字置換エラー: {e}", "EMOJI")
            return text
    
    def validate_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """
        コンテンツの絵文字検証（統合版）
        
        Args:
            content: 検証対象コンテンツ
            content_type: コンテンツタイプ（"commit", "log", "docs", "code"等）
            
        Returns:
            検証結果辞書
        """
        if not self.is_validation_enabled():
            return {
                "is_valid": True,
                "emojis_found": [],
                "cleaned_content": content,
                "content_type": content_type,
                "validation_skipped": True
            }
        
        try:
            detected_emojis = self.detect_emojis(content)
            is_valid = len(detected_emojis) == 0
            cleaned_content = self.replace_emojis_with_text(content)
            
            result = {
                "is_valid": is_valid,
                "emojis_found": detected_emojis,
                "cleaned_content": cleaned_content,
                "content_type": content_type,
                "original_length": len(content),
                "cleaned_length": len(cleaned_content),
                "validation_enabled": True
            }
            
            if not is_valid:
                logger.warning(f"{content_type}に絵文字検出: {detected_emojis}", "EMOJI")
                
                # 設定に応じて自動修正を提案
                if self.config.get('quality.auto_fix_emojis', False):
                    logger.info("自動修正が有効です", "EMOJI")
            
            return result
            
        except Exception as e:
            logger.error(f"コンテンツ検証エラー: {e}", "EMOJI")
            return {
                "is_valid": False,
                "emojis_found": [],
                "cleaned_content": content,
                "content_type": content_type,
                "error": str(e)
            }