#!/usr/bin/env python3
"""
图片转换为WebP格式的Python脚本
支持无损转换并更新引用
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 配置
IMAGES_DIR = "/Users/channing/file/chen-blog/source/images"
POSTS_DIR = "/Users/channing/file/chen-blog/source/_posts"
CONFIG_FILES = [
    "/Users/channing/file/chen-blog/_config.yml",
    "/Users/channing/file/chen-blog/_config.butterfly.yml"
]

# 支持的图片格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

def check_cwebp():
    """检查是否安装了cwebp工具"""
    try:
        subprocess.run(['cwebp', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到cwebp命令。请先安装webp工具:")
        print("macOS: brew install webp")
        print("Ubuntu: sudo apt-get install webp")
        return False

def convert_image_to_webp(image_path):
    """将图片转换为WebP格式"""
    image_path = Path(image_path)
    webp_path = image_path.with_suffix('.webp')
    
    # 如果WebP文件已存在，跳过
    if webp_path.exists():
        print(f"跳过 (已存在): {image_path.name} -> {webp_path.name}")
        return webp_path, False
    
    print(f"转换: {image_path.name} -> {webp_path.name}")
    
    try:
        # 根据文件类型选择转换参数
        ext = image_path.suffix.lower()
        if ext == '.png':
            # PNG使用无损转换
            cmd = ['cwebp', '-lossless', '-q', '100', str(image_path), '-o', str(webp_path)]
        elif ext in ['.jpg', '.jpeg']:
            # JPEG使用高质量转换
            cmd = ['cwebp', '-q', '95', str(image_path), '-o', str(webp_path)]
        else:
            # 其他格式使用默认设置
            cmd = ['cwebp', '-q', '90', str(image_path), '-o', str(webp_path)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 检查文件大小
            original_size = image_path.stat().st_size
            webp_size = webp_path.stat().st_size
            compression_ratio = (1 - webp_size / original_size) * 100
            
            print(f"  ✓ 转换成功")
            print(f"  原文件: {original_size:,} bytes")
            print(f"  WebP文件: {webp_size:,} bytes")
            print(f"  压缩率: {compression_ratio:.1f}%")
            
            # 备份原文件
            backup_dir = image_path.parent / f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(exist_ok=True)
            shutil.move(str(image_path), str(backup_dir / image_path.name))
            print(f"  原文件已备份到: {backup_dir / image_path.name}")
            
            return webp_path, True
        else:
            print(f"  ✗ 转换失败: {result.stderr}")
            if webp_path.exists():
                webp_path.unlink()
            return None, False
            
    except Exception as e:
        print(f"  ✗ 转换出错: {e}")
        if webp_path.exists():
            webp_path.unlink()
        return None, False

def find_image_files(directory):
    """查找所有需要转换的图片文件"""
    image_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in IMAGE_EXTENSIONS:
                image_files.append(file_path)
    return image_files

def update_file_references(file_path, conversion_map):
    """更新文件中的图片引用"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # 更新所有图片扩展名为webp
        for old_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            pattern = re.compile(re.escape(old_ext), re.IGNORECASE)
            if pattern.search(content):
                content = pattern.sub('.webp', content)
                updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 已更新文件: {file_path}")
            return True
        else:
            print(f"  无需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ 更新文件失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("WebP图片转换工具")
    print("=" * 50)
    
    # 检查工具
    if not check_cwebp():
        sys.exit(1)
    
    # 创建转换日志
    log_file = "/tmp/webp_conversion.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"WebP转换日志 - {datetime.now()}\n")
    
    print(f"转换日志: {log_file}")
    print()
    
    # 查找所有图片文件
    print("扫描图片文件...")
    image_files = find_image_files(IMAGES_DIR)
    print(f"找到 {len(image_files)} 个图片文件需要转换")
    print()
    
    if not image_files:
        print("没有找到需要转换的图片文件")
        return
    
    # 转换图片
    print("开始转换图片...")
    conversion_map = {}
    converted_count = 0
    
    for image_file in image_files:
        webp_file, success = convert_image_to_webp(image_file)
        if success and webp_file:
            conversion_map[image_file.name] = webp_file.name
            converted_count += 1
        print()
    
    print(f"图片转换完成！成功转换 {converted_count} 个文件")
    print()
    
    # 更新引用
    print("更新文件中的图片引用...")
    
    # 更新Markdown文件
    print("更新Markdown文件...")
    md_files = list(Path(POSTS_DIR).glob("*.md"))
    for md_file in md_files:
        update_file_references(md_file, conversion_map)
    
    # 更新配置文件
    print("\n更新配置文件...")
    for config_file in CONFIG_FILES:
        if os.path.exists(config_file):
            update_file_references(config_file, conversion_map)
    
    # 更新其他文件
    print("\n更新其他可能包含图片引用的文件...")
    project_root = Path("/Users/channing/file/chen-blog")
    for pattern in ["*.yml", "*.yaml", "*.json", "*.html"]:
        for file_path in project_root.rglob(pattern):
            # 跳过某些目录
            if any(part in str(file_path) for part in ['node_modules', '.git', 'logs']):
                continue
            update_file_references(file_path, conversion_map)
    
    print()
    print("=" * 50)
    print("WebP转换和引用更新完成！")
    print("=" * 50)
    print(f"转换日志: {log_file}")
    print()
    print("建议操作：")
    print("1. 检查网站是否正常显示图片")
    print("2. 如果有问题，可以从备份目录恢复原文件")
    print("3. 确认无误后，可以删除备份目录以节省空间")
    print()
    print(f"备份目录位置: {IMAGES_DIR}/*/.backup_*")

if __name__ == "__main__":
    main()