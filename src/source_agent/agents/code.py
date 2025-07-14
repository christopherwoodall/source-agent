class CodeAgent:
    def __init__(self, api_key=None, base_url=None, provider=None, model=None, prompt=None):
        self.api_key = api_key
        self.base_url = base_url
        self.provider = provider
        self.model = model
        self.prompt = prompt

    def greet(self):
        return "Hello, I am your coding assistant!"
