---
name: multi-agent-refactor
description: Use this MaaZJ-specific adapter when the user asks to create, continue, approve, implement, review, test, finalize, or summarize a `.agent/` multi-agent workflow task in this repository. It preserves MaaZJ resource and ProjectInterface safety rules while following the global zzq-workflow style.
---

# Multi-Agent Refactor Workflow

This is the MaaZJ repository adapter for the generic `zzq-workflow` workflow.

Use the repository `.agent/` protocol as the source of truth. The user does not need to run `npm` commands or copy long role prompts.

## Natural Language Entrypoints

Act as the Orchestrator when the user says:

- `使用 multi-agent-refactor 工作流创建并处理一个新任务：<任务描述>`
- `继续 multi-agent-refactor 工作流`
- `继续任务 .agent/tasks/<task-id>`
- `将当前 multi-agent-refactor 任务切换到 .agent/tasks/<task-id>`
- `我确认当前 plan，可以进入实现。继续 multi-agent-refactor 工作流。`
- `结束并总结当前 multi-agent-refactor 任务`

The generic global equivalent is `zzq-workflow`. In MaaZJ, prefer this adapter because it includes project-specific safety rules.

## Required Reads

Read these before acting:

- `.agent/README.md`
- `.agent/WORKFLOW.md`
- `.agent/prompts/orchestrator.md`
- `AGENTS.md`

For MaaZJ business or resource changes, also read the relevant nested `AGENTS.md` and context files required by root `AGENTS.md`.

## Codex Responsibilities

- Create task directories directly under `.agent/tasks/`.
- Never overwrite an existing task directory; append `-2`, `-3`, and so on for task-id conflicts.
- Treat `.agent/current-task.json` as a convenience pointer, not the sole source of truth.
- Prefer explicit user-provided task directories or task ids over `current-task.json`.
- Update `.agent/current-task.json` when creating a task or when the user explicitly switches active task.
- Resolve the current task from explicit user path/task id, then current-thread selection, then `current-task.json`, then recent unfinished task candidates.
- If multiple unfinished tasks are plausible, list candidates and stop for user selection.
- Read and update `state.json`.
- Stop at confirmation points.
- Produce the required stage-end status block.

## Workflow Modes

Default to `workflow_mode = "auto"`.

- `safe`: stop after plan, before manual implementation, after implementation, on test failure, when blocked, and when done.
- `auto`: only for low-risk small fixes. Still write `plan.md`, `implementation.md`, `test.md`, and `final.md`; still run review and validation.
- If high-risk files, forbidden files, or uncertain scope appear, switch to `safe` and stop for confirmation.

High-risk examples:

- `assets/interface.json`
- `assets/resource/pipeline/`
- `assets/resource/image/`
- `agent/`
- `deps/`
- `install/`
- `.github/workflows/`

## MaaZJ Safety

- Do not modify business code before plan confirmation unless `workflow_mode = "auto"` and risk is low.
- Planner and Reviewer do not modify business code.
- Do not skip review.
- Do not skip validation.
- Do not use root `interface.json` as MaaZJ runtime truth unless the task explicitly targets it.
- Keep `assets/interface.json` strict JSON.
- Do not strict-format JSONC-like pipeline files.
- For resource changes, run `python .\check_resource.py .\assets\resource\` unless the task only changes workflow, skill, or documentation files.

## Scripts

`scripts/agent-workflow/` is auxiliary only. Codex can use direct file reads/writes instead. The user does not need to run `npm`.

## Stage-End Output

Whenever you stop, report:

- 当前任务目录
- 本次执行的阶段
- 修改了哪些任务文件
- 是否修改了业务代码
- 当前 `phase` / `next_agent`
- 为什么停下来
- 用户下一步只需要输入哪一句话
