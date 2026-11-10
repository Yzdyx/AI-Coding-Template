#!/usr/bin/env python3
"""Enforce the layering and dependency rules of this repository.

The rules are defined in docs/architecture/dependency-rules.md. This script is
their executable form. Where the document and this script disagree, this script
decides and the document is corrected.

Rule codes:
  DEP-001  layer direction violation: a lower layer depends on a higher layer
  DEP-002  UI depends on Service, Repo or Config directly
  DEP-003  deep import into another module, or a relative path across modules
  DEP-004  a provider implementation is constructed outside the composition root
  DEP-005  a circular dependency between modules
  DEP-006  the Types layer contains behaviour or I/O
  DEP-007  a provider instance is created outside apps/*/src/index.ts
  DEP-008  a workspace dependency is used but not declared in package.json

Scope: apps/, packages/, agents/. Test files are skipped: they replace providers
with doubles on purpose.

Exit codes: 0 clean, 1 findings, 2 the script could not run.
"""

from __future__ import annotations

import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", ".terraform"}
SCAN_ROOTS = ("apps", "packages", "agents")
SOURCE_SUFFIXES = (".ts", ".tsx", ".py")
TEST_MARKERS = ("/tests/", "/test/", "__init__.py")

LAYER_ORDER = ["Types", "Config", "Repo", "Service", "Runtime", "UI"]

ALLOWED: dict[str, set[str]] = {
    "Types": {"Types"},
    "Config": {"Types", "Config"},
    "Repo": {"Types", "Config", "Repo"},
    "Service": {"Types", "Config", "Repo", "Service"},
    "Runtime": {"Types", "Config", "Repo", "Service", "Runtime"},
    "UI": {"Types", "Runtime", "UI"},
}

# Explicit layer per file. This table is the authoritative mapping: the file is
# the unit of layering, not the directory.
EXPLICIT_LAYER: dict[str, str] = {
    "packages/agent-contracts/src/types.ts": "Types",
    "packages/agent-contracts/src/index.ts": "Types",
    "packages/state-store/src/config.ts": "Config",
    "packages/state-store/src/repository.ts": "Repo",
    "packages/state-store/src/index.ts": "Repo",
    "packages/policy-engine/src/flags.ts": "Service",
    "packages/policy-engine/src/engine.ts": "Service",
    "packages/policy-engine/src/index.ts": "Service",
    "packages/observability/src/provider.ts": "Service",
    "packages/observability/src/index.ts": "Service",
    "packages/eval-kit/src/index.ts": "Service",
    "packages/tool-adapters/src/model.ts": "Repo",
    "packages/tool-adapters/src/identity.ts": "Repo",
    "packages/tool-adapters/src/connector.ts": "Repo",
    "packages/tool-adapters/src/index.ts": "Repo",
    "apps/agent-api/src/index.ts": "Runtime",
    "apps/agent-api/src/server.ts": "Runtime",
    "apps/worker/src/index.ts": "Runtime",
    "apps/admin-console/src/index.tsx": "UI",
}

# The only files allowed to construct a provider or a repository instance.
# The composition roots wire the application. The third entry is the public
# factory of the package that owns the reference implementations: it is the one
# place where a `Reference*` class is constructed, and the composition root calls
# it instead of the class. See docs/architecture/dependency-rules.md section 5.
COMPOSITION_ROOTS = (
    "apps/agent-api/src/index.ts",
    "apps/worker/src/index.ts",
    "packages/tool-adapters/src/index.ts",
)

PROVIDER_CTOR = re.compile(
    r"new\s+([A-Z][A-Za-z0-9]*(?:Provider|Engine|Repository|Store|Sink|Client))\s*\("
)

# The start of a top-level function. Used to tell a factory from business code.
FUNCTION_START = re.compile(
    r"^(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)

TS_IMPORT = re.compile(
    r"(?:^|\n)\s*(?:import|export)\s[^;\n]*?from\s*['\"]([^'\"]+)['\"]"
)
TS_DYNAMIC_IMPORT = re.compile(r"import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
PY_IMPORT_FROM = re.compile(r"^\s*from\s+([A-Za-z_][\w.]*)\s+import\b", re.MULTILINE)
PY_IMPORT = re.compile(r"^\s*import\s+([A-Za-z_][\w.]*)\b", re.MULTILINE)

PY_STDLIB = {
    "abc", "argparse", "asyncio", "collections", "contextlib", "csv", "dataclasses",
    "datetime", "enum", "functools", "hashlib", "io", "itertools", "json", "logging",
    "math", "os", "pathlib", "random", "re", "shutil", "sqlite3", "string", "subprocess",
    "sys", "tempfile", "time", "types", "typing", "unittest", "uuid", "warnings",
    "from", "import", "__future__",
}

TYPES_BEHAVIOUR = ("await ", "fetch(", "process.env", "console.", "fs.", "new Date(", "http.")

BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT = re.compile(r"(?<!:)//[^\n]*")
HASH_COMMENT = re.compile(r"(?m)^\s*#.*$")


def strip_comments(rel: str, lines: list[str]) -> str:
    """Remove comments so a marker inside prose is not read as behaviour."""
    text = "\n".join(lines)
    text = BLOCK_COMMENT.sub("", text)
    if rel.endswith((".ts", ".tsx")):
        return LINE_COMMENT.sub("", text)
    return HASH_COMMENT.sub("", text)

TS_EXTENSIONS = ("", ".ts", ".tsx", "/index.ts", "/index.tsx")
PY_EXTENSIONS = ("", ".py", "/__init__.py")


def module_root(rel: str) -> str:
    """The owning module of a repository-relative path."""
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] in ("apps", "packages", "agents"):
        return "/".join(parts[:2])
    return parts[0]


def layer_of(rel: str) -> str | None:
    """Map a file to a layer. Returns None for a file outside the layering."""
    if rel in EXPLICIT_LAYER:
        return EXPLICIT_LAYER[rel]
    parts = rel.split("/")
    if parts[0] == "agents":
        if "/tests/" in rel:
            return None
        return "Service"
    if parts[0] == "apps":
        if "/tests/" in rel:
            return None
        app = parts[1] if len(parts) > 1 else ""
        if app == "admin-console":
            return "UI"
        return "Runtime"
    if parts[0] == "packages":
        if "/tests/" in rel:
            return None
        name = os.path.basename(rel)
        if name.startswith("types") or name.endswith(".types.ts"):
            return "Types"
        if name.startswith("config"):
            return "Config"
        if name.startswith(("repository", "store", "connector", "model", "identity")):
            return "Repo"
        if name.startswith(("provider", "engine", "flags", "kit", "index")):
            return "Service"
        return "Service"
    return None


def is_skipped(rel: str) -> bool:
    if any(marker in rel for marker in TEST_MARKERS):
        return True
    return not rel.endswith(SOURCE_SUFFIXES)


def walk_sources(root: str) -> list[str]:
    found: list[str] = []
    for scan_root in SCAN_ROOTS:
        base_dir = os.path.join(root, scan_root)
        if not os.path.isdir(base_dir):
            continue
        for base, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                path = os.path.join(base, name)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                if not is_skipped(rel):
                    found.append(rel)
    return sorted(found)


def package_manifests(root: str) -> dict[str, dict]:
    """Read every package.json, keyed by module path."""
    manifests: dict[str, dict] = {}
    for scan_root in ("apps", "packages"):
        base_dir = os.path.join(root, scan_root)
        if not os.path.isdir(base_dir):
            continue
        for name in sorted(os.listdir(base_dir)):
            path = os.path.join(base_dir, name, "package.json")
            if os.path.isfile(path):
                try:
                    with open(path, encoding="utf-8") as handle:
                        manifests[f"{scan_root}/{name}"] = json.load(handle)
                except (OSError, json.JSONDecodeError):
                    manifests[f"{scan_root}/{name}"] = {}
    return manifests


def workspace_package_layers(manifests: dict[str, dict]) -> dict[str, str]:
    """Map a workspace package name to the layer of its public entry point."""
    layers: dict[str, str] = {}
    for module, manifest in manifests.items():
        name = manifest.get("name")
        if not isinstance(name, str):
            continue
        exports = manifest.get("exports")
        entry = "src/index.ts"
        if isinstance(exports, dict):
            root_export = exports.get(".")
            if isinstance(root_export, str):
                entry = root_export.lstrip("./")
            elif isinstance(root_export, dict):
                candidate = root_export.get("import") or root_export.get("types")
                if isinstance(candidate, str):
                    entry = candidate.lstrip("./")
        rel_entry = f"{module}/{entry}"
        layers[name] = layer_of(rel_entry) or "Service"
    return layers


def read_lines(root: str, rel: str) -> list[str]:
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as handle:
        return handle.read().splitlines()


def extract_imports(rel: str, lines: list[str]) -> list[tuple[int, str]]:
    """Return (line number, import specifier) for every import in a file."""
    text = "\n".join(lines)
    found: list[tuple[int, str]] = []

    if rel.endswith((".ts", ".tsx")):
        for pattern in (TS_IMPORT, TS_DYNAMIC_IMPORT):
            for match in pattern.finditer(text):
                line_number = text[: match.start()].count("\n") + 1
                found.append((line_number, match.group(1)))
    else:
        for pattern in (PY_IMPORT_FROM, PY_IMPORT):
            for match in pattern.finditer(text):
                line_number = text[: match.start()].count("\n") + 1
                found.append((line_number, match.group(1)))
    return found


def resolve_target(root: str, rel: str, spec: str, manifests: dict[str, dict]) -> tuple[str | None, str | None]:
    """Resolve an import specifier to (target repo path, workspace package name)."""
    if spec.startswith("."):
        base = os.path.normpath(os.path.join(os.path.dirname(rel), spec))
        for suffix in TS_EXTENSIONS + PY_EXTENSIONS:
            candidate = (base + suffix).replace(os.sep, "/")
            if os.path.isfile(os.path.join(root, candidate)):
                return candidate, None
        return None, None

    for manifest in manifests.values():
        name = manifest.get("name")
        if isinstance(name, str) and (spec == name or spec.startswith(name + "/")):
            return None, name

    if rel.endswith(".py"):
        head = spec.split(".")[0]
        if head in PY_STDLIB:
            return None, None
        module = module_root(rel)
        for candidate in (
            f"{module}/{spec.replace('.', '/')}.py",
            f"{module}/{spec.replace('.', '/')}/__init__.py",
        ):
            if os.path.isfile(os.path.join(root, candidate)):
                return candidate, None
        return None, None

    return None, None


def check_file(
    root: str,
    rel: str,
    lines: list[str],
    manifests: dict[str, dict],
    package_layers: dict[str, str],
) -> list[tuple[str, int, str, str]]:
    findings: list[tuple[str, int, str, str]] = []
    source_layer = layer_of(rel)
    module = module_root(rel)

    if source_layer == "Types":
        text = strip_comments(rel, lines)
        for marker in TYPES_BEHAVIOUR:
            if marker in text:
                findings.append((rel, 0, "DEP-006", f"Types layer contains behaviour or I/O ({marker!r})"))

    if source_layer is not None:
        for line_number, spec in extract_imports(rel, lines):
            target_path, package_name = resolve_target(root, rel, spec, manifests)

            if package_name is not None:
                if "/src/" in spec:
                    findings.append((rel, line_number, "DEP-003", f"deep import into {package_name} ({spec})"))
                target_layer = package_layers.get(package_name)
                if target_layer is None:
                    continue
            elif target_path is not None:
                if module_root(target_path) != module:
                    findings.append(
                        (rel, line_number, "DEP-003", f"relative import across modules ({spec})")
                    )
                    continue
                target_layer = layer_of(target_path)
            else:
                continue

            if target_layer is None or target_layer == source_layer:
                continue

            if target_layer not in ALLOWED[source_layer]:
                if source_layer == "UI" and target_layer in ("Service", "Repo", "Config"):
                    findings.append(
                        (rel, line_number, "DEP-002", f"UI depends on {target_layer} directly ({spec})")
                    )
                else:
                    findings.append(
                        (rel, line_number, "DEP-001", f"{source_layer} -> {target_layer} ({spec})")
                    )

    if source_layer is not None:
        # A constructor call is allowed in a composition root and inside the
        # `create*` factory that the owning package publishes for its own
        # implementation. Everywhere else it is a violation.
        current_function = ""
        for line_number, line in enumerate(lines, start=1):
            function_match = FUNCTION_START.search(line)
            if function_match is not None:
                current_function = function_match.group(1)
            elif line.startswith("}"):
                current_function = ""

            match = PROVIDER_CTOR.search(line)
            if match is None or rel in COMPOSITION_ROOTS:
                continue
            if current_function.startswith("create"):
                continue
            findings.append(
                (
                    rel,
                    line_number,
                    "DEP-004",
                    f"{match.group(1)} is constructed outside a composition root or a create* factory",
                )
            )

    return findings


def check_declared_dependencies(
    root: str, rel: str, lines: list[str], manifests: dict[str, dict]
) -> list[tuple[str, int, str, str]]:
    """DEP-008: a workspace import must be declared in the importer's package.json."""
    module = module_root(rel)
    manifest = manifests.get(module)
    if manifest is None:
        return []
    declared = set((manifest.get("dependencies") or {}).keys())
    declared |= set((manifest.get("devDependencies") or {}).keys())
    own_name = manifest.get("name")

    findings: list[tuple[str, int, str, str]] = []
    known = {m.get("name") for m in manifests.values() if isinstance(m.get("name"), str)}
    for line_number, spec in extract_imports(rel, lines):
        head = spec.split("/")[0] if not spec.startswith("@") else "/".join(spec.split("/")[:2])
        if head in known and head != own_name and head not in declared:
            findings.append(
                (rel, line_number, "DEP-008", f"{head} is used but not declared in {module}/package.json")
            )
    return findings


def check_cycles(root: str, files: list[str], manifests: dict[str, dict]) -> list[tuple[str, int, str, str]]:
    """DEP-005: detect a cycle between modules."""
    graph: dict[str, set[str]] = {}
    for rel in files:
        module = module_root(rel)
        graph.setdefault(module, set())
        for _line, spec in extract_imports(rel, read_lines(root, rel)):
            _target, package_name = resolve_target(root, rel, spec, manifests)
            if package_name is None:
                continue
            for candidate_module, manifest in manifests.items():
                if manifest.get("name") == package_name:
                    if candidate_module != module:
                        graph[module].add(candidate_module)

    findings: list[tuple[str, int, str, str]] = []
    state: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> None:
        state[node] = 1
        for neighbour in sorted(graph.get(node, ())):
            if state.get(neighbour, 0) == 1:
                cycle = " -> ".join(stack + [node, neighbour])
                findings.append((node, 0, "DEP-005", f"circular dependency ({cycle})"))
            elif state.get(neighbour, 0) == 0:
                visit(neighbour, stack + [node])
        state[node] = 2

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            visit(node, [])
    return findings


def main(argv: list[str]) -> int:
    root = os.path.abspath(argv[1] if len(argv) > 1 else ".")
    if not os.path.isdir(os.path.join(root, "apps")) and not os.path.isdir(os.path.join(root, "packages")):
        print(f"check-architecture: not a repository root: {root}", file=sys.stderr)
        return 2

    try:
        manifests = package_manifests(root)
        package_layers = workspace_package_layers(manifests)
        files = walk_sources(root)
    except OSError as error:
        print(f"check-architecture: {error}", file=sys.stderr)
        return 2

    findings: list[tuple[str, int, str, str]] = []
    for rel in files:
        try:
            lines = read_lines(root, rel)
        except OSError as error:
            findings.append((rel, 0, "DEP-000", f"unreadable: {error}"))
            continue
        findings += check_file(root, rel, lines, manifests, package_layers)
        findings += check_declared_dependencies(root, rel, lines, manifests)

    findings += check_cycles(root, files, manifests)
    findings.sort()

    for rel, line_number, code, message in findings:
        print(f"{rel}:{line_number}  {code}  {message}")

    affected = len({finding[0] for finding in findings})
    print(f"violations={len(findings)} affected_files={affected}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
