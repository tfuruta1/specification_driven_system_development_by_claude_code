#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Configuration Management
Auto-Mode設定管理モジュール
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from .activity_logger import logger
except ImportError:
    # スタンドアロン実行用
    import logging
    logger = logging.getLogger(__name__)
try:
    from .jst_utils import format_jst_datetime
    from .auto_mode_interfaces import ConfigInterface
except ImportError:
    # スタンドアロン実行用
    from jst_utils import format_jst_datetime
    from auto_mode_interfaces import ConfigInterface


class AutoModeConfig(ConfigInterface):
    """Auto-Mode設定管理クラス"""
    
    # ConfigInterfaceの抽象プロパティ実装
    @property
    def is_enabled(self) -> bool:
        """自動モードが有効かどうか"""
        return self._is_enabled
    
    @property
    def current_flow(self) -> Optional[str]:
        """現在のフロー"""
        return self._current_flow
    
    @property
    def mode(self) -> str:
        """現在のモード"""
        return self._mode
    
    @property
    def flows(self) -> List[str]:
        """利用可能なフロー一覧"""
        return self._flows
    
    @property
    def integration_tests_enabled(self) -> bool:
        """統合テストが有効かどうか"""
        return self._integration_tests_enabled
    
    @property
    def circular_import_detection(self) -> bool:
        """循環インポート検出が有効かどうか"""
        return self._circular_import_detection
    
    @property
    def component_connectivity_test(self) -> bool:
        """コンポーネント接続テストが有効かどうか"""
        return self._component_connectivity_test
    
    @property
    def initialization_test(self) -> bool:
        """初期化テストが有効かどうか"""
        return self._initialization_test
    
    def __init__(self, config_file: Path = None):
        """
        設定初期化
        
        Args:
            config_file: 設定ファイルパス（Noneの場合はデフォルト）
        """
        self.config_file = config_file or Path(".claude/core/.claude/auto_config.json")
        self._is_enabled = False
        self._mode = "pair_programming"
        self.report_path = ".claude/ActivityReport"
        self._current_flow = None
        self._flows = [
            "新規開発",
            "既存解析", 
            "バグ修正",
            "リファクタリング"
        ]
        # 統合テスト設定
        self._integration_tests_enabled = True
        self._circular_import_detection = True
        self._component_connectivity_test = True
        self._initialization_test = True
        self.integration_test_timeout = 30
        
        # 設定ファイルが存在する場合は読み込み
        if self.config_file.exists():
            self._load()
            
    def _load(self):
        """設定ファイル読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self._is_enabled = data.get('is_enabled', False)
            self._mode = data.get('mode', 'pair_programming')
            self.report_path = data.get('report_path', '.claude/ActivityReport')
            self._current_flow = data.get('current_flow')
            self._flows = data.get('flows', self._flows)
            # 統合テスト設定読み込み
            self._integration_tests_enabled = data.get('integration_tests_enabled', True)
            self._circular_import_detection = data.get('circular_import_detection', True)
            self._component_connectivity_test = data.get('component_connectivity_test', True)
            self._initialization_test = data.get('initialization_test', True)
            self.integration_test_timeout = data.get('integration_test_timeout', 30)
            
            # タイムアウト値の検証
            if self.integration_test_timeout <= 0:
                raise ValueError("Integration test timeout must be positive")
            
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}", "AUTO_MODE")
            
    def save(self):
        """設定ファイル保存"""
        try:
            # ディレクトリ作成
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'is_enabled': self._is_enabled,
                'mode': self._mode,
                'report_path': self.report_path,
                'current_flow': self._current_flow,
                'flows': self._flows,
                'integration_tests_enabled': self._integration_tests_enabled,
                'circular_import_detection': self._circular_import_detection,
                'component_connectivity_test': self._component_connectivity_test,
                'initialization_test': self._initialization_test,
                'integration_test_timeout': self.integration_test_timeout,
                'last_updated': format_jst_datetime()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"設定保存エラー: {e}", "AUTO_MODE")

    def enable(self):
        """自動モード有効化"""
        self._is_enabled = True
        self.save()
        logger.info("Auto-Mode: 有効化", "AUTO_MODE")

    def disable(self):
        """自動モード無効化"""
        self._is_enabled = False
        self.save()
        logger.info("Auto-Mode: 無効化", "AUTO_MODE")

    def set_flow(self, flow_name: str) -> bool:
        """
        現在のフロー設定
        
        Args:
            flow_name: フロー名
            
        Returns:
            設定成功フラグ
        """
        if flow_name in self.flows:
            self.current_flow = flow_name
            self.save()
            logger.info(f"Auto-Mode: フロー設定 - {flow_name}", "AUTO_MODE")
            return True
        else:
            logger.warning(f"Auto-Mode: 不明なフロー - {flow_name}", "AUTO_MODE")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """設定要約を取得"""
        return {
            "is_enabled": self.is_enabled,
            "mode": self.mode,
            "current_flow": self.current_flow,
            "available_flows": self.flows,
            "integration_tests": {
                "enabled": self.integration_tests_enabled,
                "circular_import_detection": self.circular_import_detection,
                "component_connectivity_test": self.component_connectivity_test,
                "initialization_test": self.initialization_test,
                "timeout": self.integration_test_timeout
            },
            "report_path": self.report_path,
            "config_file": str(self.config_file)
        }

    def update_integration_settings(self, **kwargs):
        """
        統合テスト設定の更新
        
        Args:
            **kwargs: 更新する設定項目
        """
        updated = []
        
        if 'integration_tests_enabled' in kwargs:
            self._integration_tests_enabled = kwargs['integration_tests_enabled']
            updated.append('integration_tests_enabled')
            
        if 'circular_import_detection' in kwargs:
            self._circular_import_detection = kwargs['circular_import_detection']
            updated.append('circular_import_detection')
            
        if 'component_connectivity_test' in kwargs:
            self._component_connectivity_test = kwargs['component_connectivity_test']
            updated.append('component_connectivity_test')
            
        if 'initialization_test' in kwargs:
            self._initialization_test = kwargs['initialization_test']
            updated.append('initialization_test')
            
        if 'integration_test_timeout' in kwargs:
            timeout = kwargs['integration_test_timeout']
            if timeout > 0:
                self.integration_test_timeout = timeout
                updated.append('integration_test_timeout')
            else:
                logger.warning("Auto-Mode: タイムアウト値は正数である必要があります", "AUTO_MODE")
        
        if updated:
            self.save()
            logger.info(f"Auto-Mode: 統合テスト設定更新 - {', '.join(updated)}", "AUTO_MODE")

# ServiceLocatorパターンで管理 - シングルトン不要