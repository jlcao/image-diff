#!/usr/bin/env python3
"""
Test script to verify image name and version display fix
"""
import os
import json
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from docker_jar_diff.main import DockerJarDiff
from docker_jar_diff.cache_manager import CacheManager


def test_image_name_fix():
    """
    Test that image names are correctly preserved and displayed in the HTML report
    """
    try:
        # Create a test diff result with image names
        diff_result = {
            "image1_name": "tomcat:9.0-jdk8-corretto",
            "image2_name": "tomcat:9.0-jdk11-corretto",
            "dir1": "/tmp/extracted/image1",
            "dir2": "/tmp/extracted/image2",
            "compare_dir": "/",
            "differences": []
        }
        
        # Test the HTML generation
        cache_manager = CacheManager()
        from docker_jar_diff.html_generator import HTMLGenerator
        html_generator = HTMLGenerator(cache_manager)
        
        # Generate the HTML report
        report_path = html_generator.generate_report(diff_result)
        print(f"Generated test report: {report_path}")
        
        # Read the generated HTML and check for image names
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check if image names are properly embedded
        if 'tomcat:9.0-jdk8-corretto' in html_content and 'tomcat:9.0-jdk11-corretto' in html_content:
            print("✅ Image names are correctly embedded in the HTML")
        else:
            print("❌ Image names are not found in the HTML")
            return False
        
        # Check if the JS code uses the image_name fields
        if 'diffResult.image1_name' in html_content and 'diffResult.image2_name' in html_content:
            print("✅ JavaScript correctly uses the image_name fields")
        else:
            print("❌ JavaScript does not use the image_name fields")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing image name and version display fix...")
    success = test_image_name_fix()
    if success:
        print("\n🎉 All tests passed! Image name fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Image name fix is not working correctly.")
        sys.exit(1)
