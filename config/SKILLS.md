## Skill: A股收盘日报生成（稳定版）

**Version:** 2.0.0  
**Domain:** 金融数据/定时报告/高可用数据采集

### Trigger
工作日 16:00（A股收盘后）自动生成并推送收盘日报

### Core Logic
1. **多源并行请求**（3个数据源同时请求）
   - 主源：东方财富 API（带时间戳参数防缓存）
   - 备用1：新浪财经（实时行情接口）
   - 备用2：乐咕乐股（市场活跃度数据）
   - 策略：任一成功即返回，其他自动取消
   - **关键：必须验证数据日期=当日，否则标记为过期数据**

2. **日期验证（强制）**
   - 获取数据后检查日期字段
   - 如日期≠当日，立即切换备用源
   - 如所有源均为历史数据，报告顶部标注"⚠️ 数据日期：YYYY-MM-DD（非今日）"

2. **超时控制**
   - 每个请求 10s 硬超时
   - 超时立即切换下一数据源
   - 总超时 2 分钟

3. **子会话心跳**
   - 每 30 秒向主会话汇报进度
   - 使用 sessions_send 发送状态

4. **兜底机制**
   - 2 分钟内未完成 → 发送简化版报告
   - 确保用户必收到信息

### Dependency
- `web_fetch` / `curl`（东方财富/新浪）
- `message`（Telegram 推送）
- `sessions_send`（子会话心跳）

### Data Points
- 三大指数点位+涨跌幅
- 两市成交额
- 涨跌家数+涨停跌停数
- 板块 TOP5 涨跌
- 龙虎榜游资动向

### Output Format
Markdown 表格，红涨绿跌配色，简洁有力

### Push Target
- **Telegram 私聊**: 8194337575
- **Telegram 群聊**: -5263836421（双发确保送达）
- **博客发布**: 同步发布到 chen-blog（Hexo + Vercel）
  - 文章位置: `source/_posts/YYYYMMDD-title.md`
  - 自动触发 Vercel 部署
  - 作为对外窗口，不含敏感信息
  - 可包含：市场分析、每日思考、学习心得

### Performance
- 成功率目标：>99%
- 平均响应：10-30s
- 最大延迟：2分钟（含兜底）

### Changelog
- v1.0: 基础版本，单数据源，偶发卡顿
- v2.0: 稳定版，多源并行+超时控制+兜底机制

---

## Skill: 期货避险雷达（稳定版）

**Version:** 2.0.0  
**Domain:** 金融风控/避险资产监控

### Trigger
每日 08:00 & 20:00（北京时间）检查黄金/白银期货

### Core Logic
1. **数据源优先级**
   - 主源：TradingEconomics（网页抓取）
   - 备用1：Yahoo Finance（yfinance）
   - 备用2：Goldprice.org API

2. **阈值控制**
   - 触发阈值：|涨跌幅| > 5%
   - 日常波动不打扰

3. **A股联动分析**
   - 贵金属板块影响
   - 避险情绪传导
   - 资金流向预判

### Dependency
- `web_fetch` / `ducksearch`
- `message`（Telegram 推送）

### Performance
- 监控频率：每日2次
- 误报率：<5%

### Changelog
- v1.0: 每30分钟检查，过于频繁
- v2.0: 每日2次+5%阈值，降低打扰

---

## Skill: 多源数据采集（通用框架）

**Version:** 1.0.0  
**Domain:** 数据采集/高可用性

### Pattern
适用于任何需要高可靠性的数据采集场景

### Core Logic
```python
def fetch_with_fallback(sources, timeout=10, max_total_time=120):
    """
    sources: [{name, url, parser}, ...]
    并行请求所有源，任一成功即返回
    超时自动切换，总时长控制
    """
```

### Key Principles
1. **Fail Fast**: 超时立即失败，不等待
2. **Parallel**: 多源同时请求，取最快成功
3. **Graceful Degrade**: 部分数据缺失也能输出
4. **Always Deliver**: 兜底机制确保有输出

### Use Cases
- A股收盘数据采集
- 期货价格监控
- 新闻快讯聚合
- 任何外部API依赖场景

---

---

## Skill: 博客文章发布（Hexo + Vercel）

**Version:** 1.0.0  
**Domain:** 内容发布/自动化写作

### Trigger
- 每日早报生成后（08:30）→ 发布盘前简报
- 每日复盘生成后（16:00）→ 发布收盘复盘
- 每日对话结束后（22:00）→ 发布对话总结
- 用户手动要求发布文章

### Core Logic
1. **内容准备**
   - 接收 Telegram 推送的原始内容
   - 格式化为 Hexo 文章 Front-matter 格式
   - 添加标签、分类、日期

2. **安全审查（强制）**
   - ✅ 可以包含：市场分析、技术学习、每日思考、心情随笔
   - ❌ 严禁包含：API Key、Token、密码、个人隐私、交易策略细节
   - 审查原则：假设文章会被任何人看到

3. **GitHub 提交**
   - 文件路径: `source/_posts/YYYYMMDD-title.md`
   - 使用 GitHub API 直接提交
   - Commit message: "博客更新: 标题 - via Cypher"

4. **Vercel 自动部署**
   - 提交后 Vercel 自动触发构建
   - 约 1-2 分钟后在线可访问
   - 博客地址: https://chen-blog.vercel.app

### Front-matter 模板
```yaml
---
title: "文章标题"
date: YYYY-MM-DD HH:MM:SS
tags: [标签1, 标签2]
categories: [分类]
---

正文内容...

---
*本文由 Cypher 自动生成于 YYYY-MM-DD*
*GitHub: https://github.com/JavaArthur/chen-blog*
```

### Dependency
- GitHub API Token（已配置）
- chen-blog 仓库写入权限

### Output
- GitHub Commit URL
- 博客文章预览链接

### Changelog
- v1.0: 初始版本，支持自动发布早报和复盘

---

*Skills last updated: 2026-02-02*  
*Author: Cypher for Channing*
