import sys
import os
import traceback

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"Module search path: {sys.path}")

# Test Docker SDK
try:
    print("\nTesting Docker SDK import...")
    import docker
    print(f"✅ Docker SDK version: {docker.__version__}")
    
    # Test Docker client connection
    print("\nTesting Docker client connection...")
    client = docker.from_env()
    print("✅ Docker client connected")
    
    # Test pulling a small image
    image_name = "hello-world:latest"
    print(f"\nTesting image pull: {image_name}")
    image = client.images.pull(image_name)
    print(f"✅ Image pulled successfully: {image.tags}")
    
    # Test container creation and listing
    print(f"\nTesting container creation from: {image_name}")
    container = client.containers.create(image_name)
    print(f"✅ Container created: {container.id}")
    
    containers = client.containers.list(all=True)
    print(f"✅ Found {len(containers)} containers")
    
    # Clean up
    print(f"\nCleaning up container: {container.id}")
    container.remove()
    print("✅ Container removed")
    
    print("\n🎉 All basic tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
