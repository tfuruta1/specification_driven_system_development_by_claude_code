#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
絵文字パターン定義モジュール - Claude Code Core v12.0
emoji_validatorシステムで使用される絵文字パターンと置換マップ

TDDテスト要求:
- 全絵文字パターンの検出
- 置換マッピングの正確性
- 国際化対応
- セキュリティ脆弱性対応（新規修正された部分）
"""

import re
from typing import Dict, List, Set, Any

# 基本絵文字パターン（Unicode範囲）
EMOJI_UNICODE_RANGES = [
    r'\U0001F600-\U0001F64F',  # 感情・人物
    r'\U0001F300-\U0001F5FF',  # その他のシンボル
    r'\U0001F680-\U0001F6FF',  # 交通・地図
    r'\U0001F1E0-\U0001F1FF',  # 旗
    r'\U00002600-\U000026FF',  # その他のシンボル
    r'\U00002700-\U000027BF',  # 装飾記号
    r'\U0001F900-\U0001F9FF',  # 補助絵文字
    r'\U0001FA70-\U0001FAFF',  # シンボルと絵文字の拡張
]

# 統合絵文字正規表現パターン
EMOJI_PATTERN = re.compile(
    '[' + ''.join(EMOJI_UNICODE_RANGES) + ']',
    re.UNICODE
)

# 絵文字から対応テキストへの置換マップ
EMOJI_REPLACEMENTS: Dict[str, str] = {
    # 感情・表情
    '😀': '[笑顔]',
    '😃': '[大きな笑顔]',
    '😄': '[目を細めた笑顔]',
    '😁': '[歯を見せた笑顔]',
    '😆': '[大笑い]',
    '😅': '[汗をかいた笑顔]',
    '🤣': '[笑い転げる]',
    '😂': '[涙を流して笑う]',
    '🙂': '[微笑み]',
    '🙃': '[逆さ顔]',
    '😉': '[ウィンク]',
    '😊': '[幸せな顔]',
    '😇': '[天使の輪]',
    '😍': '[ハート目]',
    '🤩': '[星目]',
    '😘': '[投げキス]',
    '😗': '[キス顔]',
    '😚': '[目を閉じてキス]',
    '😙': '[微笑みキス]',
    '😋': '[おいしい]',
    '😛': '[舌出し]',
    '😜': '[ウィンク舌出し]',
    '🤪': '[変な顔]',
    '😝': '[舌出し目閉じ]',
    '🤑': '[お金目]',
    '🤗': '[ハグ]',
    '🤭': '[手で口を隠す]',
    '🤫': '[しーっ]',
    '🤔': '[考え中]',
    '🤐': '[口にファスナー]',
    '🤨': '[眉を上げる]',
    '😐': '[無表情]',
    '😑': '[無言]',
    '😶': '[口なし]',
    '😏': '[にやり]',
    '😒': '[不満]',
    '🙄': '[目を回す]',
    '😬': '[歯を食いしばる]',
    '🤥': '[嘘つき]',
    '😔': '[落ち込み]',
    '😪': '[眠い]',
    '🤤': '[よだれ]',
    '😴': '[寝る]',
    '😷': '[マスク]',
    '🤒': '[熱]',
    '🤕': '[包帯]',
    '🤢': '[吐き気]',
    '🤮': '[嘔吐]',
    '🤧': '[くしゃみ]',
    '😵': '[目が回る]',
    '🤯': '[頭爆発]',
    '😕': '[困った]',
    '😟': '[心配]',
    '🙁': '[軽く落ち込み]',
    '😮': '[驚き開口]',
    '😯': '[驚き]',
    '😲': '[びっくり]',
    '😳': '[赤面]',
    '🥺': '[懇願]',
    '😦': '[落胆開口]',
    '😧': '[苦悩]',
    '😨': '[恐怖]',
    '😰': '[冷や汗]',
    '😥': '[がっかり安堵]',
    '😢': '[涙]',
    '😭': '[大泣き]',
    '😱': '[恐怖叫び]',
    '😖': '[混乱]',
    '😣': '[忍耐]',
    '😞': '[失望]',
    '😓': '[冷や汗]',
    '😩': '[疲れた]',
    '😫': '[疲労困憊]',
    '😤': '[怒り鼻息]',
    '😡': '[怒り赤]',
    '😠': '[怒り]',
    '🤬': '[罵倒]',
    
    # 手と体の動作
    '👍': '[いいね]',
    '👎': '[だめ]',
    '👌': '[OK]',
    '✌': '[ピース]',
    '🤞': '[願う]',
    '🤟': '[愛してる]',
    '🤘': '[ロック]',
    '🤙': '[電話]',
    '👈': '[左指差し]',
    '👉': '[右指差し]',
    '👆': '[上指差し]',
    '👇': '[下指差し]',
    '☝': '[人差し指]',
    '✋': '[手のひら]',
    '🤚': '[手の甲]',
    '🖖': '[バルカン挨拶]',
    '👋': '[手を振る]',
    '🤝': '[握手]',
    '👏': '[拍手]',
    '🙌': '[万歳]',
    '👐': '[開いた手]',
    '🤲': '[手のひら上向き]',
    '🙏': '[祈り]',
    
    # オブジェクト・シンボル
    '💻': '[ノートパソコン]',
    '💺': '[座席]',
    '🚗': '[車]',
    '✈️': '[飛行機]',
    '🏠': '[家]',
    '🏢': '[オフィスビル]',
    '📱': '[スマートフォン]',
    '💡': '[電球]',
    '🔧': '[レンチ]',
    '🔨': '[ハンマー]',
    '⚡': '[雷]',
    '🔥': '[火]',
    '💧': '[水滴]',
    '🌟': '[輝く星]',
    '⭐': '[星]',
    '🌈': '[虹]',
    '🌙': '[三日月]',
    '☀️': '[太陽]',
    '⛅': '[雲と太陽]',
    '☁️': '[雲]',
    '🌧': '[雨雲]',
    '⛈': '[雷雨]',
    '🌩': '[雷]',
    '❄️': '[雪]',
    
    # 活動・スポーツ
    '⚽': '[サッカー]',
    '🏀': '[バスケットボール]',
    '🏈': '[アメリカンフットボール]',
    '⚾': '[野球]',
    '🎾': '[テニス]',
    '🏐': '[バレーボール]',
    '🏓': '[卓球]',
    '🏸': '[バドミントン]',
    '🥅': '[ゴール]',
    '🏆': '[トロフィー]',
    '🥇': '[金メダル]',
    '🥈': '[銀メダル]',
    '🥉': '[銅メダル]',
    
    # 食べ物・飲み物
    '🍎': '[りんご]',
    '🍌': '[バナナ]',
    '🍊': '[オレンジ]',
    '🍓': '[いちご]',
    '🥝': '[キウイ]',
    '🍅': '[トマト]',
    '🥕': '[にんじん]',
    '🌽': '[とうもろこし]',
    '🥒': '[きゅうり]',
    '🥬': '[レタス]',
    '🧄': '[にんにく]',
    '🧅': '[玉ねぎ]',
    '🍞': '[パン]',
    '🥐': '[クロワッサン]',
    '🥖': '[フランスパン]',
    '🍕': '[ピザ]',
    '🍔': '[ハンバーガー]',
    '🌭': '[ホットドッグ]',
    '🥪': '[サンドイッチ]',
    '🌮': '[タコス]',
    '🌯': '[ブリトー]',
    '🍝': '[スパゲティ]',
    '🍜': '[ラーメン]',
    '🍲': '[鍋料理]',
    '🍱': '[弁当]',
    '🍣': '[寿司]',
    '🍤': '[エビフライ]',
    '🍙': '[おにぎり]',
    '🍚': '[ご飯]',
    '🍛': '[カレー]',
    '🥘': '[パエリア]',
    '☕': '[コーヒー]',
    '🍵': '[緑茶]',
    '🥤': '[ソフトドリンク]',
    '🍺': '[ビール]',
    '🍷': '[ワイン]',
    
    # 記号・マーク
    '❤️': '[ハート]',
    '🧡': '[オレンジハート]',
    '💛': '[黄色ハート]',
    '💚': '[緑ハート]',
    '💙': '[青ハート]',
    '💜': '[紫ハート]',
    '🖤': '[黒ハート]',
    '🤍': '[白ハート]',
    '🤎': '[茶色ハート]',
    '💕': '[2つのハート]',
    '💖': '[輝くハート]',
    '💗': '[成長するハート]',
    '💘': '[矢が刺さったハート]',
    '💝': '[リボン付きハート]',
    '💟': '[ハートの装飾]',
    '♥️': '[ハートスーツ]',
    '💌': '[ラブレター]',
    '💤': '[ZZZ]',
    '💢': '[怒りマーク]',
    '💣': '[爆弾]',
    '💥': '[爆発]',
    '💫': '[めまい]',
    '💨': '[突風]',
    '💦': '[汗しぶき]',
    '💪': '[上腕二頭筋]',
    
    # チェックマーク・記号
    '✅': '[チェックマーク]',
    '❌': '[×マーク]',
    '⭕': '[○マーク]',
    '❗': '[感嘆符]',
    '❓': '[疑問符]',
    '❔': '[白い疑問符]',
    '❕': '[白い感嘆符]',
    '‼️': '[二重感嘆符]',
    '⁉️': '[感嘆疑問符]',
    '🔴': '[赤い円]',
    '🟠': '[オレンジの円]',
    '🟡': '[黄色い円]',
    '🟢': '[緑の円]',
    '🔵': '[青い円]',
    '🟣': '[紫の円]',
    '⚫': '[黒い円]',
    '⚪': '[白い円]',
    '🟤': '[茶色の円]',
    
    # 矢印
    '⬆️': '[上矢印]',
    '↗️': '[右上矢印]',
    '➡️': '[右矢印]',
    '↘️': '[右下矢印]',
    '⬇️': '[下矢印]',
    '↙️': '[左下矢印]',
    '⬅️': '[左矢印]',
    '↖️': '[左上矢印]',
    '↕️': '[上下矢印]',
    '↔️': '[左右矢印]',
    '↩️': '[右巻き矢印]',
    '↪️': '[左巻き矢印]',
    '⤴️': '[右上カーブ矢印]',
    '⤵️': '[右下カーブ矢印]',
    '🔃': '[時計回り矢印]',
    '🔄': '[反時計回り矢印]',
    '🔙': '[BACK]',
    '🔚': '[END]',
    '🔛': '[ON]',
    '🔜': '[SOON]',
    '🔝': '[TOP]',
}

# ファイルタイプとコンテンツタイプのマッピング
FILE_TYPE_MAP: Dict[str, str] = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.vue': 'vue',
    '.jsx': 'react',
    '.tsx': 'react_typescript',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.md': 'markdown',
    '.txt': 'text',
    '.json': 'json',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.ini': 'ini',
    '.cfg': 'config',
    '.conf': 'config',
    '.sh': 'shell',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    '.ps1': 'powershell',
    '.sql': 'sql',
    '.rb': 'ruby',
    '.php': 'php',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'header',
    '.hpp': 'header',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.r': 'r',
    '.m': 'matlab',
    '.pl': 'perl',
    '.lua': 'lua',
    '.dart': 'dart',
    '.elm': 'elm',
    '.ex': 'elixir',
    '.fs': 'fsharp',
    '.hs': 'haskell',
    '.clj': 'clojure',
    '.jl': 'julia',
}

# 各コンテンツタイプでの絵文字使用の許可レベル
EMOJI_PERMISSION_LEVELS: Dict[str, str] = {
    'commit': 'strict',      # コミットメッセージは厳格
    'log': 'strict',         # ログメッセージも厳格
    'code': 'strict',        # コードは厳格
    'docs': 'moderate',      # ドキュメントは中程度
    'markdown': 'moderate',  # Markdownは中程度
    'comments': 'lenient',   # コメントは寛容
    'test': 'lenient',       # テストは寛容（テスト用データとして）
    'config': 'strict',      # 設定ファイルは厳格
    'unknown': 'moderate',   # 不明なタイプは中程度
}

def get_replacement_suggestions(emoji: str) -> List[str]:
    """
    指定された絵文字の置換候補を取得
    
    Args:
        emoji: 置換したい絵文字
        
    Returns:
        置換候補のリスト
    """
    if emoji in EMOJI_REPLACEMENTS:
        primary = EMOJI_REPLACEMENTS[emoji]
        return [primary, primary.replace('[', '(').replace(']', ')'), emoji + '_text']
    
    # フォールバック: 汎用的な置換候補
    return ['[絵文字]', '(絵文字)', 'emoji']

def get_emoji_categories() -> Dict[str, List[str]]:
    """
    絵文字をカテゴリ別に分類
    
    Returns:
        カテゴリ別の絵文字辞書
    """
    categories = {
        'emotions': [],
        'gestures': [],
        'objects': [],
        'activities': [],
        'food': [],
        'symbols': [],
        'arrows': [],
        'colors': [],
    }
    
    # カテゴリ分類ロジック（簡略版）
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        if any(word in replacement.lower() for word in ['笑', '涙', '怒', '困', '驚', '顔']):
            categories['emotions'].append(emoji)
        elif any(word in replacement.lower() for word in ['手', '指', '拍手', '握手', '祈り']):
            categories['gestures'].append(emoji)
        elif any(word in replacement.lower() for word in ['パソコン', '車', '家', '電話', '電球']):
            categories['objects'].append(emoji)
        elif any(word in replacement.lower() for word in ['サッカー', 'バスケ', 'テニス', 'トロフィー']):
            categories['activities'].append(emoji)
        elif any(word in replacement.lower() for word in ['りんご', 'パン', 'ピザ', 'コーヒー', '寿司']):
            categories['food'].append(emoji)
        elif any(word in replacement.lower() for word in ['ハート', 'マーク', '円']):
            categories['symbols'].append(emoji)
        elif '矢印' in replacement.lower():
            categories['arrows'].append(emoji)
        else:
            categories['symbols'].append(emoji)  # デフォルトはシンボル
    
    return categories

def is_emoji_allowed_in_context(emoji: str, context_type: str) -> bool:
    """
    指定されたコンテキストで絵文字が許可されているかチェック
    
    Args:
        emoji: チェックする絵文字
        context_type: コンテキストタイプ
        
    Returns:
        許可されている場合True
    """
    permission_level = EMOJI_PERMISSION_LEVELS.get(context_type, 'moderate')
    
    if permission_level == 'lenient':
        return True
    elif permission_level == 'strict':
        return False
    else:  # moderate
        # 中程度：一部の絵文字のみ許可（例：矢印、チェックマーク等）
        allowed_moderate = ['✅', '❌', '⭕', '➡️', '⬆️', '⬇️', '⬅️', '↗️', '↘️', '↙️', '↖️']
        return emoji in allowed_moderate

def get_security_risk_emojis() -> Set[str]:
    """
    セキュリティリスクのある絵文字を取得
    新しく修正された脆弱性対応部分
    
    Returns:
        セキュリティリスクのある絵文字のセット
    """
    # 視覚的に紛らわしい絵文字（フィッシング等に悪用される可能性）
    risk_emojis = {
        '🔒', '🔓', '🔑',  # セキュリティ関連アイコン（偽装リスク）
        '⚠️', '⛔', '🚫',  # 警告系（偽の警告メッセージに悪用）
        '📧', '📨', '📩',  # メール関連（フィッシングメール偽装）
        '🏦', '🏧', '💳',  # 金融関連（金融詐欺に悪用）
        '👮', '👨‍💼', '👩‍💼',  # 権威を示す職業（なりすましリスク）
        '🆘', '🚨',        # 緊急事態（偽の緊急通知）
        '✅',              # チェックマーク（偽の承認）
    }
    return risk_emojis

def validate_emoji_security(emoji: str) -> Dict[str, Any]:
    """
    絵文字のセキュリティリスクを評価
    
    Args:
        emoji: 評価する絵文字
        
    Returns:
        セキュリティ評価結果
    """
    risk_emojis = get_security_risk_emojis()
    
    return {
        'emoji': emoji,
        'is_high_risk': emoji in risk_emojis,
        'risk_level': 'HIGH' if emoji in risk_emojis else 'LOW',
        'risk_reason': 'フィッシング/詐欺に悪用される可能性' if emoji in risk_emojis else None,
        'recommendation': '使用を避ける' if emoji in risk_emojis else '使用可能'
    }

# テスト用関数
def get_test_emojis() -> Dict[str, List[str]]:
    """
    テスト用の絵文字セットを取得
    
    Returns:
        テスト用絵文字辞書
    """
    return {
        'basic': ['😀', '😃', '😄', '😁'],
        'gestures': ['👍', '👎', '👌', '✌️'],
        'objects': ['💻', '📱', '🏠', '🚗'],
        'symbols': ['❤️', '✅', '❌', '⭕'],
        'high_risk': list(get_security_risk_emojis())[:5],
        'mixed': ['😀', '💻', '✅', '🔒', '👍']
    }

# パフォーマンステスト用の大量絵文字
def generate_large_emoji_text(count: int = 1000) -> str:
    """
    パフォーマンステスト用の大量絵文字テキストを生成
    
    Args:
        count: 生成する絵文字の数
        
    Returns:
        大量の絵文字を含むテキスト
    """
    import random
    emojis = list(EMOJI_REPLACEMENTS.keys())
    selected_emojis = random.choices(emojis, k=count)
    return ' '.join(selected_emojis)

# モジュールの初期化とバリデーション
def validate_patterns() -> Dict[str, Any]:
    """
    パターン定義の整合性をチェック
    
    Returns:
        バリデーション結果
    """
    results = {
        'total_replacements': len(EMOJI_REPLACEMENTS),
        'total_file_types': len(FILE_TYPE_MAP),
        'pattern_valid': True,
        'security_risks': len(get_security_risk_emojis()),
        'issues': []
    }
    
    # パターンの有効性チェック
    try:
        test_text = "テスト 😀 🚀 💻"
        matches = EMOJI_PATTERN.findall(test_text)
        if len(matches) != 3:
            results['pattern_valid'] = False
            results['issues'].append(f"パターンマッチング異常: 期待3個、実際{len(matches)}個")
    except Exception as e:
        results['pattern_valid'] = False
        results['issues'].append(f"パターンエラー: {str(e)}")
    
    # 置換マップの整合性チェック
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        if not replacement.strip():
            results['issues'].append(f"空の置換テキスト: {emoji}")
        if not (replacement.startswith('[') and replacement.endswith(']')):
            results['issues'].append(f"置換形式異常: {emoji} -> {replacement}")
    
    return results

if __name__ == "__main__":
    print("=== 絵文字パターン定義モジュール v12.0 ===")
    
    # バリデーション実行
    validation = validate_patterns()
    print(f"置換マップ数: {validation['total_replacements']}")
    print(f"対応ファイル形式: {validation['total_file_types']}")
    print(f"セキュリティリスク絵文字: {validation['security_risks']}")
    print(f"パターン有効性: {'OK' if validation['pattern_valid'] else 'NG'}")
    
    if validation['issues']:
        print("\n⚠️ 問題発見:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    # テスト例
    test_emojis = get_test_emojis()
    print(f"\nテスト用絵文字セット:")
    for category, emojis in test_emojis.items():
        print(f"  {category}: {emojis}")
    
    # セキュリティチェック例
    print("\nセキュリティリスク例:")
    for emoji in ['✅', '🔒', '😀']:
        security = validate_emoji_security(emoji)
        print(f"  {emoji}: {security['risk_level']} - {security['recommendation']}")