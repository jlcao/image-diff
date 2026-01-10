import os
import json
from .cache_manager import CacheManager
from .docker_handler import DockerHandler
from .diff_engine import DiffEngine
from .html_generator import HTMLGenerator
from .utils import Utils

class DockerJarDiff:
    def __init__(self, base_cache_dir=None):
        # Load configuration - support both development and PyInstaller packaged environments
        import sys
        
        # Try to find config in current working directory first
        config_path = os.path.join(os.getcwd(), '.config', 'config.json')
        
        # If not found, try in program directory
        if not os.path.exists(config_path):
            if hasattr(sys, '_MEIPASS'):
                # Running from PyInstaller bundle
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running from development environment
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(app_dir, '.config', 'config.json')
        
        # If config file doesn't exist, create default config
        if not os.path.exists(config_path):
            default_config = {
                "docker": {
                    "base_url": "tcp://127.0.0.1:12375",
                    "tls": False
                },
                "beyond_compare": {
                    "path": "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Beyond Compare 5\\BCompare.exe"
                }
            }
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            # Write default config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file at: {config_path}")
        
        # Load config file
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.cache_manager = CacheManager(base_cache_dir)
        
        # Record current task cache directory for cleanup later
        self.current_task_cache_dir = self.cache_manager.task_cache_dir
        
        # Get list of all task directories for potential cleanup
        self.all_task_dirs = []
        base_cache_dir = self.cache_manager.base_cache_dir
        if os.path.exists(base_cache_dir):
            for dir_name in os.listdir(base_cache_dir):
                dir_path = os.path.join(base_cache_dir, dir_name)
                if os.path.isdir(dir_path) and dir_name.startswith('task_'):
                    self.all_task_dirs.append(dir_path)
        self.docker_handler = DockerHandler(self.cache_manager)
        self.diff_engine = DiffEngine(self.cache_manager)
        self.html_generator = HTMLGenerator(self.cache_manager)
    
    def run_diff(self, image1, image2, compare_dir=None):
        """Run the complete diff process"""
        import traceback
        try:
            print(f"Starting Docker image diff between {image1} and {image2}")
            print(f"比对目录: {compare_dir or '/'}")
            
            # Step 1: Process both images (download and extract)
            print("\nStep 1: Processing images...")
            print(f"处理第1个镜像文件: {image1}")
            image1_info = self.docker_handler.process_image(image1,compare_dir)
            error = image1_info.get('error')
            if error:
                #print(f"Error processing image {image1}: {error}")
                return -1
            else:
                extracted_dir1 = image1_info['extracted_dir']
                content_dir1 = image1_info['content_dir']
                print(f"✅第1个镜像文件解压成功: {extracted_dir1}")
            
            print(f"\n处理第2个镜像文件: {image2}")
            image2_info = self.docker_handler.process_image(image2,compare_dir)
            extracted_dir2 = image2_info['extracted_dir']
            content_dir2 = image2_info['content_dir']
            error = image1_info.get('error')
            if error:
                #print(f"Error processing image {image1}: {error}")
                return -1
            else:
                print(f"✅第2个镜像文件解压成功: {extracted_dir2}")
            
            # Step 2: Perform directory diff
            print("\nStep 2: 开始对比目录差异...")

            beyond_compare_path = self.config.get('beyond_compare', {}).get('path', "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Beyond Compare 5\\BCompare.exe")
            try:
                Utils.launch_beyond_compare_5(extracted_dir1, extracted_dir2, beyond_compare_path)
            except Exception as e:
                print(f"❌ 没有成功运行 beyond compare 5 ,请手动运行比较两个镜像文件")
                print(f"   目录1：{extracted_dir1}")
                print(f"   目录2：{extracted_dir2}")
                return -1

            return 0;
            
        except Exception as e:
            print(f"❌ Error during diff process: {e}")
            raise
        finally:
            # Clean up Docker resources
            print("\n🧹 Cleaning up resources...")
            self.docker_handler.cleanup()
    
    def cleanup(self):
        """Cleanup all resources"""
