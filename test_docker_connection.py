import os
import sys
import docker

def test_docker_connection():
    """Test Docker client connection"""
    print("Testing Docker client connection...")
    
    # Print environment variables
    print("\nDocker-related environment variables:")
    docker_env_vars = ['DOCKER_HOST', 'DOCKER_CERT_PATH', 'DOCKER_TLS_VERIFY', 'COMPOSE_PROJECT_NAME']
    for var in docker_env_vars:
        if var in os.environ:
            print(f"  {var}: {os.environ[var]}")
        else:
            print(f"  {var}: Not set")
    
    # Try different connection methods
    print("\nTrying Docker client initialization methods...")
    
    # Method 1: from_env()
    try:
        print("1. Using docker.from_env()...")
        client = docker.from_env()
        # Test if we can get version info
        version = client.version()
        print(f"   ✓ Success! Docker version: {version['Version']}")
        print(f"   ✓ API version: {version['ApiVersion']}")
        print(f"   ✓ OS: {version['Os']}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {type(e).__name__}: {e}")
    
    # Method 2: Explicit connection to Docker Desktop default
    try:
        print("2. Using Docker Desktop default socket...")
        client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
        version = client.version()
        print(f"   ✓ Success! Docker version: {version['Version']}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {type(e).__name__}: {e}")
    
    # Method 3: Try with HTTP (for Linux/macOS)
    try:
        print("3. Using HTTP connection...")
        client = docker.DockerClient(base_url='http://localhost:2375')
        version = client.version()
        print(f"   ✓ Success! Docker version: {version['Version']}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {type(e).__name__}: {e}")
    
    # Method 4: Try with HTTPS (for secure connections)
    try:
        print("4. Using HTTPS connection...")
        client = docker.DockerClient(base_url='https://localhost:2376')
        version = client.version()
        print(f"   ✓ Success! Docker version: {version['Version']}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {type(e).__name__}: {e}")
    
    print("\n❌ All connection methods failed!")
    print("\nTroubleshooting tips:")
    print("1. Make sure Docker Desktop is running")
    print("2. Check if Docker is accessible from command line: docker version")
    print("3. Verify DOCKER_HOST environment variable is correct")
    print("4. For Windows, ensure Docker Desktop is configured to allow connections")
    print("5. Restart Docker Desktop if needed")
    
    return False

if __name__ == "__main__":
    success = test_docker_connection()
    sys.exit(0 if success else 1)
