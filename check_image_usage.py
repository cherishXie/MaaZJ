from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_ID = "T4-image-usage"
PIPELINE_DIR = Path("assets") / "resource" / "pipeline"
IMAGE_DIR = Path("assets") / "resource" / "image"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
KNOWN_SHARED_IMAGES = {"红点.png", "家园图标.png", "auto_add.png", "笔记.png"}
REFERENCE_WIDTH = 720
REFERENCE_HEIGHT = 1280
LARGE_ROI_AREA_RATIO = 0.20
SMALL_ROI_AREA = 1500
EDGE_MARGIN = 5


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


def _collect_images(image_dir: Path) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, Any]]]:
    images: dict[str, list[dict[str, str]]] = defaultdict(list)
    warnings: list[dict[str, Any]] = []

    if not image_dir.exists():
        warnings.append(
            {
                "code": "image_dir_missing",
                "message": "Image directory does not exist; template file existence cannot be checked.",
                "path": image_dir.as_posix(),
            }
        )
        return {}, warnings

    for path in sorted(image_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        images[path.name].append(
            {
                "path": path.as_posix(),
                "relative_path": path.relative_to(image_dir).as_posix(),
            }
        )

    duplicates = {name: locations for name, locations in images.items() if len(locations) > 1}
    for image_name, locations in sorted(duplicates.items()):
        warnings.append(
            {
                "code": "duplicate_image_filename",
                "message": "Multiple image files share the same filename.",
                "image_name": image_name,
                "locations": [item["path"] for item in locations],
            }
        )

    return dict(images), warnings


def _flatten_template(value: Any, warnings: list[dict[str, Any]], context: dict[str, Any]) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        templates: list[str] = []
        for index, item in enumerate(value):
            templates.extend(_flatten_template(item, warnings, {**context, "template_index": index}))
        return templates
    if isinstance(value, dict):
        templates = []
        for key, item in value.items():
            templates.extend(_flatten_template(item, warnings, {**context, "template_key": key}))
        return templates

    warnings.append(
        {
            "code": "unsupported_template_shape",
            "message": "template contains a value that is not string, list, object, or null.",
            **context,
            "value_type": type(value).__name__,
        }
    )
    return []


def _normalize_reference(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _node_walk(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    items = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            items.extend(_node_walk(item, (*path, str(key))))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            items.extend(_node_walk(item, (*path, str(index))))
    return items


def _find_values_by_key(value: Any, key: str) -> list[Any]:
    return [item for path, item in _node_walk(value) if path and path[-1] == key]


def _as_roi(value: Any) -> list[float] | None:
    if not isinstance(value, list) or len(value) != 4:
        return None
    numbers: list[float] = []
    for item in value:
        if isinstance(item, (int, float)):
            numbers.append(float(item))
        else:
            return None
    return numbers


def _expected_is_regex(expected: Any) -> bool:
    regex_marks = ("^", "$", "\\d", "\\w", "\\s", ".*", ".+", "[", "]", "(", ")", "|")
    if isinstance(expected, str):
        return any(mark in expected for mark in regex_marks)
    if isinstance(expected, list):
        return any(isinstance(item, str) and _expected_is_regex(item) for item in expected)
    return False


def _expected_count(expected: Any) -> int:
    if isinstance(expected, list):
        return len(expected)
    return 1 if isinstance(expected, str) and expected else 0


def _contains_ocr(node_body: dict[str, Any]) -> bool:
    recognition = node_body.get("recognition")
    if isinstance(recognition, str) and "OCR" in recognition.upper():
        return True
    return bool(_find_values_by_key(node_body, "expected"))


def _roi_risks(node_name: str, path: str, module: str, node_body: dict[str, Any]) -> list[dict[str, Any]]:
    if not _contains_ocr(node_body):
        return []

    risks: list[dict[str, Any]] = []
    roi_values = _find_values_by_key(node_body, "roi")
    roi = _as_roi(roi_values[0]) if roi_values else None
    expected = node_body.get("expected")

    if roi is None:
        risks.append(
            {
                "risk": "no_roi",
                "node": node_name,
                "file": path,
                "module": module,
                "recognition": node_body.get("recognition"),
                "expected": expected,
                "evidence_required": True,
                "evidence_status": "not_collected",
            }
        )
    else:
        x, y, width, height = roi
        area = max(width, 0) * max(height, 0)
        area_ratio = area / (REFERENCE_WIDTH * REFERENCE_HEIGHT)
        base = {
            "node": node_name,
            "file": path,
            "module": module,
            "recognition": node_body.get("recognition"),
            "expected": expected,
            "roi": roi,
            "evidence_required": True,
            "evidence_status": "not_collected",
        }
        if area_ratio >= LARGE_ROI_AREA_RATIO:
            risks.append({"risk": "large_roi", "area_ratio": round(area_ratio, 4), **base})
        if area <= SMALL_ROI_AREA:
            risks.append({"risk": "small_roi", "area": area, **base})
        if x <= EDGE_MARGIN or y <= EDGE_MARGIN or x + width >= REFERENCE_WIDTH - EDGE_MARGIN or y + height >= REFERENCE_HEIGHT - EDGE_MARGIN:
            risks.append({"risk": "edge_roi", **base})

    if _expected_is_regex(expected):
        risks.append(
            {
                "risk": "regex_expected",
                "node": node_name,
                "file": path,
                "module": module,
                "recognition": node_body.get("recognition"),
                "expected": expected,
                "roi": roi,
                "evidence_required": True,
                "evidence_status": "not_collected",
            }
        )
    if _expected_count(expected) >= 3:
        risks.append(
            {
                "risk": "multi_expected",
                "node": node_name,
                "file": path,
                "module": module,
                "recognition": node_body.get("recognition"),
                "expected": expected,
                "roi": roi,
                "evidence_required": True,
                "evidence_status": "not_collected",
            }
        )

    return risks


def _scan_pipeline(
    pipeline_dir: Path,
    images: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    template_references: list[dict[str, Any]] = []
    ocr_roi_risks: list[dict[str, Any]] = []
    hard_failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    pipeline_files: list[dict[str, Any]] = []

    if not pipeline_dir.exists():
        hard_failures.append(
            {
                "code": "pipeline_dir_missing",
                "message": "Pipeline directory does not exist.",
                "path": pipeline_dir.as_posix(),
            }
        )
        return template_references, ocr_roi_risks, hard_failures, warnings, pipeline_files

    for path in sorted(pipeline_dir.rglob("*.json")):
        data, warning = _read_jsonc_object(path)
        file_record = {"path": path.as_posix(), "parsed": warning is None, "node_count": 0}
        if warning is not None:
            warnings.append(warning)
            pipeline_files.append(file_record)
            continue

        assert data is not None
        module = _module_for_path(path.as_posix())
        file_record["node_count"] = len(data)
        pipeline_files.append(file_record)

        for node_name, node_body in data.items():
            if not isinstance(node_body, dict):
                warnings.append(
                    {
                        "code": "pipeline_node_not_object",
                        "message": "Pipeline node body is not an object.",
                        "node": node_name,
                        "file": path.as_posix(),
                        "body_type": type(node_body).__name__,
                    }
                )
                continue

            context = {"node": node_name, "file": path.as_posix(), "module": module}
            raw_templates = _find_values_by_key(node_body, "template")
            for raw_template in raw_templates:
                for template in _flatten_template(raw_template, warnings, context):
                    image_name = Path(template).name
                    exists = image_name in images
                    record = {
                        "node": node_name,
                        "file": path.as_posix(),
                        "module": module,
                        "recognition": node_body.get("recognition"),
                        "template": template,
                        "image_name": image_name,
                        "exists": exists,
                        "image_locations": [item["path"] for item in images.get(image_name, [])],
                        "expected": node_body.get("expected"),
                        "roi": node_body.get("roi"),
                        "target": node_body.get("target"),
                        "next": _normalize_reference(node_body.get("next")),
                        "interrupt": _normalize_reference(node_body.get("interrupt")),
                        "evidence_required": False,
                        "evidence_status": "not_required",
                    }
                    template_references.append(record)
                    if not exists:
                        hard_failures.append(
                            {
                                "code": "missing_template",
                                "message": "Pipeline references a template image that does not exist.",
                                "node": node_name,
                                "file": path.as_posix(),
                                "template": template,
                                "image_name": image_name,
                            }
                        )

            ocr_roi_risks.extend(_roi_risks(node_name, path.as_posix(), module, node_body))

    return template_references, ocr_roi_risks, hard_failures, warnings, pipeline_files


def _usage_sections(
    images: dict[str, list[dict[str, str]]],
    template_references: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    refs_by_image: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ref in template_references:
        refs_by_image[ref["image_name"]].append(ref)

    image_usage = []
    for image_name, locations in sorted(images.items()):
        refs = refs_by_image.get(image_name, [])
        nodes = sorted({ref["node"] for ref in refs})
        files = sorted({ref["file"] for ref in refs})
        modules = sorted({ref["module"] for ref in refs})
        image_usage.append(
            {
                "image_name": image_name,
                "exists": True,
                "locations": [item["path"] for item in locations],
                "referenced_by_count": len(refs),
                "referenced_nodes": nodes,
                "referenced_files": files,
                "modules": modules,
                "suspected_unused": not refs,
                "candidate_only": not refs,
            }
        )

    suspected_unused = [
        {
            "image_name": item["image_name"],
            "locations": item["locations"],
            "candidate_only": True,
            "note": "Static candidate only; this is not a deletion recommendation.",
        }
        for item in image_usage
        if item["suspected_unused"]
    ]

    shared_images = []
    for image_name, refs in sorted(refs_by_image.items()):
        nodes = sorted({ref["node"] for ref in refs})
        modules = sorted({ref["module"] for ref in refs})
        if len(nodes) >= 3 or len(modules) >= 2 or image_name in KNOWN_SHARED_IMAGES:
            shared_images.append(
                {
                    "image_name": image_name,
                    "reference_count": len(refs),
                    "node_count": len(nodes),
                    "modules": modules,
                    "sample_nodes": nodes[:12],
                    "known_shared": image_name in KNOWN_SHARED_IMAGES,
                    "risk": "cross_module_reuse" if len(modules) >= 2 else "multi_reuse",
                    "note": "Shared image reuse is review input, not a cleanup instruction.",
                }
            )

    missing_usage = [
        {
            "image_name": ref["image_name"],
            "exists": False,
            "locations": [],
            "referenced_by_count": len(refs_by_image.get(ref["image_name"], [])),
            "referenced_nodes": sorted({item["node"] for item in refs_by_image.get(ref["image_name"], [])}),
            "referenced_files": sorted({item["file"] for item in refs_by_image.get(ref["image_name"], [])}),
            "modules": sorted({item["module"] for item in refs_by_image.get(ref["image_name"], [])}),
            "suspected_unused": False,
            "candidate_only": False,
        }
        for ref in template_references
        if not ref["exists"]
    ]

    return image_usage + missing_usage, suspected_unused, shared_images, missing_usage


def build_report(repo_root: Path) -> dict[str, Any]:
    pipeline_dir = repo_root / PIPELINE_DIR
    image_dir = repo_root / IMAGE_DIR

    images, image_warnings = _collect_images(image_dir)
    template_references, ocr_roi_risks, hard_failures, warnings, pipeline_files = _scan_pipeline(pipeline_dir, images)
    warnings.extend(image_warnings)

    image_usage, suspected_unused, shared_images, missing_usage = _usage_sections(images, template_references)

    for item in suspected_unused:
        warnings.append(
            {
                "code": "suspected_unused_image",
                "message": "Image file is not referenced by current static pipeline template scan.",
                "image_name": item["image_name"],
                "locations": item["locations"],
                "candidate_only": True,
                "note": "This is not a deletion recommendation.",
            }
        )
    for item in shared_images:
        warnings.append(
            {
                "code": item["risk"],
                "message": "Image is reused by multiple nodes or modules.",
                "image_name": item["image_name"],
                "reference_count": item["reference_count"],
                "node_count": item["node_count"],
                "modules": item["modules"],
                "known_shared": item["known_shared"],
                "note": item["note"],
            }
        )
    for risk, count in sorted(Counter(item["risk"] for item in ocr_roi_risks).items()):
        warnings.append(
            {
                "code": risk,
                "message": "OCR/ROI static risk candidates were found.",
                "count": count,
                "candidate_only": True,
                "note": "Requires screenshot or debug evidence before changing OCR/ROI.",
            }
        )

    template_counter = Counter(ref["image_name"] for ref in template_references)
    recognition_counter = Counter(str(ref["recognition"]) for ref in template_references)

    return {
        "check_id": CHECK_ID,
        "scope": "Image/template usage and OCR/ROI static risk audit",
        "validation_level": "V0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "pipeline_dir": PIPELINE_DIR.as_posix(),
            "image_dir": IMAGE_DIR.as_posix(),
            "root_interface": "not used",
        },
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "summary": {
            "pipeline_file_count": len(pipeline_files),
            "pipeline_file_parse_failures": len([item for item in pipeline_files if not item["parsed"]]),
            "image_file_count": sum(len(locations) for locations in images.values()),
            "unique_image_name_count": len(images),
            "template_reference_count": len(template_references),
            "unique_template_image_count": len(template_counter),
            "missing_template_count": len(missing_usage),
            "suspected_unused_image_count": len(suspected_unused),
            "shared_image_count": len(shared_images),
            "ocr_roi_risk_count": len(ocr_roi_risks),
            "template_references_by_recognition": dict(sorted(recognition_counter.items())),
            "ocr_roi_risks_by_type": dict(sorted(Counter(item["risk"] for item in ocr_roi_risks).items())),
        },
        "pipeline_files": pipeline_files,
        "image_usage": image_usage,
        "template_references": template_references,
        "ocr_roi_risks": ocr_roi_risks,
        "suspected_unused_images": suspected_unused,
        "shared_images": shared_images,
        "commands": [
            "python .\\check_image_usage.py",
        ],
        "notes": [
            "This check is read-only.",
            "Pipeline files are parsed with JSONC-aware comment stripping for analysis only; files are never rewritten.",
            "Missing template files are hard failures.",
            "Suspected unused images are review candidates only, not deletion recommendations.",
            "Shared image and OCR/ROI risks require screenshot or debug evidence before resource changes.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only image/template usage and OCR/ROI risk audit for MaaZJ."
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
