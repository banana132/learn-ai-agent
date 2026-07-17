# M2 费曼出关博客 · 框架

> 目标读者: (a) 广告工程师同事 + (d) 3个月前的自己
> 篇幅: ~1800字 + 2张ASCII图 + 1张决策表
> 对应代码: `/code/myagent/loop.py` + `registry.py` + `main.py`

---

## 1. 为什么不调包（200字）

- LangChain 藏了什么？while 循环 + messages 数组被 10 层抽象盖住
- M1 铁律：手写才能焊死
- "看了 10 遍源码，不如关掉IDE手写一遍"

---

## 2. 骨架：就是这几行（300字 + 🔁 ASCII 图）

- chat → append → tool_calls? → dispatch → 回填 → 循环
- 对应代码里的 3 个核心对象：AgentLoop / ToolRegistry / main
- 复习 M1 博客第 4 节的图，M2 把它变成了真的代码

```
ASCII 图: Agent Loop 数据流

    context = [user_msg]
            ↓
    ① LLM.chat(messages, tools)  ← 决策
            ↓
    ② context.append(assistant)   ← 回填
            ↓
    tool_calls? ──No──→ return content
        │
       Yes
        │
    ③ ToolRegistry.dispatch()    ← 执行
            ↓
    ④ context.append(tool)       ← 回填
            ↓
        回到 ①
```

---

## 3. 三个关键决策（400字）

### a) Tool Registry 独立于 Loop
- 开闭原则：加工具不改引擎
- 工具是"插件"，Loop 是"引擎"

### b) dispatch 用 `**(args or {})`
- 一行搞定有参数/无参数两种调用
- Python 的优雅：`**{}` = 不传任何参数

### c) 工具错误喂回 LLM 而不是崩
- 三板斧：LLM 加重试 / 工具包 try/except / 错误信息塞回 context
- Agent 不怕犯错，怕沉默地崩

---

## 4. Streaming：打字机体验（300字）

- 非流式 vs 流式的区别
- 踩坑：tool_calls 跨 chunk，必须按 index 合并

```
错误方式: tool_calls.extend(chunk.tool_calls)  → 碎片
正确方式: tool_call_buf[index].arguments += chunk_arguments  → 拼接
```

- 只做纯文本 streaming，工具调用保持非流式（M2-W3 才拼接）

---

## 5. Context 爆炸问题（300字）

- 消息数 vs token 数——看起来一样，实际差 1000 倍
- 滑动窗口：保留任务锚点(head[:2]) + 最近 N 条(tail)
- 归因系统类比：行为链太长就不能追溯到 90 天前

```
决策表:

| 条件 | 策略 |
|------|------|
| token 数 < 阈值 | 不管 |
| token 超限 | 保留 system + 首问 + 最后 6 条 |
| 中间历史 | 丢弃 |
```

---

## 6. 从 M1 到 M2：我变了什么（200字）

- M1：能画图、能讲清
- M2：能写出 200 行能跑的、会重试的、会裁剪的代码
- 最大的认知升级：Agent 不是神秘的黑箱，就是一个 while 循环 + 一段 messages 数组
- 下一站：M3 Eval——没有度量，Agent 优化就是玄学

---

## TODO

- [ ] 写 1. 为什么不调包
- [ ] 写 2. 骨架（含 ASCII 图）
- [ ] 写 3. 三个关键决策
- [ ] 写 4. Streaming
- [ ] 写 5. Context 爆炸
- [ ] 写 6. 从 M1 到 M2
- [ ] 对 (a) 口头回答费曼自测题
- [ ] 提交到 GitHub
