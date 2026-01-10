import os
import sys
import traceback
from docker_jar_diff.cache_manager import CacheManager
from docker_jar_diff.docker_handler import DockerHandler

def test_extract_image():
    print("Testing image extraction...")
    
    # Use a simple image that's small and easy to pull
    image_name = "alpine:latest"
    
    # Create a test directory
    test_dir = os.path.join(os.getcwd(), "test_extract_output")
    
    try:
        # Clean up any existing test directory
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
        
        os.makedirs(test_dir, exist_ok=True)
        print(f"Created test directory: {test_dir}")
        
        # Create cache manager and docker handler
        cache_manager = CacheManager()
        docker_handler = DockerHandler(cache_manager)
        
        # Pull the image
        print(f"Pulling image: {image_name}")
        docker_handler.pull_image(image_name)
        
        # Extract the image
        print(f"Extracting image to: {test_dir}")
        docker_handler.extract_image(image_name, test_dir)
        
        # Verify extraction
        print("Verifying extraction...")
        file_count = 0
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                file_count += 1
                if file_count <= 10:  # Show first 10 files
                    print(f"  Found: {os.path.join(root, file)}")
        
        if file_count == 0:
            print("❌ No files extracted!")
        else:
            print(f"✅ Successfully extracted {file_count} files!")
            
            # Check if any JAR files were extracted
            jar_files = []
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith('.jar'):
                        jar_files.append(os.path.join(root, file))
            
            if jar_files:
                print(f"Found {len(jar_files)} JAR files:")
                for jar in jar_files[:5]:  # Show first 5 JAR files
                    print(f"  {jar}")
            else:
                print("Note: No JAR files found in this image (expected for alpine).")
        
        cache_manager.cleanup()
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        
        # Clean up if possible
        try:
            if 'cache_manager' in locals():
                cache_manager.cleanup()
            if 'test_dir' in locals() and os.path.exists(test_dir):
                import shutil
                shutil.rmtree(test_dir)
        except:
            pass
        
        return False

if __name__ == "__main__":
    success = test_extract_image()
    sys.exit(0 if success else 1)