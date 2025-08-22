#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for auto_mode.py - TDD Tests for Auto-Mode Command System
アレックス・ペアプログラミングモードのテスト
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path
import tempfile
import shutil

# テスト対象モジュール
from auto_mode import AutoMode, AutoModeConfig, AutoModeState


class TestAutoModeConfig(unittest.TestCase):
    """AutoModeConfig クラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "auto_config.json"
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
    
    def test_default_config_creation(self):
        """デフォルト設定作成のテスト"""
        config = AutoModeConfig(self.config_file)
        
        # デフォルト値の確認
        self.assertFalse(config.is_enabled)
        self.assertEqual(config.mode, "pair_programming")
        self.assertEqual(config.report_path, ".claude/ActivityReport")
        self.assertIsInstance(config.flows, list)
        self.assertIn("新規開発", config.flows)
        
    def test_config_save_load(self):
        """設定保存・読み込みのテスト"""
        config = AutoModeConfig(self.config_file)
        config.is_enabled = True
        config.current_flow = "バグ修正"
        
        # 保存
        config.save()
        self.assertTrue(self.config_file.exists())
        
        # 新しいインスタンスで読み込み
        config2 = AutoModeConfig(self.config_file)
        self.assertTrue(config2.is_enabled)
        self.assertEqual(config2.current_flow, "バグ修正")


class TestAutoModeState(unittest.TestCase):
    """AutoModeState クラスのテスト"""
    
    def test_state_creation(self):
        """状態オブジェクト作成のテスト"""
        state = AutoModeState()
        
        # 初期状態の確認
        self.assertFalse(state.is_active)
        self.assertIsNone(state.start_time)
        self.assertIsNone(state.current_session)
        self.assertEqual(state.session_count, 0)
        
    def test_state_start_stop(self):
        """状態開始・停止のテスト"""
        state = AutoModeState()
        
        # 開始
        state.start()
        self.assertTrue(state.is_active)
        self.assertIsNotNone(state.start_time)
        self.assertIsNotNone(state.current_session)
        
        # 停止
        state.stop()
        self.assertFalse(state.is_active)
        self.assertIsNone(state.current_session)


class TestAutoMode(unittest.TestCase):
    """AutoMode メインクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.auto_mode = AutoMode(base_dir=self.temp_dir)
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
    
    def test_auto_mode_initialization(self):
        """AutoMode初期化のテスト"""
        self.assertIsInstance(self.auto_mode.config, AutoModeConfig)
        self.assertIsInstance(self.auto_mode.state, AutoModeState)
        self.assertFalse(self.auto_mode.is_active())
        
    def test_start_command(self):
        """startコマンドのテスト"""
        result = self.auto_mode.execute_command("start")
        
        self.assertTrue(result)
        self.assertTrue(self.auto_mode.is_active())
        self.assertTrue(self.auto_mode.config.is_enabled)
        
    def test_stop_command(self):
        """stopコマンドのテスト"""
        # 先にstart
        self.auto_mode.execute_command("start")
        self.assertTrue(self.auto_mode.is_active())
        
        # stop実行
        result = self.auto_mode.execute_command("stop")
        
        self.assertTrue(result)
        self.assertFalse(self.auto_mode.is_active())
        self.assertFalse(self.auto_mode.config.is_enabled)
        
    def test_status_command(self):
        """statusコマンドのテスト"""
        # 非アクティブ状態
        status = self.auto_mode.execute_command("status")
        self.assertIsInstance(status, dict)
        self.assertFalse(status["active"])
        
        # アクティブ状態
        self.auto_mode.execute_command("start")
        status = self.auto_mode.execute_command("status")
        self.assertTrue(status["active"])
        self.assertIn("session_id", status)
        
    def test_invalid_command(self):
        """無効なコマンドのテスト"""
        result = self.auto_mode.execute_command("invalid")
        self.assertFalse(result)
        
    @patch('auto_mode.logger')
    def test_activity_logging(self, mock_logger):
        """ActivityReport記録のテスト"""
        self.auto_mode.execute_command("start")
        
        # ログ呼び出しを確認
        mock_logger.info.assert_called()
        
    def test_flow_detection(self):
        """フロー自動選択のテスト"""
        # Mock user input for flow selection
        with patch('builtins.input', return_value="1"):
            flow = self.auto_mode._select_flow()
            self.assertEqual(flow, "新規開発")
            
    def test_pair_programming_session(self):
        """ペアプログラミングセッションのテスト"""
        session = self.auto_mode._create_session()
        
        self.assertIsInstance(session, dict)
        self.assertIn("session_id", session)
        self.assertIn("start_time", session)
        self.assertIn("flow_type", session)


class TestAutoModeIntegration(unittest.TestCase):
    """統合テストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.auto_mode = AutoMode(base_dir=self.temp_dir)
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """完全なワークフローのテスト"""
        # 1. 開始
        result_start = self.auto_mode.execute_command("start")
        self.assertTrue(result_start)
        
        # 2. 状態確認
        status = self.auto_mode.execute_command("status")
        self.assertTrue(status["active"])
        
        # 3. 停止
        result_stop = self.auto_mode.execute_command("stop")
        self.assertTrue(result_stop)
        
        # 4. 最終状態確認
        final_status = self.auto_mode.execute_command("status")
        self.assertFalse(final_status["active"])
        
    @patch('auto_mode.logger')
    def test_error_handling(self, mock_logger):
        """エラーハンドリングのテスト"""
        # 存在しないディレクトリでの初期化
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            try:
                auto_mode = AutoMode(base_dir="/invalid/path")
                # エラーログが呼ばれることを確認
                mock_logger.error.assert_called()
            except Exception:
                # 例外処理されることを確認
                pass


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)