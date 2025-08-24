"""
Claude Code SDD+TDD Core Module - REFACTOR Phase
Minimal imports for stable operation
"""

# Core System ERROR
try:
    from .unified_system import UnifiedSystem
except ImportError:
    UnifiedSystem = None

# Auto ModeERROR - Using unified auto_mode module  
try:
    from .auto_mode import AutoMode
except ImportError:
    AutoMode = None

# Essential modules only - others will be added incrementally
try:
    from .logger import Logger
except ImportError:
    Logger = None
    
try:
    from .config import ConfigManager
except ImportError:
    ConfigManager = None

__all__ = [
    # Core System
    'UnifiedSystem',
    
    # Auto Mode - unified
    'AutoMode',
    
    # Essential utilities
    'Logger',
    'ConfigManager',
]

# Version info
__version__ = '12.1.0-refactor'
__author__ = 'Alex Team'