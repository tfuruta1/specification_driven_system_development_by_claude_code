"""
共通テストユーティリティ - 22ファイルの重複setUp/tearDownの統合

このモジュールは、以下のテスト重複パターンを統合します:
- 一時ディレクトリ作成/削除 (22箇所で重複)
- ロガー初期化 (18箇所で重複)
- テスト環境クリーンアップ (15箇所で重複)
- モックオブジェクト作成 (12箇所で重複)

パフォーマンス目標: テスト実行時間30%短縮
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from unittest.mock import Mock, MagicMock
import os
import json
import time
from .shared_logger import OptimizedLogger


class TestBaseSetup:
    """
    22ファイルの重複setUp/tearDownを統合するベースクラス
    
    主な機能:
    - 高速な一時環境作成
    - 統一されたリソース管理
    - 自動クリーンアップ
    - 共通モック設定
    """
    
    def __init__(self, test_name: str = "base_test"):
        """
        テストベース環境の初期化
        
        Args:
            test_name: テスト識別名
        """
        self.test_name = test_name
        self.temp_dirs = []
        self.temp_files = []
        self.loggers = []
        self.mocks = {}
        self._cleanup_callbacks = []
        self.start_time = time.time()
    
    def create_temp_environment(self, 
                               create_subdirs: Optional[List[str]] = None,
                               create_files: Optional[Dict[str, str]] = None,
                               setup_logger: bool = True) -> Path:
        """
        共通の一時環境作成 - 22ファイルの重複パターンを統合
        
        Args:
            create_subdirs: 作成するサブディレクトリリスト
            create_files: 作成するファイル（パス: 内容）
            setup_logger: ロガー設定するかどうか
            
        Returns:
            Path: 一時ディレクトリパス
        """
        # 高性能な一時ディレクトリ作成
        temp_dir = Path(tempfile.mkdtemp(prefix=f"claude_test_{self.test_name}_"))
        self.temp_dirs.append(temp_dir)
        
        # サブディレクトリ作成
        if create_subdirs:
            for subdir in create_subdirs:
                subdir_path = temp_dir / subdir
                subdir_path.mkdir(parents=True, exist_ok=True)
        
        # テストファイル作成
        if create_files:
            for file_path, content in create_files.items():
                full_path = temp_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                self.temp_files.append(full_path)
        
        # ロガー設定
        if setup_logger:
            logger = OptimizedLogger(
                base_path=temp_dir / "logs",
                user=f"test_{self.test_name}"
            )
            self.loggers.append(logger)
            logger.log_with_context("info", f"テスト環境作成: {self.test_name}",
                                  {"temp_dir": str(temp_dir)})
        
        return temp_dir
    
    def setup_common_mocks(self) -> Dict[str, Mock]:
        """
        共通モック設定 - 12ファイルの重複モック作成を統合
        
        Returns:
            Dict[str, Mock]: 設定済みモック辞書
        """
        self.mocks = {
            # ファイル操作モック
            'file_operations': MagicMock(),
            
            # ロガーモック
            'logger': MagicMock(),
            
            # 外部API呼び出しモック
            'external_api': MagicMock(),
            
            # データベース操作モック
            'database': MagicMock(),
            
            # システム呼び出しモック
            'system_calls': MagicMock(),
            
            # 時間関連モック
            'time_mock': MagicMock(),
        }
        
        # よく使われるモック戻り値を設定
        self.mocks['file_operations'].read_text.return_value = "test content"
        self.mocks['file_operations'].exists.return_value = True
        self.mocks['logger'].log.return_value = None
        self.mocks['external_api'].get.return_value = {"status": "success"}
        
        return self.mocks
    
    def create_test_config(self, config_data: Optional[Dict] = None) -> Path:
        """
        テスト用設定ファイル作成
        
        Args:
            config_data: 設定データ
            
        Returns:
            Path: 設定ファイルパス
        """
        if not hasattr(self, 'temp_dirs') or not self.temp_dirs:
            temp_dir = self.create_temp_environment()
        else:
            temp_dir = self.temp_dirs[0]
        
        config_file = temp_dir / "test_config.json"
        
        default_config = {
            "test_mode": True,
            "debug": True,
            "log_level": "DEBUG",
            "base_path": str(temp_dir),
            "timeout": 30
        }
        
        if config_data:
            default_config.update(config_data)
        
        config_file.write_text(json.dumps(default_config, indent=2), encoding='utf-8')
        self.temp_files.append(config_file)
        
        return config_file
    
    def setup_test_files(self, file_structure: Dict[str, Any]) -> Path:
        """
        複雑なファイル構造作成
        
        Args:
            file_structure: ファイル構造定義
            
        Returns:
            Path: ベースディレクトリ
        """
        if not hasattr(self, 'temp_dirs') or not self.temp_dirs:
            base_dir = self.create_temp_environment()
        else:
            base_dir = self.temp_dirs[0]
        
        def create_structure(current_dir: Path, structure: Dict):
            for name, content in structure.items():
                path = current_dir / name
                if isinstance(content, dict):
                    path.mkdir(exist_ok=True)
                    create_structure(path, content)
                else:
                    path.write_text(str(content), encoding='utf-8')
                    self.temp_files.append(path)
        
        create_structure(base_dir, file_structure)
        return base_dir
    
    def add_cleanup_callback(self, callback: Callable) -> None:
        """
        カスタムクリーンアップコールバック追加
        
        Args:
            callback: クリーンアップ関数
        """
        self._cleanup_callbacks.append(callback)
    
    def cleanup_temp_environment(self) -> None:
        """
        共通のクリーンアップ処理 - 15ファイルの重複クリーンアップを統合
        """
        cleanup_errors = []
        
        # カスタムクリーンアップコールバック実行
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                cleanup_errors.append(f"コールバッククリーンアップエラー: {e}")
        
        # ロガークリーンアップ
        for logger in self.loggers:
            try:
                logger.close()
            except Exception as e:
                cleanup_errors.append(f"ロガークリーンアップエラー: {e}")
        
        # モッククリーンアップ
        for mock_name, mock_obj in self.mocks.items():
            try:
                mock_obj.reset_mock()
            except Exception as e:
                cleanup_errors.append(f"モック{mock_name}クリーンアップエラー: {e}")
        
        # 一時ファイル削除
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                cleanup_errors.append(f"ファイル削除エラー {temp_file}: {e}")
        
        # 一時ディレクトリ削除
        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                cleanup_errors.append(f"ディレクトリ削除エラー {temp_dir}: {e}")
        
        # エラーがあった場合は記録（テスト失敗はさせない）
        if cleanup_errors and self.loggers:
            self.loggers[0].log_with_context("warning", 
                                           "クリーンアップ中にエラーが発生",
                                           {"errors": cleanup_errors})
        
        # 実行時間記録
        execution_time = time.time() - self.start_time
        if self.loggers:
            self.loggers[0].log_with_context("info",
                                           f"テスト実行完了: {self.test_name}",
                                           {"execution_time": execution_time})


class OptimizedTestCase(unittest.TestCase):
    """
    最適化されたテストケースベースクラス
    
    22ファイルのテストクラスで重複していたsetUp/tearDownを統合
    """
    
    def setUp(self):
        """統一されたテストセットアップ"""
        self.test_base = TestBaseSetup(self.__class__.__name__)
        self.temp_dir = self.test_base.create_temp_environment()
        self.mocks = self.test_base.setup_common_mocks()
        self.logger = self.test_base.loggers[0] if self.test_base.loggers else None
        
        # テスト開始ログ
        if self.logger:
            self.logger.log_with_context("info", f"テスト開始: {self._testMethodName}")
    
    def tearDown(self):
        """統一されたテストクリーンアップ"""
        if self.logger:
            self.logger.log_with_context("info", f"テスト終了: {self._testMethodName}")
        
        self.test_base.cleanup_temp_environment()
    
    def create_test_file(self, filename: str, content: str = "test content") -> Path:
        """テストファイル作成ヘルパー"""
        file_path = self.temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def assert_file_exists(self, file_path: Path, message: str = None):
        """ファイル存在確認ヘルパー"""
        self.assertTrue(file_path.exists(), 
                       message or f"ファイルが存在しません: {file_path}")
    
    def assert_file_content(self, file_path: Path, expected_content: str):
        """ファイル内容確認ヘルパー"""
        self.assert_file_exists(file_path)
        actual_content = file_path.read_text(encoding='utf-8')
        self.assertEqual(actual_content, expected_content)


class PerformanceTestCase(OptimizedTestCase):
    """
    パフォーマンステスト用ベースクラス
    """
    
    def setUp(self):
        """パフォーマンステスト用セットアップ"""
        super().setUp()
        self.performance_data = {}
        self.start_time = time.time()
    
    def tearDown(self):
        """パフォーマンスデータ記録"""
        execution_time = time.time() - self.start_time
        self.performance_data['execution_time'] = execution_time
        
        if self.logger:
            self.logger.log_with_context("info", 
                                       f"パフォーマンステスト完了: {self._testMethodName}",
                                       self.performance_data)
        
        super().tearDown()
    
    def measure_execution_time(self, func: Callable, *args, **kwargs) -> float:
        """実行時間測定ヘルパー"""
        start = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start
        
        self.performance_data[func.__name__] = execution_time
        return execution_time


# 後方互換性のための関数群
def create_temp_test_env(test_name: str = "legacy_test") -> Path:
    """後方互換: 従来のcreate_temp_dir関数"""
    setup = TestBaseSetup(test_name)
    return setup.create_temp_environment()

def cleanup_test_env(temp_dir: Path) -> None:
    """後方互換: 従来のcleanup_temp_dir関数"""
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)