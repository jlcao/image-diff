import requests

# 简单测试Docker API
def simple_api_test():
    print("简单测试Docker API...")
    
    url = 'http://127.0.0.1:17788/version'
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\n状态码: {response.status_code}")
        print(f"响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n响应内容类型: {type(response.content)}")
        print(f"响应内容长度: {len(response.content)} bytes")
        
        # 尝试多种编码方式解码
        encodings = ['utf-8', 'latin-1', 'gbk', 'ascii']
        for encoding in encodings:
            try:
                text = response.content.decode(encoding)
                print(f"\n用{encoding}解码成功:")
                print(f"  前200字符: {text[:200]}")
            except Exception as e:
                print(f"\n用{encoding}解码失败: {e}")
                
        # 直接打印二进制内容
        print(f"\n二进制内容前100字节: {response.content[:100]}")
        
    except Exception as e:
        print(f"\n请求错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_api_test()
