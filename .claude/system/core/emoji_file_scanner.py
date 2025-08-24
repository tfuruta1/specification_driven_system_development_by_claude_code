#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTEM - Claude Code Core v11.0
EmojiValidatorCONFIG
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from .config import get_config
from .logger import logger
from .emoji_core import EmojiCoreValidator
from .emoji_patterns import FILE_TYPE_MAP

class EmojiFileScanner:
    """CONFIG"""
    
    def __init__(self):
        """CONFIG"""
        self.config = get_config()
        self.core_validator = EmojiCoreValidator()
    
    def _determine_file_type(self, file_path: Path) -> str:
        """SYSTEM"""
        suffix = file_path.suffix.lower()
        return FILE_TYPE_MAP.get(suffix, 'unknown')
    
    def _read_file_with_encoding(self, file_path: Path) -> Optional[str]:
        """"""
        encodings = ['utf-8', 'utf-8-sig', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f": {file_path.name} (encoding: {encoding})", "EMOJI")
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                logger.error(f"ERROR ({file_path.name}, {encoding}): {e}", "EMOJI")
                continue
        
        logger.error(f"ERROR: {file_path}", "EMOJI")
        return None
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        
        
        Args:
            file_path: 
            
        Returns:
            
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "error": "SUCCESS"
            }
        
        # ERROR
        file_type = self._determine_file_type(file_path)
        
        try:
            # 
            content = self._read_file_with_encoding(file_path)
            
            if content is None:
                return {
                    "success": False,
                    "file_path": str(file_path),
                    "error": "SUCCESS"
                }
            
            lines = content.split('\n')
            all_emojis = []
            emoji_lines = []
            
            # SYSTEM
            for line_num, line in enumerate(lines, 1):
                line_emojis = self.core_validator.detect_emojis(line)
                if line_emojis:
                    all_emojis.extend(line_emojis)
                    emoji_lines.append({
                        "line_number": line_num,
                        "content": line.strip(),
                        "emojis": line_emojis,
                        "cleaned_content": self.core_validator.replace_emojis_with_text(line.strip())
                    })
            
            unique_emojis = list(set(all_emojis))
            
            result = {
                "success": True,
                "file_path": str(file_path),
                "file_type": file_type,
                "emojis_found": unique_emojis,
                "line_count": len(lines),
                "emoji_lines": emoji_lines,
                "total_emoji_count": len(all_emojis),
                "unique_emoji_count": len(unique_emojis),
                "validation_enabled": self.core_validator.is_validation_enabled()
            }
            
            if unique_emojis:
                logger.info(f" '{file_path.name}' REPORT{len(unique_emojis)}ERROR", "EMOJI")
            
            return result
            
        except Exception as e:
            logger.error(f"SUCCESS ({file_path}): {e}", "EMOJI")
            return {
                "success": False,
                "file_path": str(file_path),
                "error": str(e)
            }
    
    def clean_file(self, file_path: str, backup: bool = True) -> Dict[str, Any]:
        """
        
        
        Args:
            file_path: 
            backup: SYSTEM
            
        Returns:
            SYSTEM
        """
        if not self.core_validator.is_validation_enabled():
            return {
                "success": True,
                "file_path": file_path,
                "changed": False,
                "message": ""
            }
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "error": "SUCCESS"
            }
        
        try:
            # ERROR
            original_content = self._read_file_with_encoding(file_path)
            if original_content is None:
                return {
                    "success": False,
                    "file_path": str(file_path),
                    "error": "SUCCESS"
                }
            
            # ERROR
            validation_result = self.core_validator.validate_content(
                original_content, self._determine_file_type(file_path)
            )
            
            if validation_result["is_valid"]:
                return {
                    "success": True,
                    "file_path": str(file_path),
                    "changed": False,
                    "message": ""
                }
            
            # 
            if backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.emoji_backup")
                backup_path.write_text(original_content, encoding='utf-8')
                logger.info(f": {backup_path.name}", "EMOJI")
            
            # REPORT
            cleaned_content = validation_result["cleaned_content"]
            file_path.write_text(cleaned_content, encoding='utf-8')
            
            logger.info(f"SUCCESS: {file_path.name}", "EMOJI")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "changed": True,
                "emojis_removed": validation_result["emojis_found"],
                "backup_created": backup,
                "backup_path": str(backup_path) if backup else None,
                "original_length": len(original_content),
                "cleaned_length": len(cleaned_content)
            }
            
        except Exception as e:
            logger.error(f"SUCCESS ({file_path}): {e}", "EMOJI")
            return {
                "success": False,
                "file_path": str(file_path),
                "error": str(e)
            }
    
    def scan_project(self, project_path: str = None) -> Dict[str, Any]:
        """
        
        
        Args:
            project_path: 
            
        Returns:
            CONFIG
        """
        if project_path is None:
            project_path = self.config.get_project_paths()['root']
        else:
            project_path = Path(project_path)
        
        if not project_path.exists():
            return {
                "success": False,
                "error": f"SUCCESS: {project_path}"
            }
        
        # ERROR
        scan_patterns = ['*.py', '*.js', '*.ts', '*.vue', '*.md', '*.json', '*.txt']
        
        scanned_files = []
        total_emojis = 0
        problematic_files = []
        
        try:
            for pattern in scan_patterns:
                for file_path in project_path.rglob(pattern):
                    # 
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    if 'node_modules' in file_path.parts:
                        continue
                    
                    scan_result = self.scan_file(str(file_path))
                    if scan_result['success']:
                        scanned_files.append(scan_result)
                        
                        if scan_result['unique_emoji_count'] > 0:
                            problematic_files.append({
                                'file': str(file_path.relative_to(project_path)),
                                'emoji_count': scan_result['unique_emoji_count'],
                                'emojis': scan_result['emojis_found']
                            })
                            total_emojis += scan_result['unique_emoji_count']
            
            result = {
                "success": True,
                "project_path": str(project_path),
                "scanned_files_count": len(scanned_files),
                "problematic_files_count": len(problematic_files),
                "total_unique_emojis": total_emojis,
                "problematic_files": problematic_files
            }
            
            if total_emojis > 0:
                logger.warning(f"WARNING{total_emojis}WARNING{len(problematic_files)}WARNING", "EMOJI")
            else:
                logger.info("ERROR", "EMOJI")
            
            return result
            
        except Exception as e:
            logger.error(f"SUCCESS: {e}", "EMOJI")
            return {
                "success": False,
                "error": str(e)
            }