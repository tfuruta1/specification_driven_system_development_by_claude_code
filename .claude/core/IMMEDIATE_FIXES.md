# 即時修正提案

## 概要
TDDテスト検証で発見された問題の即時修正コードを提供します。

## 1. コアシステムバリデーション強化

### test_core.pyのMock実装修正

```python
# 修正版AutoModeConfig Mock実装
class AutoModeConfig:
    def __init__(self, interval=30, max_iterations=100, timeout=300):
        # バリデーション追加
        if interval is not None and interval <= 0:
            raise ValueError("Interval must be positive")
        if max_iterations is not None and max_iterations <= 0:
            raise ValueError("Max iterations must be positive") 
        if timeout is not None and timeout <= 0:
            raise ValueError("Timeout must be positive")
            
        self.interval = interval
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.debug_mode = False
        self.strict_mode = False
        self.keywords = ['auto', 'mode', 'trigger']
```

## 2. 絵文字検出正規表現改善

### test_emoji.pyの正規表現パターン修正

```python
# 修正版絵文字パターン（複合絵文字対応）
EMOJI_PATTERN = r'(?:[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF](?:[\U0001F3FB-\U0001F3FF\uFE0F\u200D]*[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]*)*)'

class EmojiCoreValidator:
    def __init__(self):
        self.validation_enabled = True
        self.emoji_replacements = {'😀': '[笑顔]', '👍': '[いいね]', '❤️': '[ハート]'}
        # 改善された正規表現パターン
        self.emoji_pattern = re.compile(EMOJI_PATTERN, re.UNICODE)
```

## 3. キーワード検出精度向上

### test_utilities.pyのキーワード検出改善

```python
class TriggerKeywordDetector:
    def __init__(self):
        self.keywords = ['auto', 'trigger', 'activate', 'execute']
        
    def detect_keywords(self, text):
        if not text:
            return []
            
        # 単語境界を考慮した改善版検出
        import re
        detected = []
        text_lower = text.lower()
        
        for keyword in self.keywords:
            # 単語境界（\b）を使用して完全一致のみ検出
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                detected.append(keyword)
                
        return detected
```

## 4. パフォーマンステスト依存関係解決

### 環境セットアップコマンド

```bash
# 必要な依存関係をインストール
pip install psutil

# または、代替実装を使用
# test_performance.pyでpsutilが利用できない場合のフォールバック
```

### test_performance.pyの代替実装

```python
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    
class MemoryProfiler:
    def __init__(self):
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
            self.initial_memory = self.get_memory_usage()
        else:
            # フォールバック実装
            import os
            self.initial_memory = 0
            
    def get_memory_usage(self):
        if PSUTIL_AVAILABLE:
            try:
                return self.process.memory_info().rss / 1024 / 1024
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return 0
        else:
            # 簡易実装（実際のメモリ監視なし）
            return 0
```

## 5. Unicode処理エラー修正

### テスト実行環境のエンコーディング設定

```python
# test実行前にUTF-8環境設定
import sys
import os

# Windows環境でのUnicode対応
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    
# 環境変数設定
os.environ['PYTHONIOENCODING'] = 'utf-8'
```

## 実装優先順位

1. **即座に実装可能（簡単）**:
   - コアシステムのバリデーション強化
   - キーワード検出の改善

2. **短期実装（1-2日）**:
   - 絵文字正規表現の改善
   - Unicode処理エラーの修正

3. **中期実装（1週間）**:
   - パフォーマンステスト環境整備
   - 統合テストランナーの改善

## 検証方法

### 修正後のテスト実行
```bash
# 個別テスト検証
py test_core.py
py test_utilities.py
py test_emoji.py

# 全体テスト検証
py -m unittest discover -s . -p "test_*.py"
```

### 成功基準
- test_core.py: 25/25 テスト成功 (100%)
- test_utilities.py: 42/42 テスト成功 (100%)
- test_emoji.py: 30/30 テスト成功 (100%)
- 全体成功率: 99%以上

これらの修正により、TDDテストスイートの品質がさらに向上し、100%に近い成功率を達成できます。