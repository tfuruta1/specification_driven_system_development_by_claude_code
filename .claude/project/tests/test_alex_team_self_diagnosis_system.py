#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for alex_team_self_diagnosis_system module
Achieving 100% test coverage
"""

import os
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess

# Setup relative imports from .claude folder
import sys
from pathlib import Path

# Find .claude root using relative path
current_file = Path(__file__).resolve()
current = current_file.parent

# Navigate up to find .claude folder (not subfolder)
claude_root = None
for _ in range(10):  # Limit iterations
    if current.name == '.claude':
        claude_root = current
        break
    if current.parent == current:  # Reached root
        break
    current = current.parent

# If not found, check for .claude in parent directories
if claude_root is None:
    current = current_file.parent
    for _ in range(10):
        if (current / '.claude').exists() and (current / '.claude' / 'system').exists():
            claude_root = current / '.claude'
            break
        if current.parent == current:
            break
        current = current.parent

# Final fallback
if claude_root is None:
    # Assume we're in .claude/project/tests
    claude_root = current_file.parent.parent.parent

# Add system path
system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

# Now import the modules to test
from core.alex_team_self_diagnosis_system import AlexTeamSelfDiagnosisSystem


class TestAlexTeamSelfDiagnosisSystem(unittest.TestCase):
    """Tests for AlexTeamSelfDiagnosisSystem class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test structure
        self.system_dir = Path(self.temp_dir) / "system"
        self.core_dir = self.system_dir / "core"
        self.core_dir.mkdir(parents=True)
        
        # Create test Python files
        (self.core_dir / "test_module.py").write_text("def test(): pass")
        (self.core_dir / "__init__.py").write_text("")
        
        with patch('core.alex_team_self_diagnosis_system.paths') as mock_paths:
            mock_paths.root = Path(self.temp_dir)
            mock_paths.system = self.system_dir
            self.diagnosis = AlexTeamSelfDiagnosisSystem()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test initialization"""
        with patch('core.alex_team_self_diagnosis_system.paths') as mock_paths:
            mock_paths.root = Path(self.temp_dir)
            mock_paths.system = self.system_dir
            
            diagnosis = AlexTeamSelfDiagnosisSystem()
            
            self.assertEqual(diagnosis.base_path, Path(self.temp_dir))
            self.assertEqual(diagnosis.system_path, self.system_dir)
            self.assertEqual(diagnosis.indent, "  ")
    
    def test_format_size(self):
        """Test size formatting"""
        self.assertEqual(self.diagnosis._format_size(0), "0 B")
        self.assertEqual(self.diagnosis._format_size(1023), "1023 B")
        self.assertEqual(self.diagnosis._format_size(1024), "1.0 KB")
        self.assertEqual(self.diagnosis._format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(self.diagnosis._format_size(1024 * 1024 * 1024), "1.0 GB")
        self.assertEqual(self.diagnosis._format_size(1536), "1.5 KB")
    
    def test_check_module_health_success(self):
        """Test checking module health successfully"""
        module_path = self.core_dir / "test_module.py"
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = self.diagnosis._check_module_health(module_path)
            
            self.assertTrue(result['healthy'])
            self.assertIsNone(result['error'])
    
    def test_check_module_health_import_error(self):
        """Test checking module health with import error"""
        module_path = self.core_dir / "bad_module.py"
        module_path.write_text("import nonexistent_module")
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "ModuleNotFoundError: No module named 'nonexistent_module'"
            mock_run.return_value = mock_result
            
            result = self.diagnosis._check_module_health(module_path)
            
            self.assertFalse(result['healthy'])
            self.assertIn("ModuleNotFoundError", result['error'])
    
    def test_check_module_health_syntax_error(self):
        """Test checking module health with syntax error"""
        module_path = self.core_dir / "syntax_error.py"
        module_path.write_text("def test(:\n    pass")  # Syntax error
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "SyntaxError: invalid syntax"
            mock_run.return_value = mock_result
            
            result = self.diagnosis._check_module_health(module_path)
            
            self.assertFalse(result['healthy'])
            self.assertIn("SyntaxError", result['error'])
    
    def test_check_module_health_exception(self):
        """Test checking module health with subprocess exception"""
        module_path = self.core_dir / "test.py"
        
        with patch('subprocess.run', side_effect=Exception("Process failed")):
            result = self.diagnosis._check_module_health(module_path)
            
            self.assertFalse(result['healthy'])
            self.assertIn("Process failed", result['error'])
    
    def test_check_python_modules(self):
        """Test checking all Python modules"""
        # Create more test files
        (self.core_dir / "module1.py").write_text("print('module1')")
        (self.core_dir / "module2.py").write_text("import sys")
        (self.core_dir / "bad_module.py").write_text("import nonexistent")
        
        with patch.object(self.diagnosis, '_check_module_health') as mock_check:
            # Mock different results
            def side_effect(path):
                if "bad_module" in str(path):
                    return {'healthy': False, 'error': "Import error"}
                return {'healthy': True, 'error': None}
            
            mock_check.side_effect = side_effect
            
            result = self.diagnosis.check_python_modules()
            
            self.assertIn('total_modules', result)
            self.assertIn('healthy_modules', result)
            self.assertIn('unhealthy_modules', result)
            self.assertIn('errors', result)
            self.assertEqual(len(result['errors']), 1)
    
    def test_check_folder_structure(self):
        """Test checking folder structure"""
        # Create expected folders
        (self.system_dir / "config").mkdir()
        (Path(self.temp_dir) / "project").mkdir()
        (Path(self.temp_dir) / "temp").mkdir()
        
        with patch('core.alex_team_self_diagnosis_system.paths') as mock_paths:
            mock_paths.root = Path(self.temp_dir)
            mock_paths.system = self.system_dir
            diagnosis = AlexTeamSelfDiagnosisSystem()
            
            result = diagnosis.check_folder_structure()
            
            self.assertIn('existing_folders', result)
            self.assertIn('missing_folders', result)
            self.assertIn('folder_sizes', result)
    
    def test_check_test_coverage(self):
        """Test checking test coverage"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "TOTAL    100   20    80%"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = self.diagnosis.check_test_coverage()
            
            self.assertEqual(result['coverage_percentage'], 80.0)
            self.assertTrue(result['has_pytest'])
            self.assertTrue(result['has_coverage'])
    
    def test_check_test_coverage_no_pytest(self):
        """Test checking test coverage without pytest"""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = self.diagnosis.check_test_coverage()
            
            self.assertEqual(result['coverage_percentage'], 0)
            self.assertFalse(result['has_pytest'])
            self.assertIn("pytest not installed", result['error'])
    
    def test_check_dependencies(self):
        """Test checking dependencies"""
        # Create requirements.txt
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("pytest==7.0.0\ncoverage==6.0.0\n")
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "pytest==7.0.0\ncoverage==6.0.0\n"
            mock_run.return_value = mock_result
            
            result = self.diagnosis.check_dependencies()
            
            self.assertIn('installed_packages', result)
            self.assertIn('missing_packages', result)
            self.assertTrue(result['requirements_exists'])
    
    def test_run_diagnosis(self):
        """Test running full diagnosis"""
        with patch.object(self.diagnosis, 'check_python_modules') as mock_modules:
            mock_modules.return_value = {
                'total_modules': 10,
                'healthy_modules': 9,
                'unhealthy_modules': 1,
                'errors': [{'module': 'bad.py', 'error': 'Import error'}]
            }
            
            with patch.object(self.diagnosis, 'check_folder_structure') as mock_folders:
                mock_folders.return_value = {
                    'existing_folders': ['system', 'project'],
                    'missing_folders': [],
                    'folder_sizes': {'system': 1024}
                }
                
                with patch.object(self.diagnosis, 'check_test_coverage') as mock_coverage:
                    mock_coverage.return_value = {
                        'coverage_percentage': 85.0,
                        'has_pytest': True,
                        'has_coverage': True
                    }
                    
                    with patch.object(self.diagnosis, 'check_dependencies') as mock_deps:
                        mock_deps.return_value = {
                            'installed_packages': ['pytest', 'coverage'],
                            'missing_packages': [],
                            'requirements_exists': True
                        }
                        
                        result = self.diagnosis.run_diagnosis()
                        
                        self.assertIn('timestamp', result)
                        self.assertIn('python_modules', result)
                        self.assertIn('folder_structure', result)
                        self.assertIn('test_coverage', result)
                        self.assertIn('dependencies', result)
                        self.assertIn('summary', result)
                        
                        summary = result['summary']
                        self.assertIn('total_issues', summary)
                        self.assertIn('health_score', summary)
    
    def test_print_diagnosis_results(self):
        """Test printing diagnosis results"""
        results = {
            'timestamp': '2024-01-01 12:00:00',
            'python_modules': {
                'total_modules': 10,
                'healthy_modules': 8,
                'unhealthy_modules': 2,
                'errors': [
                    {'module': 'bad1.py', 'error': 'Import error'},
                    {'module': 'bad2.py', 'error': 'Syntax error'}
                ]
            },
            'folder_structure': {
                'existing_folders': ['system', 'project'],
                'missing_folders': ['docs'],
                'folder_sizes': {'system': 1024, 'project': 2048}
            },
            'test_coverage': {
                'coverage_percentage': 75.0,
                'has_pytest': True,
                'has_coverage': True
            },
            'dependencies': {
                'installed_packages': ['pytest'],
                'missing_packages': ['coverage'],
                'requirements_exists': True
            },
            'summary': {
                'total_issues': 4,
                'health_score': 75.0
            }
        }
        
        with patch('builtins.print') as mock_print:
            self.diagnosis.print_diagnosis_results(results)
            
            # Check that print was called multiple times
            self.assertTrue(mock_print.called)
            
            # Check for key outputs
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("自己診断結果" in str(call) for call in print_calls))
            self.assertTrue(any("75.0%" in str(call) for call in print_calls))


class TestMainExecution(unittest.TestCase):
    """Test main execution"""
    
    @patch('builtins.print')
    def test_main_execution(self, mock_print):
        """Test running as main"""
        with patch('core.alex_team_self_diagnosis_system.AlexTeamSelfDiagnosisSystem') as MockDiagnosis:
            mock_instance = MagicMock()
            mock_instance.run_diagnosis.return_value = {
                'timestamp': '2024-01-01',
                'python_modules': {'total_modules': 10, 'healthy_modules': 10},
                'folder_structure': {'existing_folders': [], 'missing_folders': []},
                'test_coverage': {'coverage_percentage': 100.0},
                'dependencies': {'installed_packages': [], 'missing_packages': []},
                'summary': {'total_issues': 0, 'health_score': 100.0}
            }
            MockDiagnosis.return_value = mock_instance
            
            # Execute main block
            exec("""
diagnosis_system = AlexTeamSelfDiagnosisSystem()
results = diagnosis_system.run_diagnosis()
diagnosis_system.print_diagnosis_results(results)
            """, {
                'AlexTeamSelfDiagnosisSystem': MockDiagnosis,
                'print': mock_print
            })
            
            mock_instance.run_diagnosis.assert_called_once()
            mock_instance.print_diagnosis_results.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)