#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for commands module
Achieving 100% test coverage
"""

import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

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

from core.commands import CommandExecutor


class TestCommandExecutor(unittest.TestCase):
    """Test CommandExecutor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('core.commands.logger'):
            self.executor = CommandExecutor()
    
    def test_init(self):
        """Test initialization"""
        self.assertIsNotNone(self.executor)
        self.assertTrue(hasattr(self.executor, 'commands'))
        self.assertIsInstance(self.executor.commands, dict)
    
    def test_execute_unknown_command(self):
        """Test executing unknown command"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute("unknown_command", [])
            mock_logger.error.assert_called()
    
    def test_execute_spec_command(self):
        """Test executing spec command"""
        with patch.object(self.executor, 'execute_spec') as mock_spec:
            self.executor.execute("spec", ["init"])
            mock_spec.assert_called_once_with(["init"])
    
    def test_execute_analyze_command(self):
        """Test executing analyze command"""
        with patch.object(self.executor, 'execute_analyze') as mock_analyze:
            self.executor.execute("analyze", [])
            mock_analyze.assert_called_once()
    
    def test_execute_requirements_command(self):
        """Test executing requirements command"""
        with patch.object(self.executor, 'execute_requirements') as mock_req:
            self.executor.execute("requirements", [])
            mock_req.assert_called_once()
    
    def test_execute_design_command(self):
        """Test executing design command"""
        with patch.object(self.executor, 'execute_design') as mock_design:
            self.executor.execute("design", [])
            mock_design.assert_called_once()
    
    def test_execute_tasks_command(self):
        """Test executing tasks command"""
        with patch.object(self.executor, 'execute_tasks') as mock_tasks:
            self.executor.execute("tasks", [])
            mock_tasks.assert_called_once()
    
    def test_execute_modeltest_command(self):
        """Test executing modeltest command"""
        with patch.object(self.executor, 'execute_modeltest') as mock_test:
            self.executor.execute("modeltest", [])
            mock_test.assert_called_once()
    
    def test_execute_log_command(self):
        """Test executing log command"""
        with patch.object(self.executor, 'execute_log') as mock_log:
            self.executor.execute("log", [])
            mock_log.assert_called_once()
    
    def test_execute_auto_mode_command(self):
        """Test executing auto_mode command"""
        with patch.object(self.executor, 'execute_auto_mode') as mock_auto:
            self.executor.execute("auto_mode", ["on"])
            mock_auto.assert_called_once_with(["on"])
    
    def test_spec_init(self):
        """Test spec init subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.spec_init()
            mock_logger.info.assert_called()
    
    def test_spec_requirements(self):
        """Test spec requirements subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.spec_requirements()
            mock_logger.info.assert_called()
    
    def test_spec_design(self):
        """Test spec design subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.spec_design()
            mock_logger.info.assert_called()
    
    def test_spec_tasks(self):
        """Test spec tasks subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.spec_tasks()
            mock_logger.info.assert_called()
    
    def test_spec_implement(self):
        """Test spec implement subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.spec_implement()
            mock_logger.info.assert_called()
    
    def test_spec_status(self):
        """Test spec status subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.spec_status()
            mock_logger.info.assert_called()
    
    def test_execute_spec_with_subcommands(self):
        """Test execute_spec with different subcommands"""
        subcommands = ["init", "requirements", "design", "tasks", "implement", "status"]
        
        for cmd in subcommands:
            with patch.object(self.executor, f'spec_{cmd}') as mock_method:
                self.executor.execute_spec([cmd])
                mock_method.assert_called_once()
    
    def test_execute_spec_invalid_subcommand(self):
        """Test execute_spec with invalid subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_spec(["invalid"])
            mock_logger.error.assert_called()
    
    def test_execute_spec_no_subcommand(self):
        """Test execute_spec with no subcommand"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_spec([])
            mock_logger.error.assert_called()
    
    def test_execute_analyze(self):
        """Test execute_analyze method"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_analyze([])
            mock_logger.info.assert_called()
    
    def test_execute_requirements(self):
        """Test execute_requirements method"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_requirements([])
            mock_logger.info.assert_called()
    
    def test_execute_design(self):
        """Test execute_design method"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_design([])
            mock_logger.info.assert_called()
    
    def test_execute_tasks(self):
        """Test execute_tasks method"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_tasks([])
            mock_logger.info.assert_called()
    
    def test_execute_modeltest(self):
        """Test execute_modeltest method"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_modeltest([])
            mock_logger.info.assert_called()
    
    def test_execute_log(self):
        """Test execute_log method"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_log([])
            mock_logger.info.assert_called()
    
    def test_execute_auto_mode_on(self):
        """Test turning auto mode on"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_auto_mode(["on"])
            mock_logger.info.assert_called()
    
    def test_execute_auto_mode_off(self):
        """Test turning auto mode off"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_auto_mode(["off"])
            mock_logger.info.assert_called()
    
    def test_execute_auto_mode_invalid(self):
        """Test auto mode with invalid argument"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_auto_mode(["invalid"])
            mock_logger.error.assert_called()
    
    def test_execute_auto_mode_no_args(self):
        """Test auto mode with no arguments"""
        with patch('core.commands.logger') as mock_logger:
            self.executor.execute_auto_mode([])
            mock_logger.info.assert_called()


class TestMainFunction(unittest.TestCase):
    """Test main function"""
    
    @patch('sys.argv', ['commands.py', 'spec', 'init'])
    @patch('core.commands.CommandExecutor')
    def test_main_with_args(self, mock_executor_class):
        """Test main function with arguments"""
        mock_instance = MagicMock()
        mock_executor_class.return_value = mock_instance
        
        from core.commands import main
        main()
        
        mock_executor_class.assert_called_once()
        mock_instance.execute.assert_called_once_with('spec', ['init'])
    
    @patch('sys.argv', ['commands.py'])
    @patch('core.commands.logger')
    def test_main_without_args(self, mock_logger):
        """Test main function without arguments"""
        from core.commands import main
        main()
        
        mock_logger.error.assert_called()
    
    @patch('sys.argv', ['commands.py', 'test'])
    @patch('core.commands.CommandExecutor')
    def test_main_single_command(self, mock_executor_class):
        """Test main with single command"""
        mock_instance = MagicMock()
        mock_executor_class.return_value = mock_instance
        
        from core.commands import main
        main()
        
        mock_instance.execute.assert_called_once_with('test', [])


class TestCommandIntegration(unittest.TestCase):
    """Test command integration scenarios"""
    
    def test_full_command_workflow(self):
        """Test complete command workflow"""
        with patch('core.commands.logger'):
            executor = CommandExecutor()
            
            # Test spec workflow
            with patch.object(executor, 'spec_init') as mock_init:
                with patch.object(executor, 'spec_requirements') as mock_req:
                    with patch.object(executor, 'spec_design') as mock_design:
                        with patch.object(executor, 'spec_implement') as mock_impl:
                            with patch.object(executor, 'spec_status') as mock_status:
                                # Execute spec workflow
                                executor.execute_spec(['init'])
                                executor.execute_spec(['requirements'])
                                executor.execute_spec(['design'])
                                executor.execute_spec(['implement'])
                                executor.execute_spec(['status'])
                                
                                # Verify all were called
                                mock_init.assert_called_once()
                                mock_req.assert_called_once()
                                mock_design.assert_called_once()
                                mock_impl.assert_called_once()
                                mock_status.assert_called_once()
    
    def test_error_handling(self):
        """Test error handling in commands"""
        with patch('core.commands.logger') as mock_logger:
            executor = CommandExecutor()
            
            # Test various error conditions
            executor.execute(None, [])  # None command
            executor.execute("", [])    # Empty command
            executor.execute("unknown", None)  # None args
            
            # Should handle all gracefully
            self.assertGreater(mock_logger.error.call_count, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)