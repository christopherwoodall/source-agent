import pytest
from source_agent.agents.code import CodeAgent, AgentEventType


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    monkeypatch.setattr("source_agent.agents.code.openai.OpenAI", lambda *args, **kwargs: None)


class DummyFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class DummyToolCall:
    def __init__(self, function, id):
        self.function = function
        self.id = id


class DummyMessage:
    def __init__(self, content, tool_calls):
        self.content = content
        self.tool_calls = tool_calls


class DummyChoice:
    def __init__(self, message):
        self.message = message


class DummyResponse:
    def __init__(self, choice):
        self.choices = [choice]


def test_run_stops_on_msg_complete():
    agent = CodeAgent(api_key="k", base_url="u", model="m", temperature=0, system_prompt="SP")

    def fake_call_llm(messages):
        fn = DummyFunction(name="msg_complete_tool", arguments="{}")
        tc = DummyToolCall(function=fn, id="1")
        msg = DummyMessage(content="", tool_calls=[tc])
        return DummyResponse(DummyChoice(msg))

    agent.call_llm = fake_call_llm
    events = list(agent.run(user_prompt="hi", max_steps=1))
    types = [e.type for e in events]
    assert AgentEventType.ITERATION_START in types
    assert AgentEventType.TOOL_CALL in types
    assert AgentEventType.TASK_COMPLETE in types


def test_run_max_steps_reached():
    agent = CodeAgent(api_key="k", base_url="u", model="m", temperature=0, system_prompt="SP")

    def fake_call_llm(messages):
        msg = DummyMessage(content="hello", tool_calls=[])
        return DummyResponse(DummyChoice(msg))

    agent.call_llm = fake_call_llm
    events = list(agent.run(user_prompt="hi", max_steps=2))
    assert sum(1 for e in events if e.type == AgentEventType.ITERATION_START) == 2
    assert events[-1].type == AgentEventType.MAX_STEPS_REACHED
