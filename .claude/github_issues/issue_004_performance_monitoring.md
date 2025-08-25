# Issue #4: パフォーマンス監視システムの実装

## 概要
システムのパフォーマンスを継続的に監視し、ボトルネックを特定する仕組みを追加

## 背景
現在パフォーマンスの計測が行われておらず、最適化の機会を見逃している可能性がある

## タスク

### 1. パフォーマンスモニターの作成
**新規ファイル**: `.claude/system/core/performance_monitor.py`
```python
import time
import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

@dataclass
class MetricData:
    """メトリクスデータ"""
    function_name: str
    duration: float
    timestamp: datetime
    success: bool
    memory_usage: Optional[int] = None
    
class PerformanceMonitor:
    """パフォーマンス監視システム"""
    
    def __init__(self):
        self.metrics: Dict[str, List[MetricData]] = {}
        self.metrics_file = Path(".claude/logs/performance_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
    def measure(self, include_memory: bool = False) -> Callable:
        """
        パフォーマンス計測デコレータ
        
        Args:
            include_memory: メモリ使用量も計測するか
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # 開始時刻とメモリ
                start_time = time.perf_counter()
                start_memory = None
                
                if include_memory:
                    import tracemalloc
                    tracemalloc.start()
                    start_memory = tracemalloc.get_traced_memory()[0]
                
                success = True
                try:
                    # 関数実行
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    # 終了時刻とメモリ
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    memory_usage = None
                    if include_memory:
                        current, peak = tracemalloc.get_traced_memory()
                        memory_usage = peak - start_memory
                        tracemalloc.stop()
                    
                    # メトリクス記録
                    metric = MetricData(
                        function_name=func.__name__,
                        duration=duration,
                        timestamp=datetime.now(),
                        success=success,
                        memory_usage=memory_usage
                    )
                    self._record_metric(metric)
                    
            return wrapper
        return decorator
    
    def _record_metric(self, metric: MetricData):
        """メトリクスを記録"""
        if metric.function_name not in self.metrics:
            self.metrics[metric.function_name] = []
        
        self.metrics[metric.function_name].append(metric)
        
        # 1000件を超えたら古いものを削除
        if len(self.metrics[metric.function_name]) > 1000:
            self.metrics[metric.function_name] = self.metrics[metric.function_name][-1000:]
    
    def get_statistics(self, function_name: str, 
                       last_n_minutes: Optional[int] = None) -> Dict[str, Any]:
        """
        統計情報を取得
        
        Args:
            function_name: 関数名
            last_n_minutes: 過去N分間のデータのみ対象
        """
        if function_name not in self.metrics:
            return {}
        
        metrics = self.metrics[function_name]
        
        # 時間フィルタリング
        if last_n_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=last_n_minutes)
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        if not metrics:
            return {}
        
        durations = [m.duration for m in metrics]
        success_count = sum(1 for m in metrics if m.success)
        
        stats = {
            "function_name": function_name,
            "call_count": len(metrics),
            "success_count": success_count,
            "failure_count": len(metrics) - success_count,
            "success_rate": success_count / len(metrics) * 100,
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "median_duration": statistics.median(durations),
        }
        
        # メモリ統計（あれば）
        memory_usages = [m.memory_usage for m in metrics if m.memory_usage]
        if memory_usages:
            stats.update({
                "avg_memory_usage": statistics.mean(memory_usages),
                "max_memory_usage": max(memory_usages),
            })
        
        return stats
    
    def save_metrics(self):
        """メトリクスをファイルに保存"""
        data = {}
        for func_name, metrics_list in self.metrics.items():
            data[func_name] = [
                {
                    **asdict(m),
                    "timestamp": m.timestamp.isoformat()
                }
                for m in metrics_list[-100:]  # 最新100件のみ保存
            ]
        
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_report(self) -> str:
        """パフォーマンスレポートを生成"""
        report = ["Performance Report", "=" * 50, ""]
        
        for func_name in self.metrics:
            stats = self.get_statistics(func_name)
            if stats:
                report.append(f"Function: {func_name}")
                report.append(f"  Calls: {stats['call_count']}")
                report.append(f"  Success Rate: {stats['success_rate']:.1f}%")
                report.append(f"  Avg Duration: {stats['avg_duration']:.4f}s")
                report.append(f"  Min/Max: {stats['min_duration']:.4f}s / {stats['max_duration']:.4f}s")
                
                if 'avg_memory_usage' in stats:
                    report.append(f"  Avg Memory: {stats['avg_memory_usage'] / 1024:.1f} KB")
                
                report.append("")
        
        return "\n".join(report)

# グローバルインスタンス
performance_monitor = PerformanceMonitor()
```

### 2. CoreSystemへの適用
**ファイル**: `.claude/system/core/core_system.py`

**変更前**:
```python
def organize_files(self) -> Result:
    # 処理
    return Result(True, f"Organized {moved_count} files")
```

**変更後**:
```python
from .performance_monitor import performance_monitor

class CoreSystem:
    @performance_monitor.measure()
    def organize_files(self) -> Result:
        # 処理
        return Result(True, f"Organized {moved_count} files")
    
    @performance_monitor.measure(include_memory=True)
    def run_tests(self) -> Result:
        # メモリ使用量も計測する重要な処理
        # 処理
        return Result(success, message, coverage_info)
```

### 3. パフォーマンスダッシュボードの作成
**新規ファイル**: `.claude/system/core/performance_dashboard.py`
```python
from datetime import datetime
from pathlib import Path
from .performance_monitor import performance_monitor

class PerformanceDashboard:
    """パフォーマンスダッシュボード"""
    
    def generate_html_report(self) -> str:
        """HTML形式のレポートを生成"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Performance Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .good { color: green; }
        .warning { color: orange; }
        .bad { color: red; }
    </style>
</head>
<body>
    <h1>Performance Dashboard</h1>
    <p>Generated: {timestamp}</p>
    <table>
        <tr>
            <th>Function</th>
            <th>Calls</th>
            <th>Success Rate</th>
            <th>Avg Duration</th>
            <th>Max Duration</th>
            <th>Status</th>
        </tr>
        {rows}
    </table>
</body>
</html>
"""
        rows = []
        for func_name in performance_monitor.metrics:
            stats = performance_monitor.get_statistics(func_name)
            if stats:
                # パフォーマンス判定
                if stats['avg_duration'] < 0.1:
                    status = '<span class="good">Good</span>'
                elif stats['avg_duration'] < 1.0:
                    status = '<span class="warning">Warning</span>'
                else:
                    status = '<span class="bad">Slow</span>'
                
                row = f"""
        <tr>
            <td>{func_name}</td>
            <td>{stats['call_count']}</td>
            <td>{stats['success_rate']:.1f}%</td>
            <td>{stats['avg_duration']:.4f}s</td>
            <td>{stats['max_duration']:.4f}s</td>
            <td>{status}</td>
        </tr>"""
                rows.append(row)
        
        return html.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rows="".join(rows)
        )
    
    def save_dashboard(self):
        """ダッシュボードをファイルに保存"""
        dashboard_file = Path(".claude/reports/performance_dashboard.html")
        dashboard_file.parent.mkdir(parents=True, exist_ok=True)
        
        html = self.generate_html_report()
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return dashboard_file
```

### 4. CLIコマンドの追加
**ファイル**: `.claude/claude`

**追加部分**:
```python
def execute_command(command: str, **kwargs) -> Result:
    commands = {
        # 既存のコマンド
        "organize": self.organize_files,
        "cleanup": self.cleanup_temp,
        "test": self.run_tests,
        "check": self.check_code_quality,
        "status": lambda: Result(True, "OK", self.get_status()),
        # 新規コマンド
        "perf": self.show_performance,
        "perf-report": self.generate_performance_report,
    }
    
def show_performance(self) -> Result:
    """パフォーマンス統計を表示"""
    from .performance_monitor import performance_monitor
    report = performance_monitor.generate_report()
    return Result(True, "Performance Report", {"report": report})

def generate_performance_report(self) -> Result:
    """パフォーマンスレポートを生成"""
    from .performance_dashboard import PerformanceDashboard
    dashboard = PerformanceDashboard()
    file_path = dashboard.save_dashboard()
    return Result(True, f"Dashboard saved to {file_path}")
```

### 5. テストの作成
**新規ファイル**: `.claude/project/tests/test_performance_monitor.py`
```python
import unittest
import time
from system.core.performance_monitor import PerformanceMonitor

class TestPerformanceMonitor(unittest.TestCase):
    
    def setUp(self):
        self.monitor = PerformanceMonitor()
    
    def test_measure_decorator(self):
        """計測デコレータのテスト"""
        @self.monitor.measure()
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        self.assertEqual(result, "done")
        
        stats = self.monitor.get_statistics("slow_function")
        self.assertIsNotNone(stats)
        self.assertGreaterEqual(stats['avg_duration'], 0.1)
    
    def test_memory_measurement(self):
        """メモリ計測のテスト"""
        @self.monitor.measure(include_memory=True)
        def memory_intensive():
            data = [i for i in range(100000)]
            return len(data)
        
        result = memory_intensive()
        self.assertEqual(result, 100000)
        
        stats = self.monitor.get_statistics("memory_intensive")
        self.assertIn('avg_memory_usage', stats)
    
    def test_failure_tracking(self):
        """失敗トラッキングのテスト"""
        @self.monitor.measure()
        def failing_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        stats = self.monitor.get_statistics("failing_function")
        self.assertEqual(stats['success_rate'], 0.0)
```

## 受け入れ条件
- [ ] パフォーマンスモニターが正常に動作する
- [ ] 主要な関数にデコレータが適用されている
- [ ] パフォーマンスレポートが生成される
- [ ] HTMLダッシュボードが表示される
- [ ] テストが全て通る

## 実装手順
1. performance_monitor.pyを作成
2. performance_dashboard.pyを作成
3. CoreSystemクラスにデコレータを適用
4. CLIコマンドを追加
5. テストを作成・実行

## 優先度
**中**

## 見積もり工数
3-4時間

## ラベル
- enhancement
- performance
- monitoring