import os
import difflib
import zipfile
import io
import tempfile
from .utils import Utils
from .cache_manager import CacheManager

class DiffEngine:
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def diff_directories(self, dir1, dir2, compare_dir=None):
        """Diff two directories"""
        if compare_dir:
            # Only compare specific directory
            dir1 = os.path.join(dir1, compare_dir.lstrip('/'))
            dir2 = os.path.join(dir2, compare_dir.lstrip('/'))
        
        # Create directory trees
        tree1 = self._build_directory_tree(dir1)
        tree2 = self._build_directory_tree(dir2)
        
        # Find differences
        diffs = self._find_differences(tree1, tree2, compare_dir or '/')
        
        return {
            'dir1': dir1,
            'dir2': dir2,
            'compare_dir': compare_dir or '/',
            'differences': diffs
        }
    
    def _build_directory_tree(self, root_dir):
        """Build directory tree structure"""
        tree = {}
        
        if not os.path.exists(root_dir):
            return tree
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                
                # Add to tree
                current = tree
                path_parts = rel_path.split(os.sep)
                
                for part in path_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Add file info
                file_info = Utils.get_file_info(file_path)
                if file_info:
                    current[path_parts[-1]] = file_info
        
        return tree
    
    def _find_differences(self, tree1, tree2, base_path):
        """Find differences between two directory trees"""
        diffs = []
        
        # Get all keys from both trees
        all_keys = set(tree1.keys()) | set(tree2.keys())
        
        for key in sorted(all_keys):
            path = os.path.join(base_path, key).replace('\\', '/')
            
            if key in tree1 and key in tree2:
                # Both trees have this key
                item1 = tree1[key]
                item2 = tree2[key]
                
                # Check if either item is a file info dictionary (has 'size' key)
                item1_is_file = isinstance(item1, dict) and 'size' in item1
                item2_is_file = isinstance(item2, dict) and 'size' in item2
                
                if not item1_is_file and not item2_is_file:
                    # Both are directories, recurse
                    sub_diffs = self._find_differences(item1, item2, path)
                    diffs.extend(sub_diffs)
                elif item1_is_file and item2_is_file:
                    # Both are files, compare them
                    diff_type = 'identical'
                    
                    if item1['size'] != item2['size']:
                        diff_type = 'size_diff'
                    elif item1['mtime'] != item2['mtime']:
                        diff_type = 'mtime_diff'
                    else:
                        # Same size and mtime, check content
                        try:
                            hash1 = Utils.get_file_hash(item1['path'])
                            hash2 = Utils.get_file_hash(item2['path'])
                            if hash1 != hash2:
                                diff_type = 'content_diff'
                        except Exception as e:
                            diff_type = 'error'
                    
                    if diff_type != 'identical':
                        diff_item = {
                            'path': path,
                            'type': diff_type,
                            'item1': item1,
                            'item2': item2
                        }
                        
                        # If it's a JAR file, diff the content
                        try:
                            if Utils.is_jar_file(item1['path']) and Utils.is_jar_file(item2['path']):
                                jar_diff = self._diff_jar_files(item1['path'], item2['path'], path)
                                diff_item['jar_diff'] = jar_diff
                        except Exception as e:
                            print(f"Error checking JAR file: {e}")
                        
                        diffs.append(diff_item)
            elif key in tree1:
                # Only in tree1
                item1 = tree1[key]
                diffs.append({
                    'path': path,
                    'type': 'only_in_1',
                    'item1': item1 if (isinstance(item1, dict) and 'size' in item1) else {'is_dir': True},
                    'item2': None
                })
            else:
                # Only in tree2
                item2 = tree2[key]
                diffs.append({
                    'path': path,
                    'type': 'only_in_2',
                    'item1': None,
                    'item2': item2 if (isinstance(item2, dict) and 'size' in item2) else {'is_dir': True}
                })
        
        return diffs
    
    def _diff_jar_files(self, jar1, jar2, jar_path):
        """Diff two JAR files"""
        print(f"Diffing JAR files: {jar_path}")
        
        # Extract JAR contents to temporary directories
        temp_dir1 = Utils.create_temp_dir()
        temp_dir2 = Utils.create_temp_dir()
        
        try:
            # Extract JAR files
            with zipfile.ZipFile(jar1, 'r') as z1:
                z1.extractall(temp_dir1)
            
            with zipfile.ZipFile(jar2, 'r') as z2:
                z2.extractall(temp_dir2)
            
            # Diff the extracted contents
            jar_tree1 = self._build_directory_tree(temp_dir1)
            jar_tree2 = self._build_directory_tree(temp_dir2)
            
            return self._find_differences(jar_tree1, jar_tree2, jar_path)
            
        finally:
            # Clean up
            Utils.remove_dir(temp_dir1)
            Utils.remove_dir(temp_dir2)
    
    def diff_files(self, file1, file2):
        """Diff two files and return the diff content"""
        if not os.path.exists(file1) or not os.path.exists(file2):
            return None
        
        # Check if both files are text files
        if not Utils.is_text_file(file1) or not Utils.is_text_file(file2):
            # For binary files, just return that they're different
            return {
                'type': 'binary',
                'files': [file1, file2]
            }
        
        # Read both files
        with open(file1, 'r', encoding='utf-8', errors='ignore') as f1:
            lines1 = f1.readlines()
        
        with open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
            lines2 = f2.readlines()
        
        # Generate diff
        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile=os.path.basename(file1),
            tofile=os.path.basename(file2),
            lineterm=''
        )
        
        return {
            'type': 'text',
            'diff': ''.join(diff),
            'files': [file1, file2]
        }