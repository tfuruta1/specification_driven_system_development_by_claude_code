#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Interface Abstractions
Auto-Modeインターフェース抽象化

循環依存を解消するための抽象化インターフェース定義
KISS原則に従いシンプルな設計を採用
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class ConfigInterface(ABC):
    """設定管理インターフェース"""
    
    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """自動モードが有効かどうか"""
        pass
    
    @property  
    @abstractmethod
    def current_flow(self) -> Optional[str]:
        """現在のフロー"""
        pass
    
    @property
    @abstractmethod
    def mode(self) -> str:
        """現在のモード"""
        pass
    
    @property
    @abstractmethod
    def flows(self) -> List[str]:
        """利用可能なフロー一覧"""
        pass
    
    @property
    @abstractmethod
    def integration_tests_enabled(self) -> bool:
        """統合テストが有効かどうか"""
        pass
    
    @property
    @abstractmethod
    def circular_import_detection(self) -> bool:
        """循環インポート検出が有効かどうか"""
        pass
    
    @property
    @abstractmethod
    def component_connectivity_test(self) -> bool:
        """コンポーネント接続テストが有効かどうか"""
        pass
    
    @property
    @abstractmethod
    def initialization_test(self) -> bool:
        """初期化テストが有効かどうか"""
        pass
    
    @abstractmethod
    def enable(self) -> None:
        """自動モード有効化"""
        pass
    
    @abstractmethod
    def disable(self) -> None:
        """自動モード無効化"""
        pass
    
    @abstractmethod
    def set_flow(self, flow_name: str) -> bool:
        """フロー設定"""
        pass
    
    @abstractmethod
    def update_integration_settings(self, **kwargs) -> None:
        """統合テスト設定更新"""
        pass


class StateInterface(ABC):
    """状態管理インターフェース"""
    
    @property
    @abstractmethod
    def is_active(self) -> bool:
        """アクティブ状態かどうか"""
        pass
    
    @property
    @abstractmethod
    def current_session(self) -> Optional[str]:
        """現在のセッションID"""
        pass
    
    @property
    @abstractmethod
    def start_time(self) -> Optional[str]:
        """開始時刻"""
        pass
    
    @property
    @abstractmethod
    def session_data(self) -> Dict[str, Any]:
        """セッションデータ"""
        pass
    
    @abstractmethod
    def start(self) -> str:
        """セッション開始"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """セッション停止"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """状態取得"""
        pass


class ServiceLocator:
    """
    シンプルなサービスロケーターパターン実装
    
    KISS原則に従い、複雑なDIコンテナではなく
    軽量なサービス管理を提供
    """
    
    _services: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, service_name: str, service_instance: Any) -> None:
        """サービス登録"""
        cls._services[service_name] = service_instance
    
    @classmethod
    def get(cls, service_name: str) -> Any:
        """サービス取得"""
        if service_name not in cls._services:
            raise ValueError(f"Service '{service_name}' not registered")
        return cls._services[service_name]
    
    @classmethod
    def clear(cls) -> None:
        """全サービスクリア（テスト用）"""
        cls._services.clear()


def create_default_services() -> None:
    """
    デフォルトサービスの作成と登録
    
    循環依存を避けるため、実際のインスタンス化は
    この関数内で行う
    """
    from .auto_mode_config import AutoModeConfig
    from .auto_mode_state import AutoModeState
    
    # デフォルトサービス登録
    ServiceLocator.register('config', AutoModeConfig())
    ServiceLocator.register('state', AutoModeState())


def get_config_service() -> ConfigInterface:
    """設定サービス取得"""
    try:
        return ServiceLocator.get('config')
    except ValueError:
        # 初回時のみデフォルトサービス作成
        create_default_services()
        return ServiceLocator.get('config')


def get_state_service() -> StateInterface:
    """状態サービス取得"""
    try:
        return ServiceLocator.get('state')
    except ValueError:
        # 初回時のみデフォルトサービス作成
        create_default_services()
        return ServiceLocator.get('state')