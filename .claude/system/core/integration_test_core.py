import copy
"""
TEST - Claude Code Core
IntegrationTestRunnerERROR
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
    """TEST"""
    
    def __init__(self):
        """TEST"""
        self.circular_import_detection_enabled = True
        self.component_connectivity_test_enabled = True
        self.initialization_test_enabled = True
        
        self.circular_detector = CircularImportDetector()
        self.connectivity_tester = ComponentConnectivityTester()
        self.initialization_tester = InitializationTester()
        
    def run(self, root_path: str = None) -> IntegrationTestResult:
        """
        TEST
        
        Args:
            root_path: TEST
            
        Returns:
            ERROR
        """
        start_time = time.time()
        total_tests = 0
        failed_tests = 0
        details = []
        
        # ERROR
        circular_imports = []
        connectivity_issues = []
        initialization_errors = []
        
        # ERROR
        if self.circular_import_detection_enabled:
            total_tests += 1
            circular_imports = self.circular_detector.detect(root_path)
            if circular_imports:
                failed_tests += 1
                details.append("Circular import detected")
                
        # TEST
        if self.component_connectivity_test_enabled:
            total_tests += 1
            if not self.connectivity_tester.test_connectivity():
                failed_tests += 1
                connectivity_issues = self.connectivity_tester.connectivity_issues
                details.append("Component connectivity issues found")
                
        # TEST
        if self.initialization_test_enabled:
            total_tests += 1
            if not self.initialization_tester.test_initialization():
                failed_tests += 1
                initialization_errors = self.initialization_tester.initialization_errors
                details.append("Initialization errors detected")
                
        # SUCCESS
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
        """TEST"""
        if circular_import_detection is not None:
            self.circular_import_detection_enabled = circular_import_detection
            
        if component_connectivity_test is not None:
            self.component_connectivity_test_enabled = component_connectivity_test
            
        if initialization_test is not None:
            self.initialization_test_enabled = initialization_test
            
    def get_circular_detector(self) -> CircularImportDetector:
        """TEST"""
        return self.circular_detector
        
    def get_connectivity_tester(self) -> ComponentConnectivityTester:
        """TEST"""
        return self.connectivity_tester
        
    def get_initialization_tester(self) -> InitializationTester:
        """TEST"""
        return self.initialization_tester
        
    def run_quick_test(self, root_path: str = None) -> bool:
        """
        TEST/TEST
        
        Args:
            root_path: REPORT
            
        Returns:
            SUCCESS
        """
        result = self.run(root_path)
        return result.passed
        
    def get_detailed_report(self, root_path: str = None) -> str:
        """
        REPORT
        
        Args:
            root_path: REPORT
            
        Returns:
            REPORT
        """
        result = self.run(root_path)
        
        report = "=== REPORT ===\n"
        report += result.get_summary()
        report += "\n"
        
        # REPORT
        if self.circular_import_detection_enabled:
            report += "\n=== REPORT ===\n"
            report += self.circular_detector.get_analysis_summary()
            
        if self.component_connectivity_test_enabled:
            report += "\n=== TEST ===\n"
            report += self.connectivity_tester.get_connectivity_report()
            
        if self.initialization_test_enabled:
            report += "\n=== TEST ===\n"
            report += self.initialization_tester.get_initialization_report()
            
        return report
        
    def run_targeted_test(self, test_types: list, root_path: str = None) -> IntegrationTestResult:
        """
        TEST
        
        Args:
            test_types: TEST 
                       ['circular', 'connectivity', 'initialization']
            root_path: 
            
        Returns:
            
        """
        # 
        original_circular = self.circular_import_detection_enabled
        original_connectivity = self.component_connectivity_test_enabled
        original_initialization = self.initialization_test_enabled
        
        try:
            # TEST
            self.circular_import_detection_enabled = 'circular' in test_types
            self.component_connectivity_test_enabled = 'connectivity' in test_types
            self.initialization_test_enabled = 'initialization' in test_types
            
            # TEST
            return self.run(root_path)
            
        finally:
            # 
            self.circular_import_detection_enabled = original_circular
            self.component_connectivity_test_enabled = original_connectivity
            self.initialization_test_enabled = original_initialization
            
    def reset_all_testers(self):
        """TEST"""
        # TEST
        self.circular_detector = CircularImportDetector()
        
        # TEST
        self.connectivity_tester.clear_components()
        self.connectivity_tester.clear_connections()
        self.connectivity_tester.clear_issues()
        
        # TEST
        self.initialization_tester.clear_modules()
        self.initialization_tester.clear_classes()
        self.initialization_tester.clear_errors()


# ERROR

def run_integration_tests(root_path: str = None) -> IntegrationTestResult:
    """TEST"""
    runner = IntegrationTestRunner()
    return runner.run(root_path)

def quick_integration_test(root_path: str = None) -> bool:
    """TEST"""
    runner = IntegrationTestRunner()
    return runner.run_quick_test(root_path)

def get_integration_report(root_path: str = None) -> str:
    """TEST"""
    runner = IntegrationTestRunner()
    return runner.get_detailed_report(root_path)

# TEST
if __name__ == "__main__":
    print("=== TEST TEST ===")
    
    runner = IntegrationTestRunner()
    result = runner.run()
    
    print("\nSUCCESS:")
    print(result.get_summary())
    
    if not result.passed:
        print("\nSUCCESS:")
        print(runner.get_detailed_report())