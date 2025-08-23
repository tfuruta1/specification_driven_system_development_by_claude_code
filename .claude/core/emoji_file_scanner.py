#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
絵文字ファイルスキャナー - Claude Code Core v11.0
EmojiValidatorから分離されたファイルスキャン機能
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from .config import get_config
from .logger import logger
from .emoji_core import EmojiCoreValidator
from .emoji_patterns import FILE_TYPE_MAP

class EmojiFileScanner:
    """絵文字ファイルスキャナー"""
    
    def __init__(self):
        """スキャナーの初期化"""
        self.config = get_config()
        self.core_validator = EmojiCoreValidator()
    
    def _determine_file_type(self, file_path: Path) -> str:
        """ファイルタイプの判定"""
        suffix = file_path.suffix.lower()
        return FILE_TYPE_MAP.get(suffix, 'unknown')
    
    def _read_file_with_encoding(self, file_path: Path) -> Optional[str]:
        """複数エンコーディングでファイル読み込み"""
        encodings = ['utf-8', 'utf-8-sig', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f"ファイル読み込み成功: {file_path.name} (encoding: {encoding})", "EMOJI")
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                logger.error(f"ファイル読み込みエラー ({file_path.name}, {encoding}): {e}", "EMOJI")
                continue
        
        logger.error(f"全エンコーディングでファイル読み込み失敗: {file_path}", "EMOJI")
        return None
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        ファイルスキャン（強化版）
        
        Args:
            file_path: スキャン対象ファイルパス
            
        Returns:
            スキャン結果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "error": "ファイルが見つかりません"
            }
        
        # ファイルタイプの判定
        file_type = self._determine_file_type(file_path)
        
        try:
            # ファイル読み込み
            content = self._read_file_with_encoding(file_path)
            
            if content is None:
                return {
                    "success": False,
                    "file_path": str(file_path),
                    "error": "ファイル読み込みに失敗しました"
                }
            
            lines = content.split('\n')
            all_emojis = []
            emoji_lines = []
            
            # 行ごとの絵文字チェック
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
                logger.info(f"ファイル '{file_path.name}' で{len(unique_emojis)}種類の絵文字を検出", "EMOJI")
            
            return result
            
        except Exception as e:
            logger.error(f"ファイルスキャンエラー ({file_path}): {e}", "EMOJI")
            return {
                "success": False,
                "file_path": str(file_path),
                "error": str(e)
            }
    
    def clean_file(self, file_path: str, backup: bool = True) -> Dict[str, Any]:
        """
        ファイルクリーンアップ（強化版）
        
        Args:
            file_path: 対象ファイルパス
            backup: バックアップを作成するかどうか
            
        Returns:
            クリーンアップ結果
        """
        if not self.core_validator.is_validation_enabled():
            return {
                "success": True,
                "file_path": file_path,
                "changed": False,
                "message": "絵文字検証が無効化されています"
            }
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "file_path": str(file_path),
                "error": "ファイルが見つかりません"
            }
        
        try:
            # 現在のファイル内容を読み込み
            original_content = self._read_file_with_encoding(file_path)
            if original_content is None:
                return {
                    "success": False,
                    "file_path": str(file_path),
                    "error": "ファイル読み込みに失敗しました"
                }
            
            # 絵文字検証
            validation_result = self.core_validator.validate_content(
                original_content, self._determine_file_type(file_path)
            )
            
            if validation_result["is_valid"]:
                return {
                    "success": True,
                    "file_path": str(file_path),
                    "changed": False,
                    "message": "絵文字は見つかりませんでした"
                }
            
            # バックアップ作成
            if backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.emoji_backup")
                backup_path.write_text(original_content, encoding='utf-8')
                logger.info(f"バックアップ作成: {backup_path.name}", "EMOJI")
            
            # クリーンアップされたコンテンツを書き込み
            cleaned_content = validation_result["cleaned_content"]
            file_path.write_text(cleaned_content, encoding='utf-8')
            
            logger.info(f"ファイルクリーンアップ完了: {file_path.name}", "EMOJI")
            
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
            logger.error(f"ファイルクリーンアップエラー ({file_path}): {e}", "EMOJI")
            return {
                "success": False,
                "file_path": str(file_path),
                "error": str(e)
            }
    
    def scan_project(self, project_path: str = None) -> Dict[str, Any]:
        """
        プロジェクト全体の絵文字スキャン（新機能）
        
        Args:
            project_path: プロジェクトルートパス（省略時は設定から取得）
            
        Returns:
            プロジェクトスキャン結果
        """
        if project_path is None:
            project_path = self.config.get_project_paths()['root']
        else:
            project_path = Path(project_path)
        
        if not project_path.exists():
            return {
                "success": False,
                "error": f"プロジェクトパスが見つかりません: {project_path}"
            }
        
        # スキャン対象ファイルパターン
        scan_patterns = ['*.py', '*.js', '*.ts', '*.vue', '*.md', '*.json', '*.txt']
        
        scanned_files = []
        total_emojis = 0
        problematic_files = []
        
        try:
            for pattern in scan_patterns:
                for file_path in project_path.rglob(pattern):
                    # 除外ディレクトリのスキップ
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
                logger.warning(f"プロジェクト内で{total_emojis}個の絵文字を検出（{len(problematic_files)}ファイル）", "EMOJI")
            else:
                logger.info("プロジェクト内に絵文字は見つかりませんでした", "EMOJI")
            
            return result
            
        except Exception as e:
            logger.error(f"プロジェクトスキャンエラー: {e}", "EMOJI")
            return {
                "success": False,
                "error": str(e)
            }