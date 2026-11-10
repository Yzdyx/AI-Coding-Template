#!/usr/bin/env python3
"""Check relative documentation links and index reachability.

Rules:
  DOC-001  A relative link points at a path that does not exist.
  DOC-002  A document under docs/ is not reachable from any other document.

External links (http, https, mailto) are not fetched. Fenced code blocks are
skipped: a path inside an example is not a link.

Exit codes: 0 clean, 1 findings, 2 the script could not run.
"""

from __future__ import annotations

import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", ".terraform"}

# Markdown inline link and image syntax: [text](target) and ![alt](target)
LINK_RE = re.compile('!?\\[[^\\]]*\\]\\(([^)\\s]+)\\)')

FENCE_RE = re.compile(r"^\s*(```|~~~)")

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "ftp://")

# A document under these trees is checked for reachability.
INDEXED_ROOTS = ("docs/",)

# Reachability is not required for generated content and for entry points.
REACHABILITY_EXEMPT = ("docs/generated/",)


def walk_markdown(root: str) -> list[str]:
    """Every markdown file in the repository, as a repo-relative path."""
    found: list[str] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(".md"):
                path = os.path.join(base, name)
                found.append(os.path.relpath(path, root).replace(os.sep, "/"))
    return sorted(found)


def strip_code_blocks(text: str) -> str:
    """Blank out fenced code blocks so example paths are not treated as links."""
    output: list[str] = []
    inside = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            inside = not inside
            output.append("")
            continue
        output.append("" if inside else line)
    return "\n".join(output)


def check_links(root: str, documents: list[str]) -> list[tuple[str, int, str, str]]:
    findings: list[tuple[str, int, str, str]] = []
    for rel in documents:
        absolute = os.path.join(root, rel)
        try:
            with open(absolute, encoding="utf-8") as handle:
                text = strip_code_blocks(handle.read())
        except OSError as error:
            findings.append((rel, 0, "DOC-001", f"unreadable: {error}"))
            continue

        for number, line in enumerate(text.splitlines(), start=1):
            for match in LINK_RE.finditer(line):
                target = match.group(1)
                if target.startswith(EXTERNAL_PREFIXES) or target.startswith("#"):
                    continue
                path_part = target.split("#", 1)[0]
                if path_part == "":
                    continue
                resolved = os.path.normpath(os.path.join(os.path.dirname(absolute), path_part))
                if not os.path.exists(resolved):
                    findings.append((rel, number, "DOC-001", f"broken link -> {target}"))
    return findings


def check_reachability(root: str, documents: list[str]) -> list[tuple[str, int, str, str]]:
    """A document under docs/ must be linked from at least one other document."""
    referenced: set[str] = set()
    for rel in documents:
        absolute = os.path.join(root, rel)
        try:
            with open(absolute, encoding="utf-8") as handle:
                text = strip_code_blocks(handle.read())
        except OSError:
            continue
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            if target.startswith(EXTERNAL_PREFIXES) or target.startswith("#"):
                continue
            path_part = target.split("#", 1)[0]
            if path_part == "":
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(absolute), path_part))
            referenced.add(os.path.relpath(resolved, root).replace(os.sep, "/"))

    findings: list[tuple[str, int, str, str]] = []
    for rel in documents:
        if not rel.startswith(INDEXED_ROOTS):
            continue
        if rel.startswith(REACHABILITY_EXEMPT):
            continue
        if rel not in referenced:
            findings.append((rel, 0, "DOC-002", "not reachable from any other document"))
    return findings


def main(argv: list[str]) -> int:
    root = os.path.abspath(argv[1] if len(argv) > 1 else ".")
    if not os.path.isdir(root):
        print(f"check-doc-links: not a directory: {root}", file=sys.stderr)
        return 2

    documents = walk_markdown(root)
    if not documents:
        print("check-doc-links: no markdown documents found", file=sys.stderr)
        return 2

    findings = check_links(root, documents)
    findings += check_reachability(root, documents)
    findings.sort()

    for rel, number, code, message in findings:
        print(f"{rel}:{number}  {code}  {message}")

    print(f"documents={len(documents)} violations={len(findings)} affected_files={len({f[0] for f in findings})}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
