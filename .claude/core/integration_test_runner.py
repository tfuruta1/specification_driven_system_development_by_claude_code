"""
統合テスト実行モジュール - Claude Code Core
分割されたモジュールを統合するメインインターフェース

循環参照検出、コンポーネント連携テスト、初期化エラー検出などの統合テスト機能を提供
"""

# 分割されたモジュールからインポート
from integration_test_types import IntegrationTestResult, IntegrationTestError
from circular_import_detector import CircularImportDetector
from component_connectivity import ComponentConnectivityTester
from initialization_tester import InitializationTester
from integration_test_core import IntegrationTestRunner, run_integration_tests, quick_integration_test, get_integration_report

# 後方互換性のための再エクスポート
__all__ = [
    'IntegrationTestResult',
    'IntegrationTestError',
    'CircularImportDetector',
    'ComponentConnectivityTester', 
    'InitializationTester',
    'IntegrationTestRunner',
    'run_integration_tests',
    'quick_integration_test',
    'get_integration_report'
]

# 便利関数（後方互換性）
def create_integration_test_runner():
    """統合テストランナーの作成"""
    return IntegrationTestRunner()

def run_full_integration_test(root_path: str = None):
    """フル統合テストの実行"""
    runner = IntegrationTestRunner()
    return runner.get_detailed_report(root_path)

# デモ・テスト実行
if __name__ == "__main__":
    print("=== 統合テスト実行システム（分割版） ===")
    
    # 基本的な統合テスト
    result = run_integration_tests()
    
    print("\n統合テスト結果:")
    print(result.get_summary())
    
    if not result.passed:
        print("\n詳細な問題レポート:")
        print(get_integration_report())
    
    print("\n分割されたモジュール:")
    print("  - integration_test_types.py: 共通型定義とエラークラス")
    print("  - circular_import_detector.py: 循環参照検出機能")
    print("  - component_connectivity.py: コンポーネント接続テスト")
    print("  - initialization_tester.py: 初期化テスト機能")
    print("  - integration_test_core.py: 統合テストコアと実行制御")
    
    # カスタマイズされたテストの例
    print("\n=== カスタマイズテストの例 ===")
    
    custom_runner = IntegrationTestRunner()
    
    # 特定のテストのみ実行
    custom_result = custom_runner.run_targeted_test(['circular', 'initialization'])
    print(f"ターゲットテスト結果: {'PASSED' if custom_result.passed else 'FAILED'}")
    
    # 詳細設定の例
    custom_runner.configure(
        circular_import_detection=True,
        component_connectivity_test=False,
        initialization_test=True
    )
    
    configured_result = custom_runner.run()
    print(f"設定済みテスト結果: {'PASSED' if configured_result.passed else 'FAILED'}")