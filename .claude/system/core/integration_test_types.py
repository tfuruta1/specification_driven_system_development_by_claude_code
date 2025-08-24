import copy
"""
TEST
integration_test_runnerTEST
"""

from dataclasses import dataclass, field
from typing import List

try:
    from test_strategy import TestResult
except ImportError:
    # SUCCESSTestResultSUCCESS
    class TestResult:
        def __init__(self, level=None, passed=True, failed=0, total=1, duration=0.0, details="", **kwargs):
            self.level = level
            self.passed = passed
            self.failed = failed
            self.total = total
            self.duration = duration
            self.details = details
            self.success_rate = ((total - failed) / total * 100) if total > 0 else 100.0


@dataclass
class IntegrationTestResult(TestResult):
    """TEST"""
    circular_imports: List[str] = field(default_factory=list)
    connectivity_issues: List[str] = field(default_factory=list)
    initialization_errors: List[str] = field(default_factory=list)
    
    def get_summary(self) -> str:
        """SUCCESS"""
        status = "PASSED" if self.passed else "FAILED"
        summary = f"Integration Tests - {status}\n"
        summary += f"Total: {self.total}, Passed: {self.total - self.failed}, Failed: {self.failed}\n"
        summary += f"Duration: {self.duration:.2f}s, Success Rate: {self.success_rate:.1f}%\n"
        
        if self.circular_imports:
            summary += f"\nCircular imports found:\n"
            for ci in self.circular_imports:
                summary += f"  - {ci}\n"
                
        if self.connectivity_issues:
            summary += f"\nConnectivity issues:\n"
            for issue in self.connectivity_issues:
                summary += f"  - {issue}\n"
                
        if self.initialization_errors:
            summary += f"\nInitialization errors:\n"
            for error in self.initialization_errors:
                summary += f"  - {error}\n"
                
        return summary


class IntegrationTestError(Exception):
    """SUCCESS"""
    pass