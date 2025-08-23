#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test File Cleanup Script
Remove duplicate original test files after successful consolidation
"""

import os
from pathlib import Path

# Files to keep (our consolidated tests and this script)
KEEP_FILES = {
    "test_core.py",
    "test_integration.py", 
    "test_workflow.py",
    "test_utilities.py",
    "test_emoji.py",
    "test_logging.py",
    "test_security.py",
    "test_performance.py",
    "run_consolidated_tests.py",
    "cleanup_old_tests.py"
}

def identify_old_test_files():
    """Identify original test files that should be removed"""
    current_dir = Path(__file__).parent
    all_test_files = list(current_dir.glob("test_*.py"))
    
    # Filter out files we want to keep
    old_files = [f for f in all_test_files if f.name not in KEEP_FILES]
    
    return sorted(old_files)

def remove_old_test_files(dry_run=True):
    """Remove old test files (or show what would be removed if dry_run=True)"""
    old_files = identify_old_test_files()
    
    print("=" * 80)
    print("TEST FILE CLEANUP OPERATION")
    print("=" * 80)
    
    if dry_run:
        print("DRY RUN MODE - No files will be deleted")
        print()
        print(f"Found {len(old_files)} old test files that would be removed:")
    else:
        print(f"REMOVING {len(old_files)} old test files:")
        print()
    
    removed_count = 0
    error_count = 0
    
    for old_file in old_files:
        try:
            if dry_run:
                print(f"  [WOULD REMOVE] {old_file.name}")
            else:
                old_file.unlink()
                print(f"  [REMOVED] {old_file.name}")
                removed_count += 1
        except Exception as e:
            print(f"  [ERROR] {old_file.name} - {e}")
            error_count += 1
    
    print()
    print("=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    
    if dry_run:
        print(f"Files that would be removed: {len(old_files)}")
        print("To actually remove files, run: python cleanup_old_tests.py --remove")
    else:
        print(f"Successfully removed: {removed_count}")
        print(f"Errors: {error_count}")
        print(f"Files kept (consolidated + scripts): {len(KEEP_FILES)}")
        
        # Verify final state
        remaining_test_files = list(Path(__file__).parent.glob("test_*.py"))
        kept_files = [f for f in remaining_test_files if f.name in KEEP_FILES]
        
        print()
        print("FINAL TEST FILE STRUCTURE:")
        for kept_file in sorted(kept_files):
            print(f"  ✓ {kept_file.name}")
            
        print()
        print(f"🎉 CONSOLIDATION COMPLETE: {len(old_files) + len(KEEP_FILES)} → {len(KEEP_FILES)} files")
        efficiency_gain = ((len(old_files)) / (len(old_files) + len(KEEP_FILES))) * 100
        print(f"📈 EFFICIENCY GAIN: {efficiency_gain:.1f}% reduction in test files")

def main():
    """Main cleanup function"""
    import sys
    
    # Check if we should actually remove files
    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        print("🚨 ACTUAL FILE REMOVAL MODE")
        response = input("Are you sure you want to remove old test files? (yes/no): ")
        if response.lower() == 'yes':
            remove_old_test_files(dry_run=False)
        else:
            print("Operation cancelled.")
    else:
        remove_old_test_files(dry_run=True)

if __name__ == "__main__":
    main()