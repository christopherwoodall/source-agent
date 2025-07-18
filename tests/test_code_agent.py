import json
import pytest
import json
from source_agent.agents.code import CodeAgent


class DummyFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class DummyToolCall:
    def __init__(self, function, id):
        self.function = function
        self.id = id


@pytest.fixture
def agent(monkeypatch):
    c = CodeAgent(api_key="key", base_url="url", model="m", temperature=0.1, system_prompt="SP")
    c.tool_mapping.clear()
    return c


def test_parse_response_message_json(monkeypatch):
    monkeypatch.setattr("source_agent.agents.code.openai.OpenAI", lambda *args, **kwargs: None)
    json_snip = "{'type':'text','text':'hello world'}"
    msg = f"prefix {json_snip} suffix"
    c = CodeAgent(system_prompt="SP")
    result = c.parse_response_message(msg)
    assert result == "hello world"


def test_parse_response_message_plain(monkeypatch):
    monkeypatch.setattr("source_agent.agents.code.openai.OpenAI", lambda *args, **kwargs: None)
    c = CodeAgent(system_prompt="SP")
    assert c.parse_response_message("  foo bar  ") == "foo bar"


def test_handle_tool_call_success(agent):
    def func(x, y):
        return {"sum": x + y}

    agent.tool_mapping["foo"] = func
    fn = DummyFunction(name="foo", arguments=json.dumps({"x": 2, "y": 3}))
    call = DummyToolCall(function=fn, id="tid")
    res = agent.handle_tool_call(call)
    assert res["role"] == "tool"
    assert res["tool_call_id"] == "tid"
    assert res["name"] == "foo"
    content = json.loads(res["content"])
    assert content == {"sum": 5}


def test_handle_tool_call_invalid_json(agent):
    fn = DummyFunction(name="foo", arguments="notjson")
    call = DummyToolCall(function=fn, id="tid")
    res = agent.handle_tool_call(call)
    content = json.loads(res["content"])
    assert "Invalid JSON arguments" in content["error"]


def test_handle_tool_call_unknown(agent):
    fn = DummyFunction(name="bar", arguments=json.dumps({}))
    call = DummyToolCall(function=fn, id="tid")
    res = agent.handle_tool_call(call)
    content = json.loads(res["content"])
    assert "Unknown tool" in content["error"]
