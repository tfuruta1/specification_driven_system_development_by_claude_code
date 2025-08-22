"""
テスト戦略管理モジュール

テスト戦略の階層化（ユニット → 統合 → E2E）とテスト実行フロー管理を提供
循環参照検出などの統合テスト機能をTDDワークフローに統合
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json


class TestLevel(Enum):
    """テストレベル定義"""
    UNIT = 1
    INTEGRATION = 2
    E2E = 3


@dataclass
class TestResult:
    """テスト結果データクラス"""
    level: TestLevel
    passed: bool
    failed: int
    total: int
    duration: float
    details: str = ""
    timestamp: Optional[datetime] = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """成功率計算"""
        if self.total == 0:
            return 0.0
        return ((self.total - self.failed) / self.total) * 100.0


class TestExecutionError(Exception):
    """テスト実行エラー"""
    pass


class TestStrategy:
    """テスト戦略管理クラス"""
    
    def __init__(self):
        """初期化"""
        self._enabled_levels = {
            TestLevel.UNIT: True,
            TestLevel.INTEGRATION: True,
            TestLevel.E2E: True
        }
        self._results = []
        self._runners = {}
        
    def is_level_enabled(self, level: TestLevel) -> bool:
        """テストレベルの有効性確認"""
        return self._enabled_levels.get(level, False)
        
    def enable_level(self, level: TestLevel):
        """テストレベル有効化"""
        self._enabled_levels[level] = True
        
    def disable_level(self, level: TestLevel):
        """テストレベル無効化"""
        self._enabled_levels[level] = False
        
    def get_execution_order(self) -> List[TestLevel]:
        """実行順序取得"""
        all_levels = [TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.E2E]
        return [level for level in all_levels if self.is_level_enabled(level)]
        
    def record_result(self, result: TestResult):
        """テスト結果記録"""
        self._results.append(result)
        
    def get_results(self) -> List[TestResult]:
        """全テスト結果取得"""
        return self._results.copy()
        
    def get_results_for_level(self, level: TestLevel) -> List[TestResult]:
        """レベル別テスト結果取得"""
        return [r for r in self._results if r.level == level]
        
    def set_runner(self, level: TestLevel, runner: Callable):
        """テストランナー設定"""
        self._runners[level] = runner
        
    def execute_flow(self, stop_on_failure: bool = True) -> List[TestResult]:
        """テストフロー実行"""
        results = []
        
        for level in self.get_execution_order():
            if level not in self._runners:
                continue
                
            try:
                runner = self._runners[level]
                result = runner()
                
                self.record_result(result)
                results.append(result)
                
                # 失敗時の停止判定
                if stop_on_failure and not result.passed:
                    break
                    
            except Exception as e:
                raise TestExecutionError(f"Test execution failed at {level.name}: {str(e)}")
                
        return results
        
    def execute_single_level(self, level: TestLevel) -> TestResult:
        """単一レベルテスト実行"""
        if level not in self._runners:
            raise TestExecutionError(f"No runner configured for {level.name}")
            
        try:
            runner = self._runners[level]
            result = runner()
            self.record_result(result)
            return result
        except Exception as e:
            raise TestExecutionError(f"Test execution failed for {level.name}: {str(e)}")
            
    def generate_summary(self) -> Dict[str, Any]:
        """サマリーレポート生成"""
        if not self._results:
            return {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "total_duration": 0.0,
                "success_rate": 0.0
            }
            
        total_tests = sum(r.total for r in self._results)
        failed_tests = sum(r.failed for r in self._results)
        passed_tests = total_tests - failed_tests
        total_duration = sum(r.duration for r in self._results)
        success_rate = (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "total_duration": total_duration,
            "success_rate": success_rate
        }
        
    def clear_results(self):
        """結果履歴クリア"""
        self._results.clear()
        
    def to_json(self) -> str:
        """JSON形式でエクスポート"""
        data = {
            "enabled_levels": {level.name: enabled for level, enabled in self._enabled_levels.items()},
            "results": [
                {
                    "level": r.level.name,
                    "passed": r.passed,
                    "failed": r.failed,
                    "total": r.total,
                    "duration": r.duration,
                    "details": r.details,
                    "success_rate": r.success_rate,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None
                }
                for r in self._results
            ],
            "summary": self.generate_summary()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'TestStrategy':
        """JSON形式からインポート"""
        data = json.loads(json_str)
        strategy = cls()
        
        # 有効レベル復元
        for level_name, enabled in data.get("enabled_levels", {}).items():
            level = TestLevel[level_name]
            if enabled:
                strategy.enable_level(level)
            else:
                strategy.disable_level(level)
                
        # 結果復元
        for result_data in data.get("results", []):
            level = TestLevel[result_data["level"]]
            timestamp = None
            if result_data.get("timestamp"):
                timestamp = datetime.fromisoformat(result_data["timestamp"])
                
            result = TestResult(
                level=level,
                passed=result_data["passed"],
                failed=result_data["failed"],
                total=result_data["total"],
                duration=result_data["duration"],
                details=result_data.get("details", ""),
                timestamp=timestamp
            )
            strategy.record_result(result)
            
        return strategy