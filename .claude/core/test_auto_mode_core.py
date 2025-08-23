#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Auto Mode Tests - AutoModeConfig, AutoModeState, AutoMode
元 test_v12_comprehensive.py から分割されたコアモードテスト
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime
from io import StringIO

# テスト対象モジュールのインポート
sys.path.insert(0, str(Path(__file__).parent))

from auto_mode import AutoModeConfig, AutoMode, AutoModeState


class TestAutoModeConfig(unittest.TestCase):
    """AutoModeConfigの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization_default_values(self):
        """デフォルト値での初期化テスト"""
        config = AutoModeConfig()
        
        self.assertEqual(config.interval, 30)
        self.assertEqual(config.max_iterations, 100)
        self.assertEqual(config.timeout, 300)
        self.assertFalse(config.debug_mode)
        self.assertFalse(config.strict_mode)
        self.assertIsNotNone(config.keywords)
        self.assertIsInstance(config.keywords, list)
        
    def test_initialization_custom_values(self):
        """カスタム値での初期化テスト"""
        config = AutoModeConfig(
            interval=60,
            max_iterations=50,
            timeout=600,
            debug_mode=True,
            strict_mode=True
        )
        
        self.assertEqual(config.interval, 60)
        self.assertEqual(config.max_iterations, 50)
        self.assertEqual(config.timeout, 600)
        self.assertTrue(config.debug_mode)
        self.assertTrue(config.strict_mode)
        
    def test_load_from_file_success(self):
        """ファイル読み込み成功テスト"""
        test_config = {
            "interval": 45,
            "max_iterations": 75,
            "timeout": 450,
            "debug_mode": True,
            "strict_mode": False,
            "keywords": ["test", "demo"]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
            
        config = AutoModeConfig.load_from_file(self.config_file)
        
        self.assertEqual(config.interval, 45)
        self.assertEqual(config.max_iterations, 75)
        self.assertEqual(config.timeout, 450)
        self.assertTrue(config.debug_mode)
        self.assertFalse(config.strict_mode)
        self.assertEqual(config.keywords, ["test", "demo"])
        
    def test_load_from_file_not_found(self):
        """ファイルが存在しない場合のテスト"""
        non_existent_file = Path(self.temp_dir) / "non_existent.json"
        
        config = AutoModeConfig.load_from_file(non_existent_file)
        
        # デフォルト値で初期化される
        self.assertEqual(config.interval, 30)
        self.assertEqual(config.max_iterations, 100)
        
    def test_load_from_file_invalid_json(self):
        """不正なJSONファイルの場合のテスト"""
        with open(self.config_file, 'w') as f:
            f.write("invalid json content")
            
        config = AutoModeConfig.load_from_file(self.config_file)
        
        # デフォルト値で初期化される
        self.assertEqual(config.interval, 30)
        self.assertEqual(config.max_iterations, 100)
        
    def test_save_to_file(self):
        """ファイル保存テスト"""
        config = AutoModeConfig(
            interval=90,
            max_iterations=120,
            timeout=900,
            debug_mode=True
        )
        
        config.save_to_file(self.config_file)
        
        # ファイルが作成されて正しい内容が保存される
        self.assertTrue(self.config_file.exists())
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data['interval'], 90)
        self.assertEqual(saved_data['max_iterations'], 120)
        self.assertEqual(saved_data['timeout'], 900)
        self.assertTrue(saved_data['debug_mode'])
        
    def test_update_config(self):
        """設定更新テスト"""
        config = AutoModeConfig()
        
        config.update_config({
            'interval': 120,
            'debug_mode': True,
            'new_key': 'new_value'  # 新しいキーも追加される
        })
        
        self.assertEqual(config.interval, 120)
        self.assertTrue(config.debug_mode)
        self.assertEqual(config.new_key, 'new_value')
        
    def test_to_dict(self):
        """辞書変換テスト"""
        config = AutoModeConfig(interval=60, debug_mode=True)
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['interval'], 60)
        self.assertTrue(config_dict['debug_mode'])


class TestAutoModeState(unittest.TestCase):
    """AutoModeStateの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "test_state.json"
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        state = AutoModeState(self.state_file)
        
        self.assertEqual(state.state_file, self.state_file)
        self.assertFalse(state.is_active)
        self.assertEqual(state.current_iteration, 0)
        self.assertIsNone(state.start_time)
        self.assertEqual(state.completed_tasks, 0)
        
    def test_start_auto_mode(self):
        """自動モード開始テスト"""
        state = AutoModeState(self.state_file)
        state.start_auto_mode()
        
        self.assertTrue(state.is_active)
        self.assertIsNotNone(state.start_time)
        self.assertEqual(state.current_iteration, 0)
        
    def test_stop_auto_mode(self):
        """自動モード停止テスト"""
        state = AutoModeState(self.state_file)
        state.start_auto_mode()
        
        # 停止
        state.stop_auto_mode()
        
        self.assertFalse(state.is_active)
        self.assertIsNotNone(state.start_time)  # 開始時刻は保持される
        
    def test_increment_iteration(self):
        """イテレーション増加テスト"""
        state = AutoModeState(self.state_file)
        
        initial_iteration = state.current_iteration
        state.increment_iteration()
        
        self.assertEqual(state.current_iteration, initial_iteration + 1)
        
    def test_increment_completed_tasks(self):
        """完了タスク数増加テスト"""
        state = AutoModeState(self.state_file)
        
        initial_tasks = state.completed_tasks
        state.increment_completed_tasks()
        
        self.assertEqual(state.completed_tasks, initial_tasks + 1)
        
    def test_get_runtime(self):
        """実行時間取得テスト"""
        state = AutoModeState(self.state_file)
        
        # 開始していない場合
        runtime = state.get_runtime()
        self.assertEqual(runtime, 0.0)
        
        # 開始した場合
        state.start_auto_mode()
        time.sleep(0.1)  # 短時間待機
        runtime = state.get_runtime()
        self.assertGreater(runtime, 0.0)


class TestAutoMode(unittest.TestCase):
    """AutoModeの包括的テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.json"
        self.state_file = Path(self.temp_dir) / "state.json"
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """初期化テスト"""
        auto_mode = AutoMode(
            config_file=self.config_file,
            state_file=self.state_file
        )
        
        self.assertIsInstance(auto_mode.config, AutoModeConfig)
        self.assertIsInstance(auto_mode.state, AutoModeState)
        self.assertEqual(auto_mode.state.state_file, self.state_file)
        
    @patch('builtins.input', side_effect=['y'])
    def test_start_confirmation_yes(self, mock_input):
        """開始確認でyesの場合のテスト"""
        auto_mode = AutoMode(
            config_file=self.config_file,
            state_file=self.state_file
        )
        
        with patch.object(auto_mode, '_run_loop') as mock_run:
            auto_mode.start()
            
        self.assertTrue(auto_mode.state.is_active)
        mock_run.assert_called_once()
        
    @patch('builtins.input', side_effect=['n'])
    def test_start_confirmation_no(self, mock_input):
        """開始確認でnoの場合のテスト"""
        auto_mode = AutoMode(
            config_file=self.config_file,
            state_file=self.state_file
        )
        
        with patch.object(auto_mode, '_run_loop') as mock_run:
            auto_mode.start()
            
        self.assertFalse(auto_mode.state.is_active)
        mock_run.assert_not_called()
        
    def test_stop(self):
        """停止テスト"""
        auto_mode = AutoMode(
            config_file=self.config_file,
            state_file=self.state_file
        )
        
        auto_mode.state.start_auto_mode()
        auto_mode.stop()
        
        self.assertFalse(auto_mode.state.is_active)


if __name__ == '__main__':
    unittest.main()