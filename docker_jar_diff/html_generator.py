import os
import json
from datetime import datetime
from .utils import Utils

class HTMLGenerator:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_report(self, diff_result):
        """Generate the main HTML report"""
        # Create HTML content
        html_content = self._get_html_header()
        html_content += self._get_html_body(diff_result)
        html_content += self._get_html_footer()
        
        # Write to file
        report_path = self.cache_manager.get_report_path()
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _get_html_header(self):
        """Get HTML header"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docker镜像差异比对报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .header-info {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .directory-tree {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .tree-node {
            margin-left: 20px;
            position: relative;
        }
        
        .tree-node:before {
            content: '';
            position: absolute;
            left: 0;
            top: 10px;
            width: 15px;
            height: 1px;
            background-color: #ccc;
        }
        
        .tree-node:after {
            content: '';
            position: absolute;
            left: 0;
            top: 10px;
            bottom: -10px;
            width: 1px;
            background-color: #ccc;
        }
        
        .tree-node:last-child:after {
            display: none;
        }
        
        .node-item {
            display: flex;
            align-items: center;
            padding: 5px 0;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .node-item:hover {
            background-color: #f0f0f0;
        }
        
        .node-item.expanded {
            background-color: #e3f2fd;
        }
        
        .folder-icon {
            margin-right: 5px;
            color: #ff9800;
        }
        
        .file-icon {
            margin-right: 5px;
            color: #2196f3;
        }
        
        .diff-indicator {
            margin-left: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .diff-content {
            background-color: #ffebee;
            color: #c62828;
        }
        
        .diff-size {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        
        .diff-mtime {
            background-color: #fff3e0;
            color: #ef6c00;
        }
        
        .only-in-1 {
            background-color: #e3f2fd;
            color: #1565c0;
        }
        
        .only-in-2 {
            background-color: #f3e5f5;
            color: #7b1fa2;
        }
        
        .jar-expand {
            margin-left: 10px;
            color: #4caf50;
            font-size: 12px;
            cursor: pointer;
        }
        
        .jar-content {
            margin-left: 20px;
            margin-top: 5px;
            display: none;
        }
        
        .jar-content.expanded {
            display: block;
        }
        
        .file-info {
            margin-left: auto;
            font-size: 12px;
            color: #757575;
        }
        
        .file-size {
            margin-right: 15px;
        }
        
        .file-mtime {
            margin-right: 15px;
        }
        
        .diff-button {
            background-color: #2196f3;
            color: white;
            border: none;
            padding: 2px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }
        
        .diff-button:hover {
            background-color: #1976d2;
        }
    </style>
</head>
'''
    
    def _get_html_body(self, diff_result):
        """Get HTML body"""
        body = f'''<body>
    <div class="container">
        <h1>Docker镜像差异比对报告</h1>
        
        <div class="header-info">
            <p><strong>比对时间:</strong> {self.timestamp}</p>
            <p><strong>镜像1:</strong> {diff_result['dir1'].split(os.sep)[-1]}</p>
            <p><strong>镜像2:</strong> {diff_result['dir2'].split(os.sep)[-1]}</p>
            <p><strong>比对目录:</strong> {diff_result['compare_dir']}</p>
            <p><strong>差异文件数量:</strong> {len(diff_result['differences'])}</p>
        </div>
        
        <div class="directory-tree">
            <div class="tree-node">
                <div class="node-item" onclick="toggleNode(this)">
                    <span class="folder-icon">📁</span>
                    <span>{diff_result['compare_dir']}</span>
                </div>
                <div class="tree-node">
'''
        
        # Build the directory tree
        directory_structure = self._build_directory_structure(diff_result['differences'])
        body += self._render_directory_structure(directory_structure)
        
        body += '''
                </div>
            </div>
        </div>
    </div>
'''
        
        body += self._get_javascript()
        body += '''
</body>
'''
        
        return body
    
    def _get_html_footer(self):
        """Get HTML footer"""
        return '''</html>'''
    
    def _build_directory_structure(self, differences):
        """Build a hierarchical directory structure from differences"""
        structure = {}
        
        for diff in differences:
            path = diff['path']
            path_parts = path.split('/')
            
            current = structure
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[path_parts[-1]] = diff
        
        return structure
    
    def _render_directory_structure(self, structure, level=0):
        """Render the directory structure as HTML"""
        html = ''
        
        for name, item in sorted(structure.items()):
            if isinstance(item, dict):
                # Check if it's a directory (no 'type' key) or a file diff
                if 'type' not in item:
                    # Directory
                    html += f'''<div class="tree-node">
    <div class="node-item" onclick="toggleNode(this)">
        <span class="folder-icon">📁</span>
        <span>{name}</span>
    </div>
    <div class="tree-node" style="display: none;">
'''
                    html += self._render_directory_structure(item, level + 1)
                    html += '''
    </div>
</div>
'''
                else:
                    # File with differences
                    diff = item
                    html += self._render_diff_item(diff, level)
            else:
                # Handle unexpected item type
                html += f'''<div class="tree-node">
    <div class="node-item diff-error" style="padding-left: {level * 20}px;">
        <span>⚠️ 无效的目录项: {name}</span>
    </div>
</div>'''
        
        return html
    
    def _render_diff_item(self, diff, level):
        """Render a single diff item"""
        # Add type checking to avoid TypeError
        if not isinstance(diff, dict) or 'type' not in diff:
            # Handle unexpected diff type
            return f'''<div class="tree-node">
    <div class="node-item diff-error" style="padding-left: {level * 20}px;">
        <span>⚠️ 无效的差异条目</span>
    </div>
</div>'''
            
        diff_class = diff['type']
        
        # Determine icon and display info
        if diff['type'] == 'only_in_1' and 'item1' in diff and isinstance(diff['item1'], dict):
            icon = '📄'
            info1 = f"<span class='file-size'>{self._format_size(diff['item1'].get('size', 0))}</span>"
            info1 += f"<span class='file-mtime'>{diff['item1'].get('mtime', '')}</span>"
            info2 = "<span>不存在</span>"
        elif diff['type'] == 'only_in_2' and 'item2' in diff and isinstance(diff['item2'], dict):
            icon = '📄'
            info1 = "<span>不存在</span>"
            info2 = f"<span class='file-size'>{self._format_size(diff['item2'].get('size', 0))}</span>"
            info2 += f"<span class='file-mtime'>{diff['item2'].get('mtime', '')}</span>"
        elif 'item1' in diff and 'item2' in diff and isinstance(diff['item1'], dict) and isinstance(diff['item2'], dict):
            icon = '📄'
            info1 = f"<span class='file-size'>{self._format_size(diff['item1'].get('size', 0))}</span>"
            info1 += f"<span class='file-mtime'>{diff['item1'].get('mtime', '')}</span>"
            info2 = f"<span class='file-size'>{self._format_size(diff['item2'].get('size', 0))}</span>"
            info2 += f"<span class='file-mtime'>{diff['item2'].get('mtime', '')}</span>"
        
        # Check if it's a JAR file
        is_jar = diff.get('path', '').lower().endswith('.jar')
        jar_expand_html = ''
        jar_content_html = ''
        
        if is_jar and 'jar_diff' in diff:
            jar_expand_html = f"<span class='jar-expand' onclick='toggleJar(this)'>[展开JAR差异]</span>"
            jar_content_html = f"<div class='jar-content'>{self._render_jar_diff(diff['jar_diff'])}</div>"
        
        # Safely get filename from path
        filename = ''
        if 'path' in diff:
            try:
                filename = os.path.basename(diff['path'])
            except:
                filename = str(diff.get('path', ''))
        
        # Safely get file paths for diff view
        item1_path = ''
        if 'item1' in diff and isinstance(diff['item1'], dict):
            item1_path = diff['item1'].get('path', '')
        
        item2_path = ''
        if 'item2' in diff and isinstance(diff['item2'], dict):
            item2_path = diff['item2'].get('path', '')
        
        html = f'''<div class="tree-node">
    <div class="node-item">
        <span class="file-icon">{icon}</span>
        <span>{filename}</span>
        <span class="diff-indicator {diff_class}">{self._get_diff_type_text(diff['type'])}</span>
        {jar_expand_html}
        <button class="diff-button" onclick="showDiff('{item1_path}', '{item2_path}')">查看差异</button>
        <div class="file-info">
            <span>镜像1: {info1}</span>
            <span>镜像2: {info2}</span>
        </div>
    </div>
    {jar_content_html}
</div>
'''
        
        return html
    
    def _render_jar_diff(self, jar_diff):
        """Render JAR file differences"""
        html = ''
        
        for diff in jar_diff:
            diff_class = diff['type']
            html += f'''<div class="tree-node">
    <div class="node-item">
        <span class="file-icon">📄</span>
        <span>{os.path.basename(diff['path'])}</span>
        <span class="diff-indicator {diff_class}">{self._get_diff_type_text(diff['type'])}</span>
    </div>
</div>
'''
        
        return html
    
    def _get_diff_type_text(self, diff_type):
        """Get human-readable text for diff type"""
        diff_type_map = {
            'content_diff': '内容差异',
            'size_diff': '大小差异',
            'mtime_diff': '时间差异',
            'only_in_1': '仅在镜像1',
            'only_in_2': '仅在镜像2',
            'type_mismatch': '类型不匹配'
        }
        return diff_type_map.get(diff_type, diff_type)
    
    def _format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def _get_javascript(self):
        """Get JavaScript code for interactivity"""
        return '''
    <script>
        function toggleNode(element) {
            const node = element.parentElement;
            const children = node.querySelector('.tree-node');
            
            if (children) {
                if (children.style.display === 'none' || children.style.display === '') {
                    children.style.display = 'block';
                    element.classList.add('expanded');
                } else {
                    children.style.display = 'none';
                    element.classList.remove('expanded');
                }
            }
        }
        
        function toggleJar(element) {
            const jarContent = element.parentElement.parentElement.querySelector('.jar-content');
            if (jarContent) {
                jarContent.classList.toggle('expanded');
                if (jarContent.classList.contains('expanded')) {
                    element.textContent = '[收起JAR差异]';
                } else {
                    element.textContent = '[展开JAR差异]';
                }
            }
        }
        
        function showDiff(file1, file2) {
            // This function would be implemented to show diff in a new window
            // For now, we'll just show an alert
            alert(`Showing diff between:\n${file1}\nand\n${file2}`);
        }
    </script>
'''
    
    def generate_diff_page(self, file1, file2):
        """Generate a diff page for two files"""
        # This would be implemented to generate a proper diff page
        # For now, we'll just return a placeholder
        return None