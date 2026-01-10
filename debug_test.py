import sys
import traceback

print(f"Python version: {sys.version}")
print(f"Current working directory: {sys.path[0]}")
print(f"Module search path: {sys.path}")

# Test 1: Import basic modules
print("\n=== Test 1: Importing basic modules ===")
try:
    import docker
    print("✅ Successfully imported docker module")
    import click
    print("✅ Successfully imported click module")
except Exception as e:
    print(f"❌ Failed to import modules: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Test CLI module import
print("\n=== Test 2: Importing CLI module ===")
try:
    from docker_jar_diff import cli
    print("✅ Successfully imported CLI module")
except Exception as e:
    print(f"❌ Failed to import CLI module: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test DockerHandler import and initialization
print("\n=== Test 3: Testing DockerHandler ===")
try:
    from docker_jar_diff.cache_manager import CacheManager
    from docker_jar_diff.docker_handler import DockerHandler
    
    cache_manager = CacheManager()
    print("✅ Successfully created CacheManager")
    
    docker_handler = DockerHandler(cache_manager)
    print("✅ Successfully created DockerHandler")
    
    cache_manager.cleanup()
    print("✅ Successfully cleaned up CacheManager")
except Exception as e:
    print(f"❌ Failed with DockerHandler: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 All tests passed! The basic components are working correctly.")
