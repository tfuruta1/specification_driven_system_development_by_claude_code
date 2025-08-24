#!/usr/bin/env python3
"""
JST () 
.claude
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path

#  (UTC+9)
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """
    JST
    
    Returns:
        datetime: JST
    """
    return datetime.now(JST)

def get_date_str():
    """
    JST (YYYY-MM-DD)
    
    Returns:
        str: 
    """
    return get_jst_now().strftime("%Y-%m-%d")

def get_time_str():
    """
    JST (HH:MM:SS)
    
    Returns:
        str: 
    """
    return get_jst_now().strftime("%H:%M:%S")

def get_datetime_str():
    """
    JST (YYYY-MM-DD HH:MM:SS)
    
    Returns:
        str: 
    """
    return get_jst_now().strftime("%Y-%m-%d %H:%M:%S")

def format_jst_datetime(dt=None):
    """
    JST (YYYY-MM-DD HH:MM:SS)
    
    Args:
        dt: datetime  ()
    
    Returns:
        str: 
    """
    if dt is None:
        dt = get_jst_now()
    elif dt.tzinfo is None:
        # JST
        dt = dt.replace(tzinfo=JST)
    else:
        # JST
        dt = dt.astimezone(JST)
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_session_time():
    """
     (HHMM)
    
    
    Returns:
        str:  (: "1430")
    """
    return get_jst_now().strftime("%H%M")

def get_log_timestamp():
    """
    
    
    Returns:
        str: "[HH:MM:SS JST]" 
    """
    return f"[{get_time_str()} JST]"

def get_filename_timestamp():
    """
    
    
    Returns:
        str: "YYYY-MM-DD_HHMM" 
    """
    now = get_jst_now()
    return now.strftime("%Y-%m-%d_%H%M")

def format_jst_time(dt=None, format_str="%Y-%m-%d %H:%M:%S JST"):
    """
    JST
    
    Args:
        dt: None
        format_str: 
        
    Returns:
        
    """
    if dt is None:
        dt = get_jst_now()
    elif dt.tzinfo is None:
        # JST
        dt = dt.replace(tzinfo=JST)
    elif dt.tzinfo != JST:
        # JST
        dt = dt.astimezone(JST)
    
    return dt.strftime(format_str)


def format_jst_date(dt=None):
    """
    JST
    
    Args:
        dt: None
        
    Returns:
        
    """
    return format_jst_time(dt, "%Y-%m-%d")


def get_jst_yesterday():
    """JST"""
    return get_jst_now() - timedelta(days=1)


def get_jst_tomorrow():
    """JST"""
    return get_jst_now() + timedelta(days=1)


def format_jst_header(date_str=None, session_time=None):
    """
    
    
    Args:
        date_str:  ()
        session_time:  ()
    
    Returns:
        str: 
    """
    if date_str is None:
        date_str = get_date_str()
    if session_time is None:
        session_time = get_session_time()
    
    return f"""#  - {date_str} (JST)

SYSTEM: {session_time[:2]}:{session_time[2:]} JST

CTOSYSTEM

---

"""

# SYSTEM
if __name__ == "__main__":
    print(f"SYSTEMJST: {get_jst_now()}")
    print(f"SYSTEM: {get_date_str()}")
    print(f": {get_time_str()}")
    print(f": {get_datetime_str()}")
    print(f": {get_session_time()}")
    print(f": {get_log_timestamp()}")
    print(f": {get_filename_timestamp()}")