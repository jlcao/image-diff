import os
import uuid
from datetime import datetime
from .utils import Utils

class CacheManager:
    def __init__(self, base_cache_dir=None):
        self.task_id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_cache_dir = base_cache_dir or os.path.join(os.getcwd(), ".compare_cache")
        
        # Create task-specific cache directory
        self.task_cache_dir = os.path.join(
            self.base_cache_dir, 
            f"task_{self.timestamp}_{self.task_id}"
        )
        Utils.remove_dir(self.base_cache_dir)
        
        # Subdirectories
        self.images_dir = os.path.join(self.task_cache_dir, "images")
        self.extracted_dir = os.path.join(self.task_cache_dir, "extracted")
        self.content_dir = os.path.join(self.task_cache_dir, "content")
        self.diff_dir = os.path.join(self.task_cache_dir, "diff")
        self.html_report_dir = os.path.join(self.task_cache_dir, "html_report")
        
        # Create all directories
        self._create_directories()
    
    def _create_directories(self):
        """Create all necessary directories"""
        dirs = [
            self.base_cache_dir,
            self.task_cache_dir,
            self.images_dir,
            self.extracted_dir,
            self.content_dir,
            self.diff_dir,
            self.html_report_dir
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def get_image_cache_dir(self, image_name):
        """Get cache directory for a specific image"""
        # Create a safe directory name from image name
        safe_name = image_name.replace("/", "_")
        safe_name = safe_name.replace(":", "_")
        return os.path.join(self.images_dir, safe_name)
    
    def get_extracted_dir(self, image_name):
        """Get extracted directory for a specific image"""
        # Create a safe directory name from image name
        safe_name = image_name.replace("/", "_")
        safe_name = safe_name.replace(":", "_")
        return os.path.join(self.extracted_dir, safe_name)
    
    def get_content_dir(self, image_name):
        """Get directory for extracted content (jar/class files) from a specific image"""
        # Create a safe directory name from image name
        safe_name = image_name.replace("/", "_")
        safe_name = safe_name.replace(":", "_")
        return os.path.join(self.content_dir, safe_name)
    
    def get_diff_file_path(self, file1, file2):
        """Get path to store diff result between two files"""
        # Create a unique filename for the diff
        diff_filename = f"diff_{Utils.get_file_hash(file1)[:8]}_{Utils.get_file_hash(file2)[:8]}.json"
        return os.path.join(self.diff_dir, diff_filename)
    
    def cleanup(self):
        """Cleanup cache directory"""
        Utils.remove_dir(self.task_cache_dir)
    
    def get_report_path(self):
        """Get path to the main HTML report"""
        return os.path.join(self.html_report_dir, "index.html")
    
    def get_secondary_report_path(self, report_name):
        """Get path to secondary HTML reports"""
        return os.path.join(self.html_report_dir, report_name)