class ToolRegistry:
    def __init__(self):
        self._tools = {}       # name → callable
        self._schemas = []     # OpenAI tool schema 列表

    def register(self, name, fn, schema):
        self._tools[name] = fn
        self._schemas.append(schema)

    def get_schema_list(self):
        tools = []
        for schema in self._schemas:
            tools.append(schema)
        return tools

    def dispatch(self, name, args):
        fn = self._tools.get(name)
        if fn is None:
            raise ValueError(f"Tool {name} not found")
        return fn(**(args or {}))