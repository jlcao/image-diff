import os
import sys
import json
from datetime import datetime
from .utils import Utils

class HTMLGenerator:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 获取模板文件路径，兼容开发环境和PyInstaller打包环境
        if getattr(sys, 'frozen', False):
            # 运行在PyInstaller打包后的环境
            base_path = sys._MEIPASS
        else:
            # 运行在开发环境
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_path = os.path.join(base_path, 'docker_jar_diff', 'templates', 'report_template.html')
    
    def generate_report(self, diff_result):
        """Generate the main HTML report"""
        # 读取模板文件
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 替换模板中的占位符
        html_content = template_content.replace('{{timestamp}}', self.timestamp)
        # 将diff数据直接嵌入到HTML中，避免CORS问题
        html_content = html_content.replace('{{diff_data}}', json.dumps(diff_result))
        
        # 写入报告文件
        report_path = self.cache_manager.get_report_path()
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def generate_diff_page(self, file1, file2):
        """Generate a diff page for two files"""
        # This would be implemented to generate a proper diff page
        # For now, we'll just return a placeholder
        return None