from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_ID = "T5-agent-custom"
INTERFACE_PATH = Path("assets") / "interface.json"
PIPELINE_DIR = Path("assets") / "resource" / "pipeline"
AGENT_DIR = Path("agent")
AGENT_MAIN = AGENT_DIR / "main.py"
CUSTOM_ACTION_DECORATOR = "AgentServer.custom_action"
CUSTOM_RECOGNITION_DECORATOR = "AgentServer.custom_recognition"
CUSTOM_DECLARATION_KEYS = {"action", "recognition"}
CUSTOM_DECLARATION_VALUES = {"Custom", "CustomAction", "CustomRecognition"}
RISK_CALLS = {
    "context.run_recognition": "recognition_call",
    "context.override_pipeline": "pipeline_override",
    "context.tasker.controller.post_click": "controller_click",
    "context.override_next": "next_override",
}


def _read_strict_json(path: Path) -> tuple[Any | None, dict[str, Any] | None]:
    if not path.exists():
        return None, {
            "code": "file_missing",
            "message": f"{path.as_posix()} does not exist.",
            "path": path.as_posix(),
        }
    if not path.is_file():
        return None, {
            "code": "not_a_file",
            "message": f"{path.as_posix()} is not a file.",
            "path": path.as_posix(),
        }

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file), None
    except json.JSONDecodeError as exc:
        return None, {
            "code": "strict_json_parse_failed",
            "message": exc.msg,
            "path": path.as_posix(),
            "line": exc.lineno,
            "column": exc.colno,
            "position": exc.pos,
        }


def _strip_jsonc(text: str) -> str:
    output: list[str] = []
    in_string = False
    escaped = False
    in_line_comment = False
    in_block_comment = False
    index = 0

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_line_comment:
            if char in "\r\n":
                in_line_comment = False
                output.append(char)
            index += 1
            continue

        if in_block_comment:
            if char == "*" and next_char == "/":
                in_block_comment = False
                index += 2
            else:
                if char in "\r\n":
                    output.append(char)
                index += 1
            continue

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            in_line_comment = True
            index += 2
            continue

        if char == "/" and next_char == "*":
            in_block_comment = True
            index += 2
            continue

        output.append(char)
        index += 1

    stripped = "".join(output)
    return re.sub(r",(\s*[}\]])", r"\1", stripped)


def _read_jsonc_object(path: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(_strip_jsonc(text))
    except json.JSONDecodeError as exc:
        return None, {
            "code": "pipeline_parse_failed",
            "message": exc.msg,
            "path": path.as_posix(),
            "line": exc.lineno,
            "column": exc.colno,
            "position": exc.pos,
        }

    if not isinstance(data, dict):
        return None, {
            "code": "pipeline_top_level_not_object",
            "message": "Pipeline file top level is not an object.",
            "path": path.as_posix(),
        }

    return data, None


def _parse_python(path: Path) -> tuple[ast.Module | None, dict[str, Any] | None]:
    if not path.exists():
        return None, {
            "code": "python_file_missing",
            "message": f"{path.as_posix()} does not exist.",
            "path": path.as_posix(),
        }
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix()), None
    except SyntaxError as exc:
        return None, {
            "code": "python_parse_failed",
            "message": exc.msg,
            "path": path.as_posix(),
            "line": exc.lineno,
            "column": exc.offset,
        }


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return _dotted_name(node.func)
    return None


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _imported_local_modules(main_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tree, error = _parse_python(main_path)
    if error is not None:
        return [], [error]

    assert tree is not None
    imports: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if "." in module:
                    continue
                module_path = main_path.parent / f"{module}.py"
                if module_path.exists():
                    imports.append(
                        {
                            "module": module,
                            "alias": alias.asname,
                            "path": module_path.as_posix(),
                            "line": node.lineno,
                            "imported_by_main": True,
                        }
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level != 0 or not module or "." in module:
                continue
            module_path = main_path.parent / f"{module}.py"
            if module_path.exists():
                imports.append(
                    {
                        "module": module,
                        "alias": None,
                        "path": module_path.as_posix(),
                        "line": node.lineno,
                        "imported_by_main": True,
                    }
                )

    if not imports:
        warnings.append(
            {
                "code": "main_import_chain_empty",
                "message": "agent/main.py has no direct local module imports.",
                "path": main_path.as_posix(),
            }
        )

    return imports, warnings


def _decorator_kind(decorator: ast.AST) -> str | None:
    name = _dotted_name(decorator)
    if name == CUSTOM_ACTION_DECORATOR:
        return "custom_action"
    if name == CUSTOM_RECOGNITION_DECORATOR:
        return "custom_recognition"
    return None


def _registered_names(import_chain: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    registered: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for import_record in import_chain:
        path = Path(import_record["path"])
        tree, error = _parse_python(path)
        if error is not None:
            warnings.append(error)
            continue
        assert tree is not None

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for decorator in node.decorator_list:
                kind = _decorator_kind(decorator)
                if kind is None:
                    continue
                if not isinstance(decorator, ast.Call) or not decorator.args:
                    warnings.append(
                        {
                            "code": "custom_decorator_without_literal_name",
                            "message": "Custom decorator is missing a literal registered name.",
                            "file": path.as_posix(),
                            "class_name": node.name,
                            "line": getattr(decorator, "lineno", node.lineno),
                        }
                    )
                    continue
                name = _literal_string(decorator.args[0])
                if name is None:
                    warnings.append(
                        {
                            "code": "custom_decorator_non_literal_name",
                            "message": "Custom decorator registered name is not a static string literal.",
                            "file": path.as_posix(),
                            "class_name": node.name,
                            "line": getattr(decorator, "lineno", node.lineno),
                        }
                    )
                    continue
                registered.append(
                    {
                        "registered_name": name,
                        "type": kind,
                        "file": path.as_posix(),
                        "line": getattr(decorator, "lineno", node.lineno),
                        "class_name": node.name,
                        "module": import_record["module"],
                        "imported_by_main": import_record["imported_by_main"],
                    }
                )

    duplicate_names = [
        {"registered_name": name, "count": count}
        for name, count in sorted(Counter(item["registered_name"] for item in registered).items())
        if count > 1
    ]
    for item in duplicate_names:
        warnings.append(
            {
                "code": "duplicate_registered_name",
                "message": "Registered name appears more than once in imported custom modules.",
                **item,
            }
        )

    return registered, warnings


def _node_walk(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    items = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            items.extend(_node_walk(item, (*path, str(key))))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            items.extend(_node_walk(item, (*path, str(index))))
    return items


def _find_static_name_references(
    *,
    source_kind: str,
    source_path: str,
    value: Any,
    names: set[str],
    node_name: str | None = None,
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    if not names:
        return refs
    for path, item in _node_walk(value):
        if isinstance(item, str) and item in names:
            refs.append(
                {
                    "source_kind": source_kind,
                    "source_path": source_path,
                    "node": node_name,
                    "field_path": ".".join(path),
                    "registered_name": item,
                }
            )
    return refs


def _looks_like_custom_declaration(key: str, value: Any) -> bool:
    if key not in CUSTOM_DECLARATION_KEYS:
        return False
    return isinstance(value, str) and value in CUSTOM_DECLARATION_VALUES


def _extract_custom_name_candidates(node_body: dict[str, Any]) -> set[str]:
    candidates: set[str] = set()
    for path, value in _node_walk(node_body):
        if not path or not isinstance(value, str):
            continue
        key = path[-1]
        if key in {"name", "custom_action", "custom_recognition", "registered_name"}:
            candidates.add(value)
        if key in CUSTOM_DECLARATION_KEYS and value not in CUSTOM_DECLARATION_VALUES:
            candidates.add(value)
    return candidates


def _scan_pipeline(
    pipeline_dir: Path,
    registered_names: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    static_refs: list[dict[str, Any]] = []
    custom_declarations: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not pipeline_dir.exists():
        warnings.append(
            {
                "code": "pipeline_dir_missing",
                "message": "Pipeline directory does not exist; custom static references cannot be checked.",
                "path": pipeline_dir.as_posix(),
            }
        )
        return static_refs, custom_declarations, warnings

    for path in sorted(pipeline_dir.rglob("*.json")):
        data, warning = _read_jsonc_object(path)
        if warning is not None:
            warnings.append(warning)
            continue
        assert data is not None

        for node_name, node_body in data.items():
            if not isinstance(node_body, dict):
                continue
            static_refs.extend(
                _find_static_name_references(
                    source_kind="pipeline_node",
                    source_path=path.as_posix(),
                    value=node_body,
                    names=registered_names,
                    node_name=node_name,
                )
            )

            for field_path, value in _node_walk(node_body):
                if not field_path:
                    continue
                key = field_path[-1]
                if _looks_like_custom_declaration(key, value):
                    custom_declarations.append(
                        {
                            "node": node_name,
                            "file": path.as_posix(),
                            "field_path": ".".join(field_path),
                            "declaration_kind": key,
                            "declaration_value": value,
                            "registered_name_candidates": sorted(_extract_custom_name_candidates(node_body)),
                        }
                    )

    return static_refs, custom_declarations, warnings


def _interface_agent_startup(interface: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    hard_failures: list[dict[str, Any]] = []
    if not isinstance(interface, dict):
        return {
            "configured": False,
            "child_exec": None,
            "child_args": None,
            "main_script_configured": False,
        }, [
            {
                "code": "canonical_interface_top_level_not_object",
                "message": "assets/interface.json top level is not an object.",
                "path": INTERFACE_PATH.as_posix(),
            }
        ]

    agent = interface.get("agent")
    if not isinstance(agent, dict):
        return {
            "configured": False,
            "child_exec": None,
            "child_args": None,
            "main_script_configured": False,
        }, [
            {
                "code": "canonical_agent_config_missing",
                "message": "assets/interface.json does not contain an agent object.",
                "path": INTERFACE_PATH.as_posix(),
            }
        ]

    child_exec = agent.get("child_exec")
    child_args = agent.get("child_args")
    child_args_list = child_args if isinstance(child_args, list) else []
    main_script_configured = any(
        isinstance(item, str) and item.replace("\\", "/").endswith("agent/main.py")
        for item in child_args_list
    )

    if not child_exec or not isinstance(child_exec, str):
        hard_failures.append(
            {
                "code": "canonical_agent_child_exec_missing",
                "message": "assets/interface.json agent.child_exec is missing or not a string.",
                "path": INTERFACE_PATH.as_posix(),
            }
        )
    if not child_args_list:
        hard_failures.append(
            {
                "code": "canonical_agent_child_args_missing",
                "message": "assets/interface.json agent.child_args is missing or not a non-empty list.",
                "path": INTERFACE_PATH.as_posix(),
            }
        )
    elif not main_script_configured:
        hard_failures.append(
            {
                "code": "canonical_agent_main_not_configured",
                "message": "assets/interface.json agent.child_args does not point to agent/main.py.",
                "path": INTERFACE_PATH.as_posix(),
                "child_args": child_args,
            }
        )

    startup = {
        "configured": not hard_failures,
        "child_exec": child_exec,
        "child_args": child_args,
        "main_script_configured": main_script_configured,
    }
    return startup, hard_failures


def _scan_custom_logic_risks(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    risks: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for record in records:
        path = Path(record["file"])
        tree, error = _parse_python(path)
        if error is not None:
            warnings.append(error)
            continue
        assert tree is not None

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            call_name = _dotted_name(node.func)
            if call_name not in RISK_CALLS:
                continue
            risks.append(
                {
                    "registered_name": record["registered_name"],
                    "type": record["type"],
                    "file": path.as_posix(),
                    "line": node.lineno,
                    "call": call_name,
                    "risk": RISK_CALLS[call_name],
                    "note": "Static risk only; runtime call was not verified.",
                }
            )

    if risks:
        warnings.append(
            {
                "code": "custom_logic_runtime_path_risk",
                "message": "Custom logic contains calls that may change recognition, click behavior, pipeline overrides, or next edges if invoked.",
                "count": len(risks),
                "note": "This is a static warning, not evidence that the custom logic is used at runtime.",
            }
        )

    return risks, warnings


def _find_unregistered_custom_references(
    custom_declarations: list[dict[str, Any]],
    registered_names: set[str],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for declaration in custom_declarations:
        candidates = declaration["registered_name_candidates"]
        missing = [name for name in candidates if name not in registered_names]
        for name in missing:
            failures.append(
                {
                    "code": "pipeline_custom_registered_name_missing",
                    "message": "Pipeline appears to reference a custom registered name that is not registered by imported agent modules.",
                    "registered_name": name,
                    "node": declaration["node"],
                    "file": declaration["file"],
                    "field_path": declaration["field_path"],
                    "declaration_kind": declaration["declaration_kind"],
                    "declaration_value": declaration["declaration_value"],
                }
            )
    return failures


def build_report(repo_root: Path) -> dict[str, Any]:
    interface_path = repo_root / INTERFACE_PATH
    pipeline_dir = repo_root / PIPELINE_DIR
    agent_main = repo_root / AGENT_MAIN

    interface, interface_error = _read_strict_json(interface_path)
    hard_failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if interface_error is not None:
        hard_failures.append({"code": "canonical_interface_unreadable", **interface_error})
        agent_startup = {
            "configured": False,
            "child_exec": None,
            "child_args": None,
            "main_script_configured": False,
        }
        interface_refs: list[dict[str, Any]] = []
    else:
        agent_startup, startup_failures = _interface_agent_startup(interface)
        hard_failures.extend(startup_failures)
        interface_refs = _find_static_name_references(
            source_kind="canonical_interface",
            source_path=INTERFACE_PATH.as_posix(),
            value=interface,
            names=set(),
        )

    import_chain, import_warnings = _imported_local_modules(agent_main)
    warnings.extend(import_warnings)
    registered, registration_warnings = _registered_names(import_chain)
    warnings.extend(registration_warnings)

    registered_names = {item["registered_name"] for item in registered}
    if interface_error is None and interface is not None:
        interface_refs = _find_static_name_references(
            source_kind="canonical_interface",
            source_path=INTERFACE_PATH.as_posix(),
            value=interface,
            names=registered_names,
        )

    pipeline_refs, custom_declarations, pipeline_warnings = _scan_pipeline(pipeline_dir, registered_names)
    warnings.extend(pipeline_warnings)
    hard_failures.extend(_find_unregistered_custom_references(custom_declarations, registered_names))

    logic_risks, risk_warnings = _scan_custom_logic_risks(registered)
    warnings.extend(risk_warnings)

    ref_counter = Counter(ref["registered_name"] for ref in [*interface_refs, *pipeline_refs])
    for record in registered:
        if ref_counter[record["registered_name"]] == 0:
            warnings.append(
                {
                    "code": "pipeline_static_reference_not_found",
                    "message": "Registered name is imported and registered, but no static canonical interface or pipeline reference was found.",
                    "registered_name": record["registered_name"],
                    "type": record["type"],
                    "note": "This is not a deletion recommendation.",
                }
            )

    warnings.append(
        {
            "code": "runtime_call_unverified",
            "message": "This check is V0 static analysis only; agent startup, task entry startup, and real controller calls were not executed.",
            "validation_level": "V0",
        }
    )

    type_counter = Counter(item["type"] for item in registered)
    risk_counter = Counter(item["risk"] for item in logic_risks)

    return {
        "check_id": CHECK_ID,
        "scope": "Python agent startup, custom registered name, import chain, and static pipeline reference audit",
        "validation_level": "V0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "canonical_interface": INTERFACE_PATH.as_posix(),
            "pipeline_dir": PIPELINE_DIR.as_posix(),
            "agent_main": AGENT_MAIN.as_posix(),
            "root_interface": "not used",
        },
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "summary": {
            "agent_configured": agent_startup["configured"],
            "imported_local_module_count": len(import_chain),
            "registered_name_count": len(registered),
            "registered_names_by_type": dict(sorted(type_counter.items())),
            "interface_static_reference_count": len(interface_refs),
            "pipeline_static_reference_count": len(pipeline_refs),
            "custom_declaration_count": len(custom_declarations),
            "custom_logic_risk_count": len(logic_risks),
            "custom_logic_risks_by_type": dict(sorted(risk_counter.items())),
        },
        "agent_startup": agent_startup,
        "import_chain": import_chain,
        "registered_names": registered,
        "static_references": {
            "canonical_interface": interface_refs,
            "pipeline": pipeline_refs,
            "custom_declarations": custom_declarations,
        },
        "custom_logic_risks": logic_risks,
        "commands": [
            "python .\\check_agent_custom.py",
        ],
        "notes": [
            "This check is read-only.",
            "assets/interface.json is the canonical runtime truth and is parsed as strict JSON.",
            "Root interface.json is not used.",
            "Pipeline files are parsed with JSONC-aware comment stripping for analysis only; files are never rewritten.",
            "No Python agent module is imported or executed by this script.",
            "Missing static references are review inputs only, not deletion recommendations.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Python agent custom registered name audit for MaaZJ."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to the current working directory.",
    )
    args = parser.parse_args()

    report = build_report(Path(args.repo_root))
    print(json.dumps(report, indent=2))
    return 1 if report["hard_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
