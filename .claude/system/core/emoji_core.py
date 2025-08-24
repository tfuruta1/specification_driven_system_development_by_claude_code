import copy
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTEM - Claude Code Core v11.0
EmojiValidatorCONFIG
"""

import re
from typing import List, Dict, Any
from .config import get_config
from .logger import logger
from .emoji_patterns import EMOJI_REPLACEMENTS, EMOJI_PATTERN

class EmojiCoreValidator:
    """CONFIG"""
    
    def __init__(self):
        """CONFIG"""
        self.config = get_config()
        
        # CONFIG
        self.quality_config = self.config.get_quality_config()
        self.validation_enabled = self.quality_config.get('emoji_validation', True)
        
        # CONFIG
        self.emoji_replacements = EMOJI_REPLACEMENTS
        self.emoji_pattern = EMOJI_PATTERN
    
    def is_validation_enabled(self) -> bool:
        """"""
        return self.validation_enabled
    
    def detect_emojis(self, text: str) -> List[str]:
        """
        
        
        Args:
            text: 
            
        Returns:
            
        """
        if not text or not self.is_validation_enabled():
            return []
        
        try:
            # 
            emoji_matches = self.emoji_pattern.findall(text)
            
            # 
            unique_emojis = list(set(emoji_matches))
            
            if unique_emojis:
                logger.debug(f": {unique_emojis}", "EMOJI")
            
            return unique_emojis
            
        except Exception as e:
            logger.error(f"ERROR: {e}", "EMOJI")
            return []
    
    def remove_emojis(self, text: str) -> str:
        """
        
        
        Args:
            text: 
            
        Returns:
            
        """
        if not text:
            return text
        
        if not self.is_validation_enabled():
            return text
        
        try:
            # 
            cleaned_text = self.emoji_pattern.sub('', text)
            
            # 
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            logger.debug(f": '{text[:50]}...' -> '{cleaned_text[:50]}...'", "EMOJI")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"ERROR: {e}", "EMOJI")
            return text
    
    def replace_emojis_with_text(self, text: str) -> str:
        """
        
        
        Args:
            text: 
            
        Returns:
            
        """
        if not text:
            return text
        
        if not self.is_validation_enabled():
            return text
        
        try:
            result_text = text
            replaced_count = 0
            
            # REPORT
            for emoji, replacement in self.emoji_replacements.items():
                if emoji in result_text:
                    result_text = result_text.replace(emoji, replacement)
                    replaced_count += 1
            
            # REPORT
            result_text = self.remove_emojis(result_text)
            
            if replaced_count > 0:
                logger.info(f"REPORT: {replaced_count}ERROR", "EMOJI")
            
            return result_text
            
        except Exception as e:
            logger.error(f"ERROR: {e}", "EMOJI")
            return text
    
    def validate_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """
        
        
        Args:
            content: 
            content_type: "commit", "log", "docs", "code"
            
        Returns:
            
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
                logger.warning(f"{content_type}WARNING: {detected_emojis}", "EMOJI")
                
                # WARNING
                if self.config.get('quality.auto_fix_emojis', False):
                    logger.info("ERROR", "EMOJI")
            
            return result
            
        except Exception as e:
            logger.error(f"ERROR: {e}", "EMOJI")
            return {
                "is_valid": False,
                "emojis_found": [],
                "cleaned_content": content,
                "content_type": content_type,
                "error": str(e)
            }