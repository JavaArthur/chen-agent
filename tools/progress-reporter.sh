# Progress Reporter for Discord
# 实时进度推送工具

function report_progress() {
    local stage="$1"
    local status="$2"
    local progress="$3"
    local details="$4"
    
    # 发送到 Discord（通过环境变量或配置文件获取 webhook/channel）
    curl -s -X POST "${DISCORD_WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{
            \"content\": \"⏳ **进度更新**\\n\\n阶段: ${stage}\\n状态: ${status}\\n进度: ${progress}\\n详情: ${details}\"
        }" > /dev/null 2>&1 &
}

# 使用示例：
# report_progress "信息采集" "进行中" "25%" "已抓取5/18个信源"
# report_progress "文章撰写" "完成" "75%" "共2300字"
