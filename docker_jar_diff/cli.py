import click
from docker_jar_diff.main import DockerJarDiff

@click.command()
@click.argument('image1')
@click.argument('image2')
@click.option('--compare-dir', '-d', help='指定镜像内要比较的目录')
@click.option('--cache-dir', '-c', help='指定缓存目录')
def docker_jar_diff(image1, image2, compare_dir=None, cache_dir=None):
    """对比两个docker镜像.
    
    配置存放于当前目录的 .config/config.json
    
    配置示例:
    {
    \n\t"docker": {
    \n\t\t"base_url": "tcp://127.0.0.1:12375",
    \n\t\t"tls": false
    \n\t},
    \n\t"beyond_compare": {
    \n\t\t"path": "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Beyond Compare 5\\BCompare.exe"
    \n\t}\n
    }

    IMAGE1: 第一个镜像 name/tag \n
    IMAGE2: 第二个镜像 name/tag
    
    Options:
    --compare-dir, -d: 指定镜像内要比较的目录 (default: /)
    --cache-dir, -c: 指定缓存目录 (default: ./cache)
    """
    diff_tool = DockerJarDiff(cache_dir)
    diff_tool.run_diff(image1, image2, compare_dir)

if __name__ == "__main__":
    docker_jar_diff()