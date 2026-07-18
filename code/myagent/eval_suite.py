"""
eval_suite.py — Task-level Eval：从 2 个 case 扩到 5+，覆盖不同难度

升级点 vs judge.py:
  1. 用例分级（⭐～⭐⭐⭐）
  2. 预期分数区间（判断 Judge 是否误判）
  3. 二阶 sanity check（Judge reasoning vs reference 矛盾检测）
  4. 汇总通过率
"""
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url=os.getenv('GLM_BASE_URL'),
    api_key=os.getenv('GLM_API_KEY')
)
model = os.getenv('AI_MODEL')

from registry import ToolRegistry
from loop import AgentLoop
from main import registry

agent = AgentLoop(client, registry, model)


# ═══════════════════════════════════════════
# 测试用例：按难度分级
# ═══════════════════════════════════════════
TEST_CASES = [
    # ── ⭐ 单工具 ──
    {
        "id": "TC01",
        "task": "现在几点了？",
        "reference": "应返回当前时间，包含日期和时分秒",
        "difficulty": "⭐",
        "expected_range": (4, 5),
        "expected_tools": {"get_time"},
        "forbidden_tools": {"get_weather"},
    },
    # ── ⭐⭐ 多工具串行 ──
    {
        "id": "TC02",
        "task": "深圳现在几点了？天气怎么样？",
        "reference": "应包含当前时间（日期+时分秒）和深圳天气（温度+状况）",
        "difficulty": "⭐⭐",
        "expected_range": (4, 5),
        "expected_tools": {"get_weather", "get_time"},
        "forbidden_tools": set(),
    },
    # ── ⭐⭐ 错误处理 ──
    {
        "id": "TC03",
        "task": "调一下 buggy_tool，如果坏了就告诉我",
        "reference": "应调用了 buggy_tool，捕获到错误，并明确告知用户工具坏了",
        "difficulty": "⭐⭐",
        "expected_range": (4, 5),
        "expected_tools": {"buggy_tool"},
        "forbidden_tools": {"get_weather", "get_time"},
    },
    # ── ⭐⭐⭐ 边界：Agent 没有的工具 ──
    {
        "id": "TC04",
        "task": "帮我发一封邮件给老板，说今天请假",
        "reference": "Agent 没有发邮件工具，应诚实告知用户自己做不到，不要假装能发",
        "difficulty": "⭐⭐⭐",
        "expected_range": (4, 5),
        "expected_tools": {},
        "forbidden_tools": {"get_weather", "get_time"},
    },
    # ── ⭐⭐⭐ 边界：模糊指令 ──
    {
        "id": "TC05",
        "task": "查一下",
        "reference": "应追问用户要查什么，或列出自己能做什么，而不是瞎猜一个工具去调",
        "difficulty": "⭐⭐⭐",
        "expected_range": (3, 5),
        "expected_tools": {},
        "forbidden_tools": {"get_weather", "get_time"},
    },
]


# ═══════════════════════════════════════════
# Judge prompt（和 judge.py 一样）
# ═══════════════════════════════════════════
def build_judge_prompt(task, reference, agent_output):
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


def judge(task, reference, agent_output):
    prompt = build_judge_prompt(task, reference, agent_output)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(raw)


# ═══════════════════════════════════════════
# 二阶 sanity check：Judge 和 reference 矛盾吗？
# ═══════════════════════════════════════════
def check_judge_vs_reference(reference, judge_reasoning):
    """
    让 LLM 判断：Judge 的评分理由跟 reference 矛盾吗？
    返回 "consistent" / "contradiction" / "uncertain"
    """
    prompt = f"""你是一个元评审员。判断以下 Judge 评分理由是否与参考答案矛盾。

【参考答案要点】
{reference}

【Judge 评分理由】
{judge_reasoning}

请判断：
- consistent: Judge 理由与参考答案一致，没有矛盾
- contradiction: Judge 理由明显与参考答案矛盾（如 reference 说应该有 X，Judge 说缺 X 但给了高分）
- uncertain: 无法确定

请只输出一个词：consistent / contradiction / uncertain"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    result = response.choices[0].message.content.strip().lower()
    return result

# 检查路径是否包含预期工具
def check_trajectory(trajectory, expected_tools, forbidden_tools=None):
    actual = {s['tool'] for s in trajectory if s['type'] == 'tool_call'}
    if forbidden_tools is None or len(forbidden_tools) == 0:
        unexpected = actual - expected_tools
    else:
        # 黑名单模式（你现在的逻辑）
        unexpected = actual & forbidden_tools
    errors = [s['tool'] for s in trajectory if s.get('is_error')]

    return {
        'actual': actual,
        'missing': expected_tools - actual,
        'unexpected': unexpected,
        'tool_errors': errors,
        'total_steps': len(trajectory),
        'min_steps': len(expected_tools) * 2 + 1,
    }


# ═══════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════
def main():
    results = []
    passed = 0
    failed = 0

    for tc in TEST_CASES:
        print(f"\n{'='*50}")
        print(f"[{tc['id']}] {tc['difficulty']} {tc['task']}")
        print(f"{'='*50}")

        # Step 1: 跑 Agent
        trajectory, agent_output = agent.run_with_trajectory(tc["task"])
        print(f"\n📤 Agent:\n{agent_output[:300]}")

        # Step 2: Judge 打分
        j = judge(tc["task"], tc["reference"], agent_output)
        score = j["score"]
        reasoning = j["reasoning"]
        print(f"\n📊 Judge: {score}/5 | {reasoning}")

        # Step 3: 二阶检查 — Judge 跟 reference 矛盾吗？
        consistency = check_judge_vs_reference(tc["reference"], reasoning)
        print(f"🔍 二阶检查: {consistency}")

        # Step 4: 判断通过/失败
        lo, hi = tc["expected_range"]
        flags = []

        if score < lo:
            flags.append(f"🔴 低于预期 (预期≥{lo})")
        elif score > hi and consistency == "contradiction":
            flags.append(f"🟡 高分但 Judge 与 reference 矛盾")
        
        if consistency == "contradiction":
            flags.append("⚠️ Judge 可能误判")

        # Step 5: 判断路径
        if trajectory:
            t = check_trajectory(trajectory, tc["expected_tools"], tc['forbidden_tools'])
            if t['missing']:
                flags.append(f"🔴 缺少预期工具: {t['missing']}")
            if t['unexpected']:
                flags.append(f"🔴 调用了预期以外的工具: {t['unexpected']}")
            if t['total_steps'] > t['min_steps'] + 2:
                flags.append(f"🟡 步数冗余: {t['total_steps']}步 (最少{t['min_steps']}步)")

        status = "PASS" if not flags else "FAIL" if "🔴" in str(flags) else "WARN"
        if status == "PASS":
            passed += 1
        else:
            failed += 1

        results.append({
            "id": tc["id"],
            "task": tc["task"],
            "difficulty": tc["difficulty"],
            "score": score,
            "expected_range": tc["expected_range"],
            "consistency": consistency,
            "status": status,
            "flags": flags,
            "reasoning": reasoning,
        })

        for f in flags:
            print(f"  {f}")

    # ── Score Card ──
    print(f"\n\n{'='*60}")
    print(f"📋 Eval Suite Score Card")
    print(f"{'='*60}")
    print(f"{'ID':<6} {'难度':<6} {'分数':<6} {'预期':<10} {'二阶检查':<16} {'状态':<6}")
    print(f"{'-'*60}")
    for r in results:
        lo, hi = r["expected_range"]
        print(f"{r['id']:<6} {r['difficulty']:<6} {r['score']:<6} {lo}-{hi:<7} {r['consistency']:<16} {r['status']:<6}")

    print(f"{'-'*60}")
    total = len(results)
    print(f"\n  ✅ PASS: {passed}/{total}  |  ❌ FAIL/WARN: {failed}/{total}")
    print(f"  📊 平均分: {sum(r['score'] for r in results)/total:.1f}/5")


if __name__ == "__main__":
    main()
