#!/usr/bin/env python3
"""List the consumers of a module and the contracts a change can affect.

Stdlib only. Read-only: it never writes to the repository.

Usage:
    python impact_analysis.py --root . --module @agent-platform/policy-engine
    python impact_analysis.py --root . --module agents/research-agent --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", ".terraform"}
SOURCE_SUFFIXES = (".ts", ".tsx", ".js", ".mjs", ".py", ".yaml", ".yml", ".toml")

# A module root is a directory that owns its own manifest.
MANIFEST_NAMES = ("package.json", "agent.yaml", "pyproject.toml")


def walk_files(root: str) -> list[str]:
    """Yield every source file under root, skipping generated and vendored trees."""
    found: list[str] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(SOURCE_SUFFIXES):
                found.append(os.path.join(base, name))
    return sorted(found)


def module_root(root: str, module: str) -> str:
    """Resolve a module name or path to a directory relative to root."""
    candidate = module.replace("\\", "/").strip("/")
    if candidate.startswith("@"):
        # Scoped package: find the package.json whose name matches.
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            if "package.json" not in files:
                continue
            path = os.path.join(base, "package.json")
            try:
                with open(path, encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
            if data.get("name") == candidate:
                return os.path.relpath(base, root).replace(os.sep, "/")
        return ""
    absolute = os.path.join(root, candidate)
    if os.path.isdir(absolute):
        return candidate
    return ""


def owns_manifest(directory: str) -> bool:
    return any(os.path.isfile(os.path.join(directory, name)) for name in MANIFEST_NAMES)


def import_patterns(module_dir: str) -> list[str]:
    """Build the textual patterns that mark a consumer of this module."""
    name = module_dir.rstrip("/").split("/")[-1]
    patterns = [
        rf"from\s+['\"]{re.escape(module_dir)}[/'\"]",
        rf"import\s+['\"]{re.escape(module_dir)}[/'\"]",
        rf"['\"]@agent-platform/{re.escape(name)}['\"]",
    ]
    return patterns


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--module", required=True, help="module path or package name")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    resolved = module_root(root, args.module)
    if not resolved:
        print(f"impact-analysis: module not found: {args.module}", file=sys.stderr)
        return 2

    module_dir = os.path.join(root, resolved)
    patterns = import_patterns(resolved)
    compiled = [re.compile(p) for p in patterns]

    consumers: list[dict[str, object]] = []
    for path in walk_files(root):
        if path.startswith(module_dir + os.sep):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        for pattern in compiled:
            if pattern.search(text):
                consumers.append(
                    {
                        "file": os.path.relpath(path, root).replace(os.sep, "/"),
                        "public_entry": owns_manifest(os.path.dirname(path))
                        or os.path.basename(path).startswith("index."),
                    }
                )
                break

    report = {
        "module": args.module,
        "resolved_path": resolved,
        "consumer_count": len(consumers),
        "consumers": consumers,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"module: {args.module}")
    print(f"path:   {resolved}")
    print(f"consumers: {len(consumers)}")
    print()
    print(f"{'consumer':<70} {'entry':<6}")
    for item in consumers:
        print(f"{item['file']:<70} {'yes' if item['public_entry'] else 'no':<6}")
    if not consumers:
        print("(none found)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
