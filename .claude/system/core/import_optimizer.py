#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Structure Optimizer

"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque


class ImportAnalyzer:
    """ANALYSIS"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.modules = {}
        self.dependencies = defaultdict(set)
        
    def analyze_file(self, file_path: Path) -> Dict[str, Set[str]]:
        """ANALYSIS"""
        if not file_path.exists() or file_path.suffix != '.py':
            return {}
            
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return {}
        
        imports = {
            'absolute': set(),
            'relative': set(),
            'standard': set()
        }
        
        # 
        patterns = {
            'from_relative': r'^from\s+\.([\w\.]+)\s+import',
            'from_absolute': r'^from\s+([\w\.]+)\s+import',
            'import_absolute': r'^import\s+([\w\.]+)',
        }
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 
            match = re.match(patterns['from_relative'], line)
            if match:
                imports['relative'].add(match.group(1))
                continue
                
            #  (from)
            match = re.match(patterns['from_absolute'], line)
            if match:
                module = match.group(1)
                if module.startswith('.'):
                    imports['relative'].add(module[1:])
                elif '.' not in module or module in ['os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing', 'collections', 'tempfile', 'shutil', 'unittest', 'uuid', 're']:
                    imports['standard'].add(module)
                else:
                    imports['absolute'].add(module)
                continue
                
            #  (import)
            match = re.match(patterns['import_absolute'], line)
            if match:
                module = match.group(1)
                if '.' not in module or module in ['os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing', 'collections', 'tempfile', 'shutil', 'unittest', 'uuid', 're']:
                    imports['standard'].add(module)
                else:
                    imports['absolute'].add(module)
        
        return imports
    
    def analyze_directory(self) -> None:
        """ANALYSIS"""
        for py_file in self.base_path.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
                
            module_name = py_file.stem
            imports = self.analyze_file(py_file)
            self.modules[module_name] = imports
            
            # ANALYSIS
            for relative_import in imports['relative']:
                self.dependencies[module_name].add(relative_import)
    
    def detect_circular_imports(self) -> List[List[str]]:
        """"""
        def dfs(node: str, path: List[str], visited: Set[str]) -> List[List[str]]:
            if node in path:
                # 
                cycle_start = path.index(node)
                return [path[cycle_start:] + [node]]
            
            if node in visited:
                return []
            
            visited.add(node)
            cycles = []
            
            for dependency in self.dependencies.get(node, []):
                cycles.extend(dfs(dependency, path + [node], visited))
            
            return cycles
        
        all_cycles = []
        visited = set()
        
        for module in self.modules.keys():
            if module not in visited:
                cycles = dfs(module, [], set())
                all_cycles.extend(cycles)
                visited.add(module)
        
        return all_cycles
    
    def get_dependency_layers(self) -> Dict[int, List[str]]:
        """"""
        # 
        in_degree = defaultdict(int)
        
        for module in self.modules.keys():
            for dependency in self.dependencies.get(module, []):
                in_degree[dependency] += 1
        
        # 0
        layers = defaultdict(list)
        queue = deque()
        
        for module in self.modules.keys():
            if in_degree[module] == 0:
                layers[0].append(module)
                queue.append((module, 0))
        
        while queue:
            current_module, layer = queue.popleft()
            
            for dependency in self.dependencies.get(current_module, []):
                in_degree[dependency] -= 1
                if in_degree[dependency] == 0:
                    layers[layer + 1].append(dependency)
                    queue.append((dependency, layer + 1))
        
        return dict(layers)
    
    def generate_report(self) -> str:
        """REPORT"""
        report_lines = [
            "=== Import Structure Analysis Report ===",
            f"REPORT: {self.base_path}",
            f"REPORT: {len(self.modules)}",
            ""
        ]
        
        # 
        circular_imports = self.detect_circular_imports()
        if circular_imports:
            report_lines.extend([
                "REPORT REPORT:",
                ""
            ])
            for i, cycle in enumerate(circular_imports, 1):
                report_lines.append(f"REPORT {i}: {' -> '.join(cycle)}")
            report_lines.append("")
        else:
            report_lines.extend([
                "[CHECK] REPORT",
                ""
            ])
        
        # REPORT
        layers = self.get_dependency_layers()
        report_lines.extend([
            "REPORT:",
            ""
        ])
        
        for layer_num in sorted(layers.keys()):
            modules = layers[layer_num]
            report_lines.append(f"Layer {layer_num}: {', '.join(modules)}")
        
        report_lines.append("")
        
        # REPORT
        report_lines.extend([
            "REPORT:",
            ""
        ])
        
        for module_name, imports in self.modules.items():
            report_lines.append(f"{module_name}:")
            if imports['standard']:
                report_lines.append(f"  REPORT: {', '.join(sorted(imports['standard']))}")
            if imports['relative']:
                report_lines.append(f"  REPORT: {', '.join(sorted(imports['relative']))}")
            if imports['absolute']:
                report_lines.append(f"  REPORT: {', '.join(sorted(imports['absolute']))}")
            report_lines.append("")
        
        return '\n'.join(report_lines)


def main():
    """SYSTEM"""
    base_path = Path('.claude/core')
    
    if not base_path.exists():
        print(f"SYSTEM: {base_path} SYSTEM")
        return
    
    print("=== Import Structure Optimization ===")
    print(f"ANALYSIS: {base_path.absolute()}")
    print("")
    
    # ANALYSIS
    analyzer = ImportAnalyzer(base_path)
    analyzer.analyze_directory()
    
    # REPORT
    report = analyzer.generate_report()
    print(report)
    
    # REPORT
    report_file = base_path / 'import_analysis_report.txt'
    try:
        report_file.write_text(report, encoding='utf-8')
        print(f"ERROR: {report_file}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # ERROR
    circular_imports = analyzer.detect_circular_imports()
    if circular_imports:
        print("\nANALYSIS ANALYSIS: ANALYSIS")
        return False
    else:
        print("\n[CHECK] SUCCESS")
        return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)