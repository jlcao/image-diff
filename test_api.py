import requests

# 测试Docker API连接
def test_docker_api():
    print("测试Docker API连接...")
    
    # 尝试不同的API路径
    urls = [
        "http://127.0.0.1:17788/version",
        "http://127.0.0.1:17788/v1.52/version",
        "http://127.0.0.1:17788/v1.44/version",
        "http://[::1]:17788/version",  # IPv6地址
    ]
    
    for url in urls:
        try:
            print(f"\n尝试访问: {url}")
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    test_docker_api()
