#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一インポート修正ユーティリティ
全モジュールのインポートエラーを解決するための共通機能
DRY原則に基づき、重複するインポート修正コードを一元化
"""

import sys
from pathlib import Path

def setup_import_paths():
    """
    統一されたインポートパス設定
    全モジュールで使用する共通のパス設定関数
    """
    current_file = Path(__file__).resolve()
    
    # .claudeフォルダを探す
    claude_root = None
    current = current_file.parent
    for _ in range(10):
        if current.name == '.claude':
            claude_root = current
            break
        if (current / '.claude').exists():
            claude_root = current / '.claude'
            break
        current = current.parent
        if current == current.parent:
            break
    
    if not claude_root:
        # フォールバック：3階層上を仮定
        claude_root = current_file.parent.parent.parent
    
    # システムパスを追加
    system_path = claude_root / "system"
    if str(system_path) not in sys.path:
        sys.path.insert(0, str(system_path))
    
    # ルートパスも追加
    if str(claude_root) not in sys.path:
        sys.path.insert(0, str(claude_root))
    
    return claude_root, system_path

def get_import_setup_code():
    """
    各モジュールの先頭に挿入するインポート設定コードを返す
    DRY原則: 同じコードを繰り返さない
    """
    return '''# Auto-generated import setup
import sys
from pathlib import Path

# Setup import paths
current_file = Path(__file__).resolve()
claude_root = None
current = current_file.parent
for _ in range(10):
    if current.name == '.claude':
        claude_root = current
        break
    if (current / '.claude').exists():
        claude_root = current / '.claude'
        break
    current = current.parent

if claude_root:
    sys.path.insert(0, str(claude_root / "system"))
    sys.path.insert(0, str(claude_root))
'''

def fix_module_imports(module_path: Path):
    """
    モジュールのインポートを修正
    
    Args:
        module_path: 修正対象のモジュールパス
        
    Returns:
        bool: 修正成功の場合True
    """
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既にインポート設定がある場合はスキップ
        if 'Setup import paths' in content:
            return True
        
        # インポート設定を追加
        lines = content.split('\n')
        
        # シェバンとエンコーディング宣言の後に挿入
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('#!') or line.startswith('# -*- coding'):
                insert_pos = i + 1
            elif line.strip() and not line.startswith('#'):
                break
        
        # ドキュメント文字列の後に挿入
        in_docstring = False
        for i in range(insert_pos, len(lines)):
            if '"""' in lines[i]:
                if not in_docstring:
                    in_docstring = True
                else:
                    insert_pos = i + 1
                    break
        
        # インポート設定を挿入
        setup_code = get_import_setup_code().split('\n')
        lines = lines[:insert_pos] + [''] + setup_code + [''] + lines[insert_pos:]
        
        # ファイルを更新
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
        
    except Exception as e:
        print(f"Error fixing {module_path}: {e}")
        return False