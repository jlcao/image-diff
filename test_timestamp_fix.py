#!/usr/bin/env python3
"""
Test script to verify that file modification times are preserved when extracting JAR/ZIP contents
"""
import os
import sys
import zipfile
import tempfile
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from docker_jar_diff.diff_engine import DiffEngine
from docker_jar_diff.cache_manager import CacheManager


def test_timestamp_preservation():
    """
    Test that file modification times are preserved when extracting JAR/ZIP contents
    """
    try:
        print("Testing file timestamp preservation in JAR/ZIP extraction...")
        
        # Step 1: Create a test file with a specific modification time
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test class file
            test_class_content = "public class TestClass {}"
            test_class_path = os.path.join(temp_dir, "TestClass.class")
            
            with open(test_class_path, 'w') as f:
                f.write(test_class_content)
            
            # Set a specific modification time (2 days ago)
            specific_time = datetime.now() - timedelta(days=2)
            specific_timestamp = specific_time.timestamp()
            os.utime(test_class_path, (specific_timestamp, specific_timestamp))
            
            # Verify the file has the correct timestamp
            file_stat = os.stat(test_class_path)
            actual_time = datetime.fromtimestamp(file_stat.st_mtime)
            print(f"Test file created with modification time: {specific_time}")
            print(f"Actual file modification time: {actual_time}")
            
            # Step 2: Create a ZIP file containing the test class
            zip_path = os.path.join(temp_dir, "test.jar")
            with zipfile.ZipFile(zip_path, 'w') as z:
                z.write(test_class_path, "TestClass.class")
            
            print(f"Created test JAR file: {zip_path}")
            
            # Verify the ZIP file contains the test class with correct timestamp
            with zipfile.ZipFile(zip_path, 'r') as z:
                for info in z.infolist():
                    if info.filename == "TestClass.class":
                        zip_time = datetime(*info.date_time)
                        print(f"ZIP entry modification time: {zip_time}")
                        # ZIP format only stores time with resolution of seconds
                        assert abs((zip_time - specific_time).total_seconds()) < 2, f"ZIP entry time doesn't match: {zip_time} vs {specific_time}"
            
            # Step 3: Use DiffEngine to process the ZIP file
            cache_manager = CacheManager()
            diff_engine = DiffEngine(cache_manager)
            
            # Create a directory with the test JAR
            test_dir = os.path.join(temp_dir, "test_input")
            os.makedirs(test_dir)
            shutil.copy(zip_path, os.path.join(test_dir, "test.jar"))
            
            # Build directory tree
            directory_tree = diff_engine._build_directory_tree(test_dir)
            
            # Verify that the extracted class file has the correct timestamp
            jar_entry = directory_tree.get("test.jar")
            assert jar_entry and jar_entry.get('is_archive'), "JAR entry not found in directory tree"
            
            contents = jar_entry.get('contents')
            assert contents, "JAR contents not found"
            
            class_entry = contents.get("TestClass.class")
            assert class_entry, "TestClass.class not found in JAR contents"
            
            # Get the modification time from the extracted class entry
            extracted_time_str = class_entry.get('mtime')
            assert extracted_time_str, "mtime not found in class entry"
            
            extracted_time = datetime.fromisoformat(extracted_time_str)
            print(f"Extracted class modification time: {extracted_time}")
            
            # Check if the extracted time matches the original time (with some tolerance due to ZIP format limitations)
            time_diff = abs((extracted_time - specific_time).total_seconds())
            print(f"Time difference: {time_diff} seconds")
            
            # ZIP format only stores time with resolution of seconds
            if time_diff < 2:
                print("✅ SUCCESS: File modification time was preserved correctly!")
                return True
            else:
                print(f"❌ FAILURE: File modification time was not preserved. Time difference of {time_diff} seconds.")
                return False
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Import shutil which is needed for the test
    import shutil
    
    success = test_timestamp_preservation()
    if success:
        print("\n🎉 All tests passed! Timestamp preservation fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Timestamp preservation fix is not working correctly.")
        sys.exit(1)
