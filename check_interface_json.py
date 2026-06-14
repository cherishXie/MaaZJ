from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_ID = "T1-strict-json"


def _path_status(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": path.exists(),
        "is_file": path.is_file(),
    }


def _strict_json_check(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    result: dict[str, Any] = _path_status(path)

    if not path.exists():
        errors.append(
            {
                "code": "interface_json_missing",
                "message": "assets/interface.json does not exist.",
                "path": path.as_posix(),
            }
        )
        return result, errors

    if not path.is_file():
        errors.append(
            {
                "code": "interface_json_not_file",
                "message": "assets/interface.json is not a file.",
                "path": path.as_posix(),
            }
        )
        return result, errors

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        result["parse_error"] = {
            "message": exc.msg,
            "line": exc.lineno,
            "column": exc.colno,
            "position": exc.pos,
        }
        errors.append(
            {
                "code": "interface_json_parse_failed",
                "message": "assets/interface.json failed strict JSON parsing.",
                "path": path.as_posix(),
                "line": exc.lineno,
                "column": exc.colno,
            }
        )
        return result, errors

    result["strict_json"] = True
    result["top_level_type"] = type(data).__name__
    if isinstance(data, dict):
        result["top_level_keys"] = sorted(data.keys())
        result["task_count"] = len(data.get("task", [])) if isinstance(data.get("task"), list) else None

    return result, errors


def _install_dependency_check(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    result: dict[str, Any] = _path_status(path)

    if not path.exists() or not path.is_file():
        errors.append(
            {
                "code": "install_py_missing",
                "message": "install.py is required for the strict JSON dependency check.",
                "path": path.as_posix(),
            }
        )
        return result, errors

    text = path.read_text(encoding="utf-8")
    checks = {
        "imports_json": "import json" in text,
        "uses_copy2": "shutil.copy2" in text,
        "copies_assets_interface_json": '"assets" / "interface.json"' in text
        or "'assets' / 'interface.json'" in text,
        "targets_install_interface_json": 'install_path / "interface.json"' in text
        or "install_path / 'interface.json'" in text,
        "uses_json_load": "json.load" in text,
    }
    result["checks"] = checks

    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        errors.append(
            {
                "code": "install_py_dependency_not_confirmed",
                "message": "install.py does not clearly show the expected assets/interface.json json.load dependency.",
                "missing_checks": missing,
                "path": path.as_posix(),
            }
        )

    return result, errors


def _root_interface_warning(canonical: Path, root_interface: Path) -> list[dict[str, Any]]:
    if not root_interface.exists():
        return []
    if not canonical.exists() or not canonical.is_file() or not root_interface.is_file():
        return []

    if canonical.read_bytes() != root_interface.read_bytes():
        return [
            {
                "code": "root_interface_differs",
                "message": "root interface.json differs from assets/interface.json; assets/interface.json remains canonical.",
                "path": root_interface.as_posix(),
                "canonical": canonical.as_posix(),
            }
        ]

    return []


def build_report(repo_root: Path) -> dict[str, Any]:
    interface_path = repo_root / "assets" / "interface.json"
    install_path = repo_root / "install.py"
    root_interface_path = repo_root / "interface.json"

    interface_result, interface_errors = _strict_json_check(interface_path)
    install_result, install_errors = _install_dependency_check(install_path)
    warnings = _root_interface_warning(interface_path, root_interface_path)
    hard_failures = interface_errors + install_errors

    return {
        "check_id": CHECK_ID,
        "scope": "assets/interface.json strict JSON and install.py dependency",
        "validation_level": "V0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "canonical_interface": "assets/interface.json",
            "install_script": "install.py",
            "root_interface_warning_only": "interface.json",
        },
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "results": {
            "interface_json": interface_result,
            "install_py": install_result,
        },
        "commands": [
            "python .\\check_interface_json.py",
        ],
        "notes": [
            "This check is read-only.",
            "Pipeline JSONC-like files are intentionally out of scope.",
            "Root interface.json is not used as the runtime source of truth.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only strict JSON check for MaaZJ assets/interface.json."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to the current working directory.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    report = build_report(repo_root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["hard_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
