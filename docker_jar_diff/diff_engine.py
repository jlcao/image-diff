import os
import difflib
import zipfile
import io
import tempfile
from datetime import datetime
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
                
                # Check if it's a JAR or ZIP file
                filename = path_parts[-1]
                if Utils.is_jar_file(filename) or filename.lower().endswith('.zip'):
                    # Extract JAR/ZIP contents to temporary directory
                    temp_dir = Utils.create_temp_dir()
                    extracted_tree = {}
                    
                    try:
                        # Extract the archive and get original timestamps
                        with zipfile.ZipFile(file_path, 'r') as z:
                            z.extractall(temp_dir)
                            
                            # Build directory tree with original timestamps from ZIP file
                            extracted_tree = self._build_archive_tree(z, temp_dir)
                        
                        # Add file info as a special entry with extracted content
                        file_info = Utils.get_file_info(file_path)
                        if file_info:
                            # Create a special entry for the archive file
                            archive_entry = {
                                'file_info': file_info,
                                'is_archive': True,
                                'contents': extracted_tree
                            }
                            current[filename] = archive_entry
                    except Exception as e:
                        # If extraction fails, just add it as a regular file
                        print(f"Error extracting archive {file_path}: {e}")
                        file_info = Utils.get_file_info(file_path)
                        if file_info:
                            current[filename] = file_info
                    finally:
                        # Clean up
                        Utils.remove_dir(temp_dir)
                else:
                    # Add as regular file
                    file_info = Utils.get_file_info(file_path)
                    if file_info:
                        current[filename] = file_info
        
        return tree
    
    def _build_archive_tree(self, zip_file, temp_dir):
        """Build directory tree structure from extracted archive with original timestamps"""
        tree = {}
        
        for zip_info in zip_file.infolist():
            if zip_info.is_dir():
                continue
                
            filename = zip_info.filename
            file_path = os.path.join(temp_dir, filename)
            
            # Skip if file doesn't exist (could be a broken archive)
            if not os.path.exists(file_path):
                continue
                
            # Add to tree
            current = tree
            path_parts = filename.split('/')
            
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Get file info
            abs_file_path = os.path.abspath(file_path)
            stat = os.stat(abs_file_path)
            
            # Calculate MD5
            md5 = Utils.get_file_hash(abs_file_path, algorithm='md5')
            
            # Get original timestamp from ZIP file
            original_mtime = datetime(*zip_info.date_time)
            
            file_info = {
                'name': path_parts[-1],
                'path': abs_file_path,
                'size': stat.st_size,
                'mtime': original_mtime.isoformat(),
                'is_dir': False,
                'md5': md5
            }
            
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
                
                # Check if either item is an archive entry
                item1_is_archive = isinstance(item1, dict) and item1.get('is_archive')
                item2_is_archive = isinstance(item2, dict) and item2.get('is_archive')
                
                # Get actual file info and contents for archive entries
                item1_file_info = item1.get('file_info', item1) if item1_is_archive else item1
                item2_file_info = item2.get('file_info', item2) if item2_is_archive else item2
                item1_contents = item1.get('contents', {}) if item1_is_archive else item1
                item2_contents = item2.get('contents', {}) if item2_is_archive else item2
                
                # Check if either item (or its file_info) is a file info dictionary (has 'size' key)
                item1_is_file = isinstance(item1_file_info, dict) and 'size' in item1_file_info
                item2_is_file = isinstance(item2_file_info, dict) and 'size' in item2_file_info
                
                if not item1_is_file and not item2_is_file:
                    # Both are directories or archive contents, recurse
                    sub_diffs = self._find_differences(item1_contents, item2_contents, path)
                    diffs.extend(sub_diffs)
                elif item1_is_file and item2_is_file:
                    # Both are files or archive files, compare them
                    diff_type = 'identical'
                    
                    if item1_file_info['size'] != item2_file_info['size']:
                        diff_type = 'size_diff'
                    else:
                        # Same size, check MD5 content
                        try:
                            # Use the MD5 already calculated in get_file_info
                            md5_1 = item1_file_info.get('md5')
                            md5_2 = item2_file_info.get('md5')
                            
                            # If MD5 is not available, calculate it
                            if md5_1 is None:
                                md5_1 = Utils.get_file_hash(item1_file_info['path'], algorithm='md5')
                            if md5_2 is None:
                                md5_2 = Utils.get_file_hash(item2_file_info['path'], algorithm='md5')
                            
                            if md5_1 != md5_2:
                                diff_type = 'content_diff'
                            else:
                                # Same size and MD5, files are identical
                                diff_type = 'identical'
                        except Exception as e:
                            # Log the error but still check if MD5 values are available
                            print(f"Error calculating MD5: {e}")
                            # If MD5 values are already available, use them
                            md5_1 = item1_file_info.get('md5')
                            md5_2 = item2_file_info.get('md5')
                            if md5_1 and md5_2 and md5_1 == md5_2:
                                diff_type = 'identical'
                            else:
                                diff_type = 'error'
                    
                    if diff_type != 'identical':
                        diff_item = {
                            'path': path,
                            'type': diff_type,
                            'item1': item1_file_info,
                            'item2': item2_file_info,
                            'is_archive': item1_is_archive and item2_is_archive
                        }
                        
                        # If both are archive files and have different contents, diff their extracted contents
                        if item1_is_archive and item2_is_archive:
                            try:
                                archive_diff = self._find_differences(item1_contents, item2_contents, path)
                                if archive_diff:
                                    diff_item['archive_diff'] = archive_diff
                            except Exception as e:
                                print(f"Error diffing archive contents: {e}")
                        # For backward compatibility, keep JAR diff logic
                        elif Utils.is_jar_file(item1_file_info['path']) and Utils.is_jar_file(item2_file_info['path']):
                            try:
                                jar_diff = self._diff_jar_files(item1_file_info['path'], item2_file_info['path'], path)
                                diff_item['jar_diff'] = jar_diff
                            except Exception as e:
                                print(f"Error checking JAR file: {e}")
                        
                        diffs.append(diff_item)
            elif key in tree1:
                # Only in tree1
                item1 = tree1[key]
                item1_is_archive = isinstance(item1, dict) and item1.get('is_archive')
                item1_file_info = item1.get('file_info', item1) if item1_is_archive else item1
                item1_contents = item1.get('contents', {}) if item1_is_archive else item1
                
                # Add entry for item only in tree1
                diffs.append({
                    'path': path,
                    'type': 'only_in_1',
                    'item1': item1_file_info,
                    'item2': None,
                    'is_archive': item1_is_archive
                })
                
                # If it's an archive, add its contents to the diff
                if item1_is_archive:
                    try:
                        archive_diff = self._find_differences(item1_contents, {}, path)
                        if archive_diff:
                            diffs.extend(archive_diff)
                    except Exception as e:
                        print(f"Error processing archive contents: {e}")
            else:
                # Only in tree2
                item2 = tree2[key]
                item2_is_archive = isinstance(item2, dict) and item2.get('is_archive')
                item2_file_info = item2.get('file_info', item2) if item2_is_archive else item2
                item2_contents = item2.get('contents', {}) if item2_is_archive else item2
                
                # Add entry for item only in tree2
                diffs.append({
                    'path': path,
                    'type': 'only_in_2',
                    'item1': None,
                    'item2': item2_file_info,
                    'is_archive': item2_is_archive
                })
                
                # If it's an archive, add its contents to the diff
                if item2_is_archive:
                    try:
                        archive_diff = self._find_differences({}, item2_contents, path)
                        if archive_diff:
                            diffs.extend(archive_diff)
                    except Exception as e:
                        print(f"Error processing archive contents: {e}")
        
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