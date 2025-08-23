#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
絵文字パターンと置換マップ - Claude Code Core v11.0
EmojiValidatorから分離された絵文字パターン定義
"""

import re

# 標準的な絵文字置換マッピング（CTOとアレックス用に拡張）
EMOJI_REPLACEMENTS = {
    # 基本的なステータス
    "✅": "[OK]",
    "❌": "[NG]", 
    "🎉": "[完了]",
    "🔧": "[修正]",
    "📋": "[リスト]",
    "🧪": "[テスト]",
    "📝": "[メモ]",
    "🚀": "[開始]",
    "⚠️": "[警告]",
    "ℹ️": "[情報]",
    "🔍": "[検索]",
    "💡": "[アイデア]",
    "📊": "[データ]",
    "🔐": "[セキュリティ]",
    "🌟": "[重要]",
    
    # 開発関連
    "👨‍💻": "[開発者]",
    "👩‍💻": "[開発者]",
    "💻": "[PC]",
    "📱": "[モバイル]",
    "🔄": "[更新]",
    "📤": "[送信]",
    "📥": "[受信]",
    "🎯": "[対象]",
    
    # SDD+TDD関連
    "📐": "[設計]",
    "📑": "[仕様書]",
    "🧩": "[モジュール]",
    "⚙️": "[設定]",
    "🔗": "[統合]",
    "📈": "[進捗]",
    "🏁": "[目標]",
    
    # ペアプログラミング関連
    "🤝": "[協力]",
    "💬": "[対話]",
    "🔊": "[発言]",
    "👥": "[チーム]",
    "🎪": "[デモ]",
    
    # 品質管理関連
    "🔎": "[レビュー]",
    "📏": "[測定]",
    "⚖️": "[評価]",
    "🎖️": "[品質]",
    "🛠️": "[ツール]"
}

# Unicode絵文字の包括的な範囲パターン
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # 顔文字
    "\U0001F300-\U0001F5FF"  # その他のシンボル
    "\U0001F680-\U0001F6FF"  # 交通・地図シンボル
    "\U0001F1E0-\U0001F1FF"  # 国旗
    "\U00002600-\U000026FF"  # その他のシンボル
    "\U00002700-\U000027BF"  # Dingbats
    "\U0001F900-\U0001F9FF"  # 追加シンボル
    "\U0001FA70-\U0001FAFF"  # 追加シンボル（拡張A）
    "\U00002190-\U000021FF"  # 矢印
    "\U0000FE00-\U0000FE0F"  # バリエーションセレクター
    "\U0000200D"             # ゼロ幅結合子
    "]+",
    re.UNICODE
)

# ファイルタイプマッピング
FILE_TYPE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript', 
    '.vue': 'vue',
    '.md': 'markdown',
    '.txt': 'text',
    '.json': 'json',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.log': 'log'
}

def get_replacement_suggestions(emoji: str):
    """
    絵文字の置換候補を提案
    
    Args:
        emoji: 対象絵文字
        
    Returns:
        置換候補のリスト
    """
    # 既知の置換がある場合
    if emoji in EMOJI_REPLACEMENTS:
        return [EMOJI_REPLACEMENTS[emoji]]
    
    # 類似絵文字から推測
    suggestions = []
    
    # カテゴリ別の一般的な置換候補
    if emoji in "✅✓✔️":
        suggestions.extend(["[OK]", "[完了]", "[成功]"])
    elif emoji in "❌✗✖️":
        suggestions.extend(["[NG]", "[失敗]", "[エラー]"])
    elif emoji in "⚠️⚡":
        suggestions.extend(["[警告]", "[注意]", "[重要]"])
    elif emoji in "📝📄📋":
        suggestions.extend(["[メモ]", "[文書]", "[記録]"])
    else:
        suggestions.append("[記号]")
    
    return suggestions