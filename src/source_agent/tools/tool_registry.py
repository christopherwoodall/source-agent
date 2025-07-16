class ToolRegistry:
    def __init__(self):
        self.tools = []
        self.tool_mapping = {}

    def register(self, name, description, parameters):
        def decorator(func):
            self.tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": description,
                        "parameters": parameters,
                    },
                }
            )
            self.tool_mapping[name] = func
            return func

        return decorator

    def get_tools(self):
        return self.tools

    def get_mapping(self):
        return self.tool_mapping


# Global registry instance
registry = ToolRegistry()
