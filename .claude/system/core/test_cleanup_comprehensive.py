#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for cleanup.py module - Target: 100% coverage
TDD Test Engineer - Comprehensive Test Suite for Cleanup System

This test file provides complete coverage for:
- UnifiedCleanupManager class (all methods)
- BackupInfo dataclass
- Module-level cleaner instance
- All error conditions and edge cases
- All branches and conditional logic
"""

import os
import json
import shutil
import zipfile
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from dataclasses import asdict
import pytest

# Test target imports
import sys
sys.path.append('.')

try:
    from cleanup import UnifiedCleanupManager, BackupInfo, cleaner
except ImportError:
    pytest.fail("Target module cleanup.py not found - TDD RED phase confirmed")


class TestBackupInfo:
    """Test BackupInfo dataclass - ensuring complete coverage"""
    
    def test_backup_info_creation(self):
        """Test BackupInfo dataclass instantiation"""
        backup_info = BackupInfo(
            timestamp="2024-08-24 12:00:00",
            backup_type="manual",
            file_path="/path/to/backup.zip",
            size_mb=15.5,
            description="Test backup"
        )
        
        assert backup_info.timestamp == "2024-08-24 12:00:00"
        assert backup_info.backup_type == "manual"
        assert backup_info.file_path == "/path/to/backup.zip"
        assert backup_info.size_mb == 15.5
        assert backup_info.description == "Test backup"
    
    def test_backup_info_asdict(self):
        """Test BackupInfo conversion to dict"""
        backup_info = BackupInfo(
            timestamp="2024-08-24 12:00:00",
            backup_type="error",
            file_path="/backup.zip",
            size_mb=10.0,
            description="Error backup"
        )
        
        backup_dict = asdict(backup_info)
        expected = {
            'timestamp': "2024-08-24 12:00:00",
            'backup_type': "error", 
            'file_path': "/backup.zip",
            'size_mb': 10.0,
            'description': "Error backup"
        }
        
        assert backup_dict == expected
    
    def test_backup_info_equality(self):
        """Test BackupInfo equality comparison"""
        backup1 = BackupInfo("2024-08-24", "manual", "/path.zip", 10.0, "desc")
        backup2 = BackupInfo("2024-08-24", "manual", "/path.zip", 10.0, "desc")
        backup3 = BackupInfo("2024-08-25", "auto", "/other.zip", 5.0, "other")
        
        assert backup1 == backup2
        assert backup1 != backup3


class TestUnifiedCleanupManager:
    """Comprehensive tests for UnifiedCleanupManager class - 100% coverage target"""
    
    def setup_method(self):
        """Setup test environment for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cleanup_manager = UnifiedCleanupManager()
        
        # Override paths to use temp directory
        self.cleanup_manager.base_path = self.temp_dir
        self.cleanup_manager.backup_dir = self.temp_dir / "backups"
        self.cleanup_manager.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up after each test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test UnifiedCleanupManager initialization"""
        manager = UnifiedCleanupManager()
        
        assert hasattr(manager, 'base_path')
        assert manager.temp_extensions == ['.tmp', '.bak', '.log~', '.swp']
        assert manager.temp_dirs == ['__pycache__', '.pytest_cache', 'node_modules']
        assert manager.max_backup_age_days == 7
        assert manager.max_backup_count == 5
        
        # Backup directory should be created
        assert manager.backup_dir.exists()
    
    @patch('cleanup.logger')
    def test_cleanup_project_success(self, mock_logger):
        """Test successful project cleanup"""
        # Create test files to be deleted
        temp_file1 = self.temp_dir / "test.tmp"
        temp_file2 = self.temp_dir / "test.bak"
        temp_file1.write_text("temp content")
        temp_file2.write_text("backup content")
        
        # Create test directories to be deleted
        pycache_dir = self.temp_dir / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "test.pyc").write_bytes(b"compiled")
        
        # Mock _get_folder_size to avoid logs directory issues
        with patch.object(self.cleanup_manager, '_get_folder_size', return_value=0):
            with patch.object(self.cleanup_manager, '_cleanup_old_logs'):
                with patch.object(self.cleanup_manager, '_cleanup_old_cache'):
                    with patch.object(self.cleanup_manager, '_cleanup_old_backups'):
                        result = self.cleanup_manager.cleanup_project()
        
        # Verify results structure
        assert "deleted_files" in result
        assert "deleted_dirs" in result
        assert "errors" in result
        assert "space_freed_mb" in result
        
        # Files should be deleted
        assert not temp_file1.exists()
        assert not temp_file2.exists()
        assert not pycache_dir.exists()
        
        # Should have logged success
        mock_logger.info.assert_called()
    
    @patch('cleanup.logger')
    def test_cleanup_project_with_file_errors(self, mock_logger):
        """Test project cleanup with file deletion errors"""
        # Create a file that we'll mock to cause deletion errors
        temp_file = self.temp_dir / "test.tmp"
        temp_file.write_text("content")
        
        with patch.object(self.cleanup_manager, '_get_folder_size', return_value=0):
            with patch.object(self.cleanup_manager, '_cleanup_old_logs'):
                with patch.object(self.cleanup_manager, '_cleanup_old_cache'):
                    with patch.object(self.cleanup_manager, '_cleanup_old_backups'):
                        # Mock unlink to raise permission error
                        with patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
                            result = self.cleanup_manager.cleanup_project()
        
        # Should have recorded the error
        assert len(result["errors"]) > 0
        assert "Failed to delete" in result["errors"][0]
        assert "Access denied" in result["errors"][0]
    
    @patch('cleanup.logger')
    def test_cleanup_project_with_directory_errors(self, mock_logger):
        """Test project cleanup with directory deletion errors (lines 78-79)"""
        # Create a directory that we'll mock to cause deletion errors
        pycache_dir = self.temp_dir / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "test.pyc").write_bytes(b"compiled")
        
        with patch.object(self.cleanup_manager, '_get_folder_size', return_value=0):
            with patch.object(self.cleanup_manager, '_cleanup_old_logs'):
                with patch.object(self.cleanup_manager, '_cleanup_old_cache'):
                    with patch.object(self.cleanup_manager, '_cleanup_old_backups'):
                        # Mock rmtree to raise permission error
                        with patch('shutil.rmtree', side_effect=PermissionError("Access denied")):
                            result = self.cleanup_manager.cleanup_project()
        
        # Should have recorded the error
        assert len(result["errors"]) > 0
        assert "Failed to delete" in result["errors"][0]
        assert "__pycache__" in result["errors"][0]
    
    @patch('cleanup.logger')
    def test_cleanup_project_empty_directory_removal(self, mock_logger):
        """Test removal of empty directories during cleanup"""
        # Create nested empty directories
        empty_dir = self.temp_dir / "empty" / "nested" / "dir"
        empty_dir.mkdir(parents=True)
        
        with patch.object(self.cleanup_manager, '_get_folder_size', return_value=0):
            with patch.object(self.cleanup_manager, '_cleanup_old_logs'):
                with patch.object(self.cleanup_manager, '_cleanup_old_cache'):
                    with patch.object(self.cleanup_manager, '_cleanup_old_backups'):
                        result = self.cleanup_manager.cleanup_project()
        
        # Empty directories should be removed
        assert not empty_dir.exists()
        assert len(result["deleted_dirs"]) > 0
    
    @patch('cleanup.logger')
    def test_cleanup_project_empty_directory_removal_with_error(self, mock_logger):
        """Test empty directory removal with permission errors"""
        # Create an empty directory
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()
        
        with patch.object(self.cleanup_manager, '_get_folder_size', return_value=0):
            with patch.object(self.cleanup_manager, '_cleanup_old_logs'):
                with patch.object(self.cleanup_manager, '_cleanup_old_cache'):
                    with patch.object(self.cleanup_manager, '_cleanup_old_backups'):
                        # Mock rmdir to raise permission error
                        with patch.object(Path, 'rmdir', side_effect=PermissionError("Access denied")):
                            result = self.cleanup_manager.cleanup_project()
        
        # Should handle error gracefully (pass statement in except block)
        # Directory should still exist due to error
        assert empty_dir.exists()
    
    def test_cleanup_workspace_no_workspace(self):
        """Test workspace cleanup when workspace doesn't exist"""
        result = self.cleanup_manager.cleanup_workspace()
        
        assert result == {"status": "no workspace"}
    
    def test_cleanup_workspace_success(self):
        """Test successful workspace cleanup"""
        # Create workspace with files
        workspace = self.cleanup_manager.base_path / "workspace"
        workspace.mkdir()
        
        test_file1 = workspace / "file1.txt"
        test_file2 = workspace / "file2.py"
        test_file1.write_text("content1")
        test_file2.write_text("content2")
        
        # Create a subdirectory (should not be deleted)
        subdir = workspace / "subdir"
        subdir.mkdir()
        
        result = self.cleanup_manager.cleanup_workspace()
        
        # Files should be deleted
        assert not test_file1.exists()
        assert not test_file2.exists()
        
        # Directory should still exist
        assert subdir.exists()
        
        # Should return list of deleted files
        assert "deleted" in result
        assert len(result["deleted"]) == 2
    
    @patch('cleanup.get_filename_timestamp')
    @patch('cleanup.format_jst_datetime')
    @patch('cleanup.logger')
    def test_create_backup_success(self, mock_logger, mock_format_datetime, mock_get_filename):
        """Test successful backup creation"""
        mock_get_filename.return_value = "2024-08-24_1200"
        mock_format_datetime.return_value = "2024-08-24 12:00:00"
        
        # Create test files to backup
        test_file = self.temp_dir / "test.py"
        test_file.write_text("print('hello')")
        
        # Change working directory to temp dir for relative paths
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            with patch.object(self.cleanup_manager, '_record_backup_info') as mock_record:
                result = self.cleanup_manager.create_backup("manual", "Test backup")
            
            # Should return path to backup
            assert result is not None
            assert result.exists()
            assert result.name == "manual_backup_2024-08-24_1200.zip"
            
            # Backup should contain the test file
            with zipfile.ZipFile(result, 'r') as zf:
                assert 'test.py' in zf.namelist()
            
            # Should record backup info
            mock_record.assert_called_once()
            
        finally:
            os.chdir(original_cwd)
    
    @patch('cleanup.get_filename_timestamp')
    @patch('cleanup.format_jst_datetime')
    @patch('cleanup.logger')
    def test_create_backup_excludes_protected_dirs(self, mock_logger, mock_format_datetime, mock_get_filename):
        """Test backup creation excludes protected directories"""
        mock_get_filename.return_value = "2024-08-24_1200"
        mock_format_datetime.return_value = "2024-08-24 12:00:00"
        
        # Create files in protected directories
        git_dir = self.temp_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config.py").write_text("git config")
        
        node_modules = self.temp_dir / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.py").write_text("package info")
        
        # Create file that should be included
        good_file = self.temp_dir / "good.py"
        good_file.write_text("good content")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            with patch.object(self.cleanup_manager, '_record_backup_info'):
                result = self.cleanup_manager.create_backup()
            
            # Check backup contents
            with zipfile.ZipFile(result, 'r') as zf:
                filenames = zf.namelist()
                
                # Should include good file
                assert 'good.py' in filenames
                
                # Should exclude protected directory files
                assert '.git/config.py' not in filenames
                assert 'node_modules/package.py' not in filenames
        
        finally:
            os.chdir(original_cwd)
    
    @patch('cleanup.get_filename_timestamp')
    @patch('cleanup.logger')
    def test_create_backup_file_error(self, mock_logger, mock_get_filename):
        """Test backup creation with individual file errors"""
        mock_get_filename.return_value = "2024-08-24_1200"
        
        # Create test file
        test_file = self.temp_dir / "test.py"
        test_file.write_text("test content")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            # Mock zipfile.write to raise an exception for test.py
            original_write = zipfile.ZipFile.write
            def mock_write(self, filename, arcname=None, compress_type=None, compresslevel=None):
                if 'test.py' in str(filename):
                    raise OSError("Simulated file error")
                return original_write(self, filename, arcname, compress_type, compresslevel)
            
            with patch.object(zipfile.ZipFile, 'write', side_effect=mock_write):
                with patch.object(self.cleanup_manager, '_record_backup_info'):
                    result = self.cleanup_manager.create_backup()
            
            # Backup should still be created despite individual file error
            assert result is not None
            assert result.exists()
        
        finally:
            os.chdir(original_cwd)
    
    @patch('cleanup.get_filename_timestamp')
    @patch('cleanup.logger')
    def test_create_backup_zipfile_error(self, mock_logger, mock_get_filename):
        """Test backup creation with ZipFile creation error"""
        mock_get_filename.return_value = "2024-08-24_1200"
        
        # Mock ZipFile to raise exception
        with patch('cleanup.zipfile.ZipFile', side_effect=OSError("Cannot create zip")):
            result = self.cleanup_manager.create_backup()
        
        assert result is None
        mock_logger.error.assert_called_once()
        assert "ERROR:" in mock_logger.error.call_args[0][0]
    
    def test_create_error_backup(self):
        """Test error backup creation"""
        with patch.object(self.cleanup_manager, 'create_backup', return_value=Path("error_backup.zip")) as mock_create:
            result = self.cleanup_manager.create_error_backup("Test error occurred")
        
        mock_create.assert_called_once_with("error", "ERROR: Test error occurred")
        assert result == Path("error_backup.zip")
    
    @patch('cleanup.logger')
    def test_restore_from_backup_success(self, mock_logger):
        """Test successful backup restoration"""
        # Create a test backup file
        backup_path = self.temp_dir / "test_backup.zip"
        test_content = "restored content"
        
        with zipfile.ZipFile(backup_path, 'w') as zf:
            zf.writestr("restored_file.txt", test_content)
        
        # Change to temp directory for extraction
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            result = self.cleanup_manager.restore_from_backup(backup_path)
            
            assert result is True
            
            # File should be restored
            restored_file = self.temp_dir / "restored_file.txt"
            assert restored_file.exists()
            assert restored_file.read_text() == test_content
            
            mock_logger.info.assert_called()
        
        finally:
            os.chdir(original_cwd)
    
    @patch('cleanup.logger')
    def test_restore_from_backup_error(self, mock_logger):
        """Test backup restoration with error"""
        backup_path = self.temp_dir / "nonexistent_backup.zip"
        
        result = self.cleanup_manager.restore_from_backup(backup_path)
        
        assert result is False
        mock_logger.error.assert_called_once()
        assert "ERROR:" in mock_logger.error.call_args[0][0]
    
    @patch('cleanup.format_jst_datetime')
    def test_get_disk_usage_report(self, mock_format_datetime):
        """Test disk usage report generation"""
        mock_format_datetime.return_value = "2024-08-24 12:00:00"
        
        # Create test files with known sizes
        file1 = self.temp_dir / "file1.txt"
        file2 = self.temp_dir / "file2.txt"
        file1.write_text("a" * 1024)  # 1KB
        file2.write_text("b" * 2048)  # 2KB
        
        result = self.cleanup_manager.get_disk_usage_report()
        
        assert "total_size_mb" in result
        assert "file_count" in result
        assert "timestamp" in result
        
        assert result["file_count"] == 2
        assert result["total_size_mb"] == (3072 / (1024 * 1024))  # 3KB in MB
        assert result["timestamp"] == "2024-08-24 12:00:00"
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_logs_no_log_dir(self, mock_logger, mock_jst_now):
        """Test log cleanup when logs directory doesn't exist"""
        # Ensure logs directory doesn't exist
        log_dir = self.cleanup_manager.base_path / "logs"
        if log_dir.exists():
            shutil.rmtree(log_dir)
        
        # Should return early without error
        self.cleanup_manager._cleanup_old_logs()
        
        # Should not have logged anything since no logs directory
        mock_logger.info.assert_not_called()
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_logs_success(self, mock_logger, mock_jst_now):
        """Test successful old log cleanup"""
        mock_jst_now.return_value = datetime.now()
        
        # Create logs directory with old and new files
        log_dir = self.cleanup_manager.base_path / "logs"
        log_dir.mkdir()
        
        old_log = log_dir / "old.log"
        new_log = log_dir / "new.log"
        old_log.write_text("old log content")
        new_log.write_text("new log content")
        
        # Make old log appear old
        old_time = time.time() - (10 * 24 * 3600)  # 10 days ago
        os.utime(old_log, (old_time, old_time))
        
        self.cleanup_manager._cleanup_old_logs()
        
        # Old log should be deleted, new log should remain
        assert not old_log.exists()
        assert new_log.exists()
        
        mock_logger.info.assert_called_once()
        assert "SUCCESS" in mock_logger.info.call_args[0][0]
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_logs_with_unlink_error(self, mock_logger, mock_jst_now):
        """Test log cleanup with file unlink error (lines 217-218)"""
        mock_jst_now.return_value = datetime.now()
        
        log_dir = self.cleanup_manager.base_path / "logs"
        log_dir.mkdir()
        
        old_log = log_dir / "old.log"
        old_log.write_text("old log content")
        
        # Make it appear old
        old_time = time.time() - (10 * 24 * 3600)
        os.utime(old_log, (old_time, old_time))
        
        # Create a mock that returns proper timestamps for stat but fails for unlink
        def mock_unlink_side_effect():
            raise PermissionError("Access denied")
        
        with patch.object(Path, 'unlink', side_effect=mock_unlink_side_effect):
            self.cleanup_manager._cleanup_old_logs()
        
        # Should handle error gracefully (pass statement in except block lines 217-218)
        # File should still exist due to unlink error
        assert old_log.exists()
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_cache_no_cache_dir(self, mock_logger, mock_jst_now):
        """Test cache cleanup when cache directory doesn't exist"""
        # Should return early without error
        self.cleanup_manager._cleanup_old_cache()
        
        mock_logger.info.assert_not_called()
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_cache_success(self, mock_logger, mock_jst_now):
        """Test successful old cache cleanup"""
        mock_jst_now.return_value = datetime.now()
        
        # Create cache directory with old and new files
        cache_dir = self.cleanup_manager.base_path / "cache"
        cache_dir.mkdir()
        
        old_cache = cache_dir / "old.pkl"
        new_cache = cache_dir / "new.pkl"
        old_cache.write_bytes(b"old cache data")
        new_cache.write_bytes(b"new cache data")
        
        # Make old cache appear old
        old_time = time.time() - (10 * 24 * 3600)  # 10 days ago
        os.utime(old_cache, (old_time, old_time))
        
        self.cleanup_manager._cleanup_old_cache()
        
        # Old cache should be deleted, new cache should remain
        assert not old_cache.exists()
        assert new_cache.exists()
        
        mock_logger.info.assert_called_once()
        assert "SUCCESS" in mock_logger.info.call_args[0][0]
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_cache_with_error(self, mock_logger, mock_jst_now):
        """Test cache cleanup with file access error"""
        mock_jst_now.return_value = datetime.now()
        
        cache_dir = self.cleanup_manager.base_path / "cache"
        cache_dir.mkdir()
        
        old_cache = cache_dir / "old.pkl"
        old_cache.write_bytes(b"old cache data")
        
        old_time = time.time() - (10 * 24 * 3600)
        os.utime(old_cache, (old_time, old_time))
        
        # Mock unlink to raise exception
        with patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
            self.cleanup_manager._cleanup_old_cache()
        
        # Should handle error gracefully
        assert old_cache.exists()
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_backups_by_age(self, mock_logger, mock_jst_now):
        """Test cleanup of old backups by age"""
        mock_jst_now.return_value = datetime.now()
        
        # Create old and new backup files
        old_backup = self.cleanup_manager.backup_dir / "old_backup.zip"
        new_backup = self.cleanup_manager.backup_dir / "new_backup.zip"
        old_backup.write_bytes(b"old backup data")
        new_backup.write_bytes(b"new backup data")
        
        # Make old backup appear old (beyond max_backup_age_days)
        old_time = time.time() - (10 * 24 * 3600)  # 10 days ago
        os.utime(old_backup, (old_time, old_time))
        
        self.cleanup_manager._cleanup_old_backups()
        
        # Old backup should be deleted, new backup should remain
        assert not old_backup.exists()
        assert new_backup.exists()
        
        mock_logger.info.assert_called()
        assert "SUCCESS:" in mock_logger.info.call_args[0][0]
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_backups_by_count(self, mock_logger, mock_jst_now):
        """Test cleanup of old backups by count limit"""
        # Mock to return a time that won't trigger age-based deletion
        mock_jst_now.return_value = datetime.now()
        
        # Create more backups than max_backup_count (5) - all recent so no age deletion
        backup_names = [f"backup_{i}.zip" for i in range(7)]
        backup_paths = []
        
        current_time = time.time()
        for i, name in enumerate(backup_names):
            backup_path = self.cleanup_manager.backup_dir / name
            backup_path.write_bytes(b"backup data")
            backup_paths.append(backup_path)
            
            # Set different modification times (newest first in the list)
            # Index 0 = newest, index 6 = oldest
            file_time = current_time - (i * 3600)  # Each backup 1 hour older
            os.utime(backup_path, (file_time, file_time))
        
        self.cleanup_manager._cleanup_old_backups()
        
        # Should keep only the newest 5 backups
        remaining_backups = list(self.cleanup_manager.backup_dir.glob("*.zip"))
        assert len(remaining_backups) == 5
        
        # Oldest 2 should be deleted (highest indices)
        assert backup_paths[0].exists()      # Newest (should remain)
        assert backup_paths[1].exists()      # Second newest (should remain)
        assert backup_paths[2].exists()      # Third newest (should remain)
        assert backup_paths[3].exists()      # Fourth newest (should remain) 
        assert backup_paths[4].exists()      # Fifth newest (should remain)
        assert not backup_paths[5].exists()  # Sixth newest (should be deleted)
        assert not backup_paths[6].exists()  # Oldest (should be deleted)
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger')
    def test_cleanup_old_backups_with_unlink_errors(self, mock_logger, mock_jst_now):
        """Test backup cleanup with file unlink errors (lines 266-267)"""
        mock_jst_now.return_value = datetime.now()
        
        old_backup = self.cleanup_manager.backup_dir / "old_backup.zip"
        old_backup.write_bytes(b"old backup")
        
        old_time = time.time() - (10 * 24 * 3600)
        os.utime(old_backup, (old_time, old_time))
        
        # Mock unlink to raise exception
        with patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
            self.cleanup_manager._cleanup_old_backups()
        
        # Should handle error gracefully (lines 266-267 pass statement)
        assert old_backup.exists()
    
    @patch('cleanup.get_jst_now')
    @patch('cleanup.logger') 
    def test_cleanup_old_backups_count_limit_with_unlink_error(self, mock_logger, mock_jst_now):
        """Test backup cleanup by count with unlink error (lines 266-267)"""
        mock_jst_now.return_value = datetime.now()
        
        # Create more backups than max_backup_count, all recent (no age deletion)
        backup_paths = []
        current_time = time.time()
        
        for i in range(7):  # More than max_backup_count (5)
            backup_path = self.cleanup_manager.backup_dir / f"recent_backup_{i}.zip"
            backup_path.write_bytes(b"backup data")
            backup_paths.append(backup_path)
            
            # All are recent - within max_backup_age_days
            file_time = current_time - (i * 60)  # Just minutes apart, not days
            os.utime(backup_path, (file_time, file_time))
        
        # Mock unlink to raise exception for old backups during count cleanup
        def unlink_side_effect(self):
            if "recent_backup_5.zip" in str(self) or "recent_backup_6.zip" in str(self):
                raise PermissionError("Access denied")
        
        with patch.object(Path, 'unlink', side_effect=unlink_side_effect):
            self.cleanup_manager._cleanup_old_backups()
        
        # All files should still exist due to unlink errors
        for backup_path in backup_paths:
            assert backup_path.exists()
    
    def test_get_folder_size_existing_folder(self):
        """Test folder size calculation for existing folder"""
        # Create test folder with files
        test_folder = self.temp_dir / "test_folder"
        test_folder.mkdir()
        
        file1 = test_folder / "file1.txt"
        file2 = test_folder / "file2.txt"
        file1.write_text("a" * 1000)  # 1000 bytes
        file2.write_text("b" * 2000)  # 2000 bytes
        
        size = self.cleanup_manager._get_folder_size(test_folder)
        
        assert size == 3000  # Total size in bytes
    
    def test_get_folder_size_nonexistent_folder(self):
        """Test folder size calculation for non-existent folder"""
        nonexistent = self.temp_dir / "nonexistent"
        
        size = self.cleanup_manager._get_folder_size(nonexistent)
        
        assert size == 0
    
    def test_get_folder_size_with_file_stat_error(self):
        """Test folder size calculation with file stat error (lines 277-278)"""
        # Create a custom path class that we can mock
        test_folder = self.temp_dir / "test_folder"
        test_folder.mkdir()
        
        # Create real files first
        file1 = test_folder / "file1.txt"
        file2 = test_folder / "file2.txt" 
        file1.write_text("good content")
        file2.write_text("error content")
        
        expected_size = file1.stat().st_size
        
        # Mock the entire Path constructor to return our controlled objects when rglob is called
        with patch('cleanup.Path') as MockPath:
            # Configure the mock to behave like the real folder for exists() check
            mock_folder = MockPath.return_value
            mock_folder.exists.return_value = True
            
            # Create mock entries for rglob
            mock_entry1 = Mock(spec=Path)
            mock_entry1.is_file.return_value = True
            mock_entry1.stat.return_value.st_size = expected_size
            
            mock_entry2 = Mock(spec=Path)
            mock_entry2.is_file.return_value = True
            mock_entry2.stat.side_effect = OSError("Access denied")  # This will trigger lines 277-278
            
            mock_folder.rglob.return_value = [mock_entry1, mock_entry2]
            
            # Call with the mock folder directly
            size = self.cleanup_manager._get_folder_size(mock_folder)
        
        # Should only count the first entry, second entry error is handled gracefully
        assert size == expected_size
    
    def test_record_backup_info_new_file(self):
        """Test recording backup info when info file doesn't exist"""
        backup_info = BackupInfo(
            timestamp="2024-08-24 12:00:00",
            backup_type="manual",
            file_path="/path/backup.zip",
            size_mb=10.5,
            description="Test backup"
        )
        
        self.cleanup_manager._record_backup_info(backup_info)
        
        info_file = self.cleanup_manager.backup_dir / "backup_info.json"
        assert info_file.exists()
        
        with open(info_file, 'r', encoding='utf-8') as f:
            infos = json.load(f)
        
        assert len(infos) == 1
        assert infos[0]['timestamp'] == "2024-08-24 12:00:00"
        assert infos[0]['backup_type'] == "manual"
        assert infos[0]['size_mb'] == 10.5
    
    def test_record_backup_info_existing_file(self):
        """Test recording backup info when info file exists"""
        info_file = self.cleanup_manager.backup_dir / "backup_info.json"
        
        # Create existing info
        existing_info = [{
            'timestamp': "2024-08-23 10:00:00",
            'backup_type': "auto",
            'file_path': "/old/backup.zip",
            'size_mb': 5.0,
            'description': "Old backup"
        }]
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(existing_info, f)
        
        # Add new backup info
        backup_info = BackupInfo(
            timestamp="2024-08-24 12:00:00",
            backup_type="manual",
            file_path="/new/backup.zip",
            size_mb=15.0,
            description="New backup"
        )
        
        self.cleanup_manager._record_backup_info(backup_info)
        
        with open(info_file, 'r', encoding='utf-8') as f:
            infos = json.load(f)
        
        assert len(infos) == 2
        assert infos[1]['timestamp'] == "2024-08-24 12:00:00"  # New entry
        assert infos[0]['timestamp'] == "2024-08-23 10:00:00"  # Old entry
    
    def test_record_backup_info_limit_entries(self):
        """Test backup info limiting to 20 entries"""
        info_file = self.cleanup_manager.backup_dir / "backup_info.json"
        
        # Create 21 existing entries
        existing_infos = []
        for i in range(21):
            existing_infos.append({
                'timestamp': f"2024-08-{i+1:02d} 10:00:00",
                'backup_type': "auto",
                'file_path': f"/backup_{i}.zip",
                'size_mb': 1.0,
                'description': f"Backup {i}"
            })
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(existing_infos, f)
        
        # Add new backup info
        backup_info = BackupInfo(
            timestamp="2024-08-25 12:00:00",
            backup_type="manual",
            file_path="/new/backup.zip",
            size_mb=5.0,
            description="New backup"
        )
        
        self.cleanup_manager._record_backup_info(backup_info)
        
        with open(info_file, 'r', encoding='utf-8') as f:
            infos = json.load(f)
        
        # Should only keep the last 20 entries
        assert len(infos) == 20
        # Latest entry should be the new one
        assert infos[-1]['timestamp'] == "2024-08-25 12:00:00"
    
    def test_record_backup_info_corrupted_file(self):
        """Test recording backup info with corrupted existing file"""
        info_file = self.cleanup_manager.backup_dir / "backup_info.json"
        
        # Create corrupted JSON file
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("corrupted json content")
        
        backup_info = BackupInfo(
            timestamp="2024-08-24 12:00:00",
            backup_type="manual",
            file_path="/backup.zip",
            size_mb=10.0,
            description="Test backup"
        )
        
        # Should handle corruption gracefully
        self.cleanup_manager._record_backup_info(backup_info)
        
        # Should create new valid JSON with just the new entry
        with open(info_file, 'r', encoding='utf-8') as f:
            infos = json.load(f)
        
        assert len(infos) == 1
        assert infos[0]['timestamp'] == "2024-08-24 12:00:00"


class TestModuleLevelInstance:
    """Test module-level cleaner instance"""
    
    def test_cleaner_instance_available(self):
        """Test that module-level cleaner instance is available"""
        from cleanup import cleaner
        
        assert cleaner is not None
        assert isinstance(cleaner, UnifiedCleanupManager)
        assert hasattr(cleaner, 'cleanup_project')
        assert hasattr(cleaner, 'create_backup')
        assert hasattr(cleaner, 'restore_from_backup')


class TestEdgeCasesAndErrorConditions:
    """Test edge cases and error conditions for complete coverage"""
    
    def test_backup_info_with_zero_size(self):
        """Test BackupInfo with zero size"""
        backup_info = BackupInfo(
            timestamp="2024-08-24",
            backup_type="empty",
            file_path="/empty.zip",
            size_mb=0.0,
            description=""
        )
        
        assert backup_info.size_mb == 0.0
        assert backup_info.description == ""
    
    def test_cleanup_manager_with_all_extensions(self):
        """Test cleanup manager handles all defined temp extensions"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            manager = UnifiedCleanupManager()
            manager.base_path = temp_dir
            
            # Create files with all temp extensions
            extensions = ['.tmp', '.bak', '.log~', '.swp']
            created_files = []
            
            for ext in extensions:
                test_file = temp_dir / f"test{ext}"
                test_file.write_text("temp content")
                created_files.append(test_file)
            
            with patch.object(manager, '_get_folder_size', return_value=0):
                with patch.object(manager, '_cleanup_old_logs'):
                    with patch.object(manager, '_cleanup_old_cache'):
                        with patch.object(manager, '_cleanup_old_backups'):
                            result = manager.cleanup_project()
            
            # All temp files should be deleted
            for file in created_files:
                assert not file.exists()
            
            assert len(result["deleted_files"]) == len(extensions)
        
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def test_cleanup_manager_with_all_temp_dirs(self):
        """Test cleanup manager handles all defined temp directories"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            manager = UnifiedCleanupManager()
            manager.base_path = temp_dir
            
            # Create all temp directories
            temp_dirs = ['__pycache__', '.pytest_cache', 'node_modules']
            created_dirs = []
            
            for dir_name in temp_dirs:
                test_dir = temp_dir / dir_name
                test_dir.mkdir()
                (test_dir / "dummy.txt").write_text("content")
                created_dirs.append(test_dir)
            
            with patch.object(manager, '_get_folder_size', return_value=0):
                with patch.object(manager, '_cleanup_old_logs'):
                    with patch.object(manager, '_cleanup_old_cache'):
                        with patch.object(manager, '_cleanup_old_backups'):
                            result = manager.cleanup_project()
            
            # All temp directories should be deleted
            for dir_path in created_dirs:
                assert not dir_path.exists()
            
            assert len(result["deleted_dirs"]) >= len(temp_dirs)
        
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])