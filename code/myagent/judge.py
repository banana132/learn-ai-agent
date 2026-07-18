"""
judge.py — LLM-as-Judge：让 LLM 评价 M2 Agent 的输出

流程：task → Agent.run() → Judge LLM 打分 → score card
"""
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# ═══════════════════════════════════════════
# ① 复用 M2 Agent 的 client（和 main.py 一样）
# ═══════════════════════════════════════════

client = OpenAI(
    base_url=os.getenv('GLM_BASE_URL'),
    api_key=os.getenv('GLM_API_KEY')
)
model = os.getenv('AI_MODEL')

# ═══════════════════════════════════════════
# ② 导入 M2 Agent（直接用你已经写好的）
# ═══════════════════════════════════════════
from registry import ToolRegistry
from loop import AgentLoop
from main import registry   # 复用 main.py 里注册好的 3 个工具

agent = AgentLoop(client, registry, model)


# ═══════════════════════════════════════════
# ③ 测试用例
# ═══════════════════════════════════════════
TEST_CASES = [
    {
        "task": "深圳现在几点了？天气怎么样？",
        "reference": "应包含当前时间（日期+时分秒）和深圳天气（温度+状况）"
    },
    {
        "task": "调一下 buggy_tool，如果坏了就告诉我",
        "reference": "应报告 buggy_tool 调用失败，并告知用户工具坏了"
    },
]


# ═══════════════════════════════════════════
# ④ 核心：Judge prompt 模板
# ═══════════════════════════════════════════
def build_judge_prompt(task, reference, agent_output):
    """
    构造评分 prompt。
    关键：不是调 API 的 function calling，而是用自然语言写评分规则。
    """
    return f"""你是一个严格的评分员。根据以下标准给 Agent 的输出打分。

【用户任务】
{task}

【参考答案要点】
{reference}

【Agent 实际输出】
{agent_output}

【评分标准】
- 5: 完全正确，涵盖了参考答案所有要点，表述清晰
- 4: 正确但有小瑕疵（如缺少某个非关键细节）
- 3: 部分正确，缺了重要信息或有明显错误
- 2: 大部分错误，只有少量正确
- 1: 完全错误或答非所问

请严格按以下 JSON 格式输出，不要输出任何其他内容：
{{"score": <整数1-5>, "reasoning": "<一句话评分理由>"}}"""


# ═══════════════════════════════════════════
# ⑤ 调用 Judge
# ═══════════════════════════════════════════
def judge(task, reference, agent_output):
    """让 LLM 给 Agent 输出打分"""
    prompt = build_judge_prompt(task, reference, agent_output)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # 评分要稳定，不要随机性
    )
    
    raw = response.choices[0].message.content
    # 尝试解析 JSON（LLM 可能在 JSON 外包了 ``` 标记）
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 兜底：去掉可能的 markdown 代码块标记
        raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(raw)


# ═══════════════════════════════════════════
# ⑥ 主流程：跑所有 test case → 打分 → 输出
# ═══════════════════════════════════════════
def main():
    results = []
    
    for i, tc in enumerate(TEST_CASES, 1):
        print(f"\n{'='*50}")
        print(f"Test Case {i}: {tc['task']}")
        print(f"{'='*50}")
        
        # Step 1: 跑 Agent
        agent_output = agent.run(tc["task"])
        print(f"\n📤 Agent 输出:\n{agent_output}")
        
        # Step 2: Judge 打分
        result = judge(tc["task"], tc["reference"], agent_output)
        print(f"\n📊 Judge 评分: {result['score']}/5")
        print(f"📝 Judge 理由: {result['reasoning']}")
        
        # Step 3: sanity check — Judge 自己也可能误判
        flag = ""
        if "buggy_tool" in tc["task"] and result["score"] >= 4:
            flag = " ⚠️ 可疑！buggy_tool 应该失败，高分可能是 Judge 误判"
        elif result["score"] <= 2:
            flag = " ⚠️ Agent 得分偏低，需要检查"
        
        results.append({
            "task": tc["task"],
            "output": agent_output[:200],
            "score": result["score"],
            "reasoning": result["reasoning"],
            "flag": flag
        })
    
    # Step 4: 输出汇总 score card
    print(f"\n\n{'='*50}")
    print("📋 Score Card 汇总")
    print(f"{'='*50}")
    for r in results:
        print(f"  [{r['score']}/5] {r['task']}")
        print(f"         {r['reasoning']}{r['flag']}")
    
    avg = sum(r["score"] for r in results) / len(results)
    print(f"\n  📊 平均分: {avg:.1f}/5")
    print(f"  📝 共 {len(results)} 个用例")


if __name__ == "__main__":
    main()
