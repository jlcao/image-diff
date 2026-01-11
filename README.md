# Docker JAR Diff

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

一个强大的Docker镜像JAR文件差异比较工具，能够深度分析两个Docker镜像之间的JAR文件差异，并生成直观的HTML报告。

## 🚀 核心功能

- **镜像JAR文件对比**: 深度比较两个Docker镜像中的所有JAR文件
- **JAR内容差异分析**: 解析JAR文件并比较其内部文件结构和内容
- **直观的HTML报告**: 生成树状结构的差异报告，支持目录展开/折叠
- **时间戳保留**: 精确保留原始文件的修改时间
- **自动浏览器打开**: 生成报告后自动在默认浏览器中打开
- **跨平台支持**: 支持Windows、macOS和Linux系统

## 📋 技术特点

| 特性 | 描述 |
|------|------|
| **差异检测** | 支持文件新增、删除、修改等多种差异类型 |
| **树状展示** | 目录结构以树状表格形式展示，支持多级展开 |
| **默认展开** | 自动展开包含多个子节点的目录层级 |
| **镜像名称识别** | 正确解析并显示Docker镜像名称和版本 |
| **缓存管理** | 智能管理临时文件，避免权限问题 |
| **错误处理** | 完善的错误处理和用户友好的提示信息 |

## 🛠️ 安装方法

### 环境要求
- Python 3.8+
- Docker 19.03+
- Git (可选)

### 方法一：使用 Poetry (推荐)

```bash
# 克隆项目
git clone https://github.com/yourusername/docker-jar-diff.git
cd docker-jar-diff

# 安装依赖
poetry install
```

### 方法二：使用虚拟环境

```bash
# 克隆项目
git clone https://github.com/yourusername/docker-jar-diff.git
cd docker-jar-diff

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 📖 使用指南

### 基本用法

```bash
# 使用 Poetry
poetry run docker-jar-diff <image1> <image2>

# 使用虚拟环境
docker-jar-diff <image1> <image2>
```

### 示例

```bash
# 比较两个Tomcat镜像
poetry run docker-jar-diff tomcat:9.0-jdk8-corretto tomcat:9.0-jdk11-corretto

# 比较完整镜像名称
poetry run docker-jar-diff registry.example.com/app:v1 registry.example.com/app:v2
```

### 报告查看

生成的差异报告将保存在项目目录下的 `.compare_cache` 文件夹中，并自动在默认浏览器中打开。

## 🎯 配置说明

### 配置文件

程序首次运行时会自动生成配置文件 `.config/config.json`，内容如下：

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

### Docker配置

确保Docker守护进程已开启远程访问：

#### Windows Docker Desktop
1. 进入 Settings → General
2. 勾选 "Expose daemon on tcp://localhost:2375 without TLS"

#### Linux
1. 修改 `/etc/docker/daemon.json`
   ```json
   {
     "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
   }
   ```
2. 重启Docker服务
   ```bash
   sudo systemctl restart docker
   ```

## 🏗️ 开发与测试

### 运行测试

```bash
# 使用 Poetry
poetry run pytest

# 使用虚拟环境
pytest
```

### 编译打包

#### Windows版本

```bash
# 使用PyInstaller打包
pyinstaller --onefile docker-jar-diff.spec
```

#### Linux版本

```bash
# 在Linux环境中打包
pyinstaller --onefile docker-jar-diff.spec
```

## 📊 报告说明

### 报告结构

- **头部信息**: 显示镜像名称、版本和比较目录
- **差异统计**: 显示总的差异数量
- **树状表格**:
  - **目录**: 文件/目录路径，支持树状展开
  - **差异类型**: 新增、删除、修改等
  - **镜像一文件信息**: 大小、修改时间、MD5
  - **镜像二文件信息**: 大小、修改时间、MD5

### 差异类型

| 类型 | 描述 |
|------|------|
| **新增** | 文件在镜像一中不存在，在镜像二中新增 |
| **删除** | 文件在镜像一中存在，在镜像二中删除 |
| **修改** | 文件在两个镜像中都存在，但内容有差异 |
| **大小差异** | 文件内容相同，但大小不同 |
| **MD5差异** | 文件大小相同，但内容不同 |

## 📝 注意事项

1. **权限问题**: 确保当前用户有权限访问Docker守护进程
2. **网络连接**: 首次使用时需要下载Docker镜像，请确保网络连接正常
3. **内存限制**: 处理大型镜像时建议至少4GB RAM
4. **Windows路径**: 在Windows系统中使用时，注意路径分隔符
5. **安全提示**: 不要在生产环境中暴露Docker守护进程到公网

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Docker SDK for Python](https://github.com/docker/docker-py)
- [Beyond Compare](https://www.scootersoftware.com/)
- [PyInstaller](https://www.pyinstaller.org/)

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: your.email@example.com
- GitHub: [yourusername/docker-jar-diff](https://github.com/yourusername/docker-jar-diff)

---

**Docker JAR Diff** - 让Docker镜像差异比较变得简单直观！