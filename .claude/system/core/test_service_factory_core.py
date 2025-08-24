#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ServiceFactory Core Functionality Tests
ServiceFactoryコア機能テスト - 分割版 (1/2)

初期化、サービス取得、互換性機能のテスト
Performance Optimization: 758行 → 2ファイル分割

担当: Claude Code TDD Specialist  
作成日: 2025-08-24
"""

import copy
import unittest
import threading
import time
import concurrent.futures
import gc
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# プロジェクトパス設定
sys.path.insert(0, str(Path(__file__).parent))


class TestServiceFactoryInitialization(unittest.TestCase):
    """
    ServiceFactory初期化テスト群
    
    TDD Phase: RED-GREEN-REFACTOR
    """
    
    def setUp(self):
        """テスト前の初期化処理"""
        from .service_factory import ServiceFactory
        from .auto_mode_unified import ServiceLocator
        ServiceFactory.clear_services()
        ServiceLocator.clear()
        
    def test_initial_state(self):
        """
        初期状態の確認テスト
        
        RED: 初期状態は未初期化であること
        """
        from .service_factory import ServiceFactory
        
        # 初期化状態フラグ確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # サービス未登録確認
        from .auto_mode_unified import ServiceLocator
        self.assertFalse(ServiceLocator.has('config'))
        self.assertFalse(ServiceLocator.has('state'))
        
    def test_first_initialization(self):
        """
        初回初期化テスト
        
        GREEN: 初期化処理が正常に実行されること
        """
        from .service_factory import ServiceFactory
        from .auto_mode_unified import ServiceLocator
        
        # 初期化実行
        ServiceFactory.initialize_services()
        
        # 初期化完了確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # サービス登録確認
        self.assertTrue(ServiceLocator.has('config'))
        self.assertTrue(ServiceLocator.has('state'))
        
        # サービスインスタンス確認
        config = ServiceLocator.get('config')
        state = ServiceLocator.get('state')
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        
        # インターフェース準拠確認
        from .auto_mode_unified import ConfigInterface, StateInterface
        self.assertIsInstance(config, ConfigInterface)
        self.assertIsInstance(state, StateInterface)
        
    def test_idempotent_initialization(self):
        """
        冪等性初期化テスト
        
        GREEN: 複数回初期化しても同じインスタンスを返すこと
        REFACTOR: 無駄な初期化処理を回避すること
        """
        from .service_factory import ServiceFactory
        from .auto_mode_unified import ServiceLocator
        
        # 1回目の初期化
        ServiceFactory.initialize_services()
        first_config = ServiceLocator.get('config')
        first_state = ServiceLocator.get('state')
        
        # 2回目の初期化
        ServiceFactory.initialize_services()
        second_config = ServiceLocator.get('config')
        second_state = ServiceLocator.get('state')
        
        # インスタンス同一性確認
        self.assertIs(first_config, second_config)
        self.assertIs(first_state, second_state)
        
        # 初期化状態維持確認
        self.assertTrue(ServiceFactory.is_initialized())
        
    def test_initialization_thread_safety(self):
        """
        マルチスレッド初期化テスト
        
        REFACTOR: 並行初期化時のスレッドセーフ性確認
        """
        from .service_factory import ServiceFactory
        from .auto_mode_unified import ServiceLocator
        
        results = []
        exceptions = []
        
        def initialize_concurrently(thread_id):
            try:
                ServiceFactory.initialize_services()
                config = ServiceLocator.get('config')
                state = ServiceLocator.get('state')
                
                results.append({
                    'thread_id': thread_id,
                    'config_id': id(config),
                    'state_id': id(state),
                    'initialized': ServiceFactory.is_initialized()
                })
                
            except Exception as e:
                exceptions.append({
                    'thread_id': thread_id,
                    'exception': str(e)
                })
        
        # 10スレッド同時初期化
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(initialize_concurrently, i) for i in range(10)]
            concurrent.futures.wait(futures)
        
        # 例外発生なし確認
        self.assertEqual(len(exceptions), 0, f"Exceptions occurred: {exceptions}")
        self.assertEqual(len(results), 10)
        
        # インスタンス一意性確認
        config_ids = set(result['config_id'] for result in results)
        state_ids = set(result['state_id'] for result in results)
        
        self.assertEqual(len(config_ids), 1, "Multiple config instances created")
        self.assertEqual(len(state_ids), 1, "Multiple state instances created")
        
        # 全スレッドで初期化完了確認
        for result in results:
            self.assertTrue(result['initialized'])
            
    def tearDown(self):
        """テスト後の清理処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryServiceRetrieval(unittest.TestCase):
    """
    ServiceFactoryサービス取得テスト群
    
    TDD Phase: GREEN - サービス取得機能の詳細検証
    """
    
    def setUp(self):
        """テスト前の初期化処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_get_config_service_direct(self):
        """
        設定サービス直接取得テスト
        
        GREEN: get_config_service()の正常動作確認
        """
        from .service_factory import ServiceFactory
        
        config = ServiceFactory.get_config_service()
        
        # インスタンス生成確認
        self.assertIsNotNone(config)
        
        # 自動初期化確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # インターフェース準拠確認
        from .auto_mode_unified import ConfigInterface
        self.assertIsInstance(config, ConfigInterface)
        
    def test_get_state_service_direct(self):
        """
        状態サービス直接取得テスト
        
        GREEN: get_state_service()の正常動作確認
        """
        from .service_factory import ServiceFactory
        
        state = ServiceFactory.get_state_service()
        
        # インスタンス生成確認
        self.assertIsNotNone(state)
        
        # 自動初期化確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # インターフェース準拠確認
        from .auto_mode_unified import StateInterface
        self.assertIsInstance(state, StateInterface)
        
    def test_lazy_initialization_through_service_methods(self):
        """
        レイジー初期化テスト
        
        GREEN: サービス取得時の自動初期化動作確認
        """
        from .service_factory import ServiceFactory
        
        # 初期状態確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # サービス取得による自動初期化
        config = ServiceFactory.get_config_service()
        
        # 初期化確認
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertIsNotNone(config)
        
        # 追加サービス取得
        state = ServiceFactory.get_state_service()
        self.assertIsNotNone(state)
        
    def test_service_consistency(self):
        """
        サービス一貫性テスト
        
        GREEN: 複数回取得時のインスタンス同一性確認
        """
        from .service_factory import ServiceFactory
        
        # 複数回サービス取得
        config1 = ServiceFactory.get_config_service()
        config2 = ServiceFactory.get_config_service()
        config3 = ServiceFactory.get_config_service()
        
        state1 = ServiceFactory.get_state_service()
        state2 = ServiceFactory.get_state_service()
        state3 = ServiceFactory.get_state_service()
        
        # インスタンス同一性確認
        self.assertIs(config1, config2)
        self.assertIs(config2, config3)
        self.assertIs(state1, state2)
        self.assertIs(state2, state3)
        
    def tearDown(self):
        """テスト後の清理処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


class TestServiceFactoryCompatibilityFunctions(unittest.TestCase):
    """
    ServiceFactory互換性関数テスト群
    
    TDD Phase: GREEN - 外部API互換関数の動作確認
    """
    
    def setUp(self):
        """テスト前の初期化処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()
        
    def test_get_config_service_external_function(self):
        """
        外部get_config_service関数テスト
        
        GREEN: モジュール関数としてのconfig取得確認
        """
        from .service_factory import get_config_service, ServiceFactory
        
        # 関数経由でのサービス取得
        config = get_config_service()
        
        # インスタンス生成確認
        self.assertIsNotNone(config)
        
        # 自動初期化確認  
        self.assertTrue(ServiceFactory.is_initialized())
        
        # インターフェース準拠確認
        from .auto_mode_unified import ConfigInterface
        self.assertIsInstance(config, ConfigInterface)
        
        # 一貫性確認
        config2 = get_config_service()
        self.assertIs(config, config2)
        
    def test_get_state_service_external_function(self):
        """
        外部get_state_service関数テスト
        
        GREEN: モジュール関数としてのstate取得確認
        """
        from .service_factory import get_state_service, ServiceFactory
        
        # 関数経由でのサービス取得
        state = get_state_service()
        
        # インスタンス生成確認
        self.assertIsNotNone(state)
        
        # 自動初期化確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # インターフェース準拠確認
        from .auto_mode_unified import StateInterface
        self.assertIsInstance(state, StateInterface)
        
        # 一貫性確認
        state2 = get_state_service()
        self.assertIs(state, state2)
        
    def test_initialize_services_external_function(self):
        """
        外部initialize_services関数テスト
        
        GREEN: モジュール関数としての初期化確認
        """
        from .service_factory import initialize_services, ServiceFactory
        
        # 初期状態確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 関数経由での初期化
        initialize_services()
        
        # 初期化完了確認
        self.assertTrue(ServiceFactory.is_initialized())
        
        # 冪等性確認
        initialize_services()
        self.assertTrue(ServiceFactory.is_initialized())
        
    def test_clear_services_external_function(self):
        """
        外部clear_services関数テスト
        
        GREEN: モジュール関数としてのクリア確認
        """
        from .service_factory import (
            initialize_services, 
            clear_services, 
            ServiceFactory,
            get_config_service,
            get_state_service
        )
        
        # サービス初期化
        initialize_services()
        config = get_config_service()
        state = get_state_service()
        
        # 初期化確認
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        
        # クリア実行
        clear_services()
        
        # クリア確認
        self.assertFalse(ServiceFactory.is_initialized())
        
        # サービス再取得による自動初期化確認
        new_config = get_config_service()
        new_state = get_state_service()
        
        # 新しいインスタンス確認
        self.assertIsNot(config, new_config)
        self.assertIsNot(state, new_state)
        self.assertTrue(ServiceFactory.is_initialized())
        
    def test_external_function_integration(self):
        """
        外部関数統合テスト
        
        GREEN: 全外部関数の連携動作確認
        """
        from .service_factory import (
            initialize_services,
            get_config_service, 
            get_state_service,
            clear_services,
            ServiceFactory
        )
        
        # 明示的初期化
        initialize_services()
        
        # サービス取得
        config = get_config_service()
        state = get_state_service()
        
        # 機能確認
        self.assertIsNotNone(config)
        self.assertIsNotNone(state)
        self.assertTrue(ServiceFactory.is_initialized())
        
        # クリアと再初期化
        clear_services()
        self.assertFalse(ServiceFactory.is_initialized())
        
        # 自動初期化確認
        new_config = get_config_service()
        self.assertTrue(ServiceFactory.is_initialized())
        self.assertIsNotNone(new_config)
        
    def tearDown(self):
        """テスト後の清理処理"""
        from .service_factory import ServiceFactory
        ServiceFactory.clear_services()


if __name__ == '__main__':
    # テストスイート実行
    unittest.main(
        verbosity=2,
        buffer=True,
        exit=False
    )
    
    print("\n=== ServiceFactory Core Tests Complete ===")
    print("テスト範囲: 初期化、サービス取得、互換性関数")
    print("分割最適化: 758行 → Core(350行程度) + Advanced(400行程度)")
    print("パフォーマンス向上: テスト実行速度30%向上目標")