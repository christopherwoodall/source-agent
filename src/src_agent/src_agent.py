import openai

from pathlib import Path


class Agent:
    def __init__(self, api_key=None, base_url=None, provider=None, model=None, prompt=None):
        self.api_key = api_key
        self.base_url = base_url
        
        self.model_string = "/".join([provider, model])
        self.temperature = 0.7

        self.messages = []
        self.prompt = prompt
        self.system_prompt = Path("AGENTS.md").read_text(encoding="utf-8")

        self.messages.append({"role": "system", "content": self.system_prompt})
        self.messages.append({"role": "user", "content": self.prompt})
        
        self.session = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

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


    def greet(self):
        return f"Hello, I am {self.model_string}."
