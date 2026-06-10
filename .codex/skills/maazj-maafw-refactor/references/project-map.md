# MaaZJ Project Map

## Project Identity

MaaZJ is a MaaFramework resource project for `杖剑传说小助手`, not a conventional application codebase.

Runtime behavior is mainly defined by:

- `assets/interface.json`
- `assets/resource/pipeline/`
- `assets/resource/image/`
- optional Python custom logic under `agent/`

Typical runtime flow:

```text
MFAAvalonia -> ProjectInterface -> resource bundle -> MaaFramework pipeline -> optional Python agent
```

## Runtime Truth

Use `assets/interface.json` as the canonical runtime and release-facing ProjectInterface.

Do not treat root `interface.json` as canonical unless a task explicitly targets that file. The root file may differ from `assets/interface.json`.

`install.py` copies `assets/interface.json` to `install/interface.json` and then parses it with `json.load`, so `assets/interface.json` must stay strict JSON.

## Main Directories

- `assets/interface.json`: current ProjectInterface source of truth.
- `assets/resource/pipeline/`: MaaFramework pipeline nodes and task flow.
- `assets/resource/image/`: TemplateMatch and related image resources.
- `assets/resource/model/ocr/`: OCR model files.
- `agent/`: Python custom action/custom recognition entrypoint.
- `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md`: project understanding snapshot for broad refactor or upgrade work.
- `docs/agent_design/`: AGENTS and skill design records.
- `deps/`: vendor-like runtime dependencies.
- `install/`: generated or packaged runtime output.

## Current Known Facts

- `assets/interface.json` defines controller, resource, agent, and task entries.
- Python agent startup is configured as `{PROJECT_DIR}/agent/main.py`.
- Known registered Python custom names include `地图定位检测` and `my_reco_222`.
- As of the 2026-06-06 project snapshot, those registered names were not proven to be used by business pipeline nodes.
- Account/server-specific tasks currently rely heavily on `pipeline_override`.
- Duplicate account/server task definitions are a refactor target, but should not be removed until a supported replacement exists.

## Default Safety Rules

- Keep changes scoped to the requested task.
- Do not modify `deps/` or `install/` unless the task explicitly concerns runtime, packaging, or release artifacts.
- Do not modify root `interface.json` unless explicitly requested.
- Do not remove or collapse account/server overrides without a validated replacement.
- For broad refactor or upgrade work, read `docs/agent_context/PROJECT_UNDERSTANDING_2026-06-06.md` first.

## Verification

For resource changes, run:

```powershell
python .\check_resource.py .\assets\resource\
```

For documentation-only, AGENTS-only, or skill-only changes, resource validation can be skipped, but record why.
