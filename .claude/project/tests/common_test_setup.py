#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common test setup code for relative imports
This should be copied at the top of each test file
"""

import sys
from pathlib import Path

def setup_relative_imports():
    """Setup relative imports from .claude folder"""
    # Find .claude root using relative path
    current_file = Path(__file__).resolve()
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
    
    # Add system path
    system_path = claude_root / "system"
    if str(system_path) not in sys.path:
        sys.path.insert(0, str(system_path))
    
    return claude_root

# This is the pattern to use in each test file:
"""
# Setup relative imports
import sys
from pathlib import Path

current_file = Path(__file__).resolve()
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
    claude_root = current_file.parent.parent.parent

system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))
"""