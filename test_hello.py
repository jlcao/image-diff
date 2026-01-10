import docker

# 连接到远程Docker守护进程（端口17788）
client = docker.DockerClient(base_url='tcp://127.0.0.1:12375', tls=False)

# 测试拉取镜像（你的核心需求）
try:
    print("开始拉取 tomcat:9.0-jdk8-corretto 镜像...")
    image = client.images.pull('tomcat:9.0-jdk8-corretto')
    print(f"✅ 成功！镜像信息：{image.tags}")
except Exception as e:
    print(f"❌ 失败原因：{str(e)}")