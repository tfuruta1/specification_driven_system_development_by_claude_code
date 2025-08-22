#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合絵文字検証システム - Claude Code Core v11.0
PythonCodeから移行・改良された絵文字検出・除去・置換システム

CTOとアレックスの品質管理要件に対応
"""

import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional
from .config import get_config
from .logger import logger

class EmojiValidator:
    """統合絵文字検証システム"""
    
    def __init__(self):
        """バリデーターの初期化"""
        self.config = get_config()
        
        # 設定から品質管理設定を取得
        self.quality_config = self.config.get_quality_config()
        self.validation_enabled = self.quality_config.get('emoji_validation', True)
        
        # 標準的な絵文字置換マッピング（CTOとアレックス用に拡張）
        self.emoji_replacements = {
            # 基本的なステータス
            "✅": "[OK]",
            "❌": "[NG]", 
            "🎉": "[完了]",
            "🔧": "[修正]",
            "📋": "[リスト]",
            "🧪": "[テスト]",
            "📝": "[メモ]",
            "🚀": "[開始]",
            "⚠️": "[警告]",
            "ℹ️": "[情報]",
            "🔍": "[検索]",
            "💡": "[アイデア]",
            "📊": "[データ]",
            "🔐": "[セキュリティ]",
            "🌟": "[重要]",
            
            # 開発関連
            "👨‍💻": "[開発者]",
            "👩‍💻": "[開発者]",
            "💻": "[PC]",
            "📱": "[モバイル]",
            "🔄": "[更新]",
            "📤": "[送信]",
            "📥": "[受信]",
            "🎯": "[対象]",
            
            # SDD+TDD関連
            "📐": "[設計]",
            "📑": "[仕様書]",
            "🧩": "[モジュール]",
            "⚙️": "[設定]",
            "🔗": "[統合]",
            "📈": "[進捗]",
            "🏁": "[目標]",
            
            # ペアプログラミング関連
            "🤝": "[協力]",
            "💬": "[対話]",
            "🔊": "[発言]",
            "👥": "[チーム]",
            "🎪": "[デモ]",
            
            # 品質管理関連
            "🔎": "[レビュー]",
            "📏": "[測定]",
            "⚖️": "[評価]",
            "🎖️": "[品質]",
            "🛠️": "[ツール]"
        }
        
        # Unicode絵文字の包括的な範囲パターン
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # 顔文字
            "\U0001F300-\U0001F5FF"  # その他のシンボル
            "\U0001F680-\U0001F6FF"  # 交通・地図シンボル
            "\U0001F1E0-\U0001F1FF"  # 国旗
            "\U00002600-\U000026FF"  # その他のシンボル
            "\U00002700-\U000027BF"  # Dingbats
            "\U0001F900-\U0001F9FF"  # 追加シンボル
            "\U0001FA70-\U0001FAFF"  # 追加シンボル（拡張A）
            "\U00002190-\U000021FF"  # 矢印
            "\U0000FE00-\U0000FE0F"  # バリエーションセレクター
            "\U0000200D"             # ゼロ幅結合子
            "]+",
            re.UNICODE
        )
    
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
                line_emojis = self.detect_emojis(line)
                if line_emojis:
                    all_emojis.extend(line_emojis)
                    emoji_lines.append({
                        "line_number": line_num,
                        "content": line.strip(),
                        "emojis": line_emojis,
                        "cleaned_content": self.replace_emojis_with_text(line.strip())
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
                "validation_enabled": self.is_validation_enabled()
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
    
    def _determine_file_type(self, file_path: Path) -> str:
        """ファイルタイプの判定"""
        suffix = file_path.suffix.lower()
        
        file_type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript', 
            '.vue': 'vue',
            '.md': 'markdown',
            '.txt': 'text',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.log': 'log'
        }
        
        return file_type_map.get(suffix, 'unknown')
    
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
    
    def clean_file(self, file_path: str, backup: bool = True) -> Dict[str, Any]:
        """
        ファイルクリーンアップ（強化版）
        
        Args:
            file_path: 対象ファイルパス
            backup: バックアップを作成するかどうか
            
        Returns:
            クリーンアップ結果
        """
        if not self.is_validation_enabled():
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
            validation_result = self.validate_content(original_content, self._determine_file_type(file_path))
            
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
    
    def get_replacement_suggestions(self, emoji: str) -> List[str]:
        """
        絵文字の置換候補を提案（新機能）
        
        Args:
            emoji: 対象絵文字
            
        Returns:
            置換候補のリスト
        """
        # 既知の置換がある場合
        if emoji in self.emoji_replacements:
            return [self.emoji_replacements[emoji]]
        
        # 類似絵文字から推測
        suggestions = []
        
        # カテゴリ別の一般的な置換候補
        if emoji in "✅✓✔️":
            suggestions.extend(["[OK]", "[完了]", "[成功]"])
        elif emoji in "❌✗✖️":
            suggestions.extend(["[NG]", "[失敗]", "[エラー]"])
        elif emoji in "⚠️⚡":
            suggestions.extend(["[警告]", "[注意]", "[重要]"])
        elif emoji in "📝📄📋":
            suggestions.extend(["[メモ]", "[文書]", "[記録]"])
        else:
            suggestions.append("[記号]")
        
        return suggestions

# シングルトンインスタンス（統合システム用）
emoji_validator = EmojiValidator()

# 便利関数
def validate_text(text: str) -> bool:
    """テキストに絵文字が含まれていないかチェック"""
    return emoji_validator.validate_content(text)["is_valid"]

def clean_text(text: str) -> str:
    """テキストから絵文字を除去/置換"""
    return emoji_validator.replace_emojis_with_text(text)

def scan_file_for_emojis(file_path: str) -> Dict[str, Any]:
    """ファイルの絵文字スキャン"""
    return emoji_validator.scan_file(file_path)

# デモ・テスト実行
if __name__ == "__main__":
    print("=== 統合絵文字検証システム v11.0 ===")
    
    # 基本テスト
    test_text = "CTOとアレックス 🤝 ペアプログラミング 💻 テスト完了 🎉"
    
    print(f"元のテキスト: {test_text}")
    print(f"検出絵文字: {emoji_validator.detect_emojis(test_text)}")
    print(f"クリーンテキスト: {emoji_validator.replace_emojis_with_text(test_text)}")
    
    # 設定状態表示
    print(f"\n検証有効: {emoji_validator.is_validation_enabled()}")
    print(f"設定ファイル: {emoji_validator.config.config_file}")