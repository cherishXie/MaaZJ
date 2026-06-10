# Pipeline Rules

## Scope

Pipeline files live under `assets/resource/pipeline/`.

Before editing that directory, read `assets/resource/pipeline/AGENTS.md`. If a task marks `assets/resource/pipeline/` as forbidden, treat that file as read-only context too.

## JSONC Boundary

Pipeline files may contain MaaFramework-compatible JSONC-like content such as `//` comments.

Do not:

- strict-format the whole pipeline tree;
- remove comments just to satisfy a strict JSON parser;
- rewrite unrelated nodes for formatting consistency.

Use MaaFramework resource validation as the practical compatibility check:

```powershell
python .\check_resource.py .\assets\resource\
```

## Node References

Pipeline node names may be referenced by:

- `assets/interface.json` task `entry`;
- `assets/interface.json` `pipeline_override`;
- other pipeline nodes through `next`, `interrupt`, and `on_error`.

Before deleting or renaming a node, search references:

```powershell
rg -n "节点名" assets\interface.json assets\resource\pipeline
```

## Key Fields

Treat these fields as behavior-changing:

- `recognition`
- `action`
- `expected`
- `template`
- `roi`
- `target`
- `next`
- `interrupt`
- `on_error`
- `post_delay`
- `post_wait_freezes`

`next` order can change routing and fallback behavior. `interrupt` and `on_error` often encode retry, wait, or recovery paths.

## Images And OCR

For image or OCR-related changes, check both sides:

- pipeline node recognition fields;
- files under `assets/resource/image/`.

Before renaming an image:

```powershell
rg -n "图片文件名.png" assets\resource\pipeline
```

## Python Custom Integration

Do not assume Python custom logic is used just because `agent/main.py` is configured.

Search registered names before modifying custom integration:

```powershell
rg -n "地图定位检测|my_reco_222|新的注册名" assets\interface.json assets\resource\pipeline agent
```

## Upstream Alignment

Before migrating pipeline syntax for a newer MaaFramework version, re-check current official MaaFramework pipeline protocol, recognition/action fields, custom action/custom recognition integration, and resource loading behavior.

MaaHub can be used as a reference for organization patterns, but do not copy sample nodes, ROI, image names, or game flow directly into MaaZJ.
