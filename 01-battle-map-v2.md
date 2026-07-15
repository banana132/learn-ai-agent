# 🗺️ Battle Map v2 · 讲课驱动版

> **生成日期**：2026-07-15
> **升级原因**：v1 (7/14) 跳过了 Research 4 问, 缺"讲课级出关标准"
> **核心变化**：M1 从"手写"改为"讲清 → 手写", 严格执行费曼技术

---

## 📋 Research 结论快照

```
┌────────────────────────────────────────────────────┐
│  🎯 领域:  A 算法层 + C 系统层 + D Eval 层         │
│  🎓 产出:  ① 讲课 → ② 手写 → ③ 生产 (顺序不可跳)  │
│  📊 基线:  使用层 1-2 分, 理解层 ≈ 0              │
│  ⏱️  预算:  6 个月 × 10h/周 ≈ 240h                 │
│  🎓 毕业:  运维告警诊断 agent 上线                 │
│  🎤 听众:  (a) 广告工程师同事 + (d) 3个月前的自己  │
│  📝 偏好:  中文, 论文+代码, ASCII图, 少视频        │
└────────────────────────────────────────────────────┘
```

---

## 🎯 核心战略变化 (对比 v1)

```
v1 (7/14):  [手写 loop] → [复刻 agent] → [多 agent] → [Eval] → [上线]
             ↑
             跳过"讲清"直接手写 = 假装会陷阱

v2 (7/15):  [讲清] → [手写] → [复刻] → [Eval] → [多 agent] → [上线]
             ↑
             ① 教学级出关才允许进 ② 手写级
```

**铁律**：**每个模块出关必须过"双听众测试"**
- 对 (a) 广告工程师：能用工程类比讲清（agent ≈ ?）
- 对 (d) 3 个月前的你：能戳穿"我以为我懂了"的地方

---

## ⚔️ 6 阶段地图

### M1 · Agent 基础原理（讲课级）· 7/15 - 8/14

**🎯 学习区**（4h/周 × 4 周 = 16h）

| 核心概念 | 心智模型锚点 | 出关标准（费曼测试） |
|---|---|---|
| ReAct 循环 | 复利：Thought+Action 的迭代复利 | 能对 (a) 讲：ReAct vs 一次性 prompt 差在哪 |
| Tool Calling 原理 | 供需：LLM 是"决策"，tool 是"执行" | 能对 (d) 讲：为什么不是"LLM 直接输出结果"就够 |
| Structured Output | 熵增：结构化对抗无序 | 能对 (a) 讲：JSON mode 底层怎么保证格式 |
| Function Calling vs Tool Use | — | 能对 (d) 讲：OpenAI/Anthropic 两家协议差异 |
| Chain of Thought | — | 能对 (a) 讲：CoT 为什么"想一想"就变强了 |

**📚 学习材料**（同时进行 ≤ 3 份）：
1. ReAct 原论文（Yao 2022）—— 精读
2. Anthropic "Building effective agents" 博客
3. OpenAI Function Calling 官方 doc

**🚩 Red Flag**：跳过论文只看博客 → 术语理解错乱

**✅ 出关**：
- [ ] 写一篇 2000 字博客《ReAct 到底是什么》，发给 3 个 (a) 类同事看，他们能复述
- [ ] 录 5 分钟视频讲 CoT，回看时能戳出至少 3 处"我以为我懂但其实没讲清"
- [ ] 手写 5 张 Anki 卡（M1 概念）

---

### M2 · 手写 Agent Runtime（手写级）· 8/15 - 9/14

**🎯 学习区**（10h/周 × 4 周 = 40h）

| 核心组件 | 心智模型锚点 | 出关标准 |
|---|---|---|
| Agent Loop（<200 行 Python） | 一阶思维：先跑通再优化 | 能对 (a) 讲：这 200 行是怎么把 LLM 变 agent 的 |
| Tool Registry | 复利：工具是能力乘数 | 3 个工具（search/exec/read_file）能协同 |
| Memory (short-term) | 熵增：context 会退化 | 能对 (d) 讲：为什么不能只塞历史消息 |
| Error Handling / Retry | 反脆弱（M2 引入！） | 能讲：agent 失败时应该如何"越挫越强" |
| Streaming Output | — | 用户体验层的一阶考虑 |

**📚 学习材料**：
1. 阅读 `smolagents` 源码（Hugging Face，最小实现）
2. Anthropic tool_use 文档
3. 自己的代码 = 最好的教材

**🚩 Red Flag**：
- 上来用 LangGraph → **禁用！全程手写**
- 抄代码而不写测试 → 用 pytest 逼自己验证

**✅ 出关**：
- [ ] `myagent/` 仓库能跑，README 写清架构
- [ ] 能对 (a) 现场画出 loop 时序图（30 秒内）
- [ ] 手写博客《200 行手写 Agent：我踩了 8 个坑》
- [ ] 手写 8 张 Anki 卡（M2 概念）

---

### M3 · Eval 体系（生产前置！）· 9/15 - 10/14

**⚠️ 顺序调整**：v1 把 Eval 放 M5，v2 提前到 M3
**原因**：**没 eval 的 agent 优化都是玄学**，你 L4 工程背景应该最能共鸣这一点

| 核心概念 | 心智模型锚点 | 出关标准 |
|---|---|---|
| LLM-as-Judge | 二阶思维：谁来评价评价者 | 能对 (a) 讲：judge 靠谱吗？怎么验证 |
| Task-level Eval | 熵增：没度量就退化 | 建立 20 个 test case，跑通 CI |
| Trajectory Eval | 康威定律预热 | 能讲：为什么只看结果不够 |
| Tracing (Langfuse) | — | 能对 (a) 讲：分布式 tracing 在 agent 里的映射 |
| Benchmark 生态 | — | 能对 (d) 讲：SWE-bench / τ-bench / GAIA 差在哪 |

**📚 学习材料**：
1. Langfuse 官方 doc + 部署一个自己的
2. τ-bench 论文（Anthropic 2024）
3. Anthropic "Building an evaluations framework"

**🚩 Red Flag**：
- 只用 LLM-as-judge 不 sanity check → judge 也会错
- 跳过 tracing 直接看 metrics → 出问题定位不到

**✅ 出关**：
- [ ] M2 的 agent 接入 Langfuse
- [ ] 20 个 test case + LLM judge + CI 集成
- [ ] 能对 (a) 讲清"LLM eval 和传统单元测试差在哪"
- [ ] 手写 6 张 Anki 卡

---

### M4 · Advanced Patterns（复刻级）· 10/15 - 11/14

**🎯 学习区**（10h/周 × 4 周 = 40h）

| 核心模式 | 心智模型锚点 | 出关标准 |
|---|---|---|
| Reflexion / Self-refine | 反脆弱：从失败中学 | 能对 (d) 讲：这和普通 retry 差在哪 |
| Plan-and-Execute | 一阶 vs 二阶 | 能对 (a) 讲：什么时候 plan 值得 |
| Memory (long-term) + RAG | 复利 | 给 M2 agent 加长期记忆 |
| Context Engineering | 熵增 | 能讲：context 压缩策略 |
| Multi-agent 编排（初探） | 康威定律 | 能对 (a) 讲：多 agent = 微服务？ |

**📚 学习材料**：
1. Reflexion 论文（Shinn 2023）
2. AutoGen / CrewAI 源码（读原理不用框架）
3. Anthropic "Multi-agent research system" 博客

**🚩 Red Flag**：一上来就多 agent → 先证明单 agent 不够

**✅ 出关**：
- [ ] M2 的 agent 加上 Reflexion，eval 分数提升可量化
- [ ] 长记忆能跨 session
- [ ] 手写 10 张 Anki 卡

---

### M5 · 白银毕业项目开发 · 11/15 - 12/14

**🎯 毕业项目：AI 运维告警诊断 Agent**

```
        [告警输入]
             ↓
    ┌──────────────────┐
    │ Planner Agent    │ ← 分类告警类型
    └──────────────────┘
             ↓
    ┌──────────────────┐
    │ Diagnostic Loop  │ ← M2 的 loop + M4 的 Reflexion
    │  • Query 日志    │
    │  • Query 监控    │
    │  • 关联历史故障  │
    └──────────────────┘
             ↓
    ┌──────────────────┐
    │ Synthesizer      │ ← 出诊断报告
    └──────────────────┘
             ↓
        [Langfuse 全链路]
```

**出关**：
- [ ] 内部环境跑通 10 个真实告警
- [ ] Eval 分数 ≥ 70%
- [ ] 完整 tracing + dashboard
- [ ] 写技术设计文档（对 (a) 的完整讲课材料）

---

### M6 · 上线 + 复盘 + 分享 · 12/15 - 1/14

**🎓 白银毕业标准**：

- [ ] 生产环境运行 ≥ 2 周
- [ ] 至少 1 次真实告警诊断被值班同事采纳
- [ ] 内部技术分享 ×1（对听众 a）
- [ ] 复盘博客 ×1（对听众 d，即 6 个月前的你）
- [ ] 学习档案完整，Anki 库 ≥ 40 张

---

## 🚨 三大铁律（v2 保留 v1 + 新增）

| # | 铁律 | 触发场景 |
|---|---|---|
| 1 | M1-M2 全程禁用高阶框架（LangGraph/LlamaIndex） | 手痒想抄捷径 |
| 2 | 同时进行的资料 ≤ 3 份 | 想收藏第 4 篇论文时 |
| 3 | 读完必讲：对 (a) 或 (d) 讲一次，才算过 | 觉得"读懂了"时 |
| 4 ⭐ | **未过费曼测试不进下一模块** | 想跳过 M1 直接 M2 时 |

---

## 📊 每周节奏模板（10h/周）

```
周一  1h  概念输入（读论文/博客）
周二  1h  代码实践（写/改/跑）
周三  1h  概念输入 or 代码实践
周四  1h  代码实践
周五  1h  ⭐ 主动回忆日：合上资料，讲给 (a) 或 (d) 听
周六  3h  深度模块（大块整合）
周日  2h  Anki 复习 + 周复盘 + 下周计划
─────────────────────────────────────
        10h
```

---

## 🧭 现在的位置

```
你在这里 ↓
[M1 起点]───[M2]───[M3]───[M4]───[M5]───[M6 白银🎓]
   ↑
2026-07-15
下一步: M1-W1-1 —— 精读 ReAct 论文 + 讲清 ReAct 循环
```

---

_v1 保留在 01-battle-map.md, 本文件是 v2 主用版本_
_最后更新：2026-07-15_
