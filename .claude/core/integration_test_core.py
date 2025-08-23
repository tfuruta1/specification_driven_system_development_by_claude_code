"""
統合テストコアモジュール - Claude Code Core
IntegrationTestRunnerから分離されたメインの統合テスト実行機能
"""

import time

try:
    from test_strategy import TestLevel
except ImportError:
    class TestLevel:
        INTEGRATION = 'INTEGRATION'

from integration_test_types import IntegrationTestResult
from circular_import_detector import CircularImportDetector
from component_connectivity import ComponentConnectivityTester
from initialization_tester import InitializationTester


class IntegrationTestRunner:
    """統合テスト実行器"""
    
    def __init__(self):
        """初期化"""
        self.circular_import_detection_enabled = True
        self.component_connectivity_test_enabled = True
        self.initialization_test_enabled = True
        
        self.circular_detector = CircularImportDetector()
        self.connectivity_tester = ComponentConnectivityTester()
        self.initialization_tester = InitializationTester()
        
    def run(self, root_path: str = None) -> IntegrationTestResult:
        """
        統合テスト実行
        
        Args:
            root_path: テスト対象のルートパス
            
        Returns:
            統合テスト結果
        """
        start_time = time.time()
        total_tests = 0
        failed_tests = 0
        details = []
        
        # 検出結果格納
        circular_imports = []
        connectivity_issues = []
        initialization_errors = []
        
        # 循環参照検出
        if self.circular_import_detection_enabled:
            total_tests += 1
            circular_imports = self.circular_detector.detect(root_path)
            if circular_imports:
                failed_tests += 1
                details.append("Circular import detected")
                
        # コンポーネント連携テスト
        if self.component_connectivity_test_enabled:
            total_tests += 1
            if not self.connectivity_tester.test_connectivity():
                failed_tests += 1
                connectivity_issues = self.connectivity_tester.connectivity_issues
                details.append("Component connectivity issues found")
                
        # 初期化テスト
        if self.initialization_test_enabled:
            total_tests += 1
            if not self.initialization_tester.test_initialization():
                failed_tests += 1
                initialization_errors = self.initialization_tester.initialization_errors
                details.append("Initialization errors detected")
                
        # 結果作成
        duration = time.time() - start_time
        passed = failed_tests == 0
        
        result = IntegrationTestResult(
            level=TestLevel.INTEGRATION,
            passed=passed,
            failed=failed_tests,
            total=total_tests,
            duration=duration,
            details="; ".join(details) if details else "All integration tests passed",
            circular_imports=circular_imports,
            connectivity_issues=connectivity_issues,
            initialization_errors=initialization_errors
        )
        
        return result
        
    def configure(self, circular_import_detection: bool = None,
                 component_connectivity_test: bool = None,
                 initialization_test: bool = None):
        """統合テスト設定"""
        if circular_import_detection is not None:
            self.circular_import_detection_enabled = circular_import_detection
            
        if component_connectivity_test is not None:
            self.component_connectivity_test_enabled = component_connectivity_test
            
        if initialization_test is not None:
            self.initialization_test_enabled = initialization_test
            
    def get_circular_detector(self) -> CircularImportDetector:
        """循環参照検出器取得"""
        return self.circular_detector
        
    def get_connectivity_tester(self) -> ComponentConnectivityTester:
        """連携テスター取得"""
        return self.connectivity_tester
        
    def get_initialization_tester(self) -> InitializationTester:
        """初期化テスター取得"""
        return self.initialization_tester
        
    def run_quick_test(self, root_path: str = None) -> bool:
        """
        クイック統合テスト（結果の成功/失敗のみ）
        
        Args:
            root_path: テスト対象のルートパス
            
        Returns:
            テスト成功フラグ
        """
        result = self.run(root_path)
        return result.passed
        
    def get_detailed_report(self, root_path: str = None) -> str:
        """
        詳細レポート生成
        
        Args:
            root_path: テスト対象のルートパス
            
        Returns:
            詳細レポート文字列
        """
        result = self.run(root_path)
        
        report = "=== 統合テスト詳細レポート ===\n"
        report += result.get_summary()
        report += "\n"
        
        # 各テスタの詳細レポート追加
        if self.circular_import_detection_enabled:
            report += "\n=== 循環参照検出詳細 ===\n"
            report += self.circular_detector.get_analysis_summary()
            
        if self.component_connectivity_test_enabled:
            report += "\n=== コンポーネント接続テスト詳細 ===\n"
            report += self.connectivity_tester.get_connectivity_report()
            
        if self.initialization_test_enabled:
            report += "\n=== 初期化テスト詳細 ===\n"
            report += self.initialization_tester.get_initialization_report()
            
        return report
        
    def run_targeted_test(self, test_types: list, root_path: str = None) -> IntegrationTestResult:
        """
        特定のテストのみ実行
        
        Args:
            test_types: 実行するテストタイプのリスト 
                       ['circular', 'connectivity', 'initialization']
            root_path: テスト対象のルートパス
            
        Returns:
            統合テスト結果
        """
        # 一時的に設定を変更
        original_circular = self.circular_import_detection_enabled
        original_connectivity = self.component_connectivity_test_enabled
        original_initialization = self.initialization_test_enabled
        
        try:
            # 指定されたテストのみ有効化
            self.circular_import_detection_enabled = 'circular' in test_types
            self.component_connectivity_test_enabled = 'connectivity' in test_types
            self.initialization_test_enabled = 'initialization' in test_types
            
            # テスト実行
            return self.run(root_path)
            
        finally:
            # 設定を復元
            self.circular_import_detection_enabled = original_circular
            self.component_connectivity_test_enabled = original_connectivity
            self.initialization_test_enabled = original_initialization
            
    def reset_all_testers(self):
        """全テスターの状態をリセット"""
        # 循環参照検出器のリセット（新しいインスタンス作成）
        self.circular_detector = CircularImportDetector()
        
        # 接続テスターのリセット
        self.connectivity_tester.clear_components()
        self.connectivity_tester.clear_connections()
        self.connectivity_tester.clear_issues()
        
        # 初期化テスターのリセット
        self.initialization_tester.clear_modules()
        self.initialization_tester.clear_classes()
        self.initialization_tester.clear_errors()


# 便利な関数群

def run_integration_tests(root_path: str = None) -> IntegrationTestResult:
    """統合テストの簡単実行"""
    runner = IntegrationTestRunner()
    return runner.run(root_path)

def quick_integration_test(root_path: str = None) -> bool:
    """クイック統合テスト"""
    runner = IntegrationTestRunner()
    return runner.run_quick_test(root_path)

def get_integration_report(root_path: str = None) -> str:
    """統合テスト詳細レポート取得"""
    runner = IntegrationTestRunner()
    return runner.get_detailed_report(root_path)

# デモ実行
if __name__ == "__main__":
    print("=== 統合テストコア デモ実行 ===")
    
    runner = IntegrationTestRunner()
    result = runner.run()
    
    print("\n結果サマリー:")
    print(result.get_summary())
    
    if not result.passed:
        print("\n詳細レポート:")
        print(runner.get_detailed_report())