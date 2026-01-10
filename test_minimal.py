import os
import sys
import traceback

print("Minimal Python test")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Write to a file to verify output
with open("test_output.txt", "w") as f:
    f.write("Python is working\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Current directory: {os.getcwd()}\n")

print("Wrote to test_output.txt")
print("Script completed")
