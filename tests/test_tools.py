import math
import re
import datetime
import pytest
from source_agent.tools.calculator_tool import calculate_expression_tool
from source_agent.tools.get_current_date import get_current_date
from source_agent.tools.msg_complete_tool import msg_complete_tool


def test_calculate_expression_simple():
    assert calculate_expression_tool("2+3") == 5


def test_calculate_expression_funcs_and_constants():
    res = calculate_expression_tool("sqrt(16)+pi")
    assert isinstance(res, float)
    assert res == math.sqrt(16) + math.pi


@pytest.mark.parametrize(
    "expr,err",
    [
        ("2+*3", "Invalid expression syntax"),
        ("5/0", "Division or modulo by zero"),
        ("foo(3)", "Unsupported or non-callable function"),
    ],
)
def test_calculate_expression_errors(expr, err):
    out = calculate_expression_tool(expr)
    assert "Error:" in out
    assert err in out


def test_get_current_date_format():
    result = get_current_date()
    assert result["success"] is True
    dt = datetime.datetime.fromisoformat(result["current_datetime"])
    assert isinstance(dt, datetime.datetime)


def test_msg_complete_tool():
    result = msg_complete_tool()
    assert result["success"] is True
    content = result["content"]
    assert content["status"] == "completed"
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", content["timestamp"])
