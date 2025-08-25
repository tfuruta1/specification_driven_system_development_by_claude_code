#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パスユーティリティ - .claudeフォルダを起点とした相対パス管理
ポータビリティを確保するため、全てのパスを相対パスで管理
"""

import os
import sys
from pathlib import Path
from typing import Optional

def get_claude_root() -> Path:
    """
    .claudeフォルダのルートパスを取得
    どこから実行されても.claudeフォルダを見つける
    """
    # 現在のファイルから遡って.claudeフォルダを探す
    current = Path(__file__).resolve()
    
    # 最大10階層まで遡る
    for _ in range(10):
        # パスに.claudeが含まれていて、その.claudeフォルダが存在する場合
        parts = current.parts
        for i, part in enumerate(parts):
            if part == '.claude':
                # .claudeまでのパスを構築
                claude_path = Path(*parts[:i+1])
                if claude_path.exists() and claude_path.is_dir():
                    return claude_path
        
        current = current.parent
        if current == current.parent:  # ルートディレクトリに到達
            break
    
    # 見つからない場合は、現在のディレクトリから探す
    cwd = Path.cwd()
    for _ in range(10):
        if cwd.name == '.claude':
            return cwd
        if (cwd / '.claude').exists():
            return cwd / '.claude'
        cwd = cwd.parent
        if cwd == cwd.parent:
            break
    
    # それでも見つからない場合は、スクリプトの3階層上を仮定
    # .claude/system/core/path_utils.py の場合
    return Path(__file__).resolve().parent.parent.parent

def get_relative_path(target: str, base: Optional[str] = None) -> Path:
    """
    .claudeフォルダを起点とした相対パスを取得
    
    Args:
        target: 目的のパス（例: "system/core", "temp/cache"）
        base: 基準パス（省略時は.claudeルート）
    
    Returns:
        相対パスのPathオブジェクト
    """
    claude_root = get_claude_root()
    
    if base:
        return claude_root / base / target
    else:
        return claude_root / target

def setup_import_path():
    """
    Pythonのimportパスを設定
    .claude/system/coreをパッケージとしてインポート可能にする
    """
    claude_root = get_claude_root()
    system_path = claude_root / "system"
    
    # sys.pathに追加（重複を避ける）
    system_path_str = str(system_path)
    if system_path_str not in sys.path:
        sys.path.insert(0, system_path_str)
    
    # .claudeルートも追加
    claude_root_str = str(claude_root)
    if claude_root_str not in sys.path:
        sys.path.insert(0, claude_root_str)

# パス定数（よく使うパス）
class ClaudePaths:
    """よく使用するパスの定数"""
    
    @property
    def root(self) -> Path:
        """ルートディレクトリ"""
        return get_claude_root()
    
    @property
    def system(self) -> Path:
        """システムディレクトリ"""
        return get_relative_path("system")
    
    @property
    def core(self) -> Path:
        """コアモジュールディレクトリ"""
        return get_relative_path("system/core")
    
    @property
    def config(self) -> Path:
        """設定ディレクトリ"""
        return get_relative_path("system/config")
    
    @property
    def project(self) -> Path:
        """プロジェクトディレクトリ"""
        return get_relative_path("project")
    
    @property
    def tests(self) -> Path:
        """テストディレクトリ"""
        return get_relative_path("project/tests")
    
    @property
    def temp(self) -> Path:
        """一時ファイルディレクトリ"""
        return get_relative_path("temp")
    
    @property
    def cache(self) -> Path:
        """キャッシュディレクトリ"""
        return get_relative_path("temp/cache")
    
    @property
    def logs(self) -> Path:
        """ログディレクトリ"""
        return get_relative_path("temp/logs")
    
    @property
    def reports(self) -> Path:
        """レポートディレクトリ"""
        return get_relative_path("temp/reports")

# シングルトンインスタンス
paths = ClaudePaths()

# モジュール初期化時にインポートパスを設定
setup_import_path()