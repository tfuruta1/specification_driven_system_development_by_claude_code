#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alex Team Hook Configuration
アレックスチーム自動起動フック設定

ユーザーメッセージに「アレックス」が含まれる場合、
自動的に4つのエージェントを起動します。
"""

import sys
import json
from pathlib import Path

# coreモジュールへのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from alex_team_launcher import check_and_launch


def on_user_message(message: str) -> dict:
    """
    ユーザーメッセージフック
    
    Args:
        message: ユーザーのメッセージ
        
    Returns:
        フック処理結果
    """
    # アレックスキーワードをチェック
    launch_result = check_and_launch(message)
    
    if launch_result:
        # チーム起動を通知
        return {
            'action': 'launch_agents',
            'agents': launch_result['agents'],
            'notification': f"🚀 アレックスチーム起動: {launch_result['total_agents']}名のエンジニアが準備完了",
            'auto_response': generate_team_response(launch_result)
        }
    
    return {'action': 'none'}


def generate_team_response(launch_result: dict) -> str:
    """
    チーム起動時の自動応答を生成
    
    Args:
        launch_result: 起動結果
        
    Returns:
        自動応答メッセージ
    """
    agents = launch_result['agents']
    
    response = "## 🎯 アレックスチーム起動完了\n\n"
    response += "以下の4名のエンジニアが作業準備完了しました：\n\n"
    
    for i, agent in enumerate(agents, 1):
        response += f"{i}. **{agent['name']}**\n"
        response += f"   - {agent['description']}\n"
    
    response += "\n### 利用可能なコマンド:\n"
    response += "- `/auto-mode start` - 開発フロー開始\n"
    response += "- `/auto-mode status` - 現在の状態確認\n"
    response += "- `/auto-mode stop` - セッション終了\n"
    
    return response


# フック設定エクスポート
HOOK_CONFIG = {
    'name': 'alex_team_hook',
    'version': '1.1.0',
    'description': 'アレックスチーム自動起動フック（拡張キーワード対応）',
    'triggers': ['user_message'],
    'keywords': [
        # 主要キーワード
        'アレックス', 'alex', 'Alex', 'アレックスチーム',
        # タスクキーワード
        'プロジェクト', 'project',
        '解析', '分析', 'analyze', 'analysis',
        '作成', '実装', '開発', 'create', 'implement', 'develop',
        '修正', 'バグ', 'fix', 'bug',
        'リファクタリング', 'リファクタ', 'refactor', '最適化', 'optimize'
    ],
    'agents': [
        'alex-sdd-tdd-lead',
        'code-optimizer-engineer',
        'qa-doc-engineer',
        'tdd-test-engineer'
    ]
}