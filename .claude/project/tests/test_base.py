#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base test module for setting up relative imports
All test files should import this module first
"""

import sys
from pathlib import Path

# Get the .claude root directory using relative path from test file
def setup_test_paths():
    """Setup paths for test imports - must work from any location"""
    # Get current test file directory
    current_file = Path(__file__).resolve()
    
    # Navigate up to find .claude folder
    current = current_file.parent
    while current.parent != current:
        if current.name == '.claude':
            claude_root = current
            break
        if (current / '.claude').exists():
            claude_root = current / '.claude'
            break
        current = current.parent
    else:
        # Fallback: assume we're in .claude/project/tests
        claude_root = current_file.parent.parent.parent
    
    # Add system path for imports
    system_path = claude_root / "system"
    if str(system_path) not in sys.path:
        sys.path.insert(0, str(system_path))
    
    # Now we can import core modules
    try:
        from core.path_utils import setup_import_path
        setup_import_path()
    except ImportError:
        # If import fails, just ensure the path is set
        pass
    
    return claude_root

# Automatically setup paths when imported
CLAUDE_ROOT = setup_test_paths()