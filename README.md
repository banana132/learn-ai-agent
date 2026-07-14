# 🎯 learn-ai-agent · Agent 系统架构师之路

> 6 个月白银档修炼指南
> 学习者：colinknliao ｜ 首席学习战略官：Hermes
> 启动日期：2026-07-14

---

## 📚 文档索引（按阅读顺序）

| # | 文档 | 说明 | 何时读 |
|---|---|---|---|
| **00** | [`00-learning-profile.md`](./00-learning-profile.md) | 学习档案：目标 / 终点 / 基础扫描 / 时间预算 | 迷失时先读这个 |
| **01** | [`01-battle-map.md`](./01-battle-map.md) | 6 个月作战地图：三大战场 + 月度大纲 + 心智模型 | 每月月初读一遍 |
| **02** | [`02-methodology.md`](./02-methodology.md) | 方法论 & 铁律：8 大认知科学原则 + 3 大 Red Flag | 想偷懒时读这个 |
| **📊** | [`progress.md`](./progress.md) | 每周进度打卡 | 每周日 30 分钟自测后更新 |

---

## 🎯 一句话说清我在干什么

> **6 个月内成为能独立交付真实业务 agent 系统的架构师**（白银档）。
>
> 通过手写 ReAct → 复刻 Coding Agent → 加 Memory → Multi-agent 编排 → Eval 生产化 → 上线运维告警 agent。

---

## 🗓️ 现在处于哪一阶段

**M1 · 地基期**（2026-07-14 → 2026-08-13）
- 主题：ReAct Loop 手写
- 产出物：200 行 agent loop + 3 个工具 + 费曼视频/文章 ×1
- Red Flag ⚠️：**禁用 LangChain**

查看当前进度 → [`progress.md`](./progress.md)

---

## 🧭 三大战场速览

- 🔴 **恐慌区**（别碰）：从零训 LLM / RLHF / 大规模分布式推理
- 🟡 **学习区**（主战场）：Agent Loop / Skills / Memory / Multi-agent / Eval
- 🟢 **舒适区**（已会）：Python / Docker / 生产监控 / 分布式系统

详见 [`01-battle-map.md`](./01-battle-map.md)

---

## 🚨 三大铁律（每次开工前默念）

1. **禁用高阶框架**（M1-M2 只用 SDK，不用 LangChain）
2. **资料 ≤ 3 份**（禁止囤积）
3. **主动回忆**（读完就合上，大白话讲一遍）

详见 [`02-methodology.md`](./02-methodology.md)

---

## 📂 目录结构

```
agent-learning/
├── README.md                    ← 本文件（索引）
├── 00-learning-profile.md       ← 学习档案
├── 01-battle-map.md             ← 作战地图
├── 02-methodology.md            ← 方法论 & 铁律
├── progress.md                  ← 每周进度打卡
├── notes/                       ← 项目/论文拆解笔记
├── anki/                        ← Anki 间隔重复卡片
└── code/                        ← 复刻代码
    └── learn-claude-code/       ← 已 clone（2026-07-13）
```

---

## 🔗 相关资源

- 每日 AI Agents 晨报（cron `936958794c32`，每天 9:00）
- 每周周报（cron `686591a97f57`，周日 10:00）
- [ReAct 论文](https://arxiv.org/abs/2210.03629)
- [Anthropic Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)（已通读）

---

_最后更新：2026-07-14_
