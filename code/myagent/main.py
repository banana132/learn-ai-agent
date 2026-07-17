import os
from openai import OpenAI
from registry import ToolRegistry
from loop import AgentLoop
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def get_weather(city: str) -> dict:
    return {
        "city": city,
        "temperature": 25,
        "weather": "sunny"
    }

def get_time() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def buggy_tool():
    raise ValueError("这个工具坏了!")

registry = ToolRegistry()
# 注册至少 2 个工具（建议：get_weather + get_time）
registry.register("get_weather", get_weather, {
    'type': 'function',
    'function': {
        'name': 'get_weather',
        'description': '获取指定城市当前天气. 输入城市名, 返回温度和天气状况.',
        'parameters': {
            'type': 'object',
            'properties': {
                'city': {'type': 'string', 'description': '城市名称，支持中文 (如 "深圳")'}
            }
        },
        'required': ['city']
    }
})
registry.register("get_time", get_time, {
    'type': 'function',
    'function': {
        'name': 'get_time',
        'description': '获取当前时间',
    }
})
registry.register("buggy_tool", buggy_tool, {
    'type': 'function',
    'function': {
        'name': 'buggy_tool',
        'description': '一个有bug的工具',
    }
})

client = OpenAI(
    base_url=os.getenv('GLM_BASE_URL'),
    api_key=os.getenv('GLM_API_KEY')
)
agent = AgentLoop(client, registry, os.getenv('GLM_MODEL'))
# result = agent.run("深圳现在几点了？天气怎么样？")
result = agent.run("调一下 buggy_tool，如果坏了就告诉我")
print('final result:', result)