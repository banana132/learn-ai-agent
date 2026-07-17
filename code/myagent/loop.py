import json
import time
class AgentLoop:
    
    def __init__(self, client, registry, model, max_iterations=10):
        self.client = client
        self.registry = registry
        self.model = model
        self.max_iterations = max_iterations

    def run(self, user_message: str) -> str:
        # while 循环 + messages 数组
        # 每次迭代: chat → 回填 assistant → 判断 tool_calls → 分发工具 → 回填 tool
        context = [
            {"role": "user", "content": user_message}
        ]
        times = 1
        while True:
            print("start loop:", times, ', tools: ', self.registry.get_schema_list(), ', messages: ', context)
            response = self._chat_with_retry(context)
            print("raw response:", response.model_dump_json())
            msg = response.choices[0].message
            context.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": msg.tool_calls,
            })
            if msg.tool_calls:
                print("有tool calls：", msg.tool_calls)
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments
                    try:
                        tool_result = self.registry.dispatch(tool_name, json.loads(tool_args))
                    except Exception as e:
                        print(f"Tool {tool_name} failed: {e}")
                        tool_result = {"error": str(e)}
                    context.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })
                times += 1
                if times > self.max_iterations:
                    print("超过最大迭代次数结束：", msg.content)
                    return msg.content
            else:
                print("没有tool calls结束：", msg.content)
                return msg.content
        
    def _chat_with_retry(self, context, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=context,
                    tools=self.registry.get_schema_list()
                )
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)