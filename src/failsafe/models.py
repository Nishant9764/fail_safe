from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Step:
    step_id: int
    tool_name: str
    arguments: dict[str, Any]
    status: str  # "success" | "error"
    output: Any = None
    error_type: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class Trace:
    trace_id: str
    agent_version: str
    steps: tuple[Step, ...]

    @property
    def failed_steps(self) -> list[Step]:
        return [s for s in self.steps if s.status == "error"]