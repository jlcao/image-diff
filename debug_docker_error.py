import docker
import requests
from docker.api.client import APIClient

# 直接使用API客户端调试
print("直接使用API客户端调试...")

# 初始化API客户端
client = APIClient(base_url='tcp://127.0.0.1:17788', tls=False)

# 尝试直接调用API
try:
    print("尝试调用API...")
    # 直接使用requests库调用API
    response = requests.get('http://127.0.0.1:17788/version', timeout=5)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容类型: {type(response.content)}")
    print(f"响应内容: {response.content}")
    print(f"响应文本: {response.text}")
    
    # 检查响应编码
    print(f"响应编码: {response.encoding}")
    
    # 尝试用不同编码解码
    encodings = ['utf-8', 'latin-1', 'gbk', 'utf-16']
    for enc in encodings:
        try:
            decoded = response.content.decode(enc)
            print(f"\n用{enc}解码:")
            print(f"  成功: {decoded[:200]}...")
        except Exception as e:
            print(f"\n用{enc}解码失败: {e}")
    
except Exception as e:
    print(f"总错误: {e}")
    import traceback
    traceback.print_exc()
