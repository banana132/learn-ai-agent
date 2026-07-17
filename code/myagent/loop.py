import json
import time
import tiktoken
class AgentLoop:
    
    def __init__(self, client, registry, model, max_iterations=10, token_limit=8000):
        self.client = client
        self.registry = registry
        self.model = model
        self.max_iterations = max_iterations
        self.token_limit = token_limit
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def _count_token(self, messages):
        total = 0
        for message in messages:
            content = message.get("content", "") or ""
            total += len(self.encoder.encode(content))
        return total
    
    def _trim_context(self, context, trim_last=6):
        if self._count_token(context) <= self.token_limit:
            return context
        head = context[:2]
        tail = context[-trim_last:]
        return head + tail
    
    def _serialize_tool_result(self, tool_result):
        if isinstance(tool_result, (dict, list)):
            return json.dumps(tool_result, ensure_ascii=False)
        if isinstance(tool_result, (str, int, float, bool)) or tool_result is None:
            return str(tool_result)
        return str(tool_result)

    def run(self, user_message: str) -> str:
        # while 循环 + messages 数组
        # 每次迭代: chat → 回填 assistant → 判断 tool_calls → 分发工具 → 回填 tool
        context = [
            {"role": "user", "content": user_message}
        ]
        times = 1
        while True:
            # print("start loop:", times, ', tools: ', self.registry.get_schema_list(), ', messages: ', context)
            # response = self._chat_with_retry(context)
            # print("raw response:", response.model_dump_json())
            # msg = response.choices[0].message
            # context.append({
            #     "role": "assistant",
            #     "content": msg.content,
            #     "tool_calls": msg.tool_calls,
            # })
            # tool_calls = msg.tool_calls

            try:
                content, tool_calls = self._chat_stream(context)
            except Exception as e:
                return str(e)
            context.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls,
            })
            if tool_calls:
                for tool_call in tool_calls:
                    print("tool call：", tool_call, type(tool_call))
                    tool_name = tool_call['function']['name']
                    tool_args = tool_call['function']['arguments']
                    try:
                        tool_result = self.registry.dispatch(tool_name, json.loads(tool_args))
                    except Exception as e:
                        print(f"Tool {tool_name} failed: {e}")
                        tool_result = {"error": str(e)}
                    print("call rslt：", tool_result, type(tool_result))
                    context.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": self._serialize_tool_result(tool_result)
                    })
                    context = self._trim_context(context)
                times += 1
                if times > self.max_iterations:
                    print("超过最大迭代次数结束：", content)
                    return content
            else:
                print("没有tool calls结束：", content)
                return content
        
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
    
    def _chat_stream(self, context):
        for attempt in range(3):
            try:
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=context,
                    tools=self.registry.get_schema_list(),
                    stream=True
                )
                break
            except Exception as e:
                if attempt == 2:
                    raise e
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)
        full_content = ""
        tool_call_buf = {}
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                full_content += delta.content
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_call_buf:
                        tool_call_buf[idx] = {"id":"", "name":"", "arguments":""}
                    buf = tool_call_buf[idx]
                    if tc.id:
                        buf["id"] = tc.id
                    if tc.function and tc.function.name:
                        buf["name"] = tc.function.name
                    if tc.function and tc.function.arguments:
                        buf["arguments"] += tc.function.arguments
        print()
        tool_calls = []
        for idx in sorted(tool_call_buf.keys()):
            tc = tool_call_buf[idx]
            tool_calls.append({
                'id': tc["id"],
                'type': 'function',
                'function': {
                    'name': tc["name"],
                    'arguments': tc["arguments"]
                },
            })
        return full_content, tool_calls