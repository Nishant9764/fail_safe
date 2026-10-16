import json
from pathlib import Path
from typing import Any
from .models import Step, Trace


class TraceValidationError(ValueError):
    """Raised when an execution trace violates the required schema."""


def parse_trace_file(path: Path) -> Trace:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TraceValidationError(f"Cannot read file '{path}': {exc}") from exc

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise TraceValidationError(f"Invalid JSON in '{path}': {exc}") from exc

    return validate_trace(data)


def validate_trace(data: Any) -> Trace:
    if not isinstance(data, dict):
        raise TraceValidationError("Root of trace must be a JSON object.")

    trace_id = data.get("trace_id")
    if not isinstance(trace_id, str) or not trace_id.strip():
        raise TraceValidationError("Missing or invalid 'trace_id' (must be non-empty string).")

    agent_version = data.get("agent_version", "unknown")
    if not isinstance(agent_version, str):
        raise TraceValidationError("'agent_version' must be a string.")

    raw_steps = data.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise TraceValidationError("'steps' must be a non-empty list.")

    steps: list[Step] = []
    for idx, item in enumerate(raw_steps):
        if not isinstance(item, dict):
            raise TraceValidationError(f"Step at index {idx} must be an object.")

        step_id = item.get("step_id")
        if not isinstance(step_id, int) or isinstance(step_id, bool):
            raise TraceValidationError(f"Step {idx}: 'step_id' must be an integer.")

        tool_name = item.get("tool_name")
        if not isinstance(tool_name, str) or not tool_name.isidentifier():
            raise TraceValidationError(
                f"Step {idx}: 'tool_name' must be a valid Python identifier, got {tool_name!r}."
            )

        arguments = item.get("arguments")
        if not isinstance(arguments, dict):
            raise TraceValidationError(f"Step {idx}: 'arguments' must be a JSON object.")

        status = item.get("status")
        if status not in ("success", "error"):
            raise TraceValidationError(
                f"Step {idx}: 'status' must be 'success' or 'error', got {status!r}."
            )

        error_type = item.get("error_type")
        error_message = item.get("error_message")

        if status == "error":
            if not isinstance(error_type, str) or not error_type.strip():
                raise TraceValidationError(f"Step {idx}: failed steps require 'error_type'.")
            if not isinstance(error_message, str):
                raise TraceValidationError(f"Step {idx}: failed steps require 'error_message'.")

        steps.append(
            Step(
                step_id=step_id,
                tool_name=tool_name,
                arguments=arguments,
                status=status,
                output=item.get("output"),
                error_type=error_type,
                error_message=error_message,
            )
        )

    return Trace(trace_id=trace_id, agent_version=agent_version, steps=tuple(steps))