#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Core - トリガーキーワード検出システム
CTOのトリガーワード見逃しを防ぐ自動ペアプログラミング起動システム
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

from activity_logger import logger, ActivityType


# トリガーキーワード定数
TRIGGER_KEYWORDS = ["解析", "修正", "実装", "開発", "テスト", "リファクタ", "デバッグ"]


@dataclass
class TriggerEvent:
    """トリガーイベント情報"""
    triggered: bool
    detected_keywords: List[str]
    message: str
    timestamp: datetime
    feature_name: Optional[str] = None


@dataclass 
class ActivationResult:
    """ペアプログラミング起動結果"""
    success: bool
    response_message: str
    todo_list: Optional[List[Dict]] = None
    error_message: Optional[str] = None


class TriggerKeywordDetector:
    """トリガーキーワード検出器"""
    
    def __init__(self):
        self.keywords = TRIGGER_KEYWORDS
        self.enabled = True
        
    def scan_message(self, message: str) -> TriggerEvent:
        """
        メッセージをスキャンしてトリガーキーワードを検出
        
        Args:
            message: スキャン対象のメッセージ
            
        Returns:
            TriggerEvent: 検出結果
        """
        if message is None:
            logger.error("scan_message: メッセージがNullです", "TRIGGER")
            raise ValueError("メッセージがNullです")
            
        if not self.enabled:
            return TriggerEvent(
                triggered=False,
                detected_keywords=[],
                message=message,
                timestamp=datetime.now()
            )
        
        detected_keywords = []
        
        # 各キーワードをメッセージ内で検索
        for keyword in self.keywords:
            if keyword in message:
                detected_keywords.append(keyword)
        
        # 機能名を抽出
        feature_name = self._extract_feature_name(message) if detected_keywords else None
        
        return TriggerEvent(
            triggered=len(detected_keywords) > 0,
            detected_keywords=detected_keywords,
            message=message,
            timestamp=datetime.now(),
            feature_name=feature_name
        )
    
    def _extract_feature_name(self, message: str) -> str:
        """メッセージから機能名を抽出"""
        # 簡単なパターンマッチングで機能名を抽出
        patterns = [
            r'([^、。！？]*?)(?:機能|システム|モジュール).*?(?:' + '|'.join(self.keywords) + ')',
            r'([^、。！？]*?)(?:の|を).*?(?:' + '|'.join(self.keywords) + ')',
            r'(?:' + '|'.join(self.keywords) + ').*?([^、。！？]*?)(?:機能|システム|モジュール)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                feature = match.group(1).strip()
                if feature and len(feature) > 0:
                    return feature
        
        return "指定機能"


class AutoPairProgrammingActivator:
    """自動ペアプログラミング起動器"""
    
    def __init__(self):
        self.core_dir = Path(".claude/core")
        
    def activate_pair_programming(self, keywords: List[str], message: str) -> ActivationResult:
        """
        ペアプログラミングモードを自動起動
        
        Args:
            keywords: 検出されたキーワードリスト
            message: 元のメッセージ
            
        Returns:
            ActivationResult: 起動結果
        """
        try:
            # 1. 機能名を抽出
            feature_name = self._extract_feature_from_message(message)
            
            # 2. Todoリストを作成
            todo_list = self._create_todo_from_keywords(keywords, message)
            
            # 3. CTOのアクション記録
            logger.log_cto(
                f"トリガーワード検出 [{', '.join(keywords)}] - 自動ペアプログラミング起動",
                f"'{feature_name}'について検出。アレックスと連携開始。"
            )
            
            # 4. アレックスの応答記録
            logger.log_alex(
                f"自動起動による{feature_name}の{', '.join(keywords)}作業開始",
                "TDDワークフローに従い、テストファーストで進行します！"
            )
            
            # 5. アクティビティログ記録
            logger.log_activity(
                "Alex", "[AI]", 
                ActivityType.PLANNING,
                f"トリガー検出によるペアプロ自動起動: {feature_name}"
            )
            
            # 6. 成功応答を生成
            response_message = self._generate_response_message(feature_name, keywords)
            
            return ActivationResult(
                success=True,
                response_message=response_message,
                todo_list=todo_list
            )
            
        except Exception as e:
            logger.error(f"ペアプログラミング起動エラー: {e}", "TRIGGER")
            return ActivationResult(
                success=False,
                response_message="ペアプログラミング起動に失敗しました",
                error_message=str(e)
            )
    
    def _extract_feature_from_message(self, message: str) -> str:
        """メッセージから機能名を抽出（詳細版）"""
        # 特定のキーワードから推測（完全一致を優先）
        if "ユーザー認証機能" in message:
            return "ユーザー認証機能"
        elif "データベース接続" in message:
            return "データベース接続" 
        elif "解析システム" in message:
            return "解析システム"
        elif "ログイン機能" in message:
            return "ログイン機能"
        
        # より詳細なパターンマッチング
        patterns = [
            r'([^、。！？]*?)(?:機能|システム|モジュール|アプリ|画面|ページ).*?(?:' + '|'.join(TRIGGER_KEYWORDS) + ')',
            r'([^、。！？]*?)(?:の|を|に関して|について).*?(?:' + '|'.join(TRIGGER_KEYWORDS) + ')',
            r'(?:' + '|'.join(TRIGGER_KEYWORDS) + ').*?([^、。！？]*?)(?:機能|システム|モジュール)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                feature = match.group(1).strip()
                if feature and len(feature.replace(' ', '')) > 0:
                    return feature + "機能"  # 機能を付加
        
        # 部分一致による推測
        if "認証" in message:
            return "ユーザー認証機能"
        elif "データベース" in message:
            return "データベース接続"
        elif "ログイン" in message:
            return "ログイン機能"
        elif "API" in message:
            return "API機能"
        
        return "指定機能"
    
    def _create_todo_from_keywords(self, keywords: List[str], message: str) -> List[Dict]:
        """キーワードからTodoリストを生成"""
        feature_name = self._extract_feature_from_message(message)
        todos = []
        
        # TDD原則に基づくタスク構成
        if "実装" in keywords or "開発" in keywords:
            todos.extend([
                {
                    "content": f"{feature_name}のテスト作成（TDD Red Phase）",
                    "status": "in_progress"
                },
                {
                    "content": f"{feature_name}の最小実装（TDD Green Phase）", 
                    "status": "pending"
                },
                {
                    "content": f"{feature_name}のリファクタリング（TDD Refactor Phase）",
                    "status": "pending"
                }
            ])
        
        if "テスト" in keywords:
            todos.append({
                "content": f"{feature_name}の包括的テストケース作成",
                "status": "pending" if todos else "in_progress"
            })
        
        if "解析" in keywords:
            todos.append({
                "content": f"{feature_name}の要件解析とコード調査",
                "status": "pending" if todos else "in_progress"
            })
        
        if "修正" in keywords:
            todos.extend([
                {
                    "content": f"{feature_name}の問題特定と原因分析",
                    "status": "pending" if todos else "in_progress"
                },
                {
                    "content": f"{feature_name}の修正実装",
                    "status": "pending"
                }
            ])
        
        if "デバッグ" in keywords:
            todos.extend([
                {
                    "content": f"{feature_name}のデバッグ作業開始",
                    "status": "pending" if todos else "in_progress"
                },
                {
                    "content": f"{feature_name}のバグ修正実装",
                    "status": "pending"
                }
            ])
        
        if "リファクタ" in keywords:
            todos.append({
                "content": f"{feature_name}のコード品質改善",
                "status": "pending" if todos else "in_progress"
            })
        
        # 最低限1つのタスクは保証
        if not todos:
            todos.append({
                "content": f"{feature_name}の作業実行",
                "status": "in_progress"
            })
        
        return todos
    
    def _generate_response_message(self, feature_name: str, keywords: List[str]) -> str:
        """応答メッセージを生成"""
        keyword_str = "、".join(keywords)
        
        return (
            f"Yes, CTO! アレックスです！{feature_name}の{keyword_str}について、"
            f"自動的にペアプログラミングモードを起動しました！\n\n"
            f"TDDワークフローに従い、テストファーストで進行します。\n"
            f"Currently in: Red phase - まずテストから書いていきます！"
        )


class TriggerSystemManager:
    """トリガーシステム統合管理"""
    
    def __init__(self):
        self.detector = TriggerKeywordDetector()
        self.activator = AutoPairProgrammingActivator()
        
    def process_user_message(self, message: str) -> Optional[ActivationResult]:
        """
        ユーザーメッセージを処理してトリガー検出・ペアプロ起動
        
        Args:
            message: ユーザーメッセージ
            
        Returns:
            ActivationResult: 起動された場合の結果、起動されなかった場合はNone
        """
        # キーワード検出
        trigger_event = self.detector.scan_message(message)
        
        if trigger_event.triggered:
            logger.info(
                f"トリガーキーワード検出: {trigger_event.detected_keywords}", 
                "TRIGGER"
            )
            
            # ペアプログラミング自動起動
            result = self.activator.activate_pair_programming(
                trigger_event.detected_keywords,
                message
            )
            
            if result.success:
                # TodoWrite統合（外部ツール呼び出し）
                self._execute_todo_write(result.todo_list)
                
            return result
        
        return None
    
    def _execute_todo_write(self, todo_list: List[Dict]):
        """TodoWriteツールを実行"""
        try:
            # Claude CodeのTodoWriteツールを呼び出し
            # 実際の実装では外部ツール呼び出しをシミュレート
            logger.info(f"TodoWrite実行: {len(todo_list)}件のタスク作成", "TRIGGER")
            
            # 実際の実装では以下のようなコード
            # claude_code_api.call_tool("TodoWrite", {"todos": todo_list})
            
        except Exception as e:
            logger.error(f"TodoWrite実行エラー: {e}", "TRIGGER")


# フック統合は hooks.py 側で行う（循環インポート回避）

# システム起動時の自動登録
if __name__ == "__main__":
    # テスト実行
    detector = TriggerKeywordDetector()
    activator = AutoPairProgrammingActivator()
    
    test_message = "アレックス、ユーザー認証の実装をお願いします"
    result = detector.scan_message(test_message)
    
    if result.triggered:
        activation = activator.activate_pair_programming(result.detected_keywords, test_message)
        if activation.success:
            logger.info("テスト成功: トリガーキーワード検出システム起動完了", "TRIGGER")
        else:
            logger.error("テスト失敗: ペアプログラミング起動エラー", "TRIGGER")
    else:
        logger.error("テスト失敗: キーワード検出されませんでした", "TRIGGER")