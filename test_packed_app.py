#!/usr/bin/env python3
"""
Test script to verify the packed application
"""
import os
import subprocess

# Path to the packed executable
EXE_PATH = os.path.join(os.getcwd(), 'dist', 'docker-jar-diff', 'docker-jar-diff.exe')

def test_app_starts():
    """Test that the application starts and shows help"""
    print(f"Testing application at: {EXE_PATH}")
    print(f"File exists: {os.path.exists(EXE_PATH)}")
    
    if not os.path.exists(EXE_PATH):
        print("Error: Executable not found!")
        return False
    
    try:
        # Run the app with --help to check if it starts correctly
        result = subprocess.run([EXE_PATH, '--help'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        
        if result.returncode == 0:
            print("✅ Application started successfully and showed help!")
            return True
        else:
            print(f"❌ Application returned error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Application timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False

if __name__ == "__main__":
    print("Testing packed docker-jar-diff application...")
    success = test_app_starts()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
