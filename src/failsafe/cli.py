import argparse
import sys
from pathlib import Path
from .parser import parse_trace_file, TraceValidationError
from .generator import generate_pytest_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="failsafe",
        description="Convert failed AI-agent tool traces into deterministic pytest regression tests.",
    )
    parser.add_argument(
        "trace_file",
        type=Path,
        help="Path to the JSON execution trace file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for the generated pytest file (prints to stdout if omitted).",
    )

    args = parser.parse_args(argv)

    try:
        trace = parse_trace_file(args.trace_file)
    except TraceValidationError as exc:
        print(f"[failsafe] Validation Error: {exc}", file=sys.stderr)
        return 1

    if not trace.failed_steps:
        print(
            f"[failsafe] No failed tool steps found in trace '{trace.trace_id}'. Nothing to generate.",
            file=sys.stderr,
        )
        return 2

    try:
        test_code = generate_pytest_code(trace)
    except Exception as exc:
        print(f"[failsafe] Generation Error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(test_code, encoding="utf-8")
            print(f"[failsafe] Generated {len(trace.failed_steps)} test(s) in '{args.output}'.")
        except OSError as exc:
            print(f"[failsafe] File Write Error: {exc}", file=sys.stderr)
            return 1
    else:
        print(test_code, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())