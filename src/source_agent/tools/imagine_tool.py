"""
The idea here is to let the agent hallucinate its own tools and have them
dynamically registered. Probably not a good idea...

See docs: https://github.com/awwaiid/gremllm
"""

from .plugins import registry

from gremllm import Gremllm


@registry.register(
    name="imagine",
    description="Imagine a new tool and register it dynamically.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the tool to imagine.",
            },
            "description": {
                "type": "string",
                "description": "A description of what the tool does.",
            },
            "parameters": {
                "type": "object",
                "description": "The parameters the tool accepts, in JSON schema format.",
            },
        },
        "required": ["name", "description", "parameters"],
    },
)
def imagine(name, description, parameters):
    """
    Imagine a new tool and register it dynamically.
    """
    tool = Gremllm(name)
    tool.description = description
    tool.parameters = parameters
    registry.register_tool(tool)
    return tool
