#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Mode Command System (Modular Structure)
アレックス・ペアプログラミングモード自動化システム

シンプルで強力な/auto-modeコマンドシステムを提供：
- /auto-mode start - ペアプログラミングモード開始
- /auto-mode stop - ペアプログラミングモード終了  
- /auto-mode status - 現在の状態確認
"""

from typing import Dict, List, Optional, Any

# 循環依存解決後のモジュールインポート
from .auto_mode_config import AutoModeConfig
from .auto_mode_state import AutoModeState
from .auto_mode_core import AutoMode, create_auto_mode
from .service_factory import get_config_service, get_state_service, initialize_services

# 循環依存解決後のエクスポート
__all__ = [
    'AutoModeConfig',
    'AutoModeState', 
    'AutoMode',
    'create_auto_mode',
    'get_config_service',
    'get_state_service',
    'initialize_services'
]

# デモ実行
if __name__ == "__main__":
    print("=== Auto-Mode System v13.2 (Circular Dependency Resolved) ===")
    
    # サービス初期化
    initialize_services()
    
    # サービス取得
    config = get_config_service()
    state = get_state_service()
    
    # システム状態表示
    print(f"設定有効: {config.is_enabled}")
    print(f"現在のモード: {config.mode}")
    print(f"アクティブ: {state.is_active}")
    
    # 利用可能フロー表示
    print("\n利用可能フロー:")
    for i, flow in enumerate(config.flows, 1):
        marker = "✓" if flow == config.current_flow else " "
        print(f"  {marker} {i}. {flow}")
    
    # 統合テスト設定表示
    integration_settings = config.get_config_summary()["integration_tests"]
    print("\n統合テスト設定:")
    for key, value in integration_settings.items():
        status = "有効" if value else "無効" if isinstance(value, bool) else str(value)
        print(f"  {key}: {status}")
    
    # AutoModeインスタンス作成
    auto_mode_instance = create_auto_mode()
    
    # コマンドデモ
    print("\nコマンドデモ...")
    commands = ["status", "start", "status", "stop", "status"]
    
    for cmd in commands:
        print(f"\n> /auto-mode {cmd}")
        result = auto_mode_instance.execute_command(cmd)
        print(f"結果: {result}")
    
    print("\n=== Demo Complete - Circular Dependencies Resolved ===")