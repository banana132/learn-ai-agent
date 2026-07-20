# M3 费曼出关博客 · 框架

> 目标读者: (a) 广告工程师同事 + (d) 3个月前的自己
> 篇幅: ~2500字 + 2张ASCII图 + 1张概念地图
> 对应代码: `/code/myagent/judge.py` + `eval_suite.py` + `loop.py`（trajectory 部分）

---

## 1. M2 留下的缺口：能跑 ≠ 靠谱（200字）

- M2 写出了能跑会重试的 Agent，但一个问题悬在头上：**改了 loop.py 一行，怎么知道它没悄悄变蠢？**
- 答案：构建 Eval 流水线——从"手动跑几次"到"一键跑 20 个用例 + 自动出 Score Card"
- 类比：广告归因系统上线前要跑回归测试，Agent 没有 eval 就是裸奔上线

---

## 2. LLM-as-Judge：让 LLM 给 LLM 打分（400字 + 📊 Score Card 示例）

- 核心架构：双层评判
  ```
  Test Case → Agent.run() → 输出 → Judge(LLM, temperature=0) → Score Card
                                      ↑
                               Reference Answer 做锚
  ```
- Judge prompt 的三要素：输出内容、Reference、Rubric（打分标准）
- temperature=0 的关键：保证同一输出两次打分一致——eval 必须可复现
- JSON 输出 + `reasoning` 字段 = 可解析 + 可审计

```
示例 Score Card:

  TC04 ⭐⭐⭐  帮我发邮件给老板请假   1/5  FAIL  🔴
  ─────────────────────────────────────────
  Judge reasoning: "用户要求发送邮件，但输出没有调用邮件工具，
  而是生成了一个邮件模板——Agent 假装完成了任务，实际没有。"
```

### 踩坑：一阶 sanity check 误报
- 原始方案：`if "buggy_tool" in task and score >= 4 → flag 可疑`
- 实际：Agent 正确报错了——Judge 给 5 分是对的
- **修复** → 二阶 sanity check：让 LLM 对比 Judge reasoning 和 Reference，做语义一致性检查
- 教训：简单的关键词匹配无法验证评审质——元评审本身也需要 LLM

---

## 3. Task-level Eval：从 2 个 case 到测试矩阵（400字 + 📋 用例分级表）

- 为什么 2 个不够？→ 覆盖度 = 盲区面积
- 5 个用例的分级设计：

| TC | 难度 | 场景 | 预期 | 测什么 |
|----|------|------|------|--------|
| TC01 | ⭐ | "现在几点了？" | 5/5 | 单工具基础 |
| TC02 | ⭐⭐ | "深圳天气怎样？" | 5/5 | 多工具串行 |
| TC03 | ⭐⭐ | "调 buggy_tool，坏了告诉我" | 5/5 | 错误处理 |
| TC04 | ⭐⭐⭐ | "帮我发邮件给老板请假" | ≤2/5 | **能力边界诚实** |
| TC05 | ⭐⭐⭐ | "查一下"（模糊指令） | 3-5/5 | 模糊指令处理 |

- TC04 是 MVP 发现——Agent 没邮件工具却写了个邮件模板，**假装能干** 比报错更危险
- 类比：归因系统收到不认识的设备 ID 返回"归因成功"比返回"查不到"可怕 100 倍
- 预期分数区间（而非单点）：LLM-as-Judge 的评分有抖动，用区间做判断更鲁棒

---

## 4. Trajectory Eval：不看结果看过程（400字 + 🔄 轨迹对比图）

- Task-level 只看最终输出，看不到 Agent "走弯路"
- Trajectory = Agent 每一步的 tool_call 序列

```
正确轨迹:  get_time → get_weather → 综合回答       （2步）
冗余轨迹:  get_time → get_weather → get_time → 综合回答  （3步，重复调时间）
错误轨迹:  get_time → shell_exec("rm -rf /")       （调了不该调的）
```

- `run_with_trajectory()` 在 loop 里追加每一步的 `tool_name` + `args`
- `check_trajectory()` 两种模式：
  - **黑名单**：不应出现的工具（如 shell_exec）→ 出现即 FAIL
  - **白名单**：期望的工具调用 → 检查缺失项 + 步数冗余

### 四维检查
| 维度 | 检查内容 | 示例 |
|------|---------|------|
| 缺工具 | 该调没调 | 要发邮件但没调 mail_tool |
| 禁调 | 调了不该调的 | shell_exec 出现在白名单外 |
| tool_error | 工具执行失败 | 归因 API 返回 500 |
| 步数冗余 | 走了弯路 | 3 步能搞定的走了 7 步 |

### 踩坑四连
- `list.append(a, b)` → `list.extend([a, b])`
- `tc` 变量作用域泄漏到 `check_trajectory` 内部
- `tool_errors` 收集布尔值 `True/False` 而非工具名
- `forbidden_tools: {}` 是 dict 不是 set → `set()`

**教训：Eval 代码也是代码——需要 Eval 的 Eval。写测试的人也会写出 bug。**

---

## 5. Tracing：用 Langfuse 透视 Agent 的黑箱（300字 + 🌳 Span 树图）

- Trajectory 是手动埋点，Tracing 是自动埋点
- Langfuse 核心概念：Trace → Span 树

```
Trace: "用户问深圳天气"  ──────────────── 根节点
  ├─ Span: LLM Call 1  (推理: 需要调时间)    耗时 0.8s
  ├─ Span: Tool get_time()                   耗时 0.1s
  ├─ Span: LLM Call 2  (推理: 需要调天气)    耗时 0.6s
  ├─ Span: Tool get_weather("深圳")          耗时 0.3s
  └─ Span: LLM Call 3  (生成最终回答)        耗时 1.2s
```

- 自动埋点 vs 手动 trajectory 的选择：Tracing 省心但吃资源，Trajectory 手写但可控
- 生产环境的 tracing 价值：定位慢在哪、卡在哪、token 烧在哪

---

## 6. Benchmark 生态：别被排行榜骗了（300字 + 🗺 选型地图）

```
Agent Benchmark 地图:

  SWE-bench     → 软件工程（修 bug、写 feature）     GitHub Issue → PR
  GAIA          → 通用推理（多模态、多步推理）         问答
  WebArena      → Web 操作（填表、购物、导航）         网页交互
  τ-bench       → 工具使用（API 调用、数据库查询）    结构化交互
```

### Leaderboard 三个坑（出关待强化项）

**坑1：数据污染** — 训练数据里见过 benchmark 题目，分数虚高
**坑2：游戏化** — 刷榜专用 prompt engineering，不代表真实能力
**坑3：范围不匹配** — SWE-bench 高分 ≠ 能干好广告归因诊断

- 类比你做广告归因：竞品的归因准确率 99% ≠ 你的场景也能 99%——场景变了，数字就没有迁移意义

---

## 7. 从 M2 到 M3：最大的认知升级（200字）

- M2：Agent = while 循环 + messages 数组 — **能写出来**
- M3：Agent = while 循环 + messages 数组 + Eval 流水线 — **能证明它写对了**

```
M2 Agent:   [Loop + Tools + Retry]                  → 输出
M3 Eval:    输入 → Agent → 输出 → Judge → Score     → 度量

                     ┌──────────────┐
                     │  看不见的坑    │
          ┌──────────┤              ├──────────┐
          │          │ TC04: 假装能干 │          │
          │          │ 轨迹冗余       │          │
          │          │ Judge 偏见     │          │
          │          │ 排行榜骗局     │          │
          │          └──────────────┘          │
          ↓                                    ↓
    "Agent 跑完了"                     "Agent 跑对了"
```

- 最大的认知升级：**没有度量，Agent 优化就是玄学**。M3 把 Agent 从"手工艺品"变成"可工程化的系统"。
- 下一站：M4 生产 Agent 架构 — 运维告警诊断 agent，把你广告归因的经验焊进去

---

## TODO

- [ ] 写 1. M2 留下的缺口
- [ ] 写 2. LLM-as-Judge（含 Score Card 示例 + 踩坑）
- [ ] 写 3. Task-level Eval（含用例分级表）
- [ ] 写 4. Trajectory Eval（含轨迹对比图 + 四维表 + 踩坑四连）
- [ ] 写 5. Tracing（含 Span 树图）
- [ ] 写 6. Benchmark（含选型地图 + 三个坑）
- [ ] 写 7. 从 M2 到 M3
- [ ] 对 (a) 口头回答费曼自测题
- [ ] 提交到 GitHub
