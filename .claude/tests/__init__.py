"""
Claude Code Test Suite Package
統合テストスイートの初期化
"""

# テストランナー
from .unified_test_runner import UnifiedTestRunner

# KISS原則チェッカー
from .kiss_principle_checker import KISSPrincipleChecker

__all__ = [
    'UnifiedTestRunner',
    'KISSPrincipleChecker',
]

__version__ = '12.0.0'