#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for FileAccessLogger - ファイルアクセス目的表示システム
TDD Red Phase: 失敗するテストを先に書く
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, call
import json
import io
import sys
from datetime import datetime

# テスト対象のインポート（まだ存在しない）
try:
    from file_access_logger import (
        FileAccessLogger, 
        AccessPurpose,
        ColorTerminal
    )
except ImportError:
    # TDDのため、まだ実装されていない
    pass


class TestAccessPurpose:
    """アクセス目的列挙型のテスト"""
    
    def test_purpose_values(self):
        """アクセス目的の値が正しいこと"""
        assert AccessPurpose.MODIFY.value == "[修正対象]"
        assert AccessPurpose.REFERENCE.value == "[参照のみ]" 
        assert AccessPurpose.ANALYZE.value == "[解析中]"
    
    def test_purpose_colors(self):
        """アクセス目的の色が正しいこと"""
        assert AccessPurpose.MODIFY.color == "red"
        assert AccessPurpose.REFERENCE.color == "blue"
        assert AccessPurpose.ANALYZE.color == "yellow"


class TestColorTerminal:
    """ターミナル色表示のテスト"""
    
    def test_colorize_red(self):
        """赤色の色付けが正しいこと"""
        terminal = ColorTerminal()
        result = terminal.colorize("test message", "red")
        # Windows ANSI エスケープシーケンスを確認
        assert "\033[31m" in result  # Red color code
        assert "\033[0m" in result   # Reset code
        assert "test message" in result
    
    def test_colorize_blue(self):
        """青色の色付けが正しいこと"""
        terminal = ColorTerminal()
        result = terminal.colorize("test message", "blue")
        assert "\033[34m" in result  # Blue color code
        assert "\033[0m" in result   # Reset code
    
    def test_colorize_yellow(self):
        """黄色の色付けが正しいこと"""
        terminal = ColorTerminal()
        result = terminal.colorize("test message", "yellow")
        assert "\033[33m" in result  # Yellow color code
        assert "\033[0m" in result   # Reset code
    
    def test_colorize_unsupported_color(self):
        """サポートされていない色は色付けしない"""
        terminal = ColorTerminal()
        result = terminal.colorize("test message", "purple")
        assert result == "test message"
    
    @patch('sys.stdout')
    def test_windows_compatibility(self, mock_stdout):
        """Windows環境での色表示互換性"""
        terminal = ColorTerminal()
        # Windows環境をシミュレート
        with patch('os.name', 'nt'):
            terminal.enable_windows_colors()
            # 色付きメッセージを出力
            terminal.print_colored("test", "red")
            # stdout.writeが呼ばれることを確認
            assert mock_stdout.write.called


class TestFileAccessLogger:
    """FileAccessLoggerメインクラスのテスト"""
    
    def setup_method(self):
        """各テストの前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = FileAccessLogger(base_dir=self.temp_dir)
    
    def test_init_creates_log_directory(self):
        """初期化時にログディレクトリが作成されること"""
        assert Path(self.temp_dir).exists()
        log_dir = Path(self.temp_dir) / "logs"
        # init後にログディレクトリが作成される想定
        
    @patch('builtins.print')
    def test_log_file_access_modify(self, mock_print):
        """修正対象ファイルのアクセスログが正しく出力されること"""
        file_path = "CheckSheetReview.vue"
        description = "レイアウト調整実装中"
        
        self.logger.log_file_access(
            file_path, 
            AccessPurpose.MODIFY, 
            description
        )
        
        # ターミナル出力の確認
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        
        assert "[修正対象]" in call_args
        assert file_path in call_args
        assert description in call_args
        assert "\033[31m" in call_args  # 赤色コード
        
    @patch('builtins.print')  
    def test_log_file_access_reference(self, mock_print):
        """参照のみファイルのアクセスログが正しく出力されること"""
        file_path = "DailyPlanSetting.vue"
        description = "グリッドパターン確認"
        
        self.logger.log_file_access(
            file_path,
            AccessPurpose.REFERENCE,
            description
        )
        
        call_args = mock_print.call_args[0][0]
        assert "[参照のみ]" in call_args
        assert file_path in call_args
        assert description in call_args
        assert "\033[34m" in call_args  # 青色コード
    
    @patch('builtins.print')
    def test_log_file_access_analyze(self, mock_print):
        """解析中ファイルのアクセスログが正しく出力されること"""
        file_path = "ActionButtons.vue"
        description = "関連コンポーネント調査"
        
        self.logger.log_file_access(
            file_path,
            AccessPurpose.ANALYZE, 
            description
        )
        
        call_args = mock_print.call_args[0][0]
        assert "[解析中]" in call_args
        assert file_path in call_args
        assert description in call_args
        assert "\033[33m" in call_args  # 黄色コード
    
    def test_log_to_session_file(self):
        """セッションログファイルに記録されること"""
        file_path = "test.vue"
        description = "テスト用"
        
        self.logger.log_file_access(
            file_path,
            AccessPurpose.MODIFY,
            description
        )
        
        # セッションログファイルが作成されていることを確認
        log_files = list(Path(self.temp_dir).glob("*.log"))
        assert len(log_files) >= 1
        
        # ログファイル内容の確認
        log_content = log_files[0].read_text(encoding='utf-8')
        assert file_path in log_content
        assert "[修正対象]" in log_content
        assert description in log_content
    
    def test_log_structured_json_format(self):
        """構造化JSONログの形式が正しいこと"""
        file_path = "test.vue"
        description = "テスト用"
        
        self.logger.log_file_access(
            file_path,
            AccessPurpose.REFERENCE,
            description
        )
        
        # JSONログファイルから内容を読み取り
        json_log_path = Path(self.temp_dir) / "file_access.json"
        assert json_log_path.exists()
        
        with open(json_log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        assert log_data['file_path'] == file_path
        assert log_data['purpose'] == AccessPurpose.REFERENCE.name
        assert log_data['description'] == description
        assert 'timestamp' in log_data
        assert 'session_id' in log_data
    
    def test_get_session_summary(self):
        """セッション概要が正しく生成されること"""
        # 複数のファイルアクセスを記録
        self.logger.log_file_access("file1.vue", AccessPurpose.MODIFY, "修正1")
        self.logger.log_file_access("file2.vue", AccessPurpose.REFERENCE, "参照1")
        self.logger.log_file_access("file3.vue", AccessPurpose.ANALYZE, "解析1")
        self.logger.log_file_access("file4.vue", AccessPurpose.MODIFY, "修正2")
        
        summary = self.logger.get_session_summary()
        
        assert summary['total_files'] == 4
        assert summary['by_purpose']['MODIFY'] == 2
        assert summary['by_purpose']['REFERENCE'] == 1
        assert summary['by_purpose']['ANALYZE'] == 1
        assert len(summary['file_list']) == 4
    
    @patch('file_access_logger.UnifiedLogger')
    def test_unified_logger_integration(self, mock_unified_logger):
        """UnifiedLoggerとの連携が正しく動作すること"""
        mock_logger_instance = Mock()
        mock_unified_logger.return_value = mock_logger_instance
        
        logger = FileAccessLogger()
        logger.log_file_access("test.vue", AccessPurpose.MODIFY, "テスト")
        
        # UnifiedLoggerのlogメソッドが呼ばれることを確認
        mock_logger_instance.info.assert_called_once()
        call_args = mock_logger_instance.info.call_args[0][0]
        assert "FILE_ACCESS" in call_args or "[修正対象]" in call_args
    
    def test_relative_path_conversion(self):
        """絶対パスが相対パスに変換されること"""
        abs_path = r"C:\Users\Administrator\Documents\PG\品質保管台チェックシート\src\views\CheckSheetReview.vue"
        
        result = self.logger.convert_to_relative_path(abs_path)
        
        # プロジェクトルートからの相対パスになっていること
        assert "src/views/CheckSheetReview.vue" in result or "src\\views\\CheckSheetReview.vue" in result
        assert not result.startswith("C:")
    
    def test_filename_extraction(self):
        """ファイル名抽出が正しく動作すること"""
        file_paths = [
            "src/views/CheckSheetReview.vue",
            r"C:\full\path\to\Component.vue",
            "simple_file.js"
        ]
        
        expected = [
            "CheckSheetReview.vue",
            "Component.vue", 
            "simple_file.js"
        ]
        
        for i, path in enumerate(file_paths):
            result = self.logger.extract_filename(path)
            assert result == expected[i]


class TestFileAccessLoggerIntegration:
    """統合テスト"""
    
    def test_full_workflow(self):
        """完全なワークフローのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = FileAccessLogger(base_dir=temp_dir)
            
            # 複数の目的でファイルアクセスを記録
            test_cases = [
                ("CheckSheetReview.vue", AccessPurpose.MODIFY, "レイアウト調整実装中"),
                ("DailyPlanSetting.vue", AccessPurpose.REFERENCE, "グリッドパターン確認"),
                ("ActionButtons.vue", AccessPurpose.ANALYZE, "関連コンポーネント調査")
            ]
            
            for file_path, purpose, description in test_cases:
                logger.log_file_access(file_path, purpose, description)
            
            # ログファイルが作成されていることを確認
            log_dir = Path(temp_dir)
            assert len(list(log_dir.glob("*.log"))) >= 1
            
            # セッション概要の確認
            summary = logger.get_session_summary()
            assert summary['total_files'] == 3
            assert summary['by_purpose']['MODIFY'] == 1
            assert summary['by_purpose']['REFERENCE'] == 1
            assert summary['by_purpose']['ANALYZE'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])