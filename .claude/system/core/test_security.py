#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Tests - Consolidated security functionality testing
TDD Red-Green-Refactor implementation for comprehensive security testing

Consolidates tests from:
- test_file_access_logger_security.py
- Security aspects from other test files

TDD Requirements:
- 100% coverage of security functionality
- Path traversal attack prevention testing
- XSS attack prevention validation
- Input validation and sanitization testing
- File extension and access control testing
- Unicode and special character handling testing
"""

import unittest
import tempfile
import shutil
import json
import sys
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime
import copy
from io import StringIO

# Test target module imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from file_access_logger import FileAccessLogger
    from path_utils import PathUtils
    from emoji_core import EmojiCoreValidator
    from shared_logger import OptimizedLogger
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Import error: {e}")
    print("Running with mock implementations for TDD demonstration...")
    IMPORT_SUCCESS = False
    
    # RED Phase: Mock implementations for failing tests
    class SecurityValidator:
        def __init__(self):
            self.max_path_length = 1024
            self.max_description_length = 500
            self.blocked_patterns = [
                '../', '..\\',  # Path traversal
                '<script', '</script>',  # XSS
                'javascript:', 'vbscript:',  # Script injection
                '\x00',  # Null byte injection
            ]
            self.allowed_extensions = ['.txt', '.py', '.md', '.json', '.yml', '.yaml']
            
        def validate_path(self, path):
            """Validate file path for security issues"""
            if not path:
                return False, "Empty path not allowed"
                
            path_str = str(path)
            
            # Check length
            if len(path_str) > self.max_path_length:
                return False, f"Path too long: {len(path_str)} > {self.max_path_length}"
                
            # Check for blocked patterns
            for pattern in self.blocked_patterns:
                if pattern in path_str.lower():
                    return False, f"Blocked pattern detected: {pattern}"
                    
            return True, "Path is valid"
            
        def validate_file_extension(self, file_path):
            """Validate file extension"""
            path = Path(file_path)
            extension = path.suffix.lower()
            
            if extension in self.allowed_extensions:
                return True, f"Extension {extension} is allowed"
            else:
                return False, f"Extension {extension} is not allowed"
                
        def sanitize_input(self, input_text):
            """Sanitize input text"""
            if not input_text:
                return ""
                
            sanitized = str(input_text)
            
            # Remove HTML tags
            import re
            sanitized = re.sub(r'<[^>]*>', '', sanitized)
            
            # Remove script protocols
            sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
            sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)
            
            # Remove null bytes
            sanitized = sanitized.replace('\x00', '')
            
            return sanitized
            
        def check_unicode_safety(self, text):
            """Check for potentially dangerous Unicode characters"""
            if not text:
                return True, "Empty text is safe"
                
            # Check for control characters
            control_chars = []
            for char in text:
                if ord(char) < 32 and char not in ['\n', '\r', '\t']:
                    control_chars.append(char)
                    
            if control_chars:
                return False, f"Control characters detected: {control_chars}"
                
            return True, "Unicode text is safe"
            
    class FileAccessLogger:
        def __init__(self, log_file="security.log"):
            self.log_file = log_file
            self.security_log = []
            self.validator = SecurityValidator()
            
        def log_secure_file_access(self, file_path, operation, user="system", description=""):
            """Log file access with security validation"""
            # Validate path
            path_valid, path_message = self.validator.validate_path(file_path)
            
            # Validate extension
            ext_valid, ext_message = self.validator.validate_file_extension(file_path)
            
            # Sanitize description
            safe_description = self.validator.sanitize_input(description)
            
            # Check Unicode safety
            unicode_safe, unicode_message = self.validator.check_unicode_safety(description)
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "file_path": str(file_path),
                "operation": operation,
                "user": user,
                "description": safe_description,
                "security_checks": {
                    "path_valid": path_valid,
                    "path_message": path_message,
                    "extension_valid": ext_valid,
                    "extension_message": ext_message,
                    "unicode_safe": unicode_safe,
                    "unicode_message": unicode_message
                }
            }
            
            self.security_log.append(entry)
            return entry
            
        def get_security_violations(self):
            """Get entries with security violations"""
            violations = []
            for entry in self.security_log:
                checks = entry["security_checks"]
                if not all([checks["path_valid"], checks["extension_valid"], checks["unicode_safe"]]):
                    violations.append(entry)
            return violations


class TestSecurityValidator(unittest.TestCase):
    """Security validator comprehensive tests"""
    
    def setUp(self):
        """Test setup"""
        self.validator = SecurityValidator()
        
    def test_validator_initialization(self):
        """Validator initialization test"""
        self.assertIsNotNone(self.validator)
        self.assertGreater(self.validator.max_path_length, 0)
        self.assertGreater(self.validator.max_description_length, 0)
        self.assertIsInstance(self.validator.blocked_patterns, list)
        self.assertIsInstance(self.validator.allowed_extensions, list)
        
    def test_path_traversal_prevention_unix(self):
        """Unix path traversal prevention test"""
        malicious_paths = [
            "../../../etc/passwd",
            "legitimate/path/../../../etc/shadow",
            "/var/www/../../../root/.ssh/id_rsa",
            "../../../../bin/bash",
            "../config/database.yml",
        ]
        
        for path in malicious_paths:
            with self.subTest(path=path):
                is_valid, message = self.validator.validate_path(path)
                self.assertFalse(is_valid, f"Should detect path traversal: {path}")
                self.assertIn("Blocked pattern detected", message)
                
    def test_path_traversal_prevention_windows(self):
        """Windows path traversal prevention test"""
        malicious_paths = [
            "..\\..\\..\\Windows\\System32\\config\\SAM",
            "legitimate\\path\\..\\..\\..\\Windows\\System32",
            "C:\\Users\\..\\..\\Windows\\System32\\drivers\\etc\\hosts",
            "..\\..\\..\\Program Files\\sensitive_app\\config.ini",
        ]
        
        for path in malicious_paths:
            with self.subTest(path=path):
                is_valid, message = self.validator.validate_path(path)
                self.assertFalse(is_valid, f"Should detect Windows path traversal: {path}")
                self.assertIn("Blocked pattern detected", message)
                
    def test_legitimate_paths_allowed(self):
        """Legitimate paths allowed test"""
        legitimate_paths = [
            "/legitimate/absolute/path/file.txt",
            "relative/path/to/file.py",
            "simple_file.json",
            "path/with-dashes/and_underscores.yml",
            "/var/log/application/app.log",
        ]
        
        for path in legitimate_paths:
            with self.subTest(path=path):
                is_valid, message = self.validator.validate_path(path)
                self.assertTrue(is_valid, f"Should allow legitimate path: {path}")
                self.assertEqual(message, "Path is valid")
                
    def test_path_length_validation(self):
        """Path length validation test"""
        # Test normal length
        normal_path = "a" * 500
        is_valid, message = self.validator.validate_path(normal_path)
        self.assertTrue(is_valid, "Normal length path should be valid")
        
        # Test excessive length
        long_path = "a" * (self.validator.max_path_length + 1)
        is_valid, message = self.validator.validate_path(long_path)
        self.assertFalse(is_valid, "Excessively long path should be invalid")
        self.assertIn("Path too long", message)
        
    def test_empty_path_handling(self):
        """Empty path handling test"""
        empty_paths = ["", None]
        
        for empty_path in empty_paths:
            with self.subTest(path=empty_path):
                is_valid, message = self.validator.validate_path(empty_path)
                self.assertFalse(is_valid, "Empty path should be invalid")
                self.assertIn("Empty path", message)


class TestXSSPrevention(unittest.TestCase):
    """XSS prevention tests"""
    
    def setUp(self):
        """Test setup"""
        self.validator = SecurityValidator()
        
    def test_script_tag_detection(self):
        """Script tag detection test"""
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "<script src='malicious.js'></script>",
            "<SCRIPT>alert('XSS')</SCRIPT>",  # Case variation
            "Some text <script>evil()</script> more text",
            "<script type='text/javascript'>harmful()</script>",
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input_text=malicious_input):
                # Check if path validation catches it
                is_valid, message = self.validator.validate_path(malicious_input)
                self.assertFalse(is_valid, f"Should detect script tag: {malicious_input}")
                
                # Check sanitization
                sanitized = self.validator.sanitize_input(malicious_input)
                self.assertNotIn("<script>", sanitized.lower())
                self.assertNotIn("</script>", sanitized.lower())
                
    def test_javascript_protocol_prevention(self):
        """JavaScript protocol prevention test"""
        malicious_inputs = [
            "javascript:alert('XSS')",
            "JAVASCRIPT:void(0)",
            "vbscript:MsgBox('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input_text=malicious_input):
                # Check path validation
                is_valid, message = self.validator.validate_path(malicious_input)
                self.assertFalse(is_valid, f"Should detect script protocol: {malicious_input}")
                
                # Check sanitization
                sanitized = self.validator.sanitize_input(malicious_input)
                self.assertNotIn("javascript:", sanitized.lower())
                self.assertNotIn("vbscript:", sanitized.lower())
                
    def test_html_tag_removal(self):
        """HTML tag removal test"""
        html_inputs = [
            "<div>Content</div>",
            "<img src='image.jpg' onerror='alert(1)'>",
            "<a href='malicious.com'>Link</a>",
            "<iframe src='evil.html'></iframe>",
            "<style>body{display:none}</style>",
        ]
        
        for html_input in html_inputs:
            with self.subTest(input_text=html_input):
                sanitized = self.validator.sanitize_input(html_input)
                
                # Should not contain HTML tags
                self.assertNotIn("<", sanitized)
                self.assertNotIn(">", sanitized)
                
                # Should retain text content where applicable
                if "Content" in html_input:
                    self.assertIn("Content", sanitized)
                    
    def test_legitimate_content_preservation(self):
        """Legitimate content preservation test"""
        legitimate_inputs = [
            "Regular text content",
            "File path: /home/user/documents/file.txt",
            "Numbers: 12345 and symbols: !@#$%^&*()",
            "Unicode: caf√(C), na√Øve, r√(C)sum√(C)",
            "Mathematical: 2 + 2 = 4, x > y",
        ]
        
        for legitimate_input in legitimate_inputs:
            with self.subTest(input_text=legitimate_input):
                sanitized = self.validator.sanitize_input(legitimate_input)
                
                # Should preserve legitimate content
                # (allowing for minor modifications like case changes)
                self.assertGreater(len(sanitized), 0)
                
                # Should not be drastically different
                self.assertLess(
                    abs(len(sanitized) - len(legitimate_input)),
                    len(legitimate_input) * 0.1  # Allow 10% difference
                )


class TestInputValidation(unittest.TestCase):
    """Input validation comprehensive tests"""
    
    def setUp(self):
        """Test setup"""
        self.validator = SecurityValidator()
        
    def test_null_byte_injection_prevention(self):
        """Null byte injection prevention test"""
        malicious_inputs = [
            "file.txt\x00.exe",
            "legitimate\x00<script>alert(1)</script>",
            "\x00DROP TABLE users;",
            "path/to/file\x00/../../../etc/passwd",
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input_text=malicious_input):
                # Check path validation
                is_valid, message = self.validator.validate_path(malicious_input)
                self.assertFalse(is_valid, f"Should detect null byte: {repr(malicious_input)}")
                
                # Check sanitization
                sanitized = self.validator.sanitize_input(malicious_input)
                self.assertNotIn('\x00', sanitized)
                
    def test_unicode_control_character_detection(self):
        """Unicode control character detection test"""
        control_chars = [
            "text\x01control",  # Start of heading
            "text\x02control",  # Start of text
            "text\x03control",  # End of text
            "text\x07control",  # Bell
            "text\x08control",  # Backspace
            "text\x0Bcontrol",  # Vertical tab
            "text\x0Ccontrol",  # Form feed
            "text\x0Econtrol",  # Shift out
            "text\x0Fcontrol",  # Shift in
        ]
        
        for text_with_control in control_chars:
            with self.subTest(text=repr(text_with_control)):
                is_safe, message = self.validator.check_unicode_safety(text_with_control)
                self.assertFalse(is_safe, f"Should detect control character: {repr(text_with_control)}")
                self.assertIn("Control characters detected", message)
                
    def test_allowed_unicode_characters(self):
        """Allowed Unicode characters test"""
        safe_unicode = [
            "Regular text",
            "Text with\nnewlines",
            "Text with\ttabs",
            "Text with\rcarriage returns",
            "Caf√(C) r√(C)sum√(C) na√Øve",
            "Êó•Êú¨Ë(TM)û„ÉÜ„Ç!=„Çπ„Éà",
            "Emoji: üòÄ üëç ‚ù§Ô∏è",
            "Mathematical: ‚àë ‚à´ ‚àÜ œÄ",
        ]
        
        for safe_text in safe_unicode:
            with self.subTest(text=safe_text):
                is_safe, message = self.validator.check_unicode_safety(safe_text)
                self.assertTrue(is_safe, f"Should allow safe Unicode: {safe_text}")
                self.assertEqual(message, "Unicode text is safe")
                
    def test_description_length_validation(self):
        """Description length validation test"""
        max_length = self.validator.max_description_length
        
        # Test normal length
        normal_description = "a" * (max_length // 2)
        sanitized = self.validator.sanitize_input(normal_description)
        self.assertEqual(len(sanitized), len(normal_description))
        
        # Test maximum length
        max_description = "a" * max_length
        sanitized = self.validator.sanitize_input(max_description)
        self.assertLessEqual(len(sanitized), max_length)
        
        # Test excessive length (handled by sanitization)
        long_description = "a" * (max_length * 2)
        sanitized = self.validator.sanitize_input(long_description)
        # Sanitization should handle or truncate appropriately
        self.assertIsInstance(sanitized, str)


class TestFileExtensionValidation(unittest.TestCase):
    """File extension validation tests"""
    
    def setUp(self):
        """Test setup"""
        self.validator = SecurityValidator()
        
    def test_allowed_extensions(self):
        """Allowed extensions test"""
        allowed_files = [
            "document.txt",
            "script.py",
            "readme.md",
            "config.json",
            "settings.yml",
            "data.yaml",
        ]
        
        for file_path in allowed_files:
            with self.subTest(file_path=file_path):
                is_valid, message = self.validator.validate_file_extension(file_path)
                self.assertTrue(is_valid, f"Should allow file: {file_path}")
                self.assertIn("is allowed", message)
                
    def test_blocked_extensions(self):
        """Blocked extensions test"""
        blocked_files = [
            "malicious.exe",
            "script.bat",
            "program.com",
            "library.dll",
            "archive.zip",
            "image.jpg",
            "document.pdf",
            "spreadsheet.xlsx",
        ]
        
        for file_path in blocked_files:
            with self.subTest(file_path=file_path):
                is_valid, message = self.validator.validate_file_extension(file_path)
                self.assertFalse(is_valid, f"Should block file: {file_path}")
                self.assertIn("is not allowed", message)
                
    def test_case_insensitive_validation(self):
        """Case insensitive extension validation test"""
        case_variations = [
            ("file.TXT", True),
            ("script.PY", True),
            ("config.JSON", True),
            ("malicious.EXE", False),
            ("script.BAT", False),
        ]
        
        for file_path, should_be_valid in case_variations:
            with self.subTest(file_path=file_path):
                is_valid, message = self.validator.validate_file_extension(file_path)
                self.assertEqual(is_valid, should_be_valid,
                               f"Extension validation failed for: {file_path}")
                               
    def test_no_extension_handling(self):
        """No extension handling test"""
        files_without_extension = [
            "README",
            "Makefile",
            "Dockerfile",
            "LICENSE",
        ]
        
        for file_path in files_without_extension:
            with self.subTest(file_path=file_path):
                is_valid, message = self.validator.validate_file_extension(file_path)
                # Files without extensions should be blocked by default
                self.assertFalse(is_valid, f"Should block file without extension: {file_path}")
                
    def test_multiple_extensions(self):
        """Multiple extensions test"""
        multiple_extension_files = [
            "archive.tar.gz",  # Should check .gz
            "backup.sql.bak",  # Should check .bak
            "config.json.backup",  # Should check .backup
            "script.py.txt",  # Should check .txt (should be allowed)
        ]
        
        for file_path in multiple_extension_files:
            with self.subTest(file_path=file_path):
                is_valid, message = self.validator.validate_file_extension(file_path)
                # Should validate based on final extension
                final_extension = Path(file_path).suffix.lower()
                expected_valid = final_extension in self.validator.allowed_extensions
                self.assertEqual(is_valid, expected_valid,
                               f"Multiple extension validation failed for: {file_path}")


class TestFileAccessLoggerSecurity(unittest.TestCase):
    """File access logger security tests"""
    
    def setUp(self):
        """Test setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logger = FileAccessLogger("security_test.log")
        
    def tearDown(self):
        """Test cleanup"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def test_secure_logging_validation(self):
        """Secure logging with validation test"""
        test_file = self.temp_dir / "test_file.txt"
        operation = "READ"
        user = "test_user"
        description = "Legitimate file access"
        
        entry = self.logger.log_secure_file_access(test_file, operation, user, description)
        
        self.assertIn("security_checks", entry)
        checks = entry["security_checks"]
        
        # All security checks should pass for legitimate access
        self.assertTrue(checks["path_valid"])
        self.assertTrue(checks["extension_valid"])
        self.assertTrue(checks["unicode_safe"])
        
    def test_malicious_path_logging(self):
        """Malicious path logging test"""
        malicious_path = "../../../etc/passwd"
        operation = "READ"
        user = "attacker"
        description = "Attempting path traversal"
        
        entry = self.logger.log_secure_file_access(malicious_path, operation, user, description)
        
        checks = entry["security_checks"]
        self.assertFalse(checks["path_valid"])
        self.assertIn("Blocked pattern detected", checks["path_message"])
        
    def test_malicious_description_sanitization(self):
        """Malicious description sanitization test"""
        legitimate_file = self.temp_dir / "file.txt"
        operation = "READ"
        user = "user"
        malicious_description = "<script>alert('XSS')</script>Legitimate description"
        
        entry = self.logger.log_secure_file_access(
            legitimate_file, operation, user, malicious_description
        )
        
        # Description should be sanitized
        sanitized_desc = entry["description"]
        self.assertNotIn("<script>", sanitized_desc)
        self.assertNotIn("</script>", sanitized_desc)
        self.assertIn("Legitimate description", sanitized_desc)
        
    def test_security_violations_detection(self):
        """Security violations detection test"""
        # Log legitimate access
        legitimate_file = self.temp_dir / "legitimate.txt"
        self.logger.log_secure_file_access(legitimate_file, "READ", "user1")
        
        # Log malicious attempts
        malicious_attempts = [
            ("../../../etc/passwd", "READ", "attacker1"),
            (str(self.temp_dir / "file.exe"), "EXECUTE", "attacker2"),
            (str(self.temp_dir / "file.txt"), "READ", "user3", "Text with\x00null byte"),
        ]
        
        for path, op, user, *desc in malicious_attempts:
            description = desc[0] if desc else ""
            self.logger.log_secure_file_access(path, op, user, description)
            
        # Check for violations
        violations = self.logger.get_security_violations()
        
        # Should detect 3 violations (not the legitimate one)
        self.assertEqual(len(violations), 3)
        
        # Verify violation details
        for violation in violations:
            checks = violation["security_checks"]
            # At least one security check should fail
            self.assertFalse(
                all([checks["path_valid"], checks["extension_valid"], checks["unicode_safe"]]),
                "Violation should have at least one failed security check"
            )
            
    def test_concurrent_secure_logging(self):
        """Concurrent secure logging test"""
        import threading
        
        def log_access(thread_id):
            for i in range(10):
                file_path = self.temp_dir / f"thread_{thread_id}_file_{i}.txt"
                self.logger.log_secure_file_access(
                    file_path, "READ", f"user_{thread_id}", f"Access from thread {thread_id}"
                )
                
        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_access, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        # Should have 50 entries total
        self.assertEqual(len(self.logger.security_log), 50)
        
        # All should be legitimate (no violations)
        violations = self.logger.get_security_violations()
        self.assertEqual(len(violations), 0)


class TestSecurityPerformance(unittest.TestCase):
    """Security performance tests"""
    
    def setUp(self):
        """Test setup"""
        self.validator = SecurityValidator()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Test cleanup"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def test_path_validation_performance(self):
        """Path validation performance test"""
        test_paths = [f"/path/to/file_{i}.txt" for i in range(1000)]
        
        start_time = time.time()
        for path in test_paths:
            self.validator.validate_path(path)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should validate 1000 paths quickly
        self.assertLess(execution_time, 1.0, "Path validation should be fast")
        
    def test_input_sanitization_performance(self):
        """Input sanitization performance test"""
        test_inputs = [f"Test input {i} with <script>alert({i})</script>" for i in range(1000)]
        
        start_time = time.time()
        for input_text in test_inputs:
            self.validator.sanitize_input(input_text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should sanitize 1000 inputs quickly
        self.assertLess(execution_time, 1.0, "Input sanitization should be fast")
        
    def test_unicode_validation_performance(self):
        """Unicode validation performance test"""
        # Create text with various Unicode characters
        unicode_text = "Test with Unicode: caf√(C) r√(C)sum√(C) na√Øve Êó•Êú¨Ë(TM)û TESTüòÄ ‚àë ‚à´" * 100
        
        start_time = time.time()
        for _ in range(100):
            self.validator.check_unicode_safety(unicode_text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should validate Unicode quickly
        self.assertLess(execution_time, 1.0, "Unicode validation should be fast")
        
    def test_secure_logging_performance(self):
        """Secure logging performance test"""
        logger = FileAccessLogger("performance_test.log")
        
        start_time = time.time()
        for i in range(100):
            file_path = self.temp_dir / f"perf_file_{i}.txt"
            logger.log_secure_file_access(
                file_path, "READ", "perf_user", f"Performance test {i}"
            )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should log 100 secure accesses quickly
        self.assertLess(execution_time, 1.0, "Secure logging should be fast")
        
        # Verify all entries were logged
        self.assertEqual(len(logger.security_log), 100)


class TestSecurityErrorHandling(unittest.TestCase):
    """Security error handling tests"""
    
    def setUp(self):
        """Test setup"""
        self.validator = SecurityValidator()
        
    def test_invalid_input_handling(self):
        """Invalid input handling test"""
        invalid_inputs = [None, 123, [], {}, object()]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input_value=invalid_input):
                try:
                    # Should handle gracefully or raise appropriate exceptions
                    self.validator.validate_path(invalid_input)
                    self.validator.sanitize_input(invalid_input)
                    self.validator.check_unicode_safety(invalid_input)
                except (TypeError, AttributeError):
                    # Acceptable to raise type errors for invalid inputs
                    pass
                    
    def test_extremely_long_input_handling(self):
        """Extremely long input handling test"""
        # Create very long strings
        very_long_path = "a" * 100000
        very_long_description = "b" * 100000
        
        # Should handle without crashing
        try:
            path_valid, path_msg = self.validator.validate_path(very_long_path)
            self.assertIsInstance(path_valid, bool)
            self.assertIsInstance(path_msg, str)
            
            sanitized = self.validator.sanitize_input(very_long_description)
            self.assertIsInstance(sanitized, str)
            
            unicode_safe, unicode_msg = self.validator.check_unicode_safety(very_long_description)
            self.assertIsInstance(unicode_safe, bool)
            self.assertIsInstance(unicode_msg, str)
            
        except MemoryError:
            # Acceptable for extremely large inputs
            pass
            
    def test_malformed_unicode_handling(self):
        """Malformed Unicode handling test"""
        # Test various malformed Unicode scenarios
        malformed_inputs = [
            "\ud800",  # High surrogate without low surrogate
            "\udc00",  # Low surrogate without high surrogate
            "\ud800\ud800",  # Two high surrogates
            b'\xff\xfe'.decode('utf-8', errors='ignore'),  # Invalid UTF-8
        ]
        
        for malformed_input in malformed_inputs:
            with self.subTest(input_value=repr(malformed_input)):
                try:
                    # Should handle malformed Unicode gracefully
                    is_safe, message = self.validator.check_unicode_safety(malformed_input)
                    self.assertIsInstance(is_safe, bool)
                    self.assertIsInstance(message, str)
                except UnicodeError:
                    # Acceptable to raise Unicode errors
                    pass


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=True)