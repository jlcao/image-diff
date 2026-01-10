# Docker JAR Diff

A tool to diff JAR files between Docker images.

## Features

- Compare JAR files between two Docker images
- Show differences in JAR content
- Easy to use command-line interface

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run docker-jar-diff <image1> <image2>
```

## Development

Run tests:

```bash
poetry run pytest
```

## 编译打包

### 环境要求
- Python 3.8+
- Docker SDK
- PyInstaller

### 虚拟环境搭建
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 打包Windows版本
```bash
# 使用PyInstaller打包
pyinstaller --onefile docker-jar-diff.spec

# 或直接运行
pyinstaller --onefile --hidden-import='docker' --hidden-import='click' --hidden-import='docker.api' --hidden-import='docker.api.build' --hidden-import='docker.models.containers' --hidden-import='requests' --hidden-import='urllib3' docker_jar_diff/cli.py
```

### 打包Linux版本 (WSL Debian)
```bash
# 进入WSL Debian环境
wsl -d Debian

# 进入项目目录
cd /mnt/d/resource/python/docker-jar-diff

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 打包
pyinstaller --onefile docker-jar-diff.spec

# 复制到Windows目录
cp dist/docker-jar-diff /mnt/d/resource/python/docker-jar-diff/dist/docker-jar-diff-linux
```

## 运行参数注意事项

### 基本用法
```bash
# Windows
docker-jar-diff.exe <image1> <image2>

# Linux
./docker-jar-diff-linux <image1> <image2>
```

### 参数说明
- `<image1>`: 第一个Docker镜像（基础镜像）
- `<image2>`: 第二个Docker镜像（对比镜像）

### 注意事项
1. **镜像格式**: 支持完整镜像名称（如`registry.example.com/app:v1`）和短名称（如`tomcat:9.0`）
2. **Docker连接**: 确保Docker守护进程正在运行，且配置文件中的`base_url`正确
3. **权限问题**: Linux版本需要执行权限，可通过`chmod +x docker-jar-diff-linux`添加
4. **内存限制**: 处理大型镜像时可能需要较多内存，建议至少4GB RAM
5. **网络问题**: 首次运行时需要拉取镜像，请确保网络连接正常

## 配置流程

### 配置文件位置
程序启动时会自动在`.config/config.json`生成默认配置文件。

### 配置内容
```json
{
  "docker": {
    "base_url": "tcp://127.0.0.1:12375",
    "tls": false
  },
  "beyond_compare": {
    "path": "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Beyond Compare 5\\BCompare.exe"
  }
}
```

### 配置说明
1. **Docker配置**
   - `base_url`: Docker守护进程地址
     - Windows: 默认`tcp://127.0.0.1:12375`
     - Linux/WSL: 使用Windows主机IP，如`tcp://192.168.1.209:12375`
   - `tls`: 是否启用TLS连接（布尔值）

2. **Beyond Compare配置**
   - `path`: Beyond Compare可执行文件路径
   - 仅在需要使用Beyond Compare进行差异对比时需要配置

### 配置修改方法
1. **手动修改**
   ```bash
   # 使用文本编辑器修改
   nano .config/config.json
   ```

2. **程序自动生成**
   - 首次运行程序时，若配置文件不存在，会自动生成默认配置
   - 默认配置适用于Windows环境，Linux/WSL环境需要修改`base_url`

### Docker守护进程配置
确保Docker守护进程开启远程访问：

**Windows Docker Desktop**:
1. 进入Settings -> General
2. 勾选"Expose daemon on tcp://localhost:2375 without TLS"

**Linux**:
1. 修改`/etc/docker/daemon.json`
   ```json
   {
     "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
   }
   ```
2. 重启Docker服务
   ```bash
   sudo systemctl restart docker
   ```