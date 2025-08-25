#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standard import setup for all test files
Copy this pattern to the top of each test file
"""

from pathlib import Path

IMPORT_SETUP = '''# Setup relative imports from .claude folder
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
'''

# Files to update
test_files = [
    'test_cache.py',
    'test_cache_optimized.py',
    'test_config.py',
    'test_logger.py',
    'test_jst_utils.py',
    'test_alex_team_self_diagnosis_system.py',
    'test_runner_100_coverage.py'
]

def update_test_file(filename):
    """Update test file with proper import setup"""
    filepath = Path(__file__).parent / filename
    
    if not filepath.exists():
        print(f"Skipping {filename} - not found")
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # Check if already has the new import pattern
    if "Navigate up to find .claude folder" in content:
        print(f"Skipping {filename} - already updated")
        return
    
    # Find where to insert (after imports, before actual code)
    lines = content.split('\n')
    insert_pos = 0
    
    # Find the end of docstring and imports
    in_docstring = False
    for i, line in enumerate(lines):
        if '"""' in line:
            in_docstring = not in_docstring
        elif not in_docstring:
            if line.startswith('from test_base import') or line.startswith('# Use relative import setup'):
                # Found the old import line
                # Remove old import setup lines
                while i < len(lines) and (
                    lines[i].startswith('from test_base') or 
                    lines[i].startswith('# Use relative') or
                    lines[i].strip() == ''
                ):
                    lines.pop(i)
                    if i >= len(lines):
                        break
                
                # Insert new import setup
                import_lines = IMPORT_SETUP.split('\n')
                for j, import_line in enumerate(import_lines):
                    lines.insert(i + j, import_line)
                break
    
    # Write back
    new_content = '\n'.join(lines)
    filepath.write_text(new_content, encoding='utf-8')
    print(f"Updated {filename}")

if __name__ == '__main__':
    print("Updating test files with relative import setup...")
    for test_file in test_files:
        update_test_file(test_file)
    print("Done!")