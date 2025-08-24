"""
TEST - Claude Code Core
IntegrationTestRunnerTEST
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Set, Optional


class CircularImportDetector:
    """"""
    
    def __init__(self):
        """"""
        self.visited_modules: Set[str] = set()
        self.current_path: List[str] = []
        self.circular_imports: List[str] = []
        
    def detect(self, root_path: str = None) -> List[str]:
        """
        
        
        Args:
            root_path: 
            
        Returns:
            
        """
        self._reset()
        
        if root_path is None:
            # 
            root_path = os.getcwd()
            
        # Python
        python_files = self._find_python_files(root_path)
        
        for python_file in python_files:
            module_name = self._get_module_name(python_file, root_path)
            if module_name not in self.visited_modules:
                self._analyze_module(python_file, module_name)
                
        return self.circular_imports
        
    def _reset(self):
        """"""
        self.visited_modules.clear()
        self.current_path.clear()
        self.circular_imports.clear()
        
    def _find_python_files(self, root_path: str) -> List[str]:
        """Python"""
        python_files = []
        root = Path(root_path)
        
        for file_path in root.rglob("*.py"):
            # __pycache__TEST
            if "__pycache__" not in str(file_path) and not str(file_path).endswith("_test.py"):
                python_files.append(str(file_path))
                
        return python_files
        
    def _get_module_name(self, file_path: str, root_path: str) -> str:
        """"""
        relative_path = Path(file_path).relative_to(Path(root_path))
        module_name = str(relative_path.with_suffix('')).replace(os.sep, '.')
        return module_name
        
    def _analyze_module(self, file_path: str, module_name: str) -> List[str]:
        """
        ANALYSIS
        
        Args:
            file_path: 
            module_name: 
            
        Returns:
            
        """
        if self._is_circular(module_name):
            circular_path = self._get_circular_path(module_name)
            self.circular_imports.append(circular_path)
            return [circular_path]
            
        self._enter_module(module_name)
        
        try:
            imports = self._get_module_imports(file_path)
            
            for imported_module in imports:
                if imported_module not in self.visited_modules:
                    # 
                    imported_file = self._find_module_file(imported_module)
                    if imported_file:
                        self._analyze_module(imported_file, imported_module)
                        
        except Exception as e:
            # SUCCESS
            pass
        finally:
            self._exit_module()
            
        return []
        
    def _get_module_imports(self, file_path: str) -> List[str]:
        """"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
        except Exception:
            # ERROR
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # import
                import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+([^#\n]+)'
                matches = re.findall(import_pattern, content, re.MULTILINE)
                
                for from_module, import_items in matches:
                    if from_module:
                        imports.append(from_module)
                        
            except Exception:
                pass
                
        return imports
        
    def _find_module_file(self, module_name: str) -> Optional[str]:
        """"""
        # :  sys.path 
        current_dir = Path.cwd()
        module_path = current_dir / (module_name.replace('.', os.sep) + '.py')
        
        if module_path.exists():
            return str(module_path)
            
        return None
        
    def _enter_module(self, module_name: str):
        """"""
        self.visited_modules.add(module_name)
        self.current_path.append(module_name)
        
    def _exit_module(self):
        """"""
        if self.current_path:
            self.current_path.pop()
            
    def _is_circular(self, module_name: str) -> bool:
        """"""
        return module_name in self.current_path
        
    def _get_circular_path(self, module_name: str) -> str:
        """"""
        if module_name not in self.current_path:
            return ""
            
        start_index = self.current_path.index(module_name)
        circular_path = self.current_path[start_index:] + [module_name]
        return " -> ".join(circular_path)
        
    def get_analysis_summary(self) -> str:
        """REPORT"""
        summary = f"REPORT:\n"
        summary += f"REPORT: {len(self.visited_modules)}\n"
        summary += f"REPORT: {len(self.circular_imports)}\n"
        
        if self.circular_imports:
            summary += "\nREPORT:\n"
            for i, circular in enumerate(self.circular_imports, 1):
                summary += f"  {i}. {circular}\n"
        else:
            summary += "\nREPORT\n"
            
        return summary