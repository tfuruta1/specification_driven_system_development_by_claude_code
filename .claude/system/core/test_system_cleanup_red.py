#!/usr/bin/env python3
"""
RED Phase: System Cleanup Detection Tests
Tests that should fail until issues are resolved
"""
import os
import re
import sys
from pathlib import Path
import pytest

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

class TestSystemCleanupRed:
    """RED phase tests - should fail until fixes are applied"""
    
    def setup_method(self):
        """Setup test environment"""
        self.claude_dir = Path(__file__).parent.parent
        self.core_dir = Path(__file__).parent
        
    def test_no_emoji_placeholders_exist(self):
        """RED: This test should FAIL - emoji placeholders exist"""
        emoji_pattern = re.compile(r'\[EMOJI\]')
        files_with_emojis = []
        total_emoji_count = 0
        
        for root, dirs, files in os.walk(self.claude_dir):
            # Skip .git and other irrelevant directories
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            
            for file in files:
                if file.endswith(('.py', '.md', '.json')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            matches = emoji_pattern.findall(content)
                            if matches:
                                files_with_emojis.append(str(file_path))
                                total_emoji_count += len(matches)
                    except Exception:
                        continue
        
        # This should FAIL initially
        assert len(files_with_emojis) == 0, f"Found {total_emoji_count} ERROR placeholders in {len(files_with_emojis)} files: {files_with_emojis[:5]}..."
    
    def test_no_duplicate_auto_mode_files(self):
        """RED: This test should FAIL - duplicate auto_mode.py exists"""
        auto_mode_files = []
        
        for root, dirs, files in os.walk(self.claude_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            for file in files:
                if file == 'auto_mode.py':
                    auto_mode_files.append(Path(root) / file)
        
        # This should FAIL initially
        assert len(auto_mode_files) <= 1, f"Found duplicate auto_mode.py files: {auto_mode_files}"
    
    def test_no_duplicate_init_files_with_same_content(self):
        """RED: This test should FAIL - duplicate __init__.py with same content exists"""
        init_files = []
        
        for root, dirs, files in os.walk(self.claude_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            for file in files:
                if file == '__init__.py':
                    init_files.append(Path(root) / file)
        
        # Check for content duplicates
        file_contents = {}
        duplicates = []
        
        for init_file in init_files:
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content in file_contents:
                        duplicates.append((init_file, file_contents[content]))
                    else:
                        file_contents[content] = init_file
            except Exception:
                continue
        
        # This should FAIL initially if duplicates exist
        assert len(duplicates) == 0, f"Found duplicate __init__.py content: {duplicates}"
    
    def test_no_circular_imports_detected(self):
        """RED: This test should FAIL if circular imports exist"""
        try:
            # Try importing key modules to detect circular imports
            from auto_mode import AutoMode
            from system import ClaudeCodeSystem
            from unified_system import UnifiedSystem
            success = True
        except ImportError as e:
            success = False
            error_msg = str(e)
        
        # This should FAIL initially if circular imports exist
        assert success, f"Circular import detected: {error_msg if not success else ''}"

if __name__ == "__main__":
    # Run tests to see current failures
    pytest.main([__file__, "-v", "--tb=short"])