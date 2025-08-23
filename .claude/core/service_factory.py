#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service Factory for Auto-Mode
循環依存を完全解決するサービスファクトリー

KISS原則とYAGNI原則に従い、最小限のサービス管理を提供
"""

# typing import removed - not needed for current implementation
try:
    from .auto_mode_interfaces import ServiceLocator
except ImportError:
    # スタンドアロン実行用
    from auto_mode_interfaces import ServiceLocator


class ServiceFactory:
    """
    シンプルなサービスファクトリー
    
    KISS原則に基づく単純明快な実装
    - 循環依存完全回避
    - 遅延初期化による効率化
    - テスタビリティ確保
    """
    
    _initialized: bool = False
    
    @classmethod
    def initialize_services(cls) -> None:
        """
        全サービスの初期化と登録
        
        循環依存を完全に回避するため、すべてのサービス作成を
        単一の場所で管理
        """
        if cls._initialized:
            return
            
        # 循環依存回避のため、ここでのみインポート
        try:
            from .auto_mode_config import AutoModeConfig
            from .auto_mode_state import AutoModeState
        except ImportError:
            # スタンドアロン実行用
            from auto_mode_config import AutoModeConfig
            from auto_mode_state import AutoModeState
        
        # サービス登録
        ServiceLocator.register('config', AutoModeConfig())
        ServiceLocator.register('state', AutoModeState())
        
        cls._initialized = True
    
    @classmethod
    def get_config_service(cls):
        """設定サービス取得（安全な遅延初期化）"""
        if not cls._initialized:
            cls.initialize_services()
        return ServiceLocator.get('config')
    
    @classmethod
    def get_state_service(cls):
        """状態サービス取得（安全な遅延初期化）"""
        if not cls._initialized:
            cls.initialize_services()
        return ServiceLocator.get('state')
    
    @classmethod
    def clear_services(cls) -> None:
        """サービス全クリア（テスト用）"""
        ServiceLocator.clear()
        cls._initialized = False
    
    @classmethod
    def is_initialized(cls) -> bool:
        """初期化状態確認"""
        return cls._initialized


# 互換性のためのファクトリー関数
def get_config_service():
    """設定サービス取得（互換性関数）"""
    return ServiceFactory.get_config_service()


def get_state_service():
    """状態サービス取得（互換性関数）"""
    return ServiceFactory.get_state_service()


def clear_services():
    """サービス全クリア（互換性関数）"""
    ServiceFactory.clear_services()