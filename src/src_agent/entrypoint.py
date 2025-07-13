import os

import openai


# TODO - Check args for provider
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", False)
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY environment variable")


session = openai.OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

messages = []


# # # # model = "google/gemma-7b-it"
# # # # model = "nousresearch/nous-capybara-34b"
# # # # model = "microsoft/wizardlm-2-7b"
# # # # model = "meta-llama/llama-2-13b-chat"
# # # # model = "openai/gpt-3.5-turbo"
# # # model = "moonshotai/kimi-k2"
# # This is free right now.
# # model = "moonshotai/kimi-k2:free"

# # temperature = 0.7

# # messages.append({"role": "system", "content": system_prompt})
# # messages.append({"role": "user", "content": message})

# completion = session.chat.completions.create(
#     model=model, messages=messages, temperature=temperature
# )

# response = completion.choices[0].message.content

# messages.append(
#     {"role": "assistant", "content": response}
# )

# print(response)


def main():
    print("Welcome to the Source Agent!")


if __name__ == "__main__":
    main()


# Resources
#  - [Using OpenRouter with Python](https://openrouter.ai/docs/quickstart)
