# MaaZJ Project Understanding Snapshot

Version: 2026-06-06

Audience: future coding agents working in this repository.

Purpose: preserve the current project understanding before refactor/upgrade work begins.

## Executive Summary

MaaZJ is a MaaFramework-based automation assistant project for `杖剑传说小助手`.

The project is primarily a Maa resource project, not a conventional application codebase. Most business behavior lives in:

- `assets/resource/pipeline/`: Maa pipeline nodes and task flow.
- `assets/resource/image/`: template images used by recognition.
- `assets/resource/model/ocr/`: OCR model files.
- `assets/interface.json`: the runtime ProjectInterface consumed by Maa clients such as MFAAvalonia.

The typical runtime path is:

`MFAAvalonia` -> reads `interface.json` -> loads `resource` -> MaaFramework executes pipeline -> optional Python agent custom actions/recognitions.

## Repository Roles

This project was developed from three upstream Maa ecosystem repositories:

- `MaaXYZ/MaaFramework`
  - The underlying automation framework.
  - Provides resource loading, pipeline execution, OCR/template/color recognition, controller actions, ProjectInterface support, and agent integration.

- `MaaXYZ/MFAAvalonia`
  - The generic Avalonia GUI client.
  - Reads `interface.json`, displays controllers/resources/tasks, and runs MaaFramework-based tasks.
  - Current local `install/` contains old MFAAvalonia v1.6.x artifacts.

- `MaaXYZ/MaaPracticeBoilerplate`
  - The original template structure.
  - This repo still contains template traces such as `install.py`, `configure.py`, Python agent examples, GitHub Actions, and template-like README content.

## Current Runtime Truth

Treat `assets/interface.json` as the current runtime truth.

Important: the repository also has a root-level `interface.json`, but it differs from `assets/interface.json`.

Observed on 2026-06-06:

- `assets/interface.json`: 35 tasks.
- root `interface.json`: 14 tasks.
- `install/interface.json`: generated from `assets/interface.json`, also 35 tasks.

Implication: future agents should not assume root `interface.json` is the active configuration. For release/runtime behavior, inspect `assets/interface.json` first.

## ProjectInterface Shape

`assets/interface.json` defines:

- Project name: `杖剑传说小助手`.
- Controller presets:
  - `安卓端`: `Adb`.
  - `桌面端`: `Win32`, currently matching window title `Visual Studio`.
- Resource presets:
  - `官服`: `{PROJECT_DIR}/resource`.
  - `B 服`: `{PROJECT_DIR}/resource`.
- Agent:
  - `child_exec`: `python`.
  - `child_args`: `{PROJECT_DIR}/agent/main.py`.
- Tasks:
  - standalone tasks such as `罗小黑联动`, `启动杖剑传说官`, `打野猪`, `流水线`, `刷友情币`.
  - many account/server-specific tasks generated manually through `pipeline_override`.

The account/server tasks override:

- `sub_启动杖剑传说官_选择服务器.expected`
- `用户切换_选择账号.expected`

Known server labels in `assets/interface.json`:

- `晶`
- `暖阳`
- `朋克`
- `蒸汽`

Known pattern: many tasks are duplicated by server/account pair. This is a major refactor target.

## Resource And Pipeline Structure

Observed on 2026-06-06:

- Pipeline files: about 47 JSON/JSONC files under `assets/resource/pipeline/`.
- Template image files: about 121 under `assets/resource/image/`.
- Parsed pipeline nodes: about 300+.
- Dominant node prefix: `FARM_`, used for the daily farm flow.

Major pipeline areas:

- `assets/resource/pipeline/start_up.json`
  - App launch, server selection, announcement closing, start button.

- `assets/resource/pipeline/小号/用户.json`
  - Account switching and login flow.

- `assets/resource/pipeline/小号/farm.json`
  - Entry for farm/daily flow.

- `assets/resource/pipeline/activity/刷友情币.json`
  - Friendship currency flow around `世界树`.

- `assets/resource/pipeline/小号/...`
  - Daily modules such as shop, bed, mail, guild, notebook, exploration, tasks, events, linkage activity.

- `assets/resource/pipeline/起号/...`
  - Account creation / early-game setup flows.

Recognition/action distribution observed through standard JSON parsing of valid files:

- Recognition:
  - `OCR`: dominant.
  - `TemplateMatch`: second.
  - `ColorMatch`: rare.

- Action:
  - `Click`: dominant.
  - `DoNothing`: common.
  - `Swipe`, `InputText`, `StartApp`, `StopApp`, `StopTask`: occasional.

## JSON vs JSONC Note

Several pipeline files contain comments or JSONC-style syntax. Standard JSON parsers such as PowerShell `ConvertFrom-Json` report errors on those files.

However, MaaFramework successfully loaded `assets/resource` on 2026-06-06 with:

```powershell
python .\check_resource.py .\assets\resource\
```

Result:

```text
All directories checked.
```

Implication:

- Do not blindly "fix" comments just because a strict JSON parser fails.
- For tooling, use a JSONC-capable parser or MaaFramework's own resource checker.
- Before broad formatting/migration, preserve Maa-compatible behavior.

## Python Agent State

Python agent files:

- `agent/main.py`
- `agent/my_action.py`
- `agent/my_reco.py`

Current state:

- `agent/main.py` starts `AgentServer`.
- `my_action.py` registers custom action `地图定位检测`.
- `my_reco.py` registers custom recognition `my_reco_222`.
- No pipeline references to `地图定位检测`, `my_reco_222`, `custom_action`, or `custom_recognition` were found on 2026-06-06.

Implication:

- Current business logic is almost entirely in pipeline resources.
- The Python agent appears to be mostly template/example code at this stage.
- If future refactor needs smarter state detection, Python custom action/recognition is available but not currently part of the runtime path.

## Build And Release Structure

Relevant scripts:

- `configure.py`
  - Copies the default OCR model from `assets/MaaCommonAssets/OCR/ppocr_v5/zh_cn` into `assets/resource/model/ocr` if missing.

- `check_resource.py`
  - Uses `maa.resource.Resource` to load and validate resource bundles.

- `install.py`
  - Copies MaaFramework binaries from `deps/bin`.
  - Copies `deps/share/MaaAgentBinary`.
  - Runs OCR configuration.
  - Copies `assets/resource` into `install/resource`.
  - Copies `assets/interface.json` into `install/interface.json`.
  - Copies README, LICENSE, and agent files.
  - Rewrites `interface.version` to the provided install version.

Important: `install.py` uses `assets/interface.json`, not the root `interface.json`.

GitHub Actions:

- `.github/workflows/check.yml`
  - Installs prerelease `maafw`.
  - Runs `python ./check_resource.py ./assets/resource/`.

- `.github/workflows/install.yml`
  - Downloads latest MaaFramework release artifacts.
  - Downloads MFAAvalonia artifacts.
  - Runs `install.py`.
  - Uploads packaged artifacts for multiple OS/arch combinations.

Potential issue:

- The workflow currently references `SweetSmellFox/MFAAvalonia`, while the user mentioned `MaaXYZ/MFAAvalonia`.
- Future upgrade should verify the intended upstream source and artifact naming.

## Local Dependency Snapshot

Observed local dependency state on 2026-06-06:

- `deps/bin` exists and contains MaaFramework binaries dated around 2025-07-28.
- `install/` exists and contains MaaFramework binaries plus MFAAvalonia v1.6.x artifacts.
- `assets/resource/model/ocr` exists and contains:
  - `det.onnx`
  - `rec.onnx`
  - `keys.txt`
  - `README.md`

Upstream release state checked on 2026-06-06:

- MaaFramework latest observed: `v5.10.5`, released 2026-05-19.
- MFAAvalonia latest observed: `v2.12.1`, released 2026-05-01.

Implication:

- A future upgrade is likely a cross-version migration, not a tiny patch.
- Establish a working baseline before replacing framework/UI binaries.

## Known Risks And Refactor Targets

1. Duplicate ProjectInterface files

   Root `interface.json` and `assets/interface.json` differ. This can cause future agents or humans to edit the wrong file.

2. Hardcoded account/server task explosion

   Server/account combinations are manually expanded into many tasks. This is repetitive and fragile.

3. Template leftovers

   README and some agent files still resemble MaaPracticeBoilerplate. They should be rewritten or clearly marked.

4. JSONC compatibility

   MaaFramework accepts files that strict JSON tooling rejects. Future formatting/checking must account for this.

5. Agent code not integrated

   Python custom logic is present but unused. Either remove template examples or turn them into real utilities.

6. Upgrade gap

   Local `deps` and `install` artifacts are older than current upstream MaaFramework/MFAAvalonia releases.

7. CI and local truth mismatch risk

   CI downloads latest upstream artifacts while local `deps` contains fixed older artifacts. Behavior may diverge after upstream changes.

## Suggested Refactor Order

1. Freeze and document baseline

   Keep this snapshot and run `check_resource.py` before and after each major change.

2. Unify ProjectInterface source of truth

   Decide whether `assets/interface.json` remains canonical. If yes, either remove, sync, or clearly document root `interface.json`.

3. Normalize task configuration

   Replace duplicated account/server tasks with generated config or ProjectInterface options where supported by the target MFAAvalonia version.

4. Modularize pipeline ownership

   Make module boundaries explicit:

   - startup
   - account switching
   - farm daily flow
   - activity flow
   - shop
   - guild
   - notebook
   - exploration
   - account creation

5. Clean template residue

   Rewrite README for MaaZJ and remove unused demo code if it is truly not used.

6. Upgrade framework/UI carefully

   Upgrade MaaFramework and MFAAvalonia after the project has a clean baseline, then compare behavior and resource loading.

7. Add lightweight tooling

   Useful future tools:

   - task generator for account/server combinations.
   - pipeline graph/reference checker.
   - template image usage checker.
   - JSONC-aware formatter/checker.

## Verification Performed

On 2026-06-06, the following command succeeded:

```powershell
python .\check_resource.py .\assets\resource\
```

Final observed output:

```text
Checking 1 directories...
Checking assets\resource...
All directories checked.
```

This verifies that the current resource bundle can be loaded by the installed Maa Python bindings and MaaFramework runtime available in the environment.

## Guidance For Future Agents

- Start from `assets/interface.json`, not root `interface.json`, unless the task explicitly concerns root-level files.
- Validate resource changes with `python .\check_resource.py .\assets\resource\`.
- Be cautious with standard JSON tooling because many pipeline files are JSONC-like.
- Do not remove account/server overrides until a replacement configuration mechanism exists.
- Do not assume Python agent code is active; search pipeline references first.
- Treat `install/` and `deps/` as generated/vendor-like runtime artifacts unless the user explicitly asks to update release packaging.
