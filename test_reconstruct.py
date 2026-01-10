#!/usr/bin/env python3
"""
Test script to verify the reconstructed docker_handler.py code
"""
import os
import sys
from docker_jar_diff.main import DockerJarDiff


def test_reconstructed_code():
    """Test the reconstructed docker_handler.py code"""
    try:
        # Create an instance of DockerJarDiff
        diff_tool = DockerJarDiff()
        
        # Test with a simple image and directory
        image_name = "tomcat:9.0-jdk8-corretto"
        compare_dir = "/usr/lib"
        
        print(f"Testing image extraction for {image_name}...")
        print(f"Compare directory: {compare_dir}")
        
        # Process a single image
        image_info = diff_tool.docker_handler.process_image(image_name, compare_dir)
        
        print(f"\nImage processing successful!")
        print(f"Image cache directory: {image_info['image_cache_dir']}")
        print(f"Extracted directory: {image_info['extracted_dir']}")
        print(f"Content directory: {image_info['content_dir']}")
        
        # Verify that files were extracted
        extracted_files = []
        for root, dirs, files in os.walk(image_info['extracted_dir']):
            for file in files:
                extracted_files.append(os.path.join(root, file))
                if len(extracted_files) >= 10:  # Limit to first 10 files
                    break
            if len(extracted_files) >= 10:
                break
        
        if extracted_files:
            print(f"\nExtracted files (first 10):")
            for file in extracted_files:
                print(f"  - {file}")
        else:
            print(f"\nWarning: No files were extracted!")
            
        print(f"\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_reconstructed_code()
    sys.exit(0 if success else 1)
