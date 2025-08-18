#!/usr/bin/env python3
"""
日本標準時（JST）設定モジュール
階層型エージェントシステム v8.8
全システムで統一されたJST表記を提供
"""

from datetime import datetime, timezone, timedelta

# JST タイムゾーン定義
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在のJST時刻を取得"""
    return datetime.now(JST)

def format_jst_time():
    """JST時刻を HH:MM:SS JST 形式で返す"""
    now = get_jst_now()
    return now.strftime("%H:%M:%S JST")

def format_jst_datetime():
    """JST日時を YYYY-MM-DD HH:MM:SS JST 形式で返す"""
    now = get_jst_now()
    return now.strftime("%Y-%m-%d %H:%M:%S JST")

def format_jst_date():
    """JST日付を YYYY-MM-DD 形式で返す"""
    now = get_jst_now()
    return now.strftime("%Y-%m-%d")

def format_jst_timestamp():
    """ファイル名用のJSTタイムスタンプ YYYYMMDD_HHMMSS_JST 形式で返す"""
    now = get_jst_now()
    return now.strftime("%Y%m%d_%H%M%S_JST")

def format_jst_log_timestamp():
    """ログ用のJSTタイムスタンプ [YYYY-MM-DD HH:MM:SS JST] 形式で返す"""
    now = get_jst_now()
    return f"[{now.strftime('%Y-%m-%d %H:%M:%S JST')}]"

def parse_jst_string(date_string, format_string="%Y-%m-%d %H:%M:%S"):
    """文字列をJST日時として解析"""
    dt = datetime.strptime(date_string, format_string)
    return dt.replace(tzinfo=JST)

def to_jst(dt):
    """任意のdatetimeオブジェクトをJSTに変換"""
    if dt.tzinfo is None:
        # タイムゾーンが設定されていない場合はJSTとして扱う
        return dt.replace(tzinfo=JST)
    else:
        # 他のタイムゾーンからJSTに変換
        return dt.astimezone(JST)

def get_jst_offset_hours():
    """JSTのUTCからのオフセット時間を返す"""
    return 9

def is_business_hours(dt=None):
    """営業時間内かどうかを判定（9:00-18:00 JST）"""
    if dt is None:
        dt = get_jst_now()
    else:
        dt = to_jst(dt)
    
    hour = dt.hour
    return 9 <= hour < 18

def is_weekend(dt=None):
    """週末かどうかを判定"""
    if dt is None:
        dt = get_jst_now()
    else:
        dt = to_jst(dt)
    
    # 0=月曜日, 6=日曜日
    return dt.weekday() in [5, 6]

# テスト用
if __name__ == "__main__":
    print(f"現在のJST時刻: {format_jst_time()}")
    print(f"現在のJST日時: {format_jst_datetime()}")
    print(f"現在のJST日付: {format_jst_date()}")
    print(f"タイムスタンプ: {format_jst_timestamp()}")
    print(f"ログ用タイムスタンプ: {format_jst_log_timestamp()}")
    print(f"営業時間内: {is_business_hours()}")
    print(f"週末: {is_weekend()}")