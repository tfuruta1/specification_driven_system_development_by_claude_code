#!/usr/bin/env python3
"""
階層型エージェントシステム - JST統一設定
全システムで使用する日本標準時の共通設定
"""

from datetime import datetime
import locale

# 日本のロケール設定を試みる
try:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Japanese_Japan.932')
    except:
        pass  # ロケール設定失敗しても続行

def get_jst_now():
    """現在のJST時刻を取得"""
    # Windows環境ではシステム時刻がJST
    return datetime.now()

def format_jst_datetime(dt=None):
    """日時をJST形式でフォーマット"""
    if dt is None:
        dt = get_jst_now()
    return dt.strftime("%Y-%m-%d %H:%M:%S JST")

def format_jst_date(dt=None):
    """日付をJST形式でフォーマット"""
    if dt is None:
        dt = get_jst_now()
    return dt.strftime("%Y-%m-%d")

def format_jst_time(dt=None):
    """時刻をJST形式でフォーマット"""
    if dt is None:
        dt = get_jst_now()
    return dt.strftime("%H:%M:%S JST")

def format_jst_timestamp(dt=None):
    """タイムスタンプをJST形式でフォーマット"""
    if dt is None:
        dt = get_jst_now()
    return dt.strftime("%Y%m%d_%H%M%S_JST")

def format_jst_iso(dt=None):
    """ISO形式でJSTを明記"""
    if dt is None:
        dt = get_jst_now()
    return dt.strftime("%Y-%m-%dT%H:%M:%S+09:00")