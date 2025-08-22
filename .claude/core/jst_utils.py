#!/usr/bin/env python3
"""
JST (日本標準時) ユーティリティ
.claude内のすべての時刻処理を統一するための共通モジュール
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path

# 日本標準時 (UTC+9)
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """
    現在のJST時刻を取得
    
    Returns:
        datetime: 現在のJST時刻
    """
    return datetime.now(JST)

def get_date_str():
    """
    JST日付文字列を取得 (YYYY-MM-DD形式)
    
    Returns:
        str: 日付文字列
    """
    return get_jst_now().strftime("%Y-%m-%d")

def get_time_str():
    """
    JST時刻文字列を取得 (HH:MM:SS形式)
    
    Returns:
        str: 時刻文字列
    """
    return get_jst_now().strftime("%H:%M:%S")

def get_datetime_str():
    """
    JST日時文字列を取得 (YYYY-MM-DD HH:MM:SS形式)
    
    Returns:
        str: 日時文字列
    """
    return get_jst_now().strftime("%Y-%m-%d %H:%M:%S")

def format_jst_datetime(dt=None):
    """
    JST日時をフォーマット (YYYY-MM-DD HH:MM:SS形式)
    
    Args:
        dt: datetime オブジェクト (省略時は現在時刻)
    
    Returns:
        str: フォーマット済み日時文字列
    """
    if dt is None:
        dt = get_jst_now()
    elif dt.tzinfo is None:
        # タイムゾーン情報がない場合はJSTとして扱う
        dt = dt.replace(tzinfo=JST)
    else:
        # JSTに変換
        dt = dt.astimezone(JST)
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_session_time():
    """
    セッション開始時刻を取得 (HHMM形式)
    ファイル名に使用
    
    Returns:
        str: 時刻文字列 (例: "1430")
    """
    return get_jst_now().strftime("%H%M")

def get_log_timestamp():
    """
    ログ用タイムスタンプを取得
    
    Returns:
        str: "[HH:MM:SS JST]" 形式の文字列
    """
    return f"[{get_time_str()} JST]"

def get_filename_timestamp():
    """
    ファイル名用タイムスタンプを取得
    
    Returns:
        str: "YYYY-MM-DD_HHMM" 形式の文字列
    """
    now = get_jst_now()
    return now.strftime("%Y-%m-%d_%H%M")

def format_jst_time(dt=None, format_str="%Y-%m-%d %H:%M:%S JST"):
    """
    JST時刻をフォーマット（統合テスト用）
    
    Args:
        dt: フォーマットする日時（Noneの場合は現在時刻）
        format_str: フォーマット文字列
        
    Returns:
        フォーマットされた時刻文字列
    """
    if dt is None:
        dt = get_jst_now()
    elif dt.tzinfo is None:
        # タイムゾーン未指定の場合はJSTとして扱う
        dt = dt.replace(tzinfo=JST)
    elif dt.tzinfo != JST:
        # 他のタイムゾーンの場合はJSTに変換
        dt = dt.astimezone(JST)
    
    return dt.strftime(format_str)


def format_jst_date(dt=None):
    """
    JST日付をフォーマット（統合テスト用）
    
    Args:
        dt: フォーマットする日時（Noneの場合は現在時刻）
        
    Returns:
        フォーマットされた日付文字列
    """
    return format_jst_time(dt, "%Y-%m-%d")


def get_jst_yesterday():
    """JST昨日の日時を取得（統合テスト用）"""
    return get_jst_now() - timedelta(days=1)


def get_jst_tomorrow():
    """JST明日の日時を取得（統合テスト用）"""
    return get_jst_now() + timedelta(days=1)


def format_jst_header(date_str=None, session_time=None):
    """
    ログファイルのヘッダーをフォーマット
    
    Args:
        date_str: 日付文字列 (省略時は現在日付)
        session_time: セッション開始時刻 (省略時は現在時刻)
    
    Returns:
        str: フォーマット済みヘッダー文字列
    """
    if date_str is None:
        date_str = get_date_str()
    if session_time is None:
        session_time = get_session_time()
    
    return f"""# 作業ログ - {date_str} (JST)

セッション開始: {session_time[:2]}:{session_time[2:]} JST

CTOとアレックスのペアプログラミング記録

---

"""

# 使用例
if __name__ == "__main__":
    print(f"現在のJST: {get_jst_now()}")
    print(f"日付: {get_date_str()}")
    print(f"時刻: {get_time_str()}")
    print(f"日時: {get_datetime_str()}")
    print(f"セッション時刻: {get_session_time()}")
    print(f"ログタイムスタンプ: {get_log_timestamp()}")
    print(f"ファイル名タイムスタンプ: {get_filename_timestamp()}")