#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動テスト生成システム - AI往復最適化
記事: https://zenn.dev/sakupanda/articles/ecb4ae7e9a240e に基づく実装

YAGNI: 現在必要な基本的なテスト生成のみ
DRY: 共通テストパターンの再利用
KISS: シンプルなテンプレートベース生成
TDD: RED→GREEN→REFACTORサイクルをサポート
"""

import ast
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from .common_base import BaseManager, BaseResult, create_result
    from .path_utils import paths, setup_import_path
    from .logger import logger
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from common_base import BaseManager, BaseResult, create_result
    from path_utils import paths, setup_import_path
    from logger import logger


@dataclass
class TestSpec:
    """テスト仕様定義"""
    module_name: str
    class_name: str
    methods: List[str]
    test_cases: Dict[str, List[str]]
    coverage_target: float = 95.0


class AutomatedTestGenerator(BaseManager):
    """自動テスト生成システム - AI往復最適化対応"""
    
    def __init__(self):
        """初期化"""
        super().__init__("AutomatedTestGenerator")
        self.templates = self._load_test_templates()
        
    def initialize(self) -> BaseResult:
        """システム初期化"""
        try:
            logger.info("Initializing Automated Test Generator")
            return create_result(True, "Test generator initialized successfully")
        except Exception as e:
            return create_result(False, f"Initialization failed: {e}")
            
    def cleanup(self) -> BaseResult:
        """クリーンアップ"""
        return create_result(True, "Test generator cleanup completed")
    
    def generate_tdd_test_suite(self, module_path: Path, spec: Optional[TestSpec] = None) -> BaseResult:
        """
        TDDテストスイート生成 - AI往復最適化
        RED/GREEN両フェーズのテストを一括生成
        """
        try:
            if not module_path.exists():
                return create_result(False, f"Module not found: {module_path}")
                
            # モジュール解析
            analysis = self._analyze_module(module_path)
            if not analysis['success']:
                return create_result(False, f"Module analysis failed: {analysis['error']}")
            
            # テスト仕様生成
            if spec is None:
                spec = self._generate_test_spec(analysis['data'])
            
            # RED Phase テスト生成
            red_tests = self._generate_red_phase_tests(spec)
            
            # GREEN Phase テスト生成  
            green_tests = self._generate_green_phase_tests(spec)
            
            # テストファイル作成
            test_file_path = self._get_test_file_path(module_path)
            test_content = self._combine_test_phases(red_tests, green_tests, spec)
            
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            logger.info(f"Generated TDD test suite: {test_file_path}")
            return create_result(
                True, 
                f"TDD test suite generated successfully",
                {"test_file": str(test_file_path), "spec": spec}
            )
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return create_result(False, f"Test generation failed: {e}")
    
    def run_test_verification_cycle(self, test_file_path: Path, max_iterations: int = 3) -> BaseResult:
        """
        自動テスト検証サイクル - AI往復削減のため自動修正
        失敗テストを自動的に修正試行
        """
        try:
            for iteration in range(max_iterations):
                logger.info(f"Running test verification cycle {iteration + 1}/{max_iterations}")
                
                # テスト実行
                result = self._run_tests(test_file_path)
                
                if result['success']:
                    return create_result(
                        True, 
                        f"Test verification successful after {iteration + 1} iterations",
                        result
                    )
                
                # 失敗分析と自動修正
                if iteration < max_iterations - 1:
                    fix_result = self._attempt_test_fix(test_file_path, result['errors'])
                    if not fix_result['success']:
                        logger.warning(f"Auto-fix failed in iteration {iteration + 1}")
            
            return create_result(
                False, 
                f"Test verification failed after {max_iterations} iterations",
                result
            )
            
        except Exception as e:
            return create_result(False, f"Test verification cycle failed: {e}")
    
    def _analyze_module(self, module_path: Path) -> Dict[str, Any]:
        """モジュール解析 - クラスとメソッドの抽出"""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                            methods.append({
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args],
                                'returns': ast.get_source_segment(content, item.returns) if item.returns else None
                            })
                    
                    classes.append({
                        'name': node.name,
                        'methods': methods,
                        'bases': [base.id if hasattr(base, 'id') else str(base) for base in node.bases]
                    })
                
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': ast.get_source_segment(content, node.returns) if item.returns else None
                    })
            
            return {
                'success': True,
                'data': {
                    'classes': classes,
                    'functions': functions,
                    'module_name': module_path.stem
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_test_spec(self, analysis_data: Dict[str, Any]) -> TestSpec:
        """解析データからテスト仕様生成"""
        module_name = analysis_data['module_name']
        
        # メインクラスを特定（BaseManagerを継承している、または最初のクラス）
        main_class = None
        for cls in analysis_data['classes']:
            if 'BaseManager' in cls['bases'] or main_class is None:
                main_class = cls
                break
        
        if main_class is None:
            # クラスがない場合は関数をテスト対象とする
            methods = [f['name'] for f in analysis_data['functions']]
            class_name = f"{module_name.title()}Functions"
        else:
            methods = [m['name'] for m in main_class['methods']]
            class_name = main_class['name']
        
        # テストケース生成
        test_cases = {}
        for method in methods:
            test_cases[method] = [
                f"test_{method}_valid_input",
                f"test_{method}_invalid_input", 
                f"test_{method}_edge_cases"
            ]
        
        return TestSpec(
            module_name=module_name,
            class_name=class_name,
            methods=methods,
            test_cases=test_cases
        )
    
    def _generate_red_phase_tests(self, spec: TestSpec) -> str:
        """RED Phase テスト生成 - 失敗テスト"""
        red_tests = []
        
        for method, test_cases in spec.test_cases.items():
            for test_case in test_cases:
                if 'invalid' in test_case or 'edge' in test_case:
                    red_tests.append(f'''
    def {test_case}(self):
        """RED Phase: {method} の異常系テスト"""
        # TODO: 異常なパラメータでテスト
        with self.assertRaises(Exception):
            # 実装に応じて適切な異常系テストを記述
            pass
''')
        
        return '\n'.join(red_tests)
    
    def _generate_green_phase_tests(self, spec: TestSpec) -> str:
        """GREEN Phase テスト生成 - 成功テスト"""
        green_tests = []
        
        for method, test_cases in spec.test_cases.items():
            for test_case in test_cases:
                if 'valid' in test_case:
                    green_tests.append(f'''
    def {test_case}(self):
        """GREEN Phase: {method} の正常系テスト"""
        # TODO: 正常なパラメータでテスト
        result = self.instance.{method}()
        self.assertIsNotNone(result)
        # 期待される結果を検証
''')
        
        return '\n'.join(green_tests)
    
    def _combine_test_phases(self, red_tests: str, green_tests: str, spec: TestSpec) -> str:
        """RED/GREEN両フェーズを統合したテストファイル生成"""
        template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動生成テストファイル - TDD対応
Generated by AutomatedTestGenerator
Target: {spec.module_name}
Coverage Target: {spec.coverage_target}%
"""

import unittest
import sys
from pathlib import Path

# Standard path setup pattern
current = Path(__file__).resolve()
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    current = current.parent
    if current == current.parent:
        raise RuntimeError("Could not find .claude directory")

system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

try:
    from core.{spec.module_name} import {spec.class_name}
    from core.common_base import BaseResult
except ImportError as e:
    print(f"Import error: {{e}}")
    sys.exit(1)


class Test{spec.class_name}(unittest.TestCase):
    """TDD テストクラス - {spec.class_name}"""
    
    def setUp(self):
        """テスト前準備"""
        self.instance = {spec.class_name}()
        
    def tearDown(self):
        """テスト後クリーンアップ"""
        if hasattr(self.instance, 'cleanup'):
            self.instance.cleanup()
    
    # === RED Phase Tests (失敗テスト) ===
{red_tests}
    
    # === GREEN Phase Tests (成功テスト) ===
{green_tests}


if __name__ == '__main__':
    unittest.main(verbosity=2)
'''
        return template
    
    def _get_test_file_path(self, module_path: Path) -> Path:
        """テストファイルパスを生成"""
        test_dir = paths.tests
        test_filename = f"test_{module_path.stem}_auto.py"
        return test_dir / test_filename
    
    def _run_tests(self, test_file_path: Path) -> Dict[str, Any]:
        """テスト実行"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_file_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(paths.root)
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'errors': result.stderr.split('\n') if result.stderr else []
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Test execution timed out',
                'errors': ['Timeout']
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'errors': [str(e)]
            }
    
    def _attempt_test_fix(self, test_file_path: Path, errors: List[str]) -> Dict[str, Any]:
        """テスト自動修正試行 - AI往復削減のための基本修正"""
        try:
            # 一般的なエラーパターンの自動修正
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            
            # 一般的な修正パターン
            if 'ImportError' in '\n'.join(errors):
                # インポートエラーの修正試行
                if 'from core.' in content:
                    content = content.replace('from core.', 'from ')
                    modified = True
            
            if 'AttributeError' in '\n'.join(errors):
                # メソッド名エラーの修正試行（よくあるパターン）
                common_fixes = {
                    'initialize': 'init',
                    'process': 'run',
                    'validate': 'check'
                }
                for old, new in common_fixes.items():
                    if f'.{old}()' in content:
                        content = content.replace(f'.{old}()', f'.{new}()')
                        modified = True
            
            if modified:
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {'success': True, 'message': 'Auto-fix applied'}
            
            return {'success': False, 'message': 'No applicable auto-fixes found'}
            
        except Exception as e:
            return {'success': False, 'message': f'Auto-fix failed: {e}'}
    
    def _load_test_templates(self) -> Dict[str, str]:
        """テストテンプレート読み込み"""
        # 基本的なテンプレートを内蔵
        return {
            'basic_test': '''
    def test_{method}_basic(self):
        """基本的な動作テスト"""
        result = self.instance.{method}()
        self.assertIsNotNone(result)
''',
            'error_test': '''
    def test_{method}_error(self):
        """エラーケーステスト"""
        with self.assertRaises(Exception):
            self.instance.{method}(invalid_param)
'''
        }


def generate_tests_for_module(module_name: str) -> BaseResult:
    """モジュール用テスト生成のメインエントリーポイント"""
    generator = AutomatedTestGenerator()
    
    # 初期化
    init_result = generator.initialize()
    if not init_result.success:
        return init_result
    
    # モジュールパス特定
    module_path = paths.core / f"{module_name}.py"
    
    # テスト生成
    gen_result = generator.generate_tdd_test_suite(module_path)
    if not gen_result.success:
        return gen_result
    
    # 検証サイクル実行
    test_file_path = Path(gen_result.data['test_file'])
    verify_result = generator.run_test_verification_cycle(test_file_path)
    
    # クリーンアップ
    generator.cleanup()
    
    return create_result(
        verify_result.success,
        f"Automated test generation completed for {module_name}",
        {
            'module': module_name,
            'test_file': str(test_file_path),
            'verification': verify_result.success
        }
    )


def main():
    """コマンドライン実行用"""
    if len(sys.argv) < 2:
        print("Usage: python automated_test_generator.py <module_name>")
        return 1
    
    module_name = sys.argv[1]
    result = generate_tests_for_module(module_name)
    
    print(f"Result: {result.message}")
    if result.data:
        print(f"Details: {json.dumps(result.data, indent=2)}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())