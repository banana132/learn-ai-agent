# 📊 学习进度打卡

> 每周末更新一次,记录:做了什么、踩了什么坑、下周计划。

---

## Week 0 - 启动 (2026-06-23)

**状态**:📍计划已制定

- ✅ 制定 6 个月学习路径
- ✅ 建立文档仓库 `/projects/agent-learning/`
- ⏳ 准备启动 Week 1

---

## Week 1-3 静默期 (6/23 – 7/13)

**状态**:🔴 卡住 — 计划写完后未启动,Day 1 三件事悬挂 3 周

**教训**:6 个月长路径 + "有空再做"心态 = 无限延期。后续必须绑定固定节奏 + 短反馈。

---

## Week 4 - 破零 (2026-07-13 起)

**状态**:🟢 进行中

**完成**:
- ✅ **7/13** clone `shareAI-lab/learn-claude-code`,通读全部章节
- ✅ **7/14** Battle Map v1 出炉,GitHub repo `banana132/learn-ai-agent` 建立
- ✅ **7/15** **首次真正走完费曼流程** (M1-W1-1 ReAct + M1-W1-2 Tool Calling 双章 PASS)
  - Research 4 问逐条走完, 目标锁定 A+C+D + 讲课驱动 (①→②→③)
  - Battle Map v2 生成 (讲课驱动版, 严格执行 Feynman)
  - M1-W1-1 首讲 ReAct 循环, 双听众费曼 PASS (超预期)
  - M1-W1-2 Tool Calling 协议, 暴露 type 概念污染 + 权责分离深度理解
  - ⭐ 独创贡献: 广告归因类比 + Type Drift 直觉迁移
  - 暴露 2 个漏洞已修复: O/T 混淆 + Observation 加工方向反了
  - 落盘: notes/M1-W1-01-ReAct.md, common-mistakes.md, anki/M1.tsv (v2 卡 ×10)
- ✅ **7/16** M1-W1-3 CoT vs ReAct vs Plan-and-Execute PASS
    - 三种模式精确边界 + 决策树
    - ⭐ 新增归因类比: 手游/端游分支→ReAct, 三数据并行→Plan
    - 关键洞察: 同任务不同模式取决于信息需求结构
    - Anki 卡累计: 12 张
  - ✅ **7/16** M1-W2 Agent 架构模式 PASS (Anthropic Building Effective Agents)
    - 5 级架构: 纯Prompt → Chaining → Routing → Parallel → Orchestrator → Multi-Agent
    - ⚠️ 关键术语校准: "Agent=有分支" → 实际是 Routing (级别2), 仍是 Workflow
    - 核心洞察: 流程由代码控制=Workflow(0-3), 流程由LLM控制=Agent(4-5)
    - 收费站分类员 vs 驾驶员类比
    - Anki 卡累计: 14 张

  - ✅ **7/16** M1-W3 Structured Output PASS
    - Constrained Decoding 原理: JSON Schema → 状态机 → token 级过滤
    - 关键边界: Structured Output 是 LLM 引擎能力, Agent 只是消费者
    - Agent 可靠性公式: 成功率 = (单轮)^轮次 → 串行依赖放大脆弱性
    - 三层兜底: Prompt → API strict → 代码 try/except
    - Anki 卡累计: 16 张
  
  **下一步 (M1-W4, 建议 7/17)**:
  - [ ] M1-W3: Structured Output — JSON Mode, 为什么 Agent 需要结构化输出
  - [ ] M1-W4: 综合费曼出关 — 对 (a) 讲清 Agent 全貌, 博客/视频准备

  **本周指标**:
  - 时间: 用 ≈3h / 计划 10h
  - 完成模块: 4 (M1-W1-1/2/3 + M1-W2)
  - Anki 卡累计: 14 张
- M1-W1 全部完成 🎉

---

<!-- 模版,每周复制一份
## Week N (YYYY-MM-DD)

**状态**:🟢进行中 / ✅完成 / 🔴卡住

**完成**:
-

**踩坑**:
-

**下周计划**:
-

**思考/疑问**:
-
-->
