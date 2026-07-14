# 📇 Anki 间隔重复卡片 · Week 1

> 复习节奏: Day 1 → Day 2 → Day 5 → Day 12 → Day 42

---

## M1-W1-1 · ReAct 是什么

### 卡片 1: ReAct 三动作

**Q**: ReAct 三个动作是什么? 用一句话说清关系。

**A**: Reason(想) → Act(用工具) → Observe(看结果) → 循环
核心: 每一轮都在 messages 数组末尾追加新消息,直到 LLM 不再返回 tool_calls。

---

### 卡片 2: ReAct vs CoT

**Q**: ReAct 和 CoT (Chain of Thought) 的核心区别?

**A**: CoT 只想不动手(单次输出思考步骤)。
ReAct = CoT + 工具调用 + 外部反馈闭环 + 循环。
没工具的 ReAct 退化成 CoT。

---

### 卡片 3: 运维类比

**Q**: 用你熟悉的运维场景解释 ReAct。

**A**: LLM 排查告警的过程:
看告警 → kubectl logs → 看日志 → kubectl top → 看内存 → 结论
ReAct 就是把这个流程用 3 段 prompt 教给 LLM。

---

## 复习打卡

| 日期 | 卡片 1 | 卡片 2 | 卡片 3 | 备注 |
|---|---|---|---|---|
| 2026-07-14 (Day 1 首次) | ✅ | ✅ | ✅ | 学习当天 |
| 2026-07-15 (Day 2) | ⬜ | ⬜ | ⬜ | 睡前 30 秒 |
| 2026-07-17 (Day 5) | ⬜ | ⬜ | ⬜ |  |
| 2026-07-21 (Day 12) | ⬜ | ⬜ | ⬜ |  |
| 2026-08-14 (Day 42) | ⬜ | ⬜ | ⬜ | 进入长期记忆 |
