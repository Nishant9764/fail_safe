## FAILSAFE

**Turn AI-agent tool failures into repeatable tests.**

FAILSAFE is an early-stage, open-source Python CLI prototype that converts recorded AI-agent execution traces into deterministic `pytest` tests.

The initial goal is to help developers preserve a recorded tool failure as a repeatable test case—without calling a live AI model, connecting to real tools, or making paid API requests.

> **Project status:** Prototype / early MVP. The current generated tests replay recorded failures with a stub. They do not yet prove that a real AI agent handles those failures correctly.

## What it does

Given a JSON file containing an agent execution trace, FAILSAFE aims to:

1. Read and validate the trace.
2. Identify tool steps whose status is `error`.
3. Generate a Python `pytest` file for those failed steps.
4. Let developers run the generated tests locally and repeatedly.

## What it does not do yet

- It does not diagnose every kind of AI-agent failure.
- It does not run an AI model or call an external API.
- It does not execute recorded SQL or invoke live tools.
- The generated tests do not yet validate a real agent's recovery or error-handling logic.

## Project structure

```text
failsafe/
├── pyproject.toml
├── README.md
├── src/
│   └── failsafe/
│       ├── __init__.py
│       ├── models.py
│       ├── parser.py
│       ├── generator.py
│       └── cli.py
├── examples/
│   └── failed_trace.json
└── tests/
    └── test_failsafe.py
```

## Requirements

- Python 3.11+
- `pip`
- `pytest` for development and tests

The package has no runtime dependencies beyond the Python standard library.

## Setup

From the project root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project with its development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Run the tests

```bash
python -m pytest -v
```

## Use the CLI

Print generated test code to the terminal:

```bash
failsafe examples/failed_trace.json
```

Write the generated test to a file:

```bash
failsafe examples/failed_trace.json --output tests/test_generated.py
```

Run the generated test:

```bash
python -m pytest -v tests/test_generated.py
```

The CLI accepts a JSON trace file as its positional argument. Use `--help` to view its available options.

## Trace format

A minimal example of a failed tool step:

```json
{
  "trace_id": "database-timeout",
  "agent_version": "0.1.0",
  "steps": [
    {
      "step_id": 1,
      "tool_name": "execute_sql_query",
      "arguments": {
        "query": "SELECT * FROM orders",
        "timeout_ms": 500
      },
      "status": "error",
      "error_type": "TimeoutError",
      "error_message": "Database query timed out."
    }
  ]
}
```

A trace must contain a non-empty `trace_id` and a non-empty `steps` list. Each step must have an integer `step_id`, a valid Python-identifier `tool_name`, an object of `arguments`, and a status of `success` or `error`. Failed steps must include an `error_type` and an `error_message`.

## Safety notes

Treat traces as untrusted input. The generator should never execute code or tools embedded in a trace. Syntax validation of generated Python is not a security boundary, so generated source must be reviewed and tested for safe handling of untrusted values before using this project with external traces.

Do not run generated tests from untrusted traces until the code-generation security issues have been reviewed and fixed.

## Roadmap

- [ ] Validate trace parsing and CLI behavior with automated tests.
- [ ] Fix and test code-generation handling for untrusted trace IDs, versions, and tool names.
- [ ] Improve generated-test validation and execution safety.
- [ ] Document the precise behavior and limitations of generated replay tests.
- [ ] Explore adapters for testing real agent tool wrappers and error handling.

"""

output_path = "/mnt/data/README.md"
pypandoc.convert_text(readme, "md", format="md", outputfile=output_path, extra_args=["--standalone"])
print(f"Created {output_path}")


# FAILSAFE

**Turn AI-agent tool failures into deterministic `pytest` regression tests.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Dependencies: Zero](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](#architecture--security)
[![Code Style: Strict](https://img.shields.io/badge/typing-strict-informational.svg)](#)

---

## The Problem

When an AI agent fails in production, debugging is a nightmare. 
Traditional software fails on deterministic stack traces; AI agents fail across multi-turn tool executions driven by non-deterministic LLM outputs. Trying to reproduce a production tool crash by re-prompting an LLM in a staging environment is slow, expensive, and flaky.

**What `failsafe` does:** It acts as a static compiler for agent execution traces. Give it a JSON log of a crashed agent run, and it extracts the exact tool failure boundaries, sanitizes the payloads, and emits a standalone, zero-network `pytest` regression harness.

**What `failsafe` does NOT do:** It does not fix prompt hallucinations, evaluate tone, or grade semantic quality. It targets hard boundary failures: unhandled tool exceptions, schema violations, policy rejections, and timeout crashes.

---

## Quickstart

### 1. Installation

`failsafe` requires **Python 3.11+** and uses **zero external runtime dependencies**.

```bash
git clone [https://github.com/your-org/failsafe.git](https://github.com/your-org/failsafe.git)
cd failsafe
python3 -m venv .venv
source .venv/bin/activate

# Install runtime CLI only
pip install .

# Or install with pytest to run the test suites
pip install -e ".[dev]"
```

## Contributing

Contributions, bug reports, and thoughtful feedback are welcome. This is an early prototype, so please open an issue to discuss significant changes before submitting a large pull request.


## License

<ElicitationsGroup message="Ready to evolve the prototype? Pick the next engineering milestone:">
  <Elicitation label="Build Phase 1: Live agent mock-patching (--target flag)" query="Let's build Phase 1 of the roadmap: update failsafe to accept a --target module:callable CLI flag and generate unittest.mock.patch harnesses that test a real Python function."/>
  <Elicitation label="Build Phase 2: OpenTelemetry span ingestion adapter" query="Write an OpenTelemetry JSON span adapter for failsafe that converts standard OTel trace exports into failsafe's internal Trace dataclass."/>
  <Elicitation label="Create a GitHub Actions workflow for automated trace testing" query="Write a complete GitHub Actions CI workflow (.github/workflows/ci.yml) that lints failsafe, runs pytest, and automatically compiles any new JSON traces added to an incidents/ folder."/>
</ElicitationsGroup>
