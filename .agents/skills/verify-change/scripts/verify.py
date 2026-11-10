#!/usr/bin/env python3
"""Run the repository quality gates and report the real result of each one.

Stdlib only. It runs commands; it never edits a file.

Usage:
    python verify.py --root .
    python verify.py --root . --json
    python verify.py --root . --only doc-links
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

# name, argv, required
GATES: list[tuple[str, list[str], bool]] = [
    ("architecture", ["python", "scripts/check-architecture.py"], True),
    ("agent-manifests", ["python", "scripts/check-agent-manifests.py"], True),
    ("doc-links", ["python", "scripts/check-doc-links.py"], True),
]


def run_gate(root: str, name: str, argv: list[str], required: bool) -> dict[str, object]:
    """Run one gate. A missing script is reported as blocked, never as passed."""
    script = argv[1] if len(argv) > 1 else ""
    if script and not os.path.isfile(os.path.join(root, script)):
        return {
            "gate": name,
            "status": "blocked",
            "command": " ".join(argv),
            "reason": f"{script} does not exist",
        }
    try:
        completed = subprocess.run(
            argv,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "gate": name,
            "status": "blocked",
            "command": " ".join(argv),
            "reason": str(error),
        }

    output = (completed.stdout + completed.stderr).strip()
    return {
        "gate": name,
        "status": "pass" if completed.returncode == 0 else "fail",
        "required": required,
        "command": " ".join(argv),
        "exit_code": completed.returncode,
        "output": output,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--only", default="", help="run one gate by name")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    selected = [g for g in GATES if not args.only or g[0] == args.only]
    if not selected:
        print(f"verify: no gate named {args.only!r}", file=sys.stderr)
        return 2

    results = [run_gate(root, name, cmd, required) for name, cmd, required in selected]

    if args.json:
        print(json.dumps({"root": root, "results": results}, indent=2))
    else:
        print(f"verify-change: {len(results)} gate(s) in {root}")
        for item in results:
            print(f"[{item['status']}] {item['gate']}: {item['command']}")
            if item.get("reason"):
                print(f"        reason: {item['reason']}")
            elif item["status"] != "pass" and item.get("output"):
                for line in str(item["output"]).splitlines()[:20]:
                    print(f"        {line}")

    failed = [r for r in results if r["status"] == "fail" and r.get("required", True)]
    blocked = [r for r in results if r["status"] == "blocked"]
    print()
    print(f"pass: {sum(1 for r in results if r['status'] == 'pass')} "
          f"fail: {len(failed)} blocked: {len(blocked)}")
    return 1 if failed or blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
