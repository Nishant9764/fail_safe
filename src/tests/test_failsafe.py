import json
from pathlib import Path
import pytest
from failsafe.parser import validate_trace, TraceValidationError
from failsafe.generator import generate_pytest_code
from failsafe.cli import main


def test_valid_trace_parsing_and_generation() -> None:
    raw = {
        "trace_id": "trace-001",
        "agent_version": "1.0",
        "steps": [
            {
                "step_id": 1,
                "tool_name": "read_file",
                "arguments": {"path": "/etc/hosts"},
                "status": "error",
                "error_type": "PermissionError",
                "error_message": "Access denied",
            }
        ],
    }
    trace = validate_trace(raw)
    assert len(trace.failed_steps) == 1
    code = generate_pytest_code(trace)
    assert "def test_trace_trace_001_step_1_read_file() -> None:" in code
    assert "'path': '/etc/hosts'" in code


@pytest.mark.parametrize(
    "invalid_payload, expected_msg",
    [
        ([], "Root of trace must be a JSON object"),
        ({"trace_id": ""}, "Missing or invalid 'trace_id'"),
        ({"trace_id": "t1", "steps": []}, "'steps' must be a non-empty list"),
        (
            {
                "trace_id": "t1",
                "steps": [{"step_id": 1, "tool_name": "123_invalid", "arguments": {}, "status": "error"}],
            },
            "must be a valid Python identifier",
        ),
        (
            {
                "trace_id": "t1",
                "steps": [{"step_id": 1, "tool_name": "valid_tool", "arguments": {}, "status": "error"}],
            },
            "failed steps require 'error_type'",
        ),
    ],
)
def test_invalid_traces_rejected(invalid_payload: object, expected_msg: str) -> None:
    with pytest.raises(TraceValidationError, match=expected_msg):
        validate_trace(invalid_payload)


def test_code_injection_in_arguments_is_neutralized() -> None:
    malicious_arg = "__import__('os').system('echo hacked')"
    raw = {
        "trace_id": "sec-test",
        "steps": [
            {
                "step_id": 1,
                "tool_name": "eval_tool",
                "arguments": {"payload": malicious_arg},
                "status": "error",
                "error_type": "SecurityError",
                "error_message": "Blocked",
            }
        ],
    }
    trace = validate_trace(raw)
    code = generate_pytest_code(trace)
    # Ensure it is serialized as a string literal, not executable AST Call node
    assert repr(malicious_arg) in code


def test_cli_end_to_end_and_generated_test_execution(tmp_path: Path) -> None:
    trace_file = Path("examples/failed_trace.json")
    out_file = tmp_path / "test_generated.py"

    exit_code = main([str(trace_file), "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()

    # Execute the generated file namespace in memory to verify it is runnable
    namespace: dict[str, object] = {}
    exec(out_file.read_text(encoding="utf-8"), namespace)
    test_fn = namespace["test_trace_run_9841_db_timeout_step_2_execute_sql_query"]
    assert callable(test_fn)
    test_fn()  # Runs the assertion block


def test_cli_returns_2_when_no_failures_present(tmp_path: Path) -> None:
    clean_trace = tmp_path / "clean.json"
    clean_trace.write_text(
        json.dumps(
            {
                "trace_id": "ok-1",
                "steps": [
                    {"step_id": 1, "tool_name": "ping", "arguments": {}, "status": "success"}
                ],
            }
        ),
        encoding="utf-8",
    )
    assert main([str(clean_trace)]) == 2