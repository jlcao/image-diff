import requests

# 测试不带版本前缀的Docker API
def test_no_version_api():
    print("测试不带版本前缀的Docker API...")
    
    # 测试不同的API路径格式
    urls = [
        "http://127.0.0.1:17788/version",
        "http://127.0.0.1:17788/",
        "http://127.0.0.1:17788/_ping",
        "http://127.0.0.1:17788/images/json",
    ]
    
    for url in urls:
        try:
            print(f"\n尝试访问: {url}")
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"响应内容: {response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text[:200]}")
            else:
                print(f"响应内容: {response.text}")
                
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_no_version_api()
