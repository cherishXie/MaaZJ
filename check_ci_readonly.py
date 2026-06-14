#!/usr/bin/env python3
"""Run MaaZJ readonly validation checks for CI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent

CHECKS = [
    {
        "check_id": "T1-interface-json",
        "script": "check_interface_json.py",
        "description": "assets/interface.json strict JSON check",
    },
    {
        "check_id": "T2-interface-audit",
        "script": "check_interface_audit.py",
        "description": "ProjectInterface task, entry, and override audit",
    },
    {
        "check_id": "T3-pipeline-refs",
        "script": "check_pipeline_refs.py",
        "description": "JSONC-aware pipeline reference check",
    },
    {
        "check_id": "T4-image-usage",
        "script": "check_image_usage.py",
        "description": "template image usage and OCR/ROI risk check",
    },
    {
        "check_id": "T5-agent-custom",
        "script": "check_agent_custom.py",
        "description": "Python custom action/recognition registration check",
    },
]


def run_check(item: dict[str, str]) -> dict[str, Any]:
    script = ROOT / item["script"]
    command = [sys.executable, str(script)]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )

    record: dict[str, Any] = {
        "check_id": item["check_id"],
        "script": item["script"],
        "description": item["description"],
        "command": f"python ./{item['script']}",
        "exit_code": result.returncode,
        "status": "failed",
        "hard_failures": [],
        "warnings": [],
        "summary": {},
    }

    if result.returncode != 0:
        record["hard_failures"].append(
            {
                "type": "subprocess_failed",
                "message": f"{item['script']} exited with code {result.returncode}",
                "stderr": result.stderr.strip(),
            }
        )
        return record

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        record["hard_failures"].append(
            {
                "type": "invalid_json_stdout",
                "message": str(exc),
                "stdout_prefix": result.stdout[:500],
            }
        )
        return record

    child_hard_failures = payload.get("hard_failures") or []
    child_warnings = payload.get("warnings") or []
    child_status = payload.get("status", "unknown")

    record.update(
        {
            "reported_check_id": payload.get("check_id"),
            "reported_validation_level": payload.get("validation_level"),
            "status": child_status,
            "hard_failures": child_hard_failures,
            "warnings": child_warnings,
            "summary": payload.get("summary", {}),
        }
    )

    if child_status != "passed":
        record["hard_failures"].append(
            {
                "type": "child_status_not_passed",
                "message": f"{item['script']} reported status {child_status!r}",
            }
        )

    return record


def build_report() -> dict[str, Any]:
    checks = [run_check(item) for item in CHECKS]
    hard_failures = []
    warnings = []

    for check in checks:
        for failure in check.get("hard_failures", []):
            hard_failures.append(
                {
                    "check_id": check["check_id"],
                    "script": check["script"],
                    **failure,
                }
            )
        for warning in check.get("warnings", []):
            warnings.append(
                {
                    "check_id": check["check_id"],
                    "script": check["script"],
                    "warning": warning,
                }
            )

    status = "failed" if hard_failures else "passed"
    return {
        "check_id": "T7-ci-readonly",
        "validation_level": "V0",
        "status": status,
        "scope": [
            "assets/interface.json",
            "assets/resource/pipeline/",
            "assets/resource/image/",
            "agent/",
        ],
        "summary": {
            "checks_total": len(checks),
            "checks_passed": sum(1 for check in checks if check["status"] == "passed"),
            "hard_failures": len(hard_failures),
            "warnings": len(warnings),
        },
        "hard_failures": hard_failures,
        "warnings": warnings,
        "checks": checks,
        "commands": [f"python ./{item['script']}" for item in CHECKS],
        "notes": [
            "This aggregate check is read-only and does not modify MaaZJ resources.",
            "Warnings are reported for review but do not fail CI unless a child check reports hard_failures or a non-passed status.",
            "V1 resource load remains covered by python ./check_resource.py ./assets/resource/ in .github/workflows/check.yml.",
            "T6 real-flow smoke cases are intentionally not automated in CI.",
        ],
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
