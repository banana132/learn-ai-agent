# M1-W2: Agent 架构模式

> 日期: 2026-07-16
> 状态: ✅ PASS
> 参考: Anthropic "Building Effective Agents"

---

## 核心概念

### 5 级架构阶梯

```
级别 0: 纯 Prompt            "翻译这段文字"
级别 1: Prompt Chaining      固定串联 (A→B→C)
级别 2: Routing              分类分发 (输入→分类→分支)
级别 3: Parallelization      并行→汇总
────── Workflow / Agent 分界线 ──────
级别 4: Orchestrator-Workers 一个 LLM 自主调工具
级别 5: Multi-Agent          多个 LLM 互相通信
```

### 关键辨别

**流程由代码控制 = Workflow (0-3)。流程由 LLM 自主决定 = Agent (4-5)。**

---

## ⚠️ 术语校准 (今日最重要收获)

| 用户直觉 | Anthropic 精确术语 |
|---------|-----------------|
| "Agent = 有分支逻辑" | Routing (级别2) = Workflow |
| "Agent = 比纯 Prompt 复杂" | 级别 0-3 都是 Workflow |
| 真正的 Agent | 只有级别 4-5, LLM 自主决定路径 |

类比:
- Routing: LLM 是【收费站的分类员】, 分类完路是代码定的
- Agent: LLM 是【驾驶员】, 自己决定每一步往哪开

---

## ⭐ 用户生成的类比

### 广告归因 · Workflow
> "从 Kafka 消费数据 → 校验 → 格式化输出"

→ 固定的、可预测的 pipeline = 级别 1 (Prompt Chaining)

### 广告归因 · "Agent" (实为 Routing)
> "手游平台 → 走手游归因, PC平台 → 走PC归因"

→ LLM 只做分类, 后面的路代码定 = 级别 2 (Routing), 仍是 Workflow

---

## 🔨 刻意练习结果

场景 A: "退款分类" → 级别 2 ✅ (Routing)
场景 B: "财报分析+深度挖掘" → 级别 4 ✅ (Orchestrator, 自主探索)
场景 C: "日报汇总" → 级别 3 ✅ (Parallelization)
