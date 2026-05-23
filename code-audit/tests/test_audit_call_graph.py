"""Tests for audit_call_graph.py against the sample fixture."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "audit_call_graph.py"
FIXTURE = Path(__file__).parent.parent / "fixtures" / "sample_module.py"


def run_audit(target):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    return json.loads(result.stdout)


def test_fixture_functions_detected():
    data = run_audit(FIXTURE)
    names = [f["name"] for f in data["functions"]]
    expected = [
        "main",
        "process_data",
        "validate_input",
        "format_output",
        "DataProcessor.__init__",
        "DataProcessor.run",
        "DataProcessor._transform",
        "DataProcessor._validate",
        "DataProcessor._format",
        "helper",
        "recursive_func",
    ]
    assert names == expected


def test_fixture_call_graph():
    data = run_audit(FIXTURE)
    cg = data["call_graph"]
    assert cg["main"] == ["process_data", "format_output"]
    assert cg["process_data"] == ["validate_input"]
    assert cg["DataProcessor.run"] == ["DataProcessor._transform", "DataProcessor._format"]
    assert cg["DataProcessor._transform"] == ["DataProcessor._validate"]
    assert cg["recursive_func"] == ["recursive_func"]


def test_fixture_entry_points():
    data = run_audit(FIXTURE)
    assert set(data["entry_points"]) == {
        "main",
        "DataProcessor.__init__",
        "DataProcessor.run",
        "helper",
        "recursive_func",
    }


def test_fixture_cycles():
    data = run_audit(FIXTURE)
    assert data["cycles"] == ["recursive_func"]


def test_fixture_complexity():
    data = run_audit(FIXTURE)
    complexity = {f["name"]: f["complexity"] for f in data["functions"]}
    assert complexity["main"] == 1
    assert complexity["process_data"] == 3
    assert complexity["validate_input"] == 2
    assert complexity["format_output"] == 1
    assert complexity["DataProcessor.__init__"] == 1
    assert complexity["DataProcessor.run"] == 2
    assert complexity["DataProcessor._transform"] == 3
    assert complexity["DataProcessor._validate"] == 2
    assert complexity["DataProcessor._format"] == 1
    assert complexity["helper"] == 1
    assert complexity["recursive_func"] == 2


def test_fixture_line_ranges():
    data = run_audit(FIXTURE)
    func_map = {f["name"]: f for f in data["functions"]}
    assert func_map["main"]["line_start"] == 30
    assert func_map["helper"]["line_start"] == 80
    assert func_map["recursive_func"]["line_start"] == 84


def test_fixture_called_by():
    data = run_audit(FIXTURE)
    func_map = {f["name"]: f for f in data["functions"]}
    assert func_map["validate_input"]["called_by"] == ["process_data"]
    assert func_map["process_data"]["called_by"] == ["main"]
    assert "DataProcessor.run" in func_map["DataProcessor._transform"]["called_by"]


def test_determinism():
    data1 = run_audit(FIXTURE)
    data2 = run_audit(FIXTURE)
    assert data1 == data2


def test_no_args_shows_usage():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Usage" in result.stderr
