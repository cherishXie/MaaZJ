# Upgrade Checklist

Use this checklist for MaaFramework, MFAAvalonia, MaaPracticeBoilerplate, release workflow, `deps/`, or `install/` work.

## Before Changes

- Read `AGENTS.md`.
- Read `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`.
- Confirm `assets/interface.json` is the runtime truth for the planned change.
- Freeze the current baseline.
- Run resource validation before dependency or runtime changes:

```powershell
python .\check_resource.py .\assets\resource\
```

## Upstream Confirmation

Re-check current official state for:

- MaaFramework latest stable release and artifact names.
- MFAAvalonia latest stable release and artifact names.
- MaaPracticeBoilerplate current template structure.
- MaaHub relevant skill/pipeline/custom/experience examples.

Do not rely only on historical version numbers stored in repository docs.

## Implementation Boundaries

- Keep MaaFramework and MFAAvalonia upgrades separate when possible.
- Treat MaaPracticeBoilerplate alignment as template structure alignment, not business resource replacement.
- Do not edit `deps/` or `install/` unless the task explicitly targets runtime or packaged artifacts.
- Do not change root `interface.json` unless explicitly requested.
- Do not collapse account/server `pipeline_override` behavior without a validated replacement.

## Workflow Checks

When modifying workflow upstream references, confirm:

- target upstream repository;
- artifact naming;
- operating system and architecture matrix;
- download paths;
- install/configure script assumptions.

Prefer `MaaXYZ/MFAAvalonia` for MFAAvalonia target upstream unless the user explicitly requests otherwise.

## After Changes

At minimum, compare:

- resource loading;
- task display;
- task startup behavior;
- packaging output if release artifacts are affected.

For resource-affecting changes, run:

```powershell
python .\check_resource.py .\assets\resource\
```

If validation cannot be run, record the reason and list manual checks still needed.
