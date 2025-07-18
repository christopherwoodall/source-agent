import os
import subprocess
import pathlib
import pytest
import tempfile
import shutil
import re
from source_agent.tools.file_list_tool import file_list_tool, load_gitignore
from source_agent.tools.file_read_tool import file_read_tool
from source_agent.tools.file_write_tool import file_write_tool
from source_agent.tools.file_search_tool import file_search_tool, build_plain_text_matcher, is_subpath
from source_agent.tools.execute_shell_command_tool import execute_shell_command
from source_agent.tools.run_pytest_tests_tool import run_pytest_tests
from source_agent.tools.directory_create_tool import directory_create_tool
from source_agent.tools.directory_delete_tool import directory_delete_tool
from source_agent.tools.file_delete_tool import file_delete_tool
from source_agent.tools.tool_registry import ToolRegistry
from source_agent.tools.web_search_tool import web_search_tool

# file_list_tool


def test_file_list_not_found(tmp_path):
    os.chdir(tmp_path)
    res = file_list_tool(path="nofile")
    assert not res["success"] and "Path not found" in res["error"]


def test_file_list_not_dir(tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "f.txt"
    f.write_text("x")
    res = file_list_tool(path="f.txt")
    assert not res["success"] and "Not a directory" in res["error"]


def test_file_list_non_recursive(tmp_path):
    os.chdir(tmp_path)
    (tmp_path / "a").mkdir()
    (tmp_path / "b.txt").write_text("x")
    res = file_list_tool(path=".", recursive=False)
    assert res["success"]
    assert "b.txt" in res["files"] and "a/" in res["files"]


def test_file_list_recursive(tmp_path):
    os.chdir(tmp_path)
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "c.txt").write_text("y")
    res = file_list_tool(path=".", recursive=True)
    assert res["success"] and "d/c.txt" in res["files"]


# file_read_tool


def test_file_read_success(tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "r.txt"
    f.write_text("hello")
    res = file_read_tool("r.txt")
    assert res["success"] and res["content"] == "hello"


def test_file_read_traversal(tmp_path):
    os.chdir(tmp_path)
    res = file_read_tool("../etc/passwd")
    assert not res["success"] and "Path traversal" in res["error"]


def test_file_read_not_found(tmp_path):
    os.chdir(tmp_path)
    res = file_read_tool("nofile")
    assert not res["success"] and "File not found" in res["error"]


# file_write_tool


def test_file_write_success(tmp_path):
    os.chdir(tmp_path)
    res = file_write_tool("w.txt", "data")
    assert res["success"] and (tmp_path / "w.txt").read_text() == "data"


def test_file_write_traversal(tmp_path):
    os.chdir(tmp_path)
    res = file_write_tool("../w.txt", "x")
    assert not res["success"] and "Path traversal" in res["error"]


# file_search_tool


def test_file_search_name_only(tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "f1.txt"
    f.write_text("X\nY\nZ")
    res = file_search_tool(name="*.txt")
    assert res["success"] and any("f1.txt" in item for item in res["content"])


def test_file_search_with_pattern(tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "f2.txt"
    f.write_text("hello world\nabc hello")
    res = file_search_tool(name="f2.txt", pattern="hello", ignore_case=False)
    assert res["success"] and any(":1:" in item for item in res["content"])


# helper tests


def test_build_plain_text_matcher():
    m = build_plain_text_matcher("AbC", ignore_case=True)
    assert m("xxabcxx")
    m2 = build_plain_text_matcher("AbC", ignore_case=False)
    assert not m2("xxabcxx")


def test_is_subpath(tmp_path):
    base = tmp_path
    sub = tmp_path / "s"
    sub.mkdir()
    assert is_subpath(sub, base)
    outside = pathlib.Path(tmp_path.parent)
    assert not is_subpath(outside, base)


# execute_shell_command


def test_execute_shell_command_success():
    res = execute_shell_command("echo hi")
    assert res["success"] and res["stdout"] == "hi"


# run_pytest_tests


def test_run_pytest_tests_traversal(tmp_path):
    os.chdir(tmp_path)
    res = run_pytest_tests(target_paths=[str(tmp_path.parent)])
    assert not res["success"] and "Path traversal" in res["error"]


def test_run_pytest_tests_no_tests(tmp_path):
    os.chdir(tmp_path)
    res = run_pytest_tests()
    assert res["exit_code"] != 0


# directory_create_tool


def test_directory_create_tool_success(tmp_path):
    os.chdir(tmp_path)
    res = directory_create_tool(path="d1")
    assert res["success"] and (tmp_path / "d1").exists()


def test_directory_create_tool_traversal(tmp_path):
    os.chdir(tmp_path)
    res = directory_create_tool(path="../d")
    assert not res["success"] and "Path traversal" in res["error"]


# directory_delete_tool


def test_directory_delete_tool_success(tmp_path):
    os.chdir(tmp_path)
    d = tmp_path / "dd"
    d.mkdir()
    res = directory_delete_tool(path="dd")
    assert res["success"] and not d.exists()


def test_directory_delete_tool_recursive(tmp_path):
    os.chdir(tmp_path)
    d = tmp_path / "rr"
    (d / "x").mkdir(parents=True)
    res = directory_delete_tool(path="rr", recursive=True)
    assert res["success"] and not d.exists()


# file_delete_tool


def test_file_delete_tool_success(tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "fx.txt"
    f.write_text("hi")
    res = file_delete_tool(path="fx.txt")
    assert res["success"] and not f.exists()


# tool_registry


def test_tool_registry_register():
    tr = ToolRegistry()

    @tr.register(name="n", description="d", parameters={})
    def fn():
        return True

    tools = tr.get_tools()
    mapping = tr.get_mapping()
    assert any(t["function"]["name"] == "n" for t in tools)
    assert mapping["n"] is fn


# web_search_tool error


def test_web_search_tool_failure(monkeypatch):
    class BadDDGS:
        def text(self, query, max_results):
            raise RuntimeError("fail")

    monkeypatch.setattr("source_agent.tools.web_search_tool.DDGS", BadDDGS)
    res = web_search_tool(query="x")
    assert not res["success"] and "Search failed" in res["content"][0]
