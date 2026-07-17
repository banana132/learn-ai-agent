from myagent.loop import AgentLoop

# 造一个假的 AgentLoop 实例
agent = AgentLoop(client=None, registry=None, model="test", token_limit=100)

# 造 50 条假消息
messages = [{"role": "user", "content": "初始任务"}]
for i in range(50):
    messages.append({"role": "assistant", "content": f"第 {i} 轮的回复，凑点 token"})

before = agent._count_token(messages)
messages = agent._trim_context(messages)
after = agent._count_token(messages)

print(f"裁剪前 token: {before}")
print(f"裁剪后 token: {after}")
print(f"保留消息数: {len(messages)}")
print(f"第一条: {messages[0]['content'][:20]}")
print(f"第二条: {messages[1]['content'][:20]}")