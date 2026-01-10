import subprocess
import os
import platform

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

# 示例调用
if __name__ == "__main__":
    # 替换为你要比对的两个目录
    directory1 = "D:\\resource\\python\docker-jar-diff\\.docker-jar-diff-cache\\task_20260110_114725_7f6213bf\\extracted\\tomcat_9.0-jdk8-corretto"
    directory2 = "D:\\resource\\python\docker-jar-diff\\.docker-jar-diff-cache\\task_20260110_114725_7f6213bf\\extracted\\tomcat_10-jre21"
    
    # 方式1：自动检测Beyond Compare路径
    launch_beyond_compare_5(directory1, directory2,
        "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Beyond Compare 5\\BCompare.exe"
    )
    
    # 方式2：手动指定Beyond Compare路径（如果自动检测失败）
    # launch_beyond_compare_5(
    #     directory1,
    #     directory2,
    #     bc_path=r"D:\Software\Beyond Compare 5\BCompare.exe"
    # )