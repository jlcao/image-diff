#!/usr/bin/env python3
"""
Test script to identify all dependencies
"""
import pkgutil
import docker_jar_diff
import docker
import click

# List all modules imported by the project
print("Project dependencies:")
print(f"- docker_jar_diff: {docker_jar_diff.__file__}")
print(f"- docker SDK: {docker.__file__}")
print(f"- click: {click.__file__}")

# Check for any hidden imports
print("\nChecking for hidden imports...")
try:
    from docker_jar_diff import docker_handler
    from docker_jar_diff import main
    from docker_jar_diff import utils
    from docker_jar_diff import cache_manager
    from docker_jar_diff import diff_engine
    from docker_jar_diff import html_generator
    print("All submodules imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")
