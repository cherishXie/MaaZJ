from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_ID = "T3-pipeline-ref"
INTERFACE_PATH = Path("assets") / "interface.json"
PIPELINE_DIR = Path("assets") / "resource" / "pipeline"
EDGE_FIELDS = ("next", "interrupt", "on_error")


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


def _module_for_path(path: str) -> str:
    relative = Path(path).as_posix()
    prefix = PIPELINE_DIR.as_posix() + "/"
    if relative.startswith(prefix):
        relative = relative[len(prefix):]
    parts = relative.split("/")
    if len(parts) == 1:
        return Path(parts[0]).stem
    if parts[0] == "小号" and len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def _normalize_targets(
    value: Any,
    *,
    source_kind: str,
    source: str,
    field: str,
    warnings: list[dict[str, Any]],
) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        targets: list[str] = []
        for index, item in enumerate(value):
            if isinstance(item, str) and item:
                targets.append(item)
            else:
                warnings.append(
                    {
                        "code": "non_string_reference_target",
                        "message": "Reference field contains a non-string target.",
                        "source_kind": source_kind,
                        "source": source,
                        "field": field,
                        "index": index,
                        "value_type": type(item).__name__,
                    }
                )
        return targets

    warnings.append(
        {
            "code": "unsupported_reference_shape",
            "message": "Reference field is neither a string nor a list.",
            "source_kind": source_kind,
            "source": source,
            "field": field,
            "value_type": type(value).__name__,
        }
    )
    return []


def _build_pipeline_data(
    pipeline_dir: Path,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    warnings: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []

    if not pipeline_dir.exists():
        warnings.append(
            {
                "code": "pipeline_dir_missing",
                "message": "Pipeline directory does not exist; references cannot be checked.",
                "path": pipeline_dir.as_posix(),
            }
        )
        return {}, warnings, files

    for path in sorted(pipeline_dir.rglob("*.json")):
        data, warning = _read_jsonc_object(path)
        file_record = {"path": path.as_posix(), "parsed": warning is None, "node_count": 0}
        if warning is not None:
            warnings.append(warning)
            files.append(file_record)
            continue

        assert data is not None
        file_record["node_count"] = len(data)
        files.append(file_record)
        for node_name, node_body in data.items():
            nodes[node_name].append(
                {
                    "path": path.as_posix(),
                    "module": _module_for_path(path.as_posix()),
                    "body": node_body if isinstance(node_body, dict) else {},
                    "body_type": type(node_body).__name__,
                }
            )
            if not isinstance(node_body, dict):
                warnings.append(
                    {
                        "code": "pipeline_node_not_object",
                        "message": "Pipeline node body is not an object.",
                        "node": node_name,
                        "path": path.as_posix(),
                        "body_type": type(node_body).__name__,
                    }
                )

    return dict(nodes), warnings, files


def _primary_location(nodes: dict[str, list[dict[str, Any]]], node_name: str) -> dict[str, Any] | None:
    locations = nodes.get(node_name, [])
    return locations[0] if locations else None


def _make_edge(
    *,
    source_kind: str,
    source: str,
    field: str,
    target: str,
    nodes: dict[str, list[dict[str, Any]]],
    task_name: str | None = None,
    task_index: int | None = None,
) -> dict[str, Any]:
    source_location = _primary_location(nodes, source)
    target_location = _primary_location(nodes, target)
    return {
        "source_kind": source_kind,
        "source": source,
        "field": field,
        "target": target,
        "target_exists": target_location is not None,
        "source_module": source_location["module"] if source_location else None,
        "target_module": target_location["module"] if target_location else None,
        "source_path": source_location["path"] if source_location else None,
        "target_path": target_location["path"] if target_location else None,
        "task_index": task_index,
        "task_name": task_name,
    }


def _extract_pipeline_edges(
    nodes: dict[str, list[dict[str, Any]]],
    warnings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for node_name, locations in sorted(nodes.items()):
        for location in locations:
            body = location["body"]
            for field in EDGE_FIELDS:
                for target in _normalize_targets(
                    body.get(field),
                    source_kind="pipeline_node",
                    source=node_name,
                    field=field,
                    warnings=warnings,
                ):
                    edge = _make_edge(
                        source_kind="pipeline_node",
                        source=node_name,
                        field=field,
                        target=target,
                        nodes=nodes,
                    )
                    edge["source_module"] = location["module"]
                    edge["source_path"] = location["path"]
                    edges.append(edge)
    return edges


def _extract_interface_refs(
    interface: Any,
    nodes: dict[str, list[dict[str, Any]]],
    warnings: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    hard_failures: list[dict[str, Any]] = []
    refs: list[dict[str, Any]] = []

    if not isinstance(interface, dict):
        hard_failures.append(
            {
                "code": "canonical_interface_top_level_not_object",
                "message": "assets/interface.json top level is not an object.",
                "path": INTERFACE_PATH.as_posix(),
            }
        )
        return refs, hard_failures

    tasks = interface.get("task")
    if not isinstance(tasks, list):
        hard_failures.append(
            {
                "code": "task_list_missing",
                "message": "assets/interface.json task field is missing or not a list.",
                "path": INTERFACE_PATH.as_posix(),
            }
        )
        return refs, hard_failures

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

        task_name = task.get("name")
        entry = task.get("entry")
        if isinstance(entry, str) and entry:
            refs.append(
                _make_edge(
                    source_kind="interface_task",
                    source=f"task[{task_index}].entry",
                    field="entry",
                    target=entry,
                    nodes=nodes,
                    task_name=task_name,
                    task_index=task_index,
                )
            )
        else:
            hard_failures.append(
                {
                    "code": "task_entry_missing",
                    "message": "Task entry is missing or not a string.",
                    "task_index": task_index,
                    "task_name": task_name,
                }
            )

        override = task.get("pipeline_override")
        if override is None:
            continue
        if not isinstance(override, dict):
            warnings.append(
                {
                    "code": "pipeline_override_not_object",
                    "message": "pipeline_override is present but not an object.",
                    "task_index": task_index,
                    "task_name": task_name,
                    "value_type": type(override).__name__,
                }
            )
            continue

        for node_name, patch in override.items():
            refs.append(
                _make_edge(
                    source_kind="interface_override",
                    source=f"task[{task_index}].pipeline_override",
                    field="pipeline_override",
                    target=node_name,
                    nodes=nodes,
                    task_name=task_name,
                    task_index=task_index,
                )
            )
            if not isinstance(patch, dict):
                warnings.append(
                    {
                        "code": "pipeline_override_patch_not_object",
                        "message": "pipeline_override patch is not an object.",
                        "task_index": task_index,
                        "task_name": task_name,
                        "node": node_name,
                        "value_type": type(patch).__name__,
                    }
                )
                continue

            for target in _normalize_targets(
                patch.get("next"),
                source_kind="interface_override",
                source=node_name,
                field="pipeline_override.next",
                warnings=warnings,
            ):
                refs.append(
                    _make_edge(
                        source_kind="interface_override",
                        source=node_name,
                        field="pipeline_override.next",
                        target=target,
                        nodes=nodes,
                        task_name=task_name,
                        task_index=task_index,
                    )
                )

    return refs, hard_failures


def _dangling_failures(edges: list[dict[str, Any]], refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for edge in edges:
        if not edge["target_exists"]:
            failures.append(
                {
                    "code": "pipeline_reference_target_missing",
                    "message": "Pipeline reference target node does not exist.",
                    "source": edge["source"],
                    "field": edge["field"],
                    "target": edge["target"],
                    "source_path": edge["source_path"],
                }
            )
    for ref in refs:
        if ref["target_exists"]:
            continue
        code = {
            "entry": "task_entry_target_missing",
            "pipeline_override": "override_target_missing",
            "pipeline_override.next": "override_next_target_missing",
        }.get(ref["field"], "interface_reference_target_missing")
        failures.append(
            {
                "code": code,
                "message": "Interface reference target node does not exist.",
                "task_index": ref["task_index"],
                "task_name": ref["task_name"],
                "field": ref["field"],
                "source": ref["source"],
                "target": ref["target"],
            }
        )
    return failures


def _reachable_nodes(nodes: dict[str, list[dict[str, Any]]], edges: list[dict[str, Any]], refs: list[dict[str, Any]]) -> set[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge["source"] in nodes and edge["target_exists"]:
            adjacency[edge["source"]].add(edge["target"])
    for ref in refs:
        if ref["field"] == "pipeline_override.next" and ref["source"] in nodes and ref["target_exists"]:
            adjacency[ref["source"]].add(ref["target"])

    roots = {
        ref["target"]
        for ref in refs
        if ref["target_exists"] and ref["field"] in {"entry", "pipeline_override"}
    }
    seen: set[str] = set()
    queue = deque(sorted(roots))
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        for target in sorted(adjacency.get(node, ())):
            if target not in seen:
                queue.append(target)
    return seen


def _classify_recovery(edge: dict[str, Any], nodes: dict[str, list[dict[str, Any]]]) -> str:
    source = edge["source"]
    target = edge["target"]
    target_body = (_primary_location(nodes, target) or {}).get("body", {})
    target_action = target_body.get("action") if isinstance(target_body, dict) else None
    text = f"{source} {target}"

    if target_action == "StopTask" or "终止" in text:
        return "stop"
    if edge["field"] == "on_error" or "找不到" in text:
        return "fallback"
    if source == target or "再等等" in target or "等待" in text:
        return "wait"
    if "滑动" in text:
        return "swipe"
    if any(word in text for word in ["弹窗", "关闭", "礼包"]):
        return "popup_close"
    if any(word in text for word in ["返回", "退出"]):
        return "return_exit"
    if any(word in text for word in ["奖励", "接受", "准备", "确定", "对话"]):
        return "activity_confirm"
    return "other_interrupt"


def _analysis_sections(
    nodes: dict[str, list[dict[str, Any]]],
    edges: list[dict[str, Any]],
    refs: list[dict[str, Any]],
) -> dict[str, Any]:
    reachable = _reachable_nodes(nodes, edges, refs)
    incoming_recovery: dict[str, list[dict[str, Any]]] = defaultdict(list)
    recovery_edges: list[dict[str, Any]] = []

    for edge in edges:
        if edge["field"] in {"interrupt", "on_error"}:
            category = _classify_recovery(edge, nodes)
            classified = {**edge, "category": category}
            recovery_edges.append(classified)
            incoming_recovery[edge["target"]].append(classified)

    shared_recovery = [
        {
            "node": node,
            "incoming_count": len(items),
            "categories": sorted({item["category"] for item in items}),
            "sample_sources": [item["source"] for item in items[:8]],
            "locations": [location["path"] for location in nodes.get(node, [])],
        }
        for node, items in sorted(incoming_recovery.items(), key=lambda item: (-len(item[1]), item[0]))
        if len(items) >= 5
    ]

    cross_module_edges = [
        edge
        for edge in edges
        if edge["target_exists"]
        and edge["source_module"]
        and edge["target_module"]
        and edge["source_module"] != edge["target_module"]
    ]

    self_loops = [
        edge
        for edge in edges
        if edge["source"] == edge["target"]
    ]

    unreachable = [
        {
            "node": node,
            "locations": [location["path"] for location in locations],
            "modules": sorted({location["module"] for location in locations}),
        }
        for node, locations in sorted(nodes.items())
        if node not in reachable
    ]

    recovery_counter = Counter(item["category"] for item in recovery_edges)
    return {
        "reachable_nodes": sorted(reachable),
        "unreachable_candidates": unreachable,
        "self_loops": self_loops,
        "shared_recovery": shared_recovery,
        "cross_module_edges": cross_module_edges,
        "recovery_edges": recovery_edges,
        "recovery_summary": dict(sorted(recovery_counter.items())),
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    interface_path = repo_root / INTERFACE_PATH
    pipeline_dir = repo_root / PIPELINE_DIR

    interface, interface_error = _read_strict_json(interface_path)
    nodes, warnings, pipeline_files = _build_pipeline_data(pipeline_dir)
    duplicate_nodes = {
        node: [location["path"] for location in locations]
        for node, locations in sorted(nodes.items())
        if len(locations) > 1
    }
    for node, locations in duplicate_nodes.items():
        warnings.append(
            {
                "code": "duplicate_pipeline_node_candidate",
                "message": "Node name appears in multiple pipeline files.",
                "node": node,
                "locations": locations,
            }
        )

    hard_failures: list[dict[str, Any]] = []
    if interface_error is not None:
        hard_failures.append({"code": "canonical_interface_unreadable", **interface_error})
        refs: list[dict[str, Any]] = []
    else:
        refs, interface_failures = _extract_interface_refs(interface, nodes, warnings)
        hard_failures.extend(interface_failures)

    edges = _extract_pipeline_edges(nodes, warnings)
    hard_failures.extend(_dangling_failures(edges, refs))
    analysis = _analysis_sections(nodes, edges, refs)

    edge_counter = Counter(edge["field"] for edge in edges)
    ref_counter = Counter(ref["field"] for ref in refs)
    dangling = [item for item in [*edges, *refs] if not item["target_exists"]]

    if analysis["unreachable_candidates"]:
        warnings.append(
            {
                "code": "static_unreachable_candidates",
                "message": "Some nodes are not reachable from current task entries and pipeline_override roots in a static graph.",
                "count": len(analysis["unreachable_candidates"]),
                "note": "This is not a deletion recommendation.",
            }
        )
    if analysis["self_loops"]:
        warnings.append(
            {
                "code": "self_loop_nodes",
                "message": "Some nodes reference themselves.",
                "count": len(analysis["self_loops"]),
                "note": "Self loops may be intentional wait or retry behavior.",
            }
        )
    if analysis["shared_recovery"]:
        warnings.append(
            {
                "code": "shared_recovery_nodes",
                "message": "Some recovery targets are shared by many interrupt/on_error edges.",
                "count": len(analysis["shared_recovery"]),
                "note": "Shared recovery is classification data, not a merge or cleanup requirement.",
            }
        )
    if analysis["cross_module_edges"]:
        warnings.append(
            {
                "code": "cross_module_edges",
                "message": "Some pipeline references cross module boundaries.",
                "count": len(analysis["cross_module_edges"]),
            }
        )

    return {
        "check_id": CHECK_ID,
        "scope": "Pipeline node reference graph and ProjectInterface entry/override reference audit",
        "validation_level": "V0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "canonical_interface": INTERFACE_PATH.as_posix(),
            "pipeline_dir": PIPELINE_DIR.as_posix(),
            "root_interface": "not canonical",
        },
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "summary": {
            "pipeline_file_count": len(pipeline_files),
            "pipeline_file_parse_failures": len([item for item in pipeline_files if not item["parsed"]]),
            "pipeline_node_count": len(nodes),
            "duplicate_node_count": len(duplicate_nodes),
            "pipeline_edge_count": len(edges),
            "interface_reference_count": len(refs),
            "dangling_reference_count": len(dangling),
            "reachable_node_count": len(analysis["reachable_nodes"]),
            "unreachable_candidate_count": len(analysis["unreachable_candidates"]),
            "self_loop_count": len(analysis["self_loops"]),
            "shared_recovery_count": len(analysis["shared_recovery"]),
            "cross_module_edge_count": len(analysis["cross_module_edges"]),
            "edges_by_type": dict(sorted(edge_counter.items())),
            "interface_refs_by_type": dict(sorted(ref_counter.items())),
            "recovery_by_category": analysis["recovery_summary"],
        },
        "pipeline_files": pipeline_files,
        "nodes": {
            node: [
                {
                    "path": location["path"],
                    "module": location["module"],
                    "body_type": location["body_type"],
                }
                for location in locations
            ]
            for node, locations in sorted(nodes.items())
        },
        "edges_by_type": {
            field: [edge for edge in edges if edge["field"] == field]
            for field in EDGE_FIELDS
        },
        "interface_references": refs,
        "dangling_references": dangling,
        "unreachable_candidates": analysis["unreachable_candidates"],
        "self_loops": analysis["self_loops"],
        "shared_recovery": analysis["shared_recovery"],
        "cross_module_edges": analysis["cross_module_edges"],
        "recovery_edges": analysis["recovery_edges"],
        "commands": [
            "python .\\check_pipeline_refs.py",
        ],
        "notes": [
            "This check is read-only.",
            "assets/interface.json is parsed as strict JSON.",
            "Pipeline files are parsed with JSONC-aware comment stripping for analysis only; files are never rewritten.",
            "Static unreachable candidates are not deletion recommendations.",
            "Shared recovery and cross-module edges are classification data for later review tasks.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only pipeline reference graph audit for MaaZJ."
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
