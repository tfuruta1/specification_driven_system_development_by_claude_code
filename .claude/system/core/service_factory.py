#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service Factory for Auto-Mode
統合ファイル対応版 - 循環依存解消とImport最適化

KISS原則とYAGNI原則に基づく軽量なサービスファクトリ
"""

# REFACTOR: Remove circular dependency by creating self-contained ServiceLocator
class ServiceLocator:
    """Simple service locator to avoid circular imports"""
    _services = {}
    
    @classmethod
    def register_service(cls, name: str, service):
        cls._services[name] = service
    
    @classmethod
    def get_service(cls, name: str):
        return cls._services.get(name)
    
    @classmethod
    def clear(cls):
        cls._services.clear()


class ServiceFactory:
    """
    統合Auto-Mode用サービスファクトリ
    
    KISS原則による軽量なサービス管理:
    - 設定サービス(config)の管理
    - 状態サービス(state)の管理  
    - 循環依存回避のためのレイジーローディング
    """
    
    _initialized: bool = False
    
    @classmethod
    def initialize_services(cls) -> None:
        """
        統合サービスを初期化
        
        統合ファイル構造に対応:
        auto_mode_config.py + auto_mode_unified.AutoModeState
        """
        if cls._initialized:
            return
            
        # 統合ファイル構造に対応したインポート
        try:
            from .auto_mode_config import AutoModeConfig
            from .auto_mode_unified import AutoModeState
        except ImportError:
            # フォールバック: 直接実行時
            from auto_mode_config import AutoModeConfig
            from auto_mode_unified import AutoModeState
        
        # サービス登録（循環依存回避）
        ServiceLocator.register_service('config', AutoModeConfig())
        ServiceLocator.register_service('state', AutoModeState())
        
        cls._initialized = True
    
    @classmethod
    def get_config_service(cls):
        """設定サービスを取得（レイジーローディング対応）"""
        if not cls._initialized:
            cls.initialize_services()
        return ServiceLocator.get('config')
    
    @classmethod
    def get_state_service(cls):
        """状態サービスを取得（レイジーローディング対応）"""
        if not cls._initialized:
            cls.initialize_services()
        return ServiceLocator.get('state')
    
    @classmethod
    def clear_services(cls) -> None:
        """全サービスをクリア（テスト・デバッグ用）"""
        ServiceLocator.clear()
        cls._initialized = False
    
    @classmethod
    def is_initialized(cls) -> bool:
        """初期化状態を確認"""
        return cls._initialized


# 外部API関数（後方互換性維持）
def get_config_service():
    """設定サービス取得（外部API）"""
    return ServiceFactory.get_config_service()


def get_state_service():
    """状態サービス取得（外部API）"""
    return ServiceFactory.get_state_service()


def initialize_services():
    """サービス初期化（外部API）"""
    ServiceFactory.initialize_services()


def clear_services():
    """サービスクリア（外部API・テスト用）"""
    ServiceFactory.clear_services()

# Module-level convenience functions
def register_service(name: str, service):
    """Register a service"""
    ServiceLocator.register_service(name, service)

def get_service(name: str):
    """Get a service by name"""
    return ServiceLocator.get_service(name)

def is_initialized() -> bool:
    """Check if services are initialized"""
    return ServiceFactory.is_initialized()