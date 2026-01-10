import docker
import requests

# 测试不同API版本的连接
def test_api_versions():
    print("测试Docker API版本兼容性...")
    
    # 检查Docker SDK的版本信息
    print(f"\nDocker SDK版本: {docker.__version__}")
    
    # 尝试不同的API版本
    api_versions = [
        "1.44",  # Docker 29.x的最低API版本
        "1.45",
        "1.46",
        "1.47",
        "1.48",
        "1.49",
        "1.50",
        "1.51",
        "1.52",  # Docker 29.x的当前API版本
    ]
    
    for api_version in api_versions:
        try:
            print(f"\n尝试API版本: {api_version}")
            
            # 使用指定的API版本创建客户端
            client = docker.DockerClient(
                base_url='tcp://127.0.0.1:17788', 
                tls=False,
                version=api_version  # 手动指定API版本
            )
            
            # 测试连接
            version_info = client.version()
            print(f"✅ 成功连接！API版本: {version_info['ApiVersion']}")
            print(f"   Docker版本: {version_info['Version']}")
            print(f"   Git提交: {version_info['GitCommit']}")
            
            # 测试基本操作
            images = client.images.list()
            print(f"   本地镜像数量: {len(images)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            import traceback
            traceback.print_exc()
    
    return False

if __name__ == "__main__":
    test_api_versions()
