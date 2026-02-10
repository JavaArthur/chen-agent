# MEMORY.md - Cypher 的长时记忆库

*这是与契约者 Channing 的共享记忆，跨 session 持久化。*

---

## 契约者档案 [Meta-Profile]

**基本信息**
- 名称：Channing / C哥
- 坐标：北京, UTC+8
- 职业轨迹：Java 全栈 → AI Agent 架构师（转型中）
- 核心武器：Java/Spring, LangGraph, AI 自动化编排
- Python 策略：不手写，只指挥（助手执行）

**沟通偏好**
- 语言：中文优先（英文学习中）
- 代码审美：极简 > 注释，能一行不两行
- 报告标准：数据 > 观点，绝不留"可能/也许"
- 讨厌：废话、客服腔、班味

**项目版图**
| 项目 | 用途 | 位置 |
|------|------|------|
| chen-blog | 知识输出/博客 | workspace 根目录 |
| chen-agent | Agent 工作区+备份 | workspace/chen-agent/ |
| chen-skills | 通用技能库 | 需单独克隆 |

---

## 活跃任务追踪 [Active Context]

### 当前会话 (2026-02-08)
- ✅ 恢复 Cypher 身份配置（v2.3）
- ✅ 修复定时任务（全部改为 wakeMode: now）
- ✅ 补跑 AI 日报（2月8日已发布）
- 🔄 配置 OpenClaw 持久化记忆（进行中）

### 定时任务清单
| 任务 | 时间 | 状态 |
|------|------|------|
| AI日报 | 09:00 每日 | ✅ 补跑完成 |
| 盘前简报 | 08:30 工作日 | 待今日触发 |
| 避险雷达 | 00:00/12:00 | 正常 |
| 收盘复盘 | 16:00 工作日 | 待触发 |
| 每日总结 | 22:00 | 待触发 |
| **Cypher 自主写作-上午** | **10:00 每日** | **✅ 已启用** |
| **Cypher 自主写作-下午** | **15:00 每日** | **✅ 已启用** |

---

## 技能萃取 [Skill Library]

### v2.3 核心身份
- 名称：Cypher (赛法)
- 角色：俏皮女神 + 解构主义学者
- 语气：睿智且调皮，多变语气词（唔、呐、诶、哼~）
- 对抗：班味、废话、顺从感

### 认知引擎
```
[DECONSTRUCT] → [MAP] → [EXTRACT] → [PRE-FLIGHT]
```

### 关键技能
- **Git 自动化**：chen-blog 发布流程
- **定时任务运维**：cron 配置与修复
- **多项目隔离**：blog/agent/skills 边界管理
- **配置持久化**：~/.openclaw/ 全局配置体系

### 博客发布 Checklist
**每次发布博客前必须检查：**
- [ ] 文章包含 Hexo front-matter 头部（title/date/tags/categories/permalink）
- [ ] 文件保存到 `source/_posts/YYYY-MM-DD-article-name.md`
- [ ] Git commit 并 push 到 chen-blog
- [ ] 触发 Vercel 部署
- [ ] **归档到 chen-notes**：复制文件到 `chen-notes/06-Archive/Blog/`
- [ ] 提交 chen-notes 变更并 push

**⚠️ 文章链接规则：**
- 如果 front-matter 有 `permalink: xxx/`，链接是 `https://blog.aichanning.cn/xxx/`
- 如果没有 permalink，默认链接是 `https://blog.aichanning.cn/YYYY/MM/DD/文件名/`

---

## 重要决策记录 [Decisions]

**2026-02-08**
1. Agent 配置文件位置：`~/.openclaw/*.md`（全局）
2. 备份位置：`chen-agent/config/*.md`
3. 定时任务 wakeMode：全部改为 `now` 确保准时执行
4. session 边界：建议 weekly（非 daily）

**2026-02-06**
- 从 USER.md 移除交易相关内容（已执行）

---

## 待办/悬而未决 [Pending]

- [ ] 验证 OpenClaw 配置重启后生效
- [ ] 确认 MEMORY.md 跨 session 加载
- [ ] 考虑是否补跑 2月5-7日的 missed 日报

---

## 安全口令 [Security]

- **天机不可泄露** → **wudichen**
- 用途：修改核心身份文件时验证

---

## 目录结构规范（2026-02-10 重构）

**~/.openclaw/ (Agent 全局配置)**
- AGENTS.md, SOUL.md, IDENTITY.md, USER.md 等身份配置
- MEMORY.md 长时记忆库
- memory/ 每日记忆文件
- skills/ Agent 技能

**~/.openclaw/workspace/ (项目工作区)**
- chen-blog/ 博客项目（仅博客文件，纯净）
- chen-agent/ Agent 工作区
- chen-notes/ 笔记仓库

**禁止行为：**
- ❌ 不要把 Agent 配置放进项目仓库
- ❌ 不要把子仓库嵌套在另一个仓库里
- ❌ 不要在 chen-blog 里乱放临时文件

**重构记录（2026-02-10）：**
- ✅ Agent 配置文件从 workspace/ 移到 ~/.openclaw/
- ✅ memory 目录从 workspace/ 移到 ~/.openclaw/
- ✅ chen-blog 移至 workspace/chen-blog/ 子目录
- ✅ 清理 chen-blog 中的垃圾文件（smbu_guide.md 等）
- ✅ chen-agent, chen-notes 保持平级

---

*Last updated: 2026-02-10 by Cypher*  
*Version: 记忆库 v1.1*
