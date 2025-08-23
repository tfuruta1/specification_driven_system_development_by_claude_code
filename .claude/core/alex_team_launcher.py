#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Team Launcher
アレックスチーム自動起動システム

キーワード「アレックス」を検出して4エージェントを同時起動
"""

import re
from typing import List, Dict, Any
from pathlib import Path


class AlexTeamLauncher:
    """アレックスチーム起動クラス"""
    
    # アレックスチーム起動トリガーキーワード
    TRIGGER_KEYWORDS = [
        # アレックス関連
        r'アレックス',
        r'alex',
        r'Alex',
        r'ALEX',
        r'アレックスチーム',
        r'alex[\s\-_]?team',
        r'Alex[\s\-_]?Team',
        # プロジェクト関連
        r'プロジェクト',
        r'project',
        r'Project',
        r'PROJECT',
        # 解析関連
        r'解析',
        r'分析',
        r'analyze',
        r'Analyze',
        r'analysis',
        r'Analysis',
        # 作成関連
        r'作成',
        r'実装',
        r'開発',
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
        r'リファクタ',
        r'refactor',
        r'Refactor',
        r'REFACTOR',
        r'最適化',
        r'optimize',
        r'Optimize',
    ]
    
    # 起動する4エージェント
    TEAM_AGENTS = [
        'alex-sdd-tdd-lead',      # SDD+TDDリーダー
        'code-optimizer-engineer', # コード最適化エンジニア
        'qa-doc-engineer',        # QAドキュメントエンジニア
        'tdd-test-engineer'       # TDDテストエンジニア
    ]
    
    def __init__(self):
        """初期化"""
        self.pattern = self._compile_patterns()
        
    def _compile_patterns(self) -> re.Pattern:
        """トリガーパターンをコンパイル"""
        pattern_str = '|'.join(f'({p})' for p in self.TRIGGER_KEYWORDS)
        return re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
        
    def detect_trigger(self, text: str) -> bool:
        """
        テキストからアレックストリガーを検出
        
        Args:
            text: 検査するテキスト
            
        Returns:
            トリガーが見つかった場合True
        """
        return bool(self.pattern.search(text))
        
    def launch_team(self) -> Dict[str, Any]:
        """
        アレックスチーム全体を起動
        
        Returns:
            起動結果
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
        """エージェントの説明を取得"""
        descriptions = {
            'alex-sdd-tdd-lead': 'SDD+TDD開発主任、アーキテクチャ設計とチーム統括',
            'code-optimizer-engineer': 'コード最適化とリファクタリング専門',
            'qa-doc-engineer': '品質保証とドキュメント生成',
            'tdd-test-engineer': 'テスト戦略と100%カバレッジ実現'
        }
        return descriptions.get(agent, '専門エンジニア')
        
    def get_team_status(self) -> Dict[str, Any]:
        """
        チームの状態を取得
        
        Returns:
            チーム状態情報
        """
        return {
            'team_name': 'Alex Team',
            'total_members': len(self.TEAM_AGENTS),
            'members': self.TEAM_AGENTS,
            'trigger_keywords': self.TRIGGER_KEYWORDS[:5],  # 主要キーワードのみ
            'status': 'ready'
        }


# グローバルインスタンス
alex_launcher = AlexTeamLauncher()


def check_and_launch(message: str) -> Dict[str, Any]:
    """
    メッセージをチェックして必要に応じてチームを起動
    
    Args:
        message: ユーザーメッセージ
        
    Returns:
        起動結果（起動した場合）またはNone
    """
    if alex_launcher.detect_trigger(message):
        return alex_launcher.launch_team()
    return None