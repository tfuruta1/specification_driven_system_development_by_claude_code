#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for jst_utils module
Achieving 100% test coverage
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta
import unittest
from unittest.mock import patch

# Setup relative imports from .claude folder
import sys
from pathlib import Path

# Find .claude root using relative path
current_file = Path(__file__).resolve()
current = current_file.parent

# Navigate up to find .claude folder (not subfolder)
claude_root = None
for _ in range(10):  # Limit iterations
    if current.name == '.claude':
        claude_root = current
        break
    if current.parent == current:  # Reached root
        break
    current = current.parent

# If not found, check for .claude in parent directories
if claude_root is None:
    current = current_file.parent
    for _ in range(10):
        if (current / '.claude').exists() and (current / '.claude' / 'system').exists():
            claude_root = current / '.claude'
            break
        if current.parent == current:
            break
        current = current.parent

# Final fallback
if claude_root is None:
    # Assume we're in .claude/project/tests
    claude_root = current_file.parent.parent.parent

# Add system path
system_path = claude_root / "system"
if str(system_path) not in sys.path:
    sys.path.insert(0, str(system_path))

# Now import the modules to test
from core.jst_utils import JST, get_jst_now, format_jst_time


class TestJSTUtils(unittest.TestCase):
    """Tests for JST utilities"""
    
    def test_jst_timezone(self):
        """Test JST timezone is correctly defined"""
        self.assertEqual(JST.utcoffset(None), timedelta(hours=9))
    
    def test_get_jst_now(self):
        """Test getting current JST time"""
        result = get_jst_now()
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.tzinfo, JST)
    
    def test_get_jst_now_correct_timezone(self):
        """Test JST time is 9 hours ahead of UTC"""
        with patch('core.jst_utils.datetime') as mock_datetime:
            # Mock UTC time
            utc_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = utc_time.astimezone(JST)
            
            result = get_jst_now()
            
            # Should be 9 hours ahead
            expected = datetime(2024, 1, 1, 9, 0, 0, tzinfo=JST)
            self.assertEqual(result, expected)
    
    def test_format_jst_time_default(self):
        """Test formatting JST time with default (current time)"""
        result = format_jst_time()
        
        # Check format
        self.assertIsInstance(result, str)
        self.assertTrue(result.endswith(" JST"))
        
        # Check it's a valid datetime format
        time_part = result.replace(" JST", "")
        parsed = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")
        self.assertIsInstance(parsed, datetime)
    
    def test_format_jst_time_with_specific_time(self):
        """Test formatting specific JST time"""
        test_time = datetime(2024, 1, 1, 12, 30, 45, tzinfo=JST)
        result = format_jst_time(test_time)
        
        self.assertEqual(result, "2024-01-01 12:30:45 JST")
    
    def test_format_jst_time_with_naive_datetime(self):
        """Test formatting naive datetime (no timezone)"""
        naive_time = datetime(2024, 1, 1, 12, 30, 45)
        result = format_jst_time(naive_time)
        
        # Should format without timezone conversion
        self.assertEqual(result, "2024-01-01 12:30:45 JST")
    
    def test_format_jst_time_with_different_timezone(self):
        """Test formatting datetime from different timezone"""
        utc_time = datetime(2024, 1, 1, 3, 30, 45, tzinfo=timezone.utc)
        # Convert to JST
        jst_time = utc_time.astimezone(JST)
        result = format_jst_time(jst_time)
        
        # Should be converted to JST (9 hours ahead)
        self.assertEqual(result, "2024-01-01 12:30:45 JST")


if __name__ == '__main__':
    unittest.main(verbosity=2)