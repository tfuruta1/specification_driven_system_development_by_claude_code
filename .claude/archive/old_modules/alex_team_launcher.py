#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Team Launcher


4
"""

import re
from typing import List, Dict, Any
from pathlib import Path

# REFACTOR Phase: Integration with SelfRefactoringSystem
try:
    from .self_refactoring_system import SelfRefactoringSystem
except ImportError:
    try:
        from self_refactoring_system import SelfRefactoringSystem
    except ImportError:
        # Fallback - system will work without self-refactoring
        SelfRefactoringSystem = None


class AlexTeamLauncher:
    """SYSTEM"""
    
    # トリガーキーワード定義
    TRIGGER_KEYWORDS = [
        # アレックスチーム関連
        r'アレックスチーム',
        r'alex',
        r'Alex',
        r'ALEX',
        r'アレックス',
        r'alex[\s\-_]?team',
        r'Alex[\s\-_]?Team',
        # 自己診断関連（追加）
        r'自己診断',
        r'self[\s\-_]?diagnosis',
        r'Self[\s\-_]?Diagnosis',
        r'SELF[\s\-_]?DIAGNOSIS',
        r'診断',
        r'diagnosis',
        r'Diagnosis',
        # プロジェクト関連
        r'プロジェクト',
        r'project',
        r'Project',
        r'PROJECT',
        # 分析関連
        r'分析',
        r'解析',
        r'analyze',
        r'Analyze',
        r'analysis',
        r'Analysis',
        # 作成関連
        r'作成',
        r'新規',
        r'実装',
        r'create',
        r'Create',
        r'implement',
        r'Implement',
        r'develop',
        r'Develop',
        # 修正関連
        r'修正',
        r'バグ',
        r'fix',
        r'Fix',
        r'bug',
        r'Bug',
        r'repair',
        r'Repair',
        # リファクタリング関連
        r'リファクタリング',
        r'最適化',
        r'refactor',
        r'Refactor',
        r'REFACTOR',
        r'改善',
        r'optimize',
        r'Optimize',
    ]
    
    # 4
    TEAM_AGENTS = [
        'alex-sdd-tdd-lead',      # SDD+TDD
        'code-optimizer-engineer', # TEST
        'qa-doc-engineer',        # QATEST
        'tdd-test-engineer'       # TDDTEST
    ]
    
    def __init__(self):
        """TEST"""
        self.pattern = self._compile_patterns()
        
        # REFACTOR Phase: Initialize self-refactoring system
        self.self_refactoring = None
        if SelfRefactoringSystem:
            try:
                self.self_refactoring = SelfRefactoringSystem()
            except Exception as e:
                print(f"Warning: Self-refactoring system initialization failed: {e}")
                self.self_refactoring = None
        
    def _compile_patterns(self) -> re.Pattern:
        """"""
        pattern_str = '|'.join(f'({p})' for p in self.TRIGGER_KEYWORDS)
        return re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
        
    def detect_trigger(self, text: str) -> bool:
        """
        
        
        Args:
            text: 
            
        Returns:
            True
        """
        return bool(self.pattern.search(text))
        
    def launch_team(self) -> Dict[str, Any]:
        """
        REPORT
        
        Returns:
            REPORT
        """
        results = {
            'status': 'launching',
            'agents': []
        }
        
        for agent in self.TEAM_AGENTS:
            agent_info = {
                'name': agent,
                'status': 'ready',
                'description': self._get_agent_description(agent)
            }
            results['agents'].append(agent_info)
            
        results['status'] = 'launched'
        results['total_agents'] = len(self.TEAM_AGENTS)
        
        return results
        
    def _get_agent_description(self, agent: str) -> str:
        """REPORT"""
        descriptions = {
            'alex-sdd-tdd-lead': 'SDD+TDD',
            'code-optimizer-engineer': 'TEST',
            'qa-doc-engineer': 'TEST',
            'tdd-test-engineer': 'TEST100%TEST'
        }
        return descriptions.get(agent, 'TEST')
        
    def get_team_status(self) -> Dict[str, Any]:
        """
        
        
        Returns:
            
        """
        return {
            'team_name': 'Alex Team',
            'total_members': len(self.TEAM_AGENTS),
            'members': self.TEAM_AGENTS,
            'trigger_keywords': self.TRIGGER_KEYWORDS[:5],  # 
            'status': 'ready',
            'self_refactoring_enabled': self.self_refactoring is not None
        }
    
    # REFACTOR Phase: Self-refactoring capabilities
    
    def check_self_modification(self, file_path: str) -> bool:
        """
        Check if a file modification involves .claude directory
        
        Args:
            file_path: Path to check for self-modification
            
        Returns:
            True if this is a self-modification, False otherwise
        """
        if not self.self_refactoring:
            return False
        
        return self.self_refactoring.is_self_modification(file_path)
    
    def enforce_formal_flow(self, modification_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce formal SDD+TDD flow for self-modifications
        
        Args:
            modification_request: Details about the requested modification
            
        Returns:
            Result of formal flow enforcement
        """
        if not self.self_refactoring:
            return {'status': 'no_self_refactoring', 'proceed': True}
        
        file_path = modification_request.get('file_path', '')
        
        if self.check_self_modification(file_path):
            # Block direct modification, require formal flow
            return {
                'status': 'blocked',
                'reason': 'Self-modification detected',
                'required_action': 'formal_flow',
                'proceed': False,
                'message': 'Use formal SDD+TDD flow for .claude directory modifications'
            }
        
        return {'status': 'allowed', 'proceed': True}
    
    def launch_self_refactoring(self, change_description: str) -> Dict[str, Any]:
        """
        Launch self-refactoring process with formal SDD+TDD flow
        
        Args:
            change_description: Description of the desired changes
            
        Returns:
            Result of self-refactoring process launch
        """
        if not self.self_refactoring:
            return {
                'status': 'unavailable',
                'message': 'Self-refactoring system not available'
            }
        
        try:
            # Step 1: Start self-modification
            start_result = self.self_refactoring.start_self_modification(change_description)
            
            if not start_result.get('started', False):
                return {
                    'status': 'failed_to_start',
                    'message': 'Could not initiate self-modification'
                }
            
            # Step 2: Launch Alex Team for formal process
            team_result = self.launch_team()
            
            # Step 3: Integrate results
            return {
                'status': 'launched',
                'self_refactoring_started': True,
                'alex_team_activated': True,
                'formal_flow_initiated': True,
                'change_description': change_description,
                'team_info': team_result,
                'process_state': start_result.get('state', {})
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Self-refactoring launch failed: {str(e)}'
            }
    
    def launch_self_diagnosis(self) -> Dict[str, Any]:
        """
        自己診断モード: .claudeディレクトリ全体を解析
        
        Returns:
            診断結果レポート
        """
        from pathlib import Path
        import json
        
        claude_root = self.self_refactoring.claude_root if self.self_refactoring else Path('.claude')
        
        diagnosis_result = {
            'status': 'diagnosing',
            'claude_root': str(claude_root),
            'analysis': {},
            'issues': [],
            'recommendations': []
        }
        
        try:
            # .claudeディレクトリの構造解析
            if claude_root.exists():
                # ファイル数とサイズの統計
                py_files = list(claude_root.rglob('*.py'))
                md_files = list(claude_root.rglob('*.md'))
                json_files = list(claude_root.rglob('*.json'))
                
                diagnosis_result['analysis'] = {
                    'total_python_files': len(py_files),
                    'total_markdown_files': len(md_files),
                    'total_json_files': len(json_files),
                    'core_modules': len([f for f in py_files if 'core' in str(f.parent)]),
                    'test_files': len([f for f in py_files if 'test' in f.name]),
                    'agent_definitions': len([f for f in md_files if 'agents' in str(f.parent)])
                }
                
                # 問題検出
                # 1. 絵文字プレースホルダーのチェック
                emoji_issues = []
                import re
                emoji_pattern = re.compile(r'\[EMOJI_[A-Z_]+\]')
                for py_file in py_files:
                    try:
                        content = py_file.read_text(encoding='utf-8')
                        if emoji_pattern.search(content):
                            emoji_issues.append(str(py_file.relative_to(claude_root)))
                    except Exception:
                        pass
                
                if emoji_issues:
                    diagnosis_result['issues'].append({
                        'type': 'emoji_placeholders',
                        'severity': 'medium',
                        'files': emoji_issues,
                        'description': '絵文字プレースホルダーが残っています'
                    })
                
                # 2. 重複ファイルの検出
                file_names = {}
                for py_file in py_files:
                    name = py_file.name
                    if name in file_names:
                        file_names[name].append(str(py_file.relative_to(claude_root)))
                    else:
                        file_names[name] = [str(py_file.relative_to(claude_root))]
                
                duplicates = {k: v for k, v in file_names.items() if len(v) > 1}
                if duplicates:
                    diagnosis_result['issues'].append({
                        'type': 'duplicate_files',
                        'severity': 'high',
                        'files': duplicates,
                        'description': '重複ファイルが検出されました'
                    })
                
                # 3. 循環依存のチェック
                if self.self_refactoring:
                    circular_deps = []
                    for py_file in py_files:
                        if self.self_refactoring._has_circular_imports(py_file):
                            circular_deps.append(str(py_file.relative_to(claude_root)))
                    
                    if circular_deps:
                        diagnosis_result['issues'].append({
                            'type': 'circular_dependencies',
                            'severity': 'critical',
                            'files': circular_deps,
                            'description': '循環依存が検出されました'
                        })
                
                # 推奨事項の生成
                if diagnosis_result['issues']:
                    diagnosis_result['recommendations'].append(
                        'アレックスチームによる自己修正プロセスの実行を推奨します'
                    )
                    diagnosis_result['recommendations'].append(
                        'SDD+TDD方式でのリファクタリングが必要です'
                    )
                else:
                    diagnosis_result['recommendations'].append(
                        '.claudeディレクトリは健全な状態です'
                    )
                
                diagnosis_result['status'] = 'completed'
                
            else:
                diagnosis_result['status'] = 'error'
                diagnosis_result['issues'].append({
                    'type': 'directory_not_found',
                    'severity': 'critical',
                    'description': '.claudeディレクトリが見つかりません'
                })
                
        except Exception as e:
            diagnosis_result['status'] = 'error'
            diagnosis_result['error'] = str(e)
        
        # アレックスチームを起動して診断結果を処理
        if diagnosis_result['issues']:
            team_result = self.launch_team()
            diagnosis_result['alex_team_activated'] = True
            diagnosis_result['team_info'] = team_result
        
        return diagnosis_result


# REPORT
alex_launcher = AlexTeamLauncher()


def check_and_launch(message: str, file_path: str = None) -> Dict[str, Any]:
    """
    Enhanced trigger system with self-refactoring detection
    
    Args:
        message: User message to analyze for triggers
        file_path: Optional file path being modified (for self-refactoring detection)
        
    Returns:
        Launch result or None if no trigger detected
    """
    # 自己診断キーワードのチェック
    if any(keyword in message for keyword in ['自己診断', 'self-diagnosis', 'self diagnosis']):
        return alex_launcher.launch_self_diagnosis()
    
    # Check for self-modification first
    if file_path and alex_launcher.check_self_modification(file_path):
        return alex_launcher.launch_self_refactoring(
            f"Self-modification detected for: {file_path}\nContext: {message}"
        )
    
    # Standard trigger detection
    if alex_launcher.detect_trigger(message):
        return alex_launcher.launch_team()
    
    return None


# REFACTOR Phase: Additional utility functions

def enforce_self_modification_flow(modification_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Utility function to enforce formal flow for self-modifications
    
    Args:
        modification_request: Contains file_path and other modification details
        
    Returns:
        Flow enforcement result
    """
    return alex_launcher.enforce_formal_flow(modification_request)


def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive status of Alex Team and Self-Refactoring systems
    
    Returns:
        System status information
    """
    team_status = alex_launcher.get_team_status()
    
    if alex_launcher.self_refactoring:
        try:
            # Check if self-refactoring is currently active
            state_file = alex_launcher.self_refactoring.state_file
            active_modification = None
            
            if state_file.exists():
                import json
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                        if state.get('in_progress'):
                            active_modification = state
                except Exception:
                    pass
            
            team_status['self_refactoring_status'] = {
                'available': True,
                'active_modification': active_modification,
                'claude_root': str(alex_launcher.self_refactoring.claude_root)
            }
        except Exception as e:
            team_status['self_refactoring_status'] = {
                'available': False,
                'error': str(e)
            }
    else:
        team_status['self_refactoring_status'] = {
            'available': False,
            'reason': 'SelfRefactoringSystem not initialized'
        }
    
    return team_status