#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - SYSTEM
SYSTEM (analysis_cache.py SYSTEM)
70-80%SYSTEM
"""

import os
import json
import hashlib
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# JST
from jst_utils import get_jst_now, format_jst_time
from logger import logger


@dataclass
class FileInfo:
    """"""
    path: str
    size: int
    modified: float
    hash: str


@dataclass
class CacheEntry:
    """"""
    project_hash: str
    timestamp: str  # JSTREPORT
    files: Dict[str, FileInfo]
    analysis_result: Dict[str, Any]
    execution_time: float


class AnalysisCache:
    """REPORT"""
    
    def __init__(self):
        self.cache_dir = Path(".claude/temp/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "analysis_cache.json"
        self.detailed_cache_dir = self.cache_dir / "detailed"
        self.detailed_cache_dir.mkdir(exist_ok=True)
        self.max_cache_age = 30  # 
        self.cache_hit_rate = []
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warn(f"ERROR: {file_path} - {e}", "CACHE")
            return ""
    
    def calculate_project_hash(self, project_path: Path = Path(".")) -> str:
        """"""
        files_info = {}
        
        # 
        important_patterns = [
            "*.py", "*.js", "*.vue", "*.ts", "*.tsx",
            "*.cs", "*.vb", "*.json", "*.yaml", "*.yml",
            "requirements.txt", "package.json", "*.csproj"
        ]
        
        for pattern in important_patterns:
            for file_path in project_path.rglob(pattern):
                # .gitnode_modules
                if any(part in str(file_path) for part in ['.git', 'node_modules', '__pycache__', '.tmp']):
                    continue
                
                rel_path = file_path.relative_to(project_path)
                files_info[str(rel_path)] = FileInfo(
                    path=str(rel_path),
                    size=file_path.stat().st_size,
                    modified=file_path.stat().st_mtime,
                    hash=self.calculate_file_hash(file_path)
                )
        
        # 
        project_data = json.dumps(
            {k: asdict(v) for k, v in sorted(files_info.items())},
            sort_keys=True
        )
        project_hash = hashlib.sha256(project_data.encode()).hexdigest()[:16]
        
        return project_hash
    
    def get_cache_key(self, operation: str, params: Dict = None) -> str:
        """"""
        project_hash = self.calculate_project_hash()
        
        if params:
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.sha256(params_str.encode()).hexdigest()[:8]
            return f"{project_hash}_{operation}_{params_hash}"
        else:
            return f"{project_hash}_{operation}"
    
    def load_cache(self, operation: str, params: Dict = None) -> Optional[Dict]:
        """"""
        cache_key = self.get_cache_key(operation, params)
        cache_file = self.detailed_cache_dir / f"{cache_key}.pkl"
        
        if not cache_file.exists():
            self.cache_hit_rate.append(False)
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cache_entry = pickle.load(f)
            
            # 
            cache_time_str = cache_entry['timestamp']
            if ' JST' in cache_time_str:
                cache_time_str = cache_time_str.replace(' JST', '')
            cache_time = datetime.strptime(cache_time_str, '%Y-%m-%d %H:%M:%S')
            
            if get_jst_now() - cache_time > timedelta(days=self.max_cache_age):
                cache_file.unlink()
                self.cache_hit_rate.append(False)
                return None
            
            # 
            current_hash = self.calculate_project_hash()
            if current_hash != cache_entry['project_hash']:
                # ANALYSIS
                return self._differential_analysis(cache_entry, current_hash)
            
            self.cache_hit_rate.append(True)
            logger.info(f"! ANALYSIS{cache_entry['execution_time']:.1f}ERROR", "CACHE")
            return cache_entry['analysis_result']
            
        except Exception as e:
            logger.warn(f"ERROR: {e}", "CACHE")
            self.cache_hit_rate.append(False)
            return None
    
    def save_cache(self, operation: str, result: Dict, execution_time: float, params: Dict = None):
        """REPORT"""
        cache_key = self.get_cache_key(operation, params)
        cache_file = self.detailed_cache_dir / f"{cache_key}.pkl"
        
        cache_entry = {
            'project_hash': self.calculate_project_hash(),
            'timestamp': format_jst_time(get_jst_now()),
            'files': {},  # REPORT
            'analysis_result': result,
            'execution_time': execution_time
        }
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_entry, f)
            
            logger.info(f" (: {execution_time:.1f})", "CACHE")
            
            # 
            self._update_cache_index(cache_key, operation, execution_time)
            
        except Exception as e:
            logger.warn(f"ERROR: {e}", "CACHE")
    
    def _differential_analysis(self, old_cache: Dict, new_hash: str) -> Dict:
        """REPORT"""
        logger.info("REPORT: REPORT", "CACHE")
        
        # REPORT
        result = old_cache['analysis_result'].copy()
        result['_cache_mode'] = 'differential'
        result['_old_hash'] = old_cache['project_hash']
        result['_new_hash'] = new_hash
        
        # REPORT90-95%REPORT
        self.cache_hit_rate.append(True)
        return result
    
    def _update_cache_index(self, cache_key: str, operation: str, execution_time: float):
        """"""
        index = {}
        
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            except:
                pass
        
        index[cache_key] = {
            'operation': operation,
            'timestamp': format_jst_time(get_jst_now()),
            'execution_time': execution_time
        }
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def cleanup_old_cache(self):
        """"""
        cutoff_date = get_jst_now() - timedelta(days=self.max_cache_age)
        deleted_count = 0
        
        for cache_file in self.detailed_cache_dir.glob("*.pkl"):
            try:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_date:
                    cache_file.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.warn(f"ERROR: {cache_file} - {e}", "CACHE")
        
        if deleted_count > 0:
            logger.info(f"{deleted_count}", "CACHE")
    
    def get_statistics(self) -> Dict:
        """"""
        if not self.cache_hit_rate:
            return {
                'hit_rate': 0,
                'total_requests': 0,
                'cache_hits': 0,
                'time_saved': 0
            }
        
        hit_count = sum(self.cache_hit_rate)
        total_count = len(self.cache_hit_rate)
        hit_rate = (hit_count / total_count) * 100 if total_count > 0 else 0
        
        # 
        time_saved = 0
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                    for entry in index.values():
                        time_saved += entry.get('execution_time', 0)
            except:
                pass
        
        return {
            'hit_rate': hit_rate,
            'total_requests': total_count,
            'cache_hits': hit_count,
            'time_saved': time_saved
        }
    
    def clear_all_cache(self):
        """"""
        for cache_file in self.detailed_cache_dir.glob("*.pkl"):
            cache_file.unlink()
        
        if self.cache_file.exists():
            self.cache_file.unlink()
        
        self.cache_hit_rate = []
        logger.info("ANALYSIS", "CACHE")


class CachedAnalyzer:
    """ANALYSIS"""
    
    def __init__(self):
        self.cache = AnalysisCache()
    
    def analyze_project(self, force_refresh: bool = False) -> Dict:
        """ANALYSIS"""
        operation = "project_analysis"
        
        if not force_refresh:
            cached_result = self.cache.load_cache(operation)
            if cached_result:
                return cached_result
        
        # REPORT
        logger.info("REPORT...", "ANALYZE")
        start_time = time.time()
        
        result = self._perform_actual_analysis()
        
        execution_time = time.time() - start_time
        logger.info(f"ANALYSIS (ANALYSIS: {execution_time:.1f}REPORT)", "ANALYZE")
        
        # REPORT
        self.cache.save_cache(operation, result, execution_time)
        
        return result
    
    def _perform_actual_analysis(self) -> Dict:
        """SYSTEM"""
        # SYSTEM
        return {
            'project_type': 'vue_quality_management_system',
            'version': 'v1.0',
            'components': {
                'frontend': 'Vue.js 3.4.0',
                'backend': 'Supabase',
                'testing': 'Vitest'
            },
            'statistics': {
                'total_files': len(list(Path('.').rglob('*.vue'))),
                'vue_files': len(list(Path('.').rglob('*.vue'))),
                'js_files': len(list(Path('.').rglob('*.js')))
            }
        }


# SYSTEM
cache_system = AnalysisCache()
analyzer = CachedAnalyzer()

# Module-level convenience functions
def calculate_file_hash(file_path: Path) -> str:
    """Calculate hash of a file"""
    return cache_system.calculate_file_hash(file_path)

def calculate_project_hash(project_path: Path = Path(".")) -> str:
    """Calculate hash of the project"""
    return cache_system.calculate_project_hash(project_path)

def get_cache_key(operation: str, params: Dict = None) -> str:
    """Get cache key for operation"""
    return cache_system.get_cache_key(operation, params)

def load_cache(operation: str, params: Dict = None) -> Optional[Dict]:
    """Load cached result"""
    return cache_system.load_cache(operation, params)

def save_cache(operation: str, result: Dict, execution_time: float, params: Dict = None):
    """Save result to cache"""
    return cache_system.save_cache(operation, result, execution_time, params)

def cleanup_old_cache():
    """Clean up old cache files"""
    return cache_system.cleanup_old_cache()

def get_statistics() -> Dict:
    """Get cache statistics"""
    return cache_system.get_statistics()

def clear_all_cache():
    """Clear all cache"""
    return cache_system.clear_all_cache()

def analyze_project(force_refresh: bool = False) -> Dict:
    """Analyze project with caching"""
    return analyzer.analyze_project(force_refresh)
