import os
import platform
import logging
from re import split
import shutil
import zipfile
from pathlib import Path
import json
from .utils import Utils
from .cache_manager import CacheManager
import docker

# Set up logging to file
logging.basicConfig(
    filename='docker_handler.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DockerHandler:
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
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
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Initialize Docker client from config
        try:
            docker_config = config.get('docker', {})
            base_url = docker_config.get('base_url', 'tcp://127.0.0.1:12375')
            tls = docker_config.get('tls', False)
            self.client = docker.DockerClient(base_url=base_url, tls=tls)
            print("Docker client initialized successfully")
        except docker.errors.DockerException as e:
            raise RuntimeError(f"Failed to initialize Docker client: {e}")
    
    def extract_image(self, image_tar , extract_path):
        os.makedirs(extract_path, exist_ok=True)
        Utils.run_tar_command(
            operation="extract",
            tar_path=str(image_tar),
            target_path=str(extract_path),
            extra_args=[],  # Docker 镜像 tar 包一般是 gzip 压缩
            encoding="gbk" if platform.system() == "Windows" else "utf-8"
        )

    def _check_and_pull_image(self, image_name):
        """Check if image exists locally, pull from Docker Hub if not"""
        try:
            # 检查本地是否已存在镜像
            self.client.images.get(image_name)
            print(f"✅ 镜像 {image_name} 已存在于本地")
        except docker.errors.ImageNotFound:
            # 本地不存在，从Docker Hub拉取
            print(f"⏳ 镜像 {image_name} 本地不存在，开始从Docker Hub拉取...")
            try:
                self.client.images.pull(image_name)
                print(f"✅ 镜像 {image_name} 拉取成功")
            except docker.errors.APIError as e:
                # 拉取失败，可能是远程镜像不存在
                if "not found" in str(e).lower():
                    raise RuntimeError(f"❌ 镜像 {image_name} 在远程仓库也不存在")
                else:
                    raise RuntimeError(f"❌ 拉取镜像 {image_name} 时发生错误: {e}")
        except docker.errors.APIError as e:
            # 处理API错误
            raise RuntimeError(f"❌ 操作镜像 {image_name} 时发生错误: {e}")

    def _create_temp_container(self, image_name):
        """Create a temporary container from the specified image"""
        return self.client.containers.create(image=image_name, auto_remove=False)

    def _get_container_directory(self, container, directory):
        """Get the tar archive of a directory from a container"""
        try:
            bits, _ = container.get_archive(directory)
            print(f"✅ 容器中目录 {directory} 存在并成功获取")
            return bits
        except docker.errors.NotFound as e:
            # 捕获目录不存在的异常
            raise RuntimeError(f"❌ 容器中不存在目录 {directory}")
        except docker.errors.APIError as e:
            # 处理其他API错误
            raise RuntimeError(f"❌ 获取容器目录时发生错误: {e}")

    def _save_tar_archive(self, bits, save_dir, filename="image.tar"):
        """Save the tar archive bits to a local file"""
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        with open(save_path, 'wb') as f:
            for chunk in bits:
                f.write(chunk)
        print(f"✅ 临时 tar 包已保存：{save_path}")
        print(f"📦 tar 包大小：{os.path.getsize(save_path) / 1024 / 1024:.2f} MB")
        return save_path

    def _extract_tar_archive(self, tar_path, extract_dir, source_dir):
        """Extract the tar archive to the specified directory"""

        tmpPath = Path(os.path.join(extract_dir,source_dir.rstrip('/').lstrip('/') ))
        print(f"[4/4] 解压 tar 包 to {str(tmpPath.parent)}...")
        self.extract_image(tar_path, tmpPath.parent)
        return tmpPath

    def process_image(self, image_name, compare_dir):
        """Process an image: pull, save, extract, and extract jar/class files"""
        image_cache_dir = self.cache_manager.get_image_cache_dir(image_name)
        extracted_dir = self.cache_manager.get_extracted_dir(image_name)
        content_dir = self.cache_manager.get_content_dir(image_name)
        temp_container = None
        temp_tar_path = None
        docker_client = None
        
        if not compare_dir:
            compare_dir = '/'
            
        try:
            # 1. 检查并拉取镜像
            print(f"[1/4] 检查镜像 {image_name}...")
            self._check_and_pull_image(image_name)
            
            # 2. 创建临时容器
            print(f"[2/4] 创建临时容器...")
            temp_container = self._create_temp_container(image_name)
            
            # 3. 获取容器目录的 tar 包
            print(f"[3/4] 下载镜像目录 {compare_dir}...")
            bits = self._get_container_directory(temp_container, compare_dir)
            
            # 4. 保存 tar 包到本地
            temp_tar_path = self._save_tar_archive(bits, image_cache_dir)
            
            # 5. 解压 tar 包
            self._extract_tar_archive(temp_tar_path, extracted_dir, compare_dir)
            
            # Extract jar and class files
            #self.extract_jar_class_files(image_name, content_dir)
        except Exception as e:
            print(f"Error processing image {image_name}: {e}")
            return {'error':str(e)}
        finally:
            if temp_container:
                print("\n🧹 清理临时容器...")
            try:
                temp_container.remove(v=True)
            except:
                pass
            self.cleanup()
    
        return {
            'image_cache_dir': image_cache_dir,
            'extracted_dir': extracted_dir,
            'content_dir': content_dir
        }
        
    def cleanup(self):
        """Cleanup Docker client resources"""
        try:
            self.client.close()
            print("Docker client closed successfully")
        except Exception as e:
            print(f"Error closing Docker client: {e}")