import json

import openai

from pathlib import Path


def test_tool():
    return "THIS WAS A TEST OF TOOL USAGE. THE SECRET IS '6789012345'"


tools = [
  {
    "type": "function",
    "function": {
      "name": "test_tool",
      "description": "A tool for testing purposes.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  }
]


TOOL_MAPPING = {
    "test_tool": test_tool
}


class Agent:
    def __init__(self, api_key=None, base_url=None, provider=None, model=None, prompt=None):
        self.api_key = api_key
        self.base_url = base_url
        
        self.model_string = "/".join([provider, model])
        self.temperature = 0.7

        self.messages = []
        self.prompt = prompt
        self.system_prompt = Path("AGENTS.md").read_text(encoding="utf-8")
      
        self.session = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        # self.messages.append({"role": "system", "content": self.system_prompt})
        # self.messages.append({"role": "user", "content": self.prompt})

        # completion = session.chat.completions.create(
        #     model=model, messages=messages, temperature=temperature
        # )

        # response = completion.choices[0].message.content

        # messages.append({"role": "assistant", "content": response})
                
        # print(src_agent)
        # print(response)
        # print("\n---\n")
        # print("Messages:" f"\n{messages}\n---\n")

        # return response

        self.system_prompt = "You are a helpful assistant."
        self.prompt = "Test tool usage."

        self.messages.append({"role": "system", "content": self.system_prompt})
        self.messages.append({"role": "user", "content": self.prompt})


        response_1 = self.chat(message="test tool usage")
        response_2 = response_1.choices[0]

        import pprint
        print(response_1)
        pprint.pprint(response_1.to_dict())

        tool_calls = response_2.message.tool_calls

        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call.function.name

                tool_args = json.loads(tool_call.function.arguments)

                # Look up the correct tool locally, and call it with the provided arguments
                # Other tools can be added without changing the agentic loop
                tool_response = TOOL_MAPPING[tool_name](**tool_args)

                # self.messages.append({
                # "role": "tool",
                # "tool_call_id": tool_call.id,
                # "name": tool_name,
                # "content": json.dumps(tool_response),
                # })

                print(f"Tool call: {tool_name} with args: {tool_args}")
                print(f"Tool response: {tool_response}")


    def determine_intent(self, message):
        ...


    def chat(self, message=None):
        if message:
            self.messages.append({"role": "user", "content": message})

        request = {
            "model": self.model_string,
            "messages": self.messages,
            "tools": tools,
            "temperature": self.temperature
        }

        response = self.session.chat.completions.create(**request)

        # return response.choices[0].message.content
        return response
    

    def greet(self):
        return f"Hello, I am {self.model_string}."


# Resources
# - https://openrouter.ai/docs/features/tool-calling
# - https://openrouter.ai/docs/api-reference/overview
