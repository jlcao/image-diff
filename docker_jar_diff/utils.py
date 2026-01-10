import os
import shutil
import tempfile
import hashlib
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime

class Utils:
    @staticmethod
    def create_temp_dir(base_dir=None):
        """Create a temporary directory"""
        if base_dir:
            os.makedirs(base_dir, exist_ok=True)
            return tempfile.mkdtemp(dir=base_dir)
        return tempfile.mkdtemp()
    
    @staticmethod
    def remove_dir(dir_path, max_retries=3, retry_delay=1):
        """Remove a directory and all its contents with retry mechanism
        
        Args:
            dir_path: Directory path to remove
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        if not os.path.exists(dir_path):
            return
            
        import time
        import stat
        
        def on_rm_error(func, path, exc_info):
            """Error handler for shutil.rmtree"""
            # Try to change permissions and retry
            if not os.access(path, os.W_OK):
                os.chmod(path, stat.S_IWUSR)
                func(path)
            else:
                # If still can't remove, raise the error
                raise
        
        for retry in range(max_retries):
            try:
                shutil.rmtree(dir_path, onerror=on_rm_error)
                return
            except (PermissionError, OSError) as e:
                if retry == max_retries - 1:
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    @staticmethod
    def get_file_hash(file_path, algorithm='sha256'):
        """Get file hash"""
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    @staticmethod
    def get_file_info(file_path):
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': stat.st_size,
            'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'is_dir': os.path.isdir(file_path)
        }
    
    @staticmethod
    def save_json(data, file_path):
        """Save data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_json(file_path):
        """Load data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def is_jar_file(file_path):
        """Check if file is a JAR file"""
        return file_path.lower().endswith('.jar')
    
    @staticmethod
    def is_text_file(file_path):
        """Check if file is a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except:
            return False
    
    @staticmethod
    def get_relative_path(path, base_dir):
        """Get relative path from base directory"""
        return os.path.relpath(path, base_dir)
    @staticmethod
    def run_tar_command(
        operation: str,
        tar_path: str,
        target_path: str,
        extra_args: list = None,
        encoding: str = "utf-8"
        ) -> tuple:
        """
        在 Python 中执行系统 tar 命令
        
        Args:
            operation: 操作类型，支持 'extract'（解压）/ 'create'（压缩）
            tar_path: tar 包路径（解压时是输入，压缩时是输出）
            target_path: 目标路径（解压时是输出目录，压缩时是待压缩文件/目录）
            extra_args: tar 命令额外参数（如 ['-v', '-z']）
            encoding: 命令输出编码（Windows 建议用 'gbk'）
        
        Returns:
            tuple: (return_code, stdout, stderr)
                return_code=0 表示执行成功
        """
        # 1. 适配不同系统的 tar 命令路径
        system = platform.system()
        tar_cmd = "tar"  # Linux/Mac 默认
        if system == "Windows":
            # Windows 下优先用 Git Bash 的 tar（需安装 Git），其次用系统自带的 tar
            git_bash_tar = "C:\\Program Files\\Git\\usr\\bin\\tar.exe"
            if Path(git_bash_tar).exists():
                tar_cmd = git_bash_tar
            else:
                # 系统自带 tar（Windows 10/11 内置）
                tar_cmd = "tar.exe"
        
        # 2. 构建 tar 命令参数
        args = [tar_cmd]
        extra_args = extra_args or []
        
        if operation == "extract":
            # 解压命令：tar -xf [tar包] -C [目标目录]
            args.extend(["-xf", tar_path, "-C", target_path])
        elif operation == "create":
            # 压缩命令：tar -cf [输出tar包] [待压缩文件/目录]
            args.extend(["-cf", tar_path, target_path])
        else:
            raise ValueError(f"不支持的操作类型：{operation}，仅支持 extract/create")
        
        # 添加额外参数（如 -z 解压 gzip 压缩包，-v 显示详细信息）
        args.extend(extra_args)
        
        # 3. 执行 tar 命令
        print(f"📢 执行 tar 命令：{' '.join(args)}")
        try:
            # 捕获 stdout 和 stderr，设置超时时间
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding=encoding,
                timeout=300,  # 超时 5 分钟
                shell=False  # Windows 下也建议设为 False，避免命令注入风险
            )
            
            # 打印执行结果
            if result.returncode == 0:
                print(f"✅ tar 命令执行成功")
                if result.stdout:
                    print(f"📝 标准输出：\n{result.stdout}")
            else:
                print(f"❌ tar 命令执行失败（返回码：{result.returncode}）")
                print(f"🚨 错误输出：\n{result.stderr}")
            
            return (result.returncode, result.stdout, result.stderr)
        
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"tar 命令执行超时（超过 5 分钟）")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"未找到 tar 命令！\n"
                f"- Linux/Mac：请安装 tar（一般自带）\n"
                f"- Windows：请安装 Git（自带 tar）或升级到 Windows 10/11（内置 tar）"
            )
        except Exception as e:
            raise RuntimeError(f"执行 tar 命令时发生异常：{e}")
            
    @staticmethod
    def launch_beyond_compare_5(dir1, dir2, bc_path=None):
        """
        启动Beyond Compare 5并自动比对指定的两个目录
        
        Args:
            dir1 (str): 第一个要比对的目录路径
            dir2 (str): 第二个要比对的目录路径
            bc_path (str, optional): Beyond Compare 5可执行文件路径，默认自动检测
        
        Returns:
            bool: 启动成功返回True，失败返回False
        """
        # 校验目录是否存在
        if not os.path.isdir(dir1):
            print(f"错误：目录不存在 - {dir1}")
            return False
        if not os.path.isdir(dir2):
            print(f"错误：目录不存在 - {dir2}")
            return False
        
        # 自动检测不同系统下的Beyond Compare 5路径
        system = platform.system()
        if bc_path is None:
            if system == "Windows":
                # Windows默认安装路径（64位）
                bc_path = r"C:\Program Files\Beyond Compare 5\BCompare.exe"
                # 备选路径（32位）
                if not os.path.exists(bc_path):
                    bc_path = r"C:\Program Files (x86)\Beyond Compare 5\BCompare.exe"
            elif system == "Darwin":  # macOS
                bc_path = "/Applications/Beyond Compare 5.app/Contents/MacOS/bcomp"
            elif system == "Linux":  # Linux
                bc_path = "/usr/bin/bcompare"
            else:
                print(f"不支持的操作系统：{system}")
                return False
        
        # 校验Beyond Compare 5是否存在
        if not os.path.exists(bc_path):
            print(f"错误：Beyond Compare 5未找到，请检查路径：{bc_path}")
            print("请手动指定bc_path参数，例如：launch_beyond_compare_5(dir1, dir2, '/自定义路径/BCompare.exe')")
            return False
        
        # 构造命令行参数：bc_path dir1 dir2
        # 注意路径中的空格需要被正确处理，subprocess会自动处理
        cmd = [bc_path, dir1, dir2]
        
        try:
            # 启动Beyond Compare 5（不阻塞Python脚本，创建新进程）
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # Windows下隐藏控制台窗口
                creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0
            )
            print(f"✅ 成功启动Beyond Compare 5，正在比对：")
            print(f"   目录1：{dir1}")
            print(f"   目录2：{dir2}")
            return True
        except Exception as e:
            print(f"❌ 启动失败：{str(e)}")
            return False