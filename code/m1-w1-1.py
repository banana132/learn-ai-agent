"""
M1-W1-1 手写练习: 最小 ReAct 循环
============================================
日期: 2026-07-15
作者: banana132 (伪代码) + 教练 review (完整版)

背景:
  这份代码是首次费曼 PASS 后, 学习者主动尝试写的伪代码。
  没用过 SDK, 但骨架直觉正确, 暴露了 6 个工程盲点。
  这些盲点正好覆盖 M1-W1-2 (Tool Calling 协议) 的 80% 内容。

学到的元原则 (2026-07-15):
  1. LLM 决策 vs 代码执行 · 权责分离
  2. JSON Schema = LLM 和代码的合同
  3. 4 种 role: system/user/assistant/tool
  4. tool_call_id = agent 版 request_id (无状态协议靠 id 关联)
  5. assistant 必须回填 = context 是 LLM 全部记忆
  6. OpenAI vs Anthropic 协议差异 (M2 手写 runtime 会做抽象层)
"""

# ==================== 学习者原版 (伪代码 · 2026-07-15) ====================
# 保留原版做对照, 展示学习轨迹

"""
tools = {                          # ❌ 应该是 [] (list, 不是 set)
    {                              # ❌ dict 不能进 set
        "name": "get_weather",
        "description": "获取天气情况",
    }                              # ❌ 缺 parameters (JSON Schema)
}

quest = "今天深圳天气怎么样？"
context = {                        # ❌ 应该是 [] (list)
    {"role":"user", "content": quest}
}
while True:
    response = openAISDK.think(context, tools)
    # ❌ 缺: 把 assistant 决策回填 context

    if len(response.tool_calls) == 0:
        print("I got the answer: ", response.content)
        break
    for tool in response.tools:
        if tool.name == "get_weather":
            # ❌ tool.result 从哪来? LLM 不执行工具!
            # ❌ 应该是你的代码调 get_weather(...) 拿 result
            # ❌ role 应该是 "tool" 不是 "assistant"
            # ❌ 缺 tool_call_id 关联
            context.append({"role":"assistant", "content": tool.result})
"""


# ==================== 教练修正版 (2026-07-15) ====================
import json
from openai import OpenAI

client = OpenAI()

# --- 1. 工具定义 (list of dict, 带完整 JSON Schema) ---
# JSON Schema = LLM 和你代码的【合同】
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市当前天气. 输入城市名, 返回温度和天气状况.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称, 支持中文 (如 '深圳')"
                }
            },
            "required": ["city"]
        }
    }
}]


# --- 2. 工具的真实实现 (在【你的代码】里, 不在 LLM 里!) ---
def get_weather(city: str) -> dict:
    """假的天气工具, 真实场景会调用外部 API."""
    fake_data = {
        "深圳": {"temp": 28, "condition": "晴"},
        "北京": {"temp": 22, "condition": "多云"},
    }
    return fake_data.get(city, {"temp": None, "condition": "未知城市"})


# name → callable 的映射表 (dispatch table)
TOOL_IMPL = {
    "get_weather": get_weather,
}


# --- 3. Context 初始化 (list, 不是 set/dict!) ---
context = [
    {"role": "user", "content": "今天深圳天气怎么样?"}
]


# --- 4. ReAct 循环 ---
MAX_ITERATIONS = 5  # 【安全网】防止 LLM 陷入死循环

for iteration in range(MAX_ITERATIONS):
    print(f"\n=== Round {iteration + 1} ===")

    # 4.1 LLM 决策 (只决策, 不执行!)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=context,
        tools=tools,
    )
    msg = response.choices[0].message

    # 4.2 【关键 1】把 assistant 决策回填 context
    #     否则 LLM 下一轮不记得自己刚才想调什么工具!
    #     Context = LLM 的全部记忆
    context.append({
        "role": "assistant",
        "content": msg.content,
        "tool_calls": msg.tool_calls,
    })

    # 4.3 【关键 2】没有 tool_calls = LLM 觉得可以答了
    if not msg.tool_calls:
        print(f"Final Answer: {msg.content}")
        break

    # 4.4 【关键 3】执行工具 + 回填 tool 消息 (原样, 带 id!)
    #     这里体现 3 个原则:
    #     • 权责分离: 你的代码执行, LLM 不执行
    #     • Faithfulness: 结果原样塞回, 不加工
    #     • id 关联: tool_call_id 保证多工具场景对齐
    for tool_call in msg.tool_calls:
        fn_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        print(f"  → LLM 想调 {fn_name}({args})")

        fn = TOOL_IMPL[fn_name]      # dispatch
        result = fn(**args)          # 【你的代码】执行

        print(f"  ← 工具返回: {result}")

        context.append({
            "role": "tool",
            "tool_call_id": tool_call.id,      # ← 【无状态协议靠 id 关联】
            "content": json.dumps(result, ensure_ascii=False),  # 原样, 不加工
        })

else:
    print("⚠️  达到最大迭代次数, agent 未收敛")


# ==================== 学习者暴露的 6 个盲点 (全部命中 M1-W1-2) ====================
# 1. {} vs []                  → 语法层
# 2. tool 定义 vs tool 执行     → 权责分离 (最大金矿!)
# 3. JSON Schema 必须写         → 合同意识
# 4. tool result 不是 assistant → 4 种 role 认知
# 5. 缺 tool_call_id            → 无状态协议元原则 (广告归因直觉映射)
# 6. 缺 assistant 回填          → context = LLM 全部记忆
