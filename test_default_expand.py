#!/usr/bin/env python3
"""
Test script to verify that directories with multiple children are expanded by default
"""
import os
import sys
import json

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from docker_jar_diff.html_generator import HTMLGenerator
from docker_jar_diff.cache_manager import CacheManager


def test_default_expand():
    """
    Test that directories with multiple children are expanded by default in the HTML report
    """
    try:
        print("Testing default expansion of directories with multiple children...")
        
        # Create a diff result with a directory structure that has multiple levels
        diff_result = {
            "image1_name": "test:1.0",
            "image2_name": "test:2.0",
            "dir1": "/tmp/image1",
            "dir2": "/tmp/image2",
            "compare_dir": "/",
            "differences": [
                # Top-level directory with multiple children
                {
                    "path": "/parent",
                    "type": "directory",
                    "item1": {"path": "/tmp/image1/parent", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True},
                    "item2": {"path": "/tmp/image2/parent", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True}
                },
                # First child of parent directory
                {
                    "path": "/parent/child1",
                    "type": "directory",
                    "item1": {"path": "/tmp/image1/parent/child1", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True},
                    "item2": {"path": "/tmp/image2/parent/child1", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True}
                },
                # Second child of parent directory (makes parent have multiple children)
                {
                    "path": "/parent/child2",
                    "type": "directory",
                    "item1": {"path": "/tmp/image1/parent/child2", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True},
                    "item2": {"path": "/tmp/image2/parent/child2", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True}
                },
                # Third child of parent directory
                {
                    "path": "/parent/child3",
                    "type": "file",
                    "item1": {"path": "/tmp/image1/parent/child3.txt", "size": 10, "mtime": "2023-01-01T00:00:00", "is_dir": False, "md5": "test123"},
                    "item2": {"path": "/tmp/image2/parent/child3.txt", "size": 15, "mtime": "2023-01-01T00:00:00", "is_dir": False, "md5": "test456"}
                },
                # Directory with only one child (should remain collapsed)
                {
                    "path": "/single-child",
                    "type": "directory",
                    "item1": {"path": "/tmp/image1/single-child", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True},
                    "item2": {"path": "/tmp/image2/single-child", "size": 0, "mtime": "2023-01-01T00:00:00", "is_dir": True}
                },
                # Only child of single-child directory
                {
                    "path": "/single-child/only-child",
                    "type": "file",
                    "item1": {"path": "/tmp/image1/single-child/only-child.txt", "size": 5, "mtime": "2023-01-01T00:00:00", "is_dir": False, "md5": "test789"},
                    "item2": {"path": "/tmp/image2/single-child/only-child.txt", "size": 5, "mtime": "2023-01-01T00:00:00", "is_dir": False, "md5": "test789"}
                }
            ]
        }
        
        # Generate the HTML report
        cache_manager = CacheManager()
        html_generator = HTMLGenerator(cache_manager)
        report_path = html_generator.generate_report(diff_result)
        
        print(f"Generated test report at: {report_path}")
        
        # Verify the report file exists
        if not os.path.exists(report_path):
            print("❌ Report file was not generated")
            return False
        
        # Read the generated HTML content
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check if the directory expansion logic is correctly implemented
        # We'll look for the key components of the default expansion functionality
        
        # Check for child count calculation
        child_count_calc = 'childCount' in html_content and 'Object.keys' in html_content
        
        # Check for expansion condition
        expansion_condition = 'childCount > 1' in html_content and 'style.display' in html_content
        
        # Check for icon update
        icon_update = 'expandIcon' in html_content and 'expanded' in html_content and '▼' in html_content
        
        if child_count_calc and expansion_condition and icon_update:
            print("✅ Directory expansion logic is correctly implemented")
            return True
        else:
            print("❌ Directory expansion logic is not correctly implemented")
            print(f"   Child count calculation: {child_count_calc}")
            print(f"   Expansion condition: {expansion_condition}")
            print(f"   Icon update: {icon_update}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_default_expand()
    if success:
        print("\n🎉 All tests passed! Default expansion functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Default expansion functionality is not working correctly.")
        sys.exit(1)
