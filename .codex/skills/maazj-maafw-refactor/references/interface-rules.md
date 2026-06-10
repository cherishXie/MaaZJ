# Interface Rules

## Canonical File

`assets/interface.json` is the canonical ProjectInterface for MaaZJ runtime and release behavior.

Root `interface.json` is not canonical unless the task explicitly targets it.

`install.py` copies `assets/interface.json` into `install/interface.json` and parses it with `json.load`, so `assets/interface.json` must remain strict JSON:

- no comments;
- no trailing commas;
- no JSONC-only syntax.

## ProjectInterface Responsibilities

`assets/interface.json` defines:

- `controller`
- `resource`
- `agent`
- `task`

Task behavior starts at `task[].entry`. To understand actual execution, follow the entry node into pipeline `next`, `interrupt`, and `on_error` paths.

## Task Entries

Before changing a task `entry`, confirm the target node exists in `assets/resource/pipeline/`.

Use:

```powershell
rg -n '"entry"|"pipeline_override"|节点名' assets\interface.json
```

## Pipeline Override

`pipeline_override` currently carries important account, server, and task-entry differences.

Do not remove, fold, or regenerate these overrides unless:

- a generator exists and is approved; or
- a supported MFAAvalonia/ProjectInterface configuration mechanism has been verified; and
- existing behavior can be compared or validated.

Especially protect overrides for:

- server selection;
- account switching;
- task-specific `expected`;
- task-specific `next` or `action`.

## Agent Configuration

`assets/interface.json` configures Python agent startup, currently through `{PROJECT_DIR}/agent/main.py`.

This does not prove custom action/custom recognition is used in business pipeline. Search registered names before changing agent-related behavior.

## Validation

After modifying `assets/interface.json`, run resource validation:

```powershell
python .\check_resource.py .\assets\resource\
```

Also manually confirm task display and task startup behavior when changes affect task entries, controller/resource/agent settings, or account/server flows.
