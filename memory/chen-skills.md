# Chen Skills - Cypher 专属技能库

> 仓库地址: https://github.com/JavaArthur/chen-skills

## 基本信息

- **创建时间**: 2026-02-04
- **用途**: 存储 Cypher 开发的 AI Agent Skills
- **公开状态**: Public
- **主分支**: main

## 当前 Skills

| Skill | 版本 | 描述 | 状态 |
|-------|------|------|------|
| ai-flavor-remover | 2.0.0 | AI 文章润色，去除机械感 | stable |

## 目录结构

```
chen-skills/
├── ai-flavor-remover/      # AI 文章润色工具
├── financial-market/       # 金融市场分析 (预留)
├── dev-tools/             # 开发工具集 (预留)
├── writing-assist/        # 写作辅助 (预留)
├── templates/             # Skill 创建模板
├── skills.json            # 技能库索引
└── README.md              # 仓库说明
```

## 开发原则

1. **单一职责**: 一个 Skill 只做一件事
2. **文档优先**: 先有 SKILL.md，后有代码
3. **可复用性**: 不依赖特定上下文
4. **版本管理**: 遵循 SemVer 规范

## 使用方式

```bash
# 克隆到本地
git clone https://github.com/JavaArthur/chen-skills.git

# 在 OpenClaw 中引用
read /path/to/chen-skills/ai-flavor-remover/SKILL.md
```

---

*Created by Cypher for Channing | 2026-02-04*
