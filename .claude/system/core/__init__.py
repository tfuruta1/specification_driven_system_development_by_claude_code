"""
Claude Code SDD+TDD Core Module v14.0
Complete module exports for proper relative imports
"""

# Core System modules
try:
    from .unified_system import UnifiedSystem
except ImportError:
    UnifiedSystem = None

# Auto Mode module  
try:
    from .auto_mode import AutoMode
except ImportError:
    AutoMode = None

# Essential utilities
try:
    from .logger import Logger
except ImportError:
    Logger = None
    
try:
    from .config import ConfigManager
except ImportError:
    ConfigManager = None

# Development Rules modules - required for relative imports
try:
    from .dev_rules_core import dev_rules_core, RuleType, TDDPhase
except ImportError:
    dev_rules_core = None
    RuleType = None
    TDDPhase = None

try:
    from .dev_rules_checklist import checklist_manager
except ImportError:
    checklist_manager = None

try:
    from .dev_rules_tdd import tdd_manager
except ImportError:
    tdd_manager = None

try:
    from .dev_rules_tasks import task_manager
except ImportError:
    task_manager = None

try:
    from .dev_rules_integration import integration_manager
except ImportError:
    integration_manager = None

try:
    from .development_rules import DevelopmentRulesEngine
except ImportError:
    DevelopmentRulesEngine = None

# Alex Team modules
try:
    from .alex_team_core import AlexTeamCore
except ImportError:
    AlexTeamCore = None

# Service and Error handling
try:
    from .service_factory import ServiceFactory
except ImportError:
    ServiceFactory = None

try:
    from .error_handler import ErrorHandler
except ImportError:
    ErrorHandler = None

__all__ = [
    # Core System
    'UnifiedSystem',
    
    # Auto Mode
    'AutoMode',
    
    # Essential utilities
    'Logger',
    'ConfigManager',
    
    # Development Rules
    'DevelopmentRulesEngine',
    'dev_rules_core',
    'RuleType',
    'TDDPhase',
    'checklist_manager',
    'tdd_manager',
    'task_manager',
    'integration_manager',
    
    # Alex Team
    'AlexTeamCore',
    
    # Services
    'ServiceFactory',
    'ErrorHandler',
]

# Version info
__version__ = '14.0.0'
__author__ = 'Alex Team'