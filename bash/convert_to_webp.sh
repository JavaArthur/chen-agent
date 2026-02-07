#!/bin/bash

# 图片转换为WebP格式的脚本
# 支持无损转换并更新引用

IMAGES_DIR="/Users/channing/file/chen-blog/source/images"
POSTS_DIR="/Users/channing/file/chen-blog/source/_posts"
CONFIG_FILES=("/Users/channing/file/chen-blog/_config.yml" "/Users/channing/file/chen-blog/_config.butterfly.yml")

# 检查是否安装了cwebp
if ! command -v cwebp >/dev/null 2>&1; then
    echo "错误: 未找到cwebp命令。请先安装webp工具:"
    echo "macOS: brew install webp"
    echo "Ubuntu: sudo apt-get install webp"
    exit 1
fi

# 创建转换日志
CONVERSION_LOG="/tmp/webp_conversion.log"
echo "WebP转换日志 - $(date)" > "$CONVERSION_LOG"

echo "开始扫描和转换图片..."

# 查找所有需要转换的图片文件
find "$IMAGES_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.tiff" \) | while read -r file; do
    # 获取文件信息
    dir=$(dirname "$file")
    filename=$(basename "$file")
    name="${filename%.*}"
    ext="${filename##*.}"
    
    # 生成webp文件名
    webp_file="$dir/$name.webp"
    
    echo "转换: $file -> $webp_file"
    
    # 转换扩展名为小写
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    
    # 根据文件类型选择转换参数
    case "$ext_lower" in
        "png")
            # PNG使用无损转换
            if cwebp -lossless -q 100 "$file" -o "$webp_file"; then
                echo "✓ 成功转换 (无损): $filename -> $name.webp" | tee -a "$CONVERSION_LOG"
            else
                echo "✗ 转换失败: $filename" | tee -a "$CONVERSION_LOG"
                continue
            fi
            ;;
        "jpg"|"jpeg")
            # JPEG使用高质量转换
            if cwebp -q 95 "$file" -o "$webp_file"; then
                echo "✓ 成功转换 (高质量): $filename -> $name.webp" | tee -a "$CONVERSION_LOG"
            else
                echo "✗ 转换失败: $filename" | tee -a "$CONVERSION_LOG"
                continue
            fi
            ;;
        "gif")
            # GIF转换为动画WebP
            if cwebp -q 90 "$file" -o "$webp_file"; then
                echo "✓ 成功转换 (GIF): $filename -> $name.webp" | tee -a "$CONVERSION_LOG"
            else
                echo "✗ 转换失败: $filename" | tee -a "$CONVERSION_LOG"
                continue
            fi
            ;;
        *)
            # 其他格式使用默认设置
            if cwebp -q 90 "$file" -o "$webp_file"; then
                echo "✓ 成功转换: $filename -> $name.webp" | tee -a "$CONVERSION_LOG"
            else
                echo "✗ 转换失败: $filename" | tee -a "$CONVERSION_LOG"
                continue
            fi
            ;;
    esac
    
    # 验证转换后的文件
    if [[ -f "$webp_file" && $(stat -f%z "$webp_file") -gt 0 ]]; then
        echo "  文件大小对比:"
        echo "    原文件: $(stat -f%z "$file") bytes"
        echo "    WebP文件: $(stat -f%z "$webp_file") bytes"
        
        # 计算压缩率
        original_size=$(stat -f%z "$file")
        webp_size=$(stat -f%z "$webp_file")
        compression_ratio=$(echo "scale=2; (1 - $webp_size / $original_size) * 100" | bc)
        echo "    压缩率: ${compression_ratio}%"
        
        # 备份原文件
        backup_dir="$dir/.backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        mv "$file" "$backup_dir/"
        echo "  原文件已备份到: $backup_dir/$filename"
    else
        echo "✗ WebP文件创建失败或为空，跳过删除原文件"
        rm -f "$webp_file"
    fi
done

echo ""
echo "图片转换完成！"
echo "转换日志保存在: $CONVERSION_LOG"
echo ""
echo "接下来将更新文件中的图片引用..."

# 更新Markdown文件中的图片引用
update_references() {
    local file="$1"
    local temp_file=$(mktemp)
    local updated=false
    
    echo "检查文件: $file"
    
    # 读取转换映射并更新引用
    while IFS= read -r line; do
        updated_line="$line"
        
        # 查找图片引用模式
        if echo "$line" | grep -qE '\!\[.*\]\([^)]*\.(jpg|jpeg|png|gif|bmp|tiff)\)' || 
           echo "$line" | grep -qE '["\'"'"']/[^"'"'"']*\.(jpg|jpeg|png|gif|bmp|tiff)["\'"'"']' ||
           echo "$line" | grep -qE '\.(jpg|jpeg|png|gif|bmp|tiff)'; then
            
            # 替换各种图片格式
            updated_line=$(echo "$line" | sed -E 's/\.(jpg|jpeg|png|gif|bmp|tiff)/.webp/g')
            
            if [[ "$updated_line" != "$line" ]]; then
                echo "  更新引用: $line"
                echo "         -> $updated_line"
                updated=true
            fi
        fi
        
        echo "$updated_line" >> "$temp_file"
    done < "$file"
    
    if [[ "$updated" == true ]]; then
        mv "$temp_file" "$file"
        echo "✓ 已更新文件: $file"
    else
        rm "$temp_file"
        echo "  无需更新: $file"
    fi
}

# 更新所有Markdown文件
echo "更新Markdown文件中的图片引用..."
find "$POSTS_DIR" -name "*.md" | while read -r md_file; do
    update_references "$md_file"
done

# 更新配置文件
echo ""
echo "更新配置文件中的图片引用..."
for config_file in "${CONFIG_FILES[@]}"; do
    if [[ -f "$config_file" ]]; then
        update_references "$config_file"
    fi
done

# 更新其他可能包含图片引用的文件
echo ""
echo "更新其他文件中的图片引用..."
find "/Users/channing/file/chen-blog" -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.html" | while read -r file; do
    # 跳过node_modules等目录
    if [[ "$file" =~ node_modules|\.git|logs ]]; then
        continue
    fi
    update_references "$file"
done

echo ""
echo "=========================================="
echo "WebP转换和引用更新完成！"
echo "=========================================="
echo "转换日志: $CONVERSION_LOG"
echo ""
echo "建议操作："
echo "1. 检查网站是否正常显示图片"
echo "2. 如果有问题，可以从备份目录恢复原文件"
echo "3. 确认无误后，可以删除备份目录以节省空间"
echo ""
echo "备份目录位置: $IMAGES_DIR/*/.backup_*"