import docker
import os
import tarfile
import shutil
from pathlib import Path

def extract_docker_image_windows(
    image_name: str,
    output_dir: str,
    docker_client=None
):
    """
    Windows 专用：解压 Docker 镜像核心文件（跳过特殊文件，确保输出有内容）
    """
    # 初始化 Docker 客户端
    client = docker_client or docker.from_env()
    
    # ========== 关键修复1：强制转换为 Windows 绝对路径 ==========
    output_path = Path(output_dir).resolve()  # 转为绝对路径，避免相对路径问题
    print(f"📌 解压目标绝对路径：{output_path}")
    
    # 清空并重建输出目录（确保干净）
    if output_path.exists():
        shutil.rmtree(output_path, ignore_errors=True)
    output_path.mkdir(parents=True, exist_ok=True)
    
    temp_container = None
    temp_tar_path = None
    try:
        # 1. 拉取/检查镜像
        print(f"[1/4] 检查镜像 {image_name}...")
        client.images.pull(image_name)
        
        # 2. 创建临时容器
        print(f"[2/4] 创建临时容器...")
        temp_container = client.containers.create(image=image_name, auto_remove=False)
        
        # 3. 获取根目录 tar 包（核心修复2：分块保存，确保完整）
        print(f"[3/4] 下载镜像 tar 包...")
        bits, _ = temp_container.get_archive('/')
        
        # 保存 tar 包（Windows 短路径，避免中文/空格问题）
        temp_tar_path = output_path / "temp_image.tar"
        with open(temp_tar_path, 'wb') as f:
            for chunk in bits:
                f.write(chunk)
        print(f"✅ 临时 tar 包已保存：{temp_tar_path}")
        print(f"📦 tar 包大小：{os.path.getsize(temp_tar_path) / 1024 / 1024:.2f} MB")
        
        # ========== 关键修复3：自动识别 tar 包压缩格式 ==========
        # 4. 解压 tar 包（只保留核心目录，确保有内容输出）
        print(f"[4/4] 解压核心文件到 {output_dir}...")
        # 只保留的核心目录（确保有内容）
        KEEP_DIRS = ['/usr', '/opt', '/etc', '/var', '/bin', '/lib', '/lib64']
        # 跳过的无效目录
        SKIP_DIRS = ['/dev', '/proc', '/sys', '/tmp', '/run', '/mnt', '/srv']
        
        # 关键：用 'r:*' 自动识别压缩格式，避免 tar 包无法读取
        with tarfile.open(temp_tar_path, 'r:*') as tar:
            for member in tar.getmembers():
                # 跳过无效目录
                if any(member.name.startswith(skip) for skip in SKIP_DIRS):
                    continue
                
                # 只保留核心目录（确保有内容输出）
                if not any(member.name.startswith(keep) for keep in KEEP_DIRS):
                    continue
                
                # ========== 关键修复4：处理路径分隔符 ==========
                # 将 Linux 路径转为 Windows 路径
                win_member_path = member.name.replace('/', '\\')
                member.name = win_member_path  # 重命名 tar 内文件路径
                
                # 跳过软链接（Windows 不支持，避免报错）
                if member.issym() or member.islnk():
                    continue
                
                # 解压文件（容错处理）
                try:
                    # 强制指定编码，避免中文文件名乱码
                    tar.extract(member, path=output_path, numeric_owner=True)
                    print(f"✅ 解压：{member.name}")
                except Exception as e:
                    print(f"⚠️  跳过文件 {member.name}：{e}")
        
        # ========== 验证是否有文件输出 ==========
        file_count = sum(1 for _ in output_path.rglob('*'))
        if file_count == 0:
            raise RuntimeError("解压完成但输出目录为空！可能是过滤规则错误")
        
        print(f"\n🎉 解压成功！")
        print(f"📂 输出目录：{output_path}")
        print(f"📊 解压文件总数：{file_count}")
        print(f"🔍 核心目录示例：")
        for keep_dir in KEEP_DIRS:
            check_dir = output_path / keep_dir.lstrip('/')
            if check_dir.exists():
                print(f"   - {check_dir}（存在）")
        
        return str(output_path)
    
    except docker.errors.APIError as e:
        raise RuntimeError(f"Docker 错误：{e}")
    except tarfile.TarError as e:
        raise RuntimeError(f"tar 包解压错误：{e}（可能是 tar 包损坏）")
    except Exception as e:
        raise RuntimeError(f"未知错误：{e}")
    finally:
        # 清理资源
        if temp_container:
            print("\n🧹 清理临时容器...")
            try:
                temp_container.remove(v=True)
            except:
                pass
        
        # 删除临时 tar 包（Windows 需延迟删除，避免文件锁定）
        if temp_tar_path and temp_tar_path.exists():
            try:
                os.unlink(temp_tar_path)
            except:
                print(f"⚠️  临时 tar 包 {temp_tar_path} 未删除，请手动删除")

# 示例调用（Tomcat 镜像测试）
if __name__ == "__main__":
    # 替换为你的镜像名称
    TARGET_IMAGE = "tomcat:9.0-jdk8-corretto"
    OUTPUT_DIR = "./tomcat_windows_extract"
    
    try:
        extract_docker_image_windows(TARGET_IMAGE, OUTPUT_DIR)
        print(f"\n✅ 全部完成！请查看目录：{OUTPUT_DIR}")
    except Exception as e:
        print(f"\n❌ 执行失败：{e}")
        # 暂停窗口，方便查看错误
        input("按回车键退出...")