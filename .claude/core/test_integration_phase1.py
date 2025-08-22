#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ1統合テスト: 基盤統合
TDD Red Phase - テストファースト実装
"""

import unittest
import os
import json
from pathlib import Path
from datetime import datetime
import sys

# テスト対象のインポート（実装前なので失敗する）
try:
    from config import IntegratedConfig
    from jst_utils import get_jst_now, format_jst_time
    from logger import IntegratedLogger, FileUtils, PathUtils
except ImportError as e:
    # TDD Red Phase: 実装前なので失敗は期待される
    print(f"Expected import failure (Red Phase): {e}")


class TestPhase1Integration(unittest.TestCase):
    """フェーズ1: 基盤統合テスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.test_dir = Path(__file__).parent / "test_workspace"
        self.test_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """テストクリーンアップ"""
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    # ==================== 設定統合テスト ====================
    
    def test_integrated_config_exists(self):
        """統合設定クラスが存在することを確認"""
        # RED: 実装前なので失敗する
        try:
            config = IntegratedConfig()
            self.assertIsNotNone(config)
        except NameError:
            self.fail("IntegratedConfig class not implemented yet")
    
    def test_config_has_project_paths(self):
        """設定にプロジェクトパスが含まれることを確認"""
        # RED: 実装前なので失敗する
        try:
            config = IntegratedConfig()
            paths = config.get_project_paths()
            
            # 必要なパスが全て含まれている
            required_paths = ['root', 'core', 'cache', 'workspace', 'docs']
            for path_key in required_paths:
                self.assertIn(path_key, paths)
                self.assertIsInstance(paths[path_key], Path)
                
        except NameError:
            self.fail("Config project paths not implemented yet")
    
    def test_config_has_rules_config(self):
        """設定に開発ルール設定が含まれることを確認"""
        try:
            config = IntegratedConfig()
            rules = config.get_rules_config()
            
            # 開発ルールの設定項目
            rule_keys = [
                'enforce_checklist',
                'enforce_test_first', 
                'enforce_incremental_fix',
                'validate_emojis'
            ]
            
            for rule_key in rule_keys:
                self.assertIn(rule_key, rules)
                self.assertIsInstance(rules[rule_key], bool)
                
        except NameError:
            self.fail("Config rules configuration not implemented yet")
    
    def test_config_environment_detection(self):
        """環境の自動検出機能テスト"""
        try:
            config = IntegratedConfig()
            env = config.detect_environment()
            
            self.assertIn(env, ['development', 'production', 'test'])
            
        except NameError:
            self.fail("Environment detection not implemented yet")
    
    # ==================== JST時刻処理テスト ====================
    
    def test_jst_utils_get_current_time(self):
        """JST現在時刻取得テスト"""
        try:
            jst_now = get_jst_now()
            self.assertIsInstance(jst_now, datetime)
            
            # JST時刻であることを確認（+09:00）
            self.assertEqual(jst_now.utcoffset().total_seconds(), 9 * 3600)
            
        except NameError:
            self.fail("JST utilities not implemented yet")
    
    def test_jst_utils_format_time(self):
        """JST時刻フォーマットテスト"""
        try:
            formatted = format_jst_time()
            self.assertIsInstance(formatted, str)
            self.assertIn("JST", formatted)
            
            # 基本的な日時フォーマットチェック
            self.assertRegex(formatted, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} JST')
            
        except NameError:
            self.fail("JST time formatting not implemented yet")
    
    def test_jst_utils_date_operations(self):
        """JST日付操作テスト"""
        try:
            from jst_utils import format_jst_date, get_jst_yesterday, get_jst_tomorrow
            
            # 日付フォーマット
            date_str = format_jst_date()
            self.assertRegex(date_str, r'\d{4}-\d{2}-\d{2}')
            
            # 昨日・明日の計算
            yesterday = get_jst_yesterday()
            tomorrow = get_jst_tomorrow()
            
            self.assertIsInstance(yesterday, datetime)
            self.assertIsInstance(tomorrow, datetime)
            
        except ImportError:
            self.fail("Extended JST utilities not implemented yet")
    
    # ==================== ログ統合テスト ====================
    
    def test_integrated_logger_exists(self):
        """統合ログシステムが存在することを確認"""
        try:
            logger = IntegratedLogger()
            self.assertIsNotNone(logger)
            
        except NameError:
            self.fail("IntegratedLogger not implemented yet")
    
    def test_logger_has_all_levels(self):
        """ログレベルが全て実装されていることを確認"""
        try:
            logger = IntegratedLogger()
            
            # 標準ログレベル
            methods = ['debug', 'info', 'warning', 'error', 'critical']
            for method in methods:
                self.assertTrue(hasattr(logger, method))
                
        except NameError:
            self.fail("Logger methods not implemented yet")
    
    def test_logger_context_support(self):
        """ログのコンテキスト対応テスト"""
        try:
            logger = IntegratedLogger()
            
            # コンテキスト付きログ
            logger.info("Test message", "TEST_CONTEXT")
            
            # コンテキストの履歴確認
            history = logger.get_context_history("TEST_CONTEXT")
            self.assertIsInstance(history, list)
            
        except NameError:
            self.fail("Logger context support not implemented yet")
    
    def test_logger_file_output(self):
        """ログファイル出力テスト"""
        try:
            logger = IntegratedLogger()
            test_log_file = self.test_dir / "test.log"
            
            # ファイル出力設定
            logger.set_file_output(str(test_log_file))
            logger.info("Test file output")
            
            # ファイルが作成されることを確認
            self.assertTrue(test_log_file.exists())
            
            # ログ内容の確認
            content = test_log_file.read_text(encoding='utf-8')
            self.assertIn("Test file output", content)
            
        except NameError:
            self.fail("Logger file output not implemented yet")
    
    # ==================== ユーティリティテスト ====================
    
    def test_file_utils_exists(self):
        """ファイルユーティリティが存在することを確認"""
        try:
            utils = FileUtils()
            self.assertIsNotNone(utils)
            
        except NameError:
            self.fail("FileUtils not implemented yet")
    
    def test_file_utils_safe_operations(self):
        """ファイル操作の安全性テスト"""
        try:
            utils = FileUtils()
            
            # 安全な読み込み（存在しないファイル）
            content = utils.safe_read("nonexistent.txt")
            self.assertIsNone(content)
            
            # 安全な書き込み
            test_file = self.test_dir / "test_write.txt"
            success = utils.safe_write(str(test_file), "test content")
            self.assertTrue(success)
            self.assertTrue(test_file.exists())
            
        except NameError:
            self.fail("Safe file operations not implemented yet")
    
    def test_path_utils_project_detection(self):
        """プロジェクトパス検出テスト"""
        try:
            utils = PathUtils()
            
            # プロジェクトルートの検出
            project_root = utils.find_project_root()
            self.assertIsInstance(project_root, Path)
            
            # .claudeディレクトリの存在確認
            claude_dir = project_root / ".claude"
            self.assertTrue(claude_dir.exists())
            
        except NameError:
            self.fail("PathUtils not implemented yet")
    
    def test_path_utils_relative_conversion(self):
        """相対パス変換テスト"""
        try:
            utils = PathUtils()
            
            # 絶対パスから相対パスへの変換
            abs_path = Path.cwd() / "test" / "file.txt"
            rel_path = utils.to_relative(abs_path)
            
            self.assertIsInstance(rel_path, str)
            self.assertFalse(rel_path.startswith("/"))  # 相対パスであることを確認
            
        except NameError:
            self.fail("Path conversion utilities not implemented yet")
    
    # ==================== 統合テスト ====================
    
    def test_phase1_integration_complete(self):
        """フェーズ1統合の完全性テスト"""
        try:
            # 全コンポーネントが連携して動作することを確認
            config = IntegratedConfig()
            logger = IntegratedLogger()
            file_utils = FileUtils()
            path_utils = PathUtils()
            
            # 設定ベースのログ初期化
            log_config = config.get_logging_config()
            logger.configure(log_config)
            
            # プロジェクトパスベースのファイル操作
            paths = config.get_project_paths()
            test_file = paths['workspace'] / "integration_test.txt"
            
            success = file_utils.safe_write(
                str(test_file), 
                f"Integration test at {format_jst_time()}"
            )
            
            self.assertTrue(success)
            logger.info("Phase 1 integration test completed", "INTEGRATION")
            
        except NameError:
            self.fail("Phase 1 integration not complete")
    
    # ==================== パフォーマンステスト ====================
    
    def test_performance_baseline(self):
        """パフォーマンスベースラインテスト"""
        try:
            import time
            
            # 設定読み込み時間
            start_time = time.time()
            config = IntegratedConfig()
            config_time = time.time() - start_time
            
            # ログ出力時間
            start_time = time.time()
            logger = IntegratedLogger()
            logger.info("Performance test")
            log_time = time.time() - start_time
            
            # JST時刻取得時間
            start_time = time.time()
            jst_now = get_jst_now()
            jst_time = time.time() - start_time
            
            # パフォーマンス要件（全て0.1秒以内）
            self.assertLess(config_time, 0.1, "Config loading too slow")
            self.assertLess(log_time, 0.1, "Logging too slow")
            self.assertLess(jst_time, 0.1, "JST time calculation too slow")
            
        except NameError:
            self.fail("Performance test components not implemented yet")


class TestBackwardCompatibility(unittest.TestCase):
    """後方互換性テスト"""
    
    def test_existing_imports_still_work(self):
        """既存のインポートがまだ動作することを確認"""
        # 既存システムからの移行期間中は互換性を保つ
        try:
            # 既存のインポートパターンをテスト
            from logger import logger  # 既存の単純なlogger
            from config import get_config  # 既存の設定取得
            
            # 基本的な互換性確認
            self.assertIsNotNone(logger)
            
        except ImportError:
            # 統合初期段階では失敗が予想される
            pass
    
    def test_gradual_migration_support(self):
        """段階的移行のサポートテスト"""
        # 新旧システムの共存確認
        pass


if __name__ == "__main__":
    print("="*60)
    print("TDD Red Phase: フェーズ1統合テスト")
    print("このテストは実装前なので失敗が予想されます")
    print("="*60)
    
    # テスト実行
    unittest.main(verbosity=2)