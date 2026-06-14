from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_ID = "T2-interface-audit"
PIPELINE_DIR = Path("assets") / "resource" / "pipeline"


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


def _build_pipeline_index(pipeline_dir: Path) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    index: dict[str, list[str]] = defaultdict(list)
    warnings: list[dict[str, Any]] = []

    if not pipeline_dir.exists():
        warnings.append(
            {
                "code": "pipeline_dir_missing",
                "message": "Pipeline directory does not exist; entry and override references cannot be confirmed.",
                "path": pipeline_dir.as_posix(),
            }
        )
        return index, warnings

    for path in sorted(pipeline_dir.rglob("*.json")):
        data, warning = _read_jsonc_object(path)
        if warning is not None:
            warnings.append(warning)
            continue
        assert data is not None
        for node_name in data:
            index[node_name].append(path.as_posix())

    return dict(index), warnings


def _field_presence(interface: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    hard_failures: list[dict[str, Any]] = []
    checks = {
        "controller": isinstance(interface.get("controller"), list) and bool(interface.get("controller")),
        "resource": isinstance(interface.get("resource"), list) and bool(interface.get("resource")),
        "agent": isinstance(interface.get("agent"), dict),
        "task": isinstance(interface.get("task"), list),
    }

    agent = interface.get("agent") if isinstance(interface.get("agent"), dict) else {}
    checks["agent.child_exec"] = bool(agent.get("child_exec"))
    checks["agent.child_args"] = isinstance(agent.get("child_args"), list) and bool(agent.get("child_args"))

    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        hard_failures.append(
            {
                "code": "project_interface_required_field_missing",
                "message": "ProjectInterface required fields are missing or empty.",
                "missing": missing,
            }
        )

    return checks, hard_failures


def _audit_tasks(
    tasks: list[Any],
    pipeline_index: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    task_entries: list[dict[str, Any]] = []
    hard_failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    entry_counter: Counter[str] = Counter()

    for task_index, task in enumerate(tasks):
        if not isinstance(task, dict):
            hard_failures.append(
                {
                    "code": "task_not_object",
                    "message": "Task item is not an object.",
                    "task_index": task_index,
                }
            )
            continue

        name = task.get("name")
        entry = task.get("entry")
        override = task.get("pipeline_override")
        entry_locations = pipeline_index.get(entry, []) if isinstance(entry, str) else []
        entry_counter.update([entry] if isinstance(entry, str) else [])

        if not isinstance(entry, str) or not entry:
            hard_failures.append(
                {
                    "code": "task_entry_missing",
                    "message": "Task entry is missing or not a string.",
                    "task_index": task_index,
                    "task_name": name,
                }
            )
        elif not entry_locations:
            hard_failures.append(
                {
                    "code": "task_entry_target_missing",
                    "message": "Task entry target node does not exist in pipeline index.",
                    "task_index": task_index,
                    "task_name": name,
                    "entry": entry,
                }
            )

        if "pipeline_override" in task and override == {}:
            warnings.append(
                {
                    "code": "empty_pipeline_override",
                    "message": "Task has an explicit empty pipeline_override object.",
                    "task_index": task_index,
                    "task_name": name,
                }
            )

        task_entries.append(
            {
                "task_index": task_index,
                "task_name": name,
                "entry": entry,
                "entry_exists": bool(entry_locations),
                "entry_locations": entry_locations,
                "has_pipeline_override": "pipeline_override" in task,
                "override_node_count": len(override) if isinstance(override, dict) else 0,
            }
        )

    repeated_entries = [
        {"entry": entry, "count": count}
        for entry, count in sorted(entry_counter.items())
        if count > 1
    ]

    summary = {
        "task_count": len(tasks),
        "unique_entry_count": len(entry_counter),
        "repeated_entries": repeated_entries,
    }
    return task_entries, hard_failures, warnings, summary


def _audit_overrides(
    tasks: list[Any],
    pipeline_index: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    hard_failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    signature_tasks: dict[tuple[str, ...], list[str]] = defaultdict(list)
    override_total = 0
    empty_override_count = 0
    next_or_action_count = 0

    for task_index, task in enumerate(tasks):
        if not isinstance(task, dict):
            continue
        task_name = task.get("name")
        override = task.get("pipeline_override")
        if not isinstance(override, dict):
            continue

        if not override:
            empty_override_count += 1
            continue

        signature_tasks[tuple(sorted(override.keys()))].append(str(task_name))

        for node_name, patch in override.items():
            override_total += 1
            node_locations = pipeline_index.get(node_name, [])
            if not node_locations:
                hard_failures.append(
                    {
                        "code": "override_target_missing",
                        "message": "pipeline_override target node does not exist in pipeline index.",
                        "task_index": task_index,
                        "task_name": task_name,
                        "node": node_name,
                    }
                )

            patch_keys = sorted(patch.keys()) if isinstance(patch, dict) else []
            has_next = isinstance(patch, dict) and "next" in patch
            has_action = isinstance(patch, dict) and "action" in patch
            if has_next or has_action:
                next_or_action_count += 1
                warnings.append(
                    {
                        "code": "special_next_or_action_override",
                        "message": "pipeline_override changes next or action; keep behavior explicit.",
                        "task_index": task_index,
                        "task_name": task_name,
                        "node": node_name,
                        "fields": [field for field in ["next", "action"] if field in patch_keys],
                    }
                )

            records.append(
                {
                    "task_index": task_index,
                    "task_name": task_name,
                    "node": node_name,
                    "node_exists": bool(node_locations),
                    "node_locations": node_locations,
                    "fields": patch_keys,
                    "has_next_override": has_next,
                    "has_action_override": has_action,
                }
            )

    repeated_override_shapes = [
        {
            "override_nodes": list(signature),
            "task_count": len(task_names),
            "sample_tasks": task_names[:5],
        }
        for signature, task_names in sorted(signature_tasks.items(), key=lambda item: (-len(item[1]), item[0]))
        if len(task_names) > 1
    ]
    for group in repeated_override_shapes:
        warnings.append(
            {
                "code": "repeated_account_server_override_shape",
                "message": "Multiple tasks share the same override node shape; keep as audit info only.",
                **group,
            }
        )

    summary = {
        "override_total": override_total,
        "empty_override_count": empty_override_count,
        "special_next_or_action_override_count": next_or_action_count,
        "repeated_override_shape_count": len(repeated_override_shapes),
    }
    return records, hard_failures, warnings, summary


def build_report(repo_root: Path) -> dict[str, Any]:
    interface_path = repo_root / "assets" / "interface.json"
    pipeline_dir = repo_root / PIPELINE_DIR

    interface, interface_error = _read_strict_json(interface_path)
    pipeline_index, pipeline_warnings = _build_pipeline_index(pipeline_dir)

    hard_failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = pipeline_warnings
    field_checks: dict[str, Any] = {}
    task_entries: list[dict[str, Any]] = []
    pipeline_overrides: list[dict[str, Any]] = []
    task_summary: dict[str, Any] = {}
    override_summary: dict[str, Any] = {}

    if interface_error is not None:
        hard_failures.append({"code": "canonical_interface_unreadable", **interface_error})
        tasks: list[Any] = []
    elif not isinstance(interface, dict):
        hard_failures.append(
            {
                "code": "canonical_interface_top_level_not_object",
                "message": "assets/interface.json top level is not an object.",
                "path": interface_path.as_posix(),
            }
        )
        tasks = []
    else:
        field_checks, field_failures = _field_presence(interface)
        hard_failures.extend(field_failures)
        tasks = interface.get("task", []) if isinstance(interface.get("task"), list) else []

        task_entries, task_failures, task_warnings, task_summary = _audit_tasks(tasks, pipeline_index)
        hard_failures.extend(task_failures)
        warnings.extend(task_warnings)

        pipeline_overrides, override_failures, override_warnings, override_summary = _audit_overrides(
            tasks, pipeline_index
        )
        hard_failures.extend(override_failures)
        warnings.extend(override_warnings)

    v2_candidate_entries = [
        {
            "task_name": item["task_name"],
            "entry": item["entry"],
            "has_pipeline_override": item["has_pipeline_override"],
            "override_node_count": item["override_node_count"],
        }
        for item in task_entries
        if item["entry_exists"]
    ]

    return {
        "check_id": CHECK_ID,
        "scope": "ProjectInterface task, entry, pipeline_override, controller, resource, and agent audit",
        "validation_level": "V0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "canonical_interface": "assets/interface.json",
            "pipeline_dir": PIPELINE_DIR.as_posix(),
            "root_interface": "not canonical",
        },
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "summary": {
            **task_summary,
            **override_summary,
            "pipeline_file_count": len(list(pipeline_dir.rglob("*.json"))) if pipeline_dir.exists() else 0,
            "pipeline_node_count": len(pipeline_index),
            "field_checks": field_checks,
        },
        "task_entries": task_entries,
        "pipeline_overrides": pipeline_overrides,
        "v2_candidate_entries": v2_candidate_entries,
        "commands": [
            "python .\\check_interface_audit.py",
        ],
        "notes": [
            "This check is read-only.",
            "Pipeline files are parsed with JSONC-aware comment stripping for node indexing only.",
            "Repeated account/server overrides are warnings, not cleanup instructions.",
            "Root interface.json is not used as the runtime source of truth.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only ProjectInterface audit for MaaZJ assets/interface.json."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to the current working directory.",
    )
    args = parser.parse_args()

    report = build_report(Path(args.repo_root))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["hard_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
