# Refactor Workflow

Use this reference for MaaZJ follow-up refactor, test automation, D4/D5/N1, and reusable task workflow work.

## Canonical Design Entry

Use `docs/agent_design/refactor_design_maafw_test_automation_2026-06-07.md` as the current task-splitting and feedback-loop design for MaaFramework adaptation work.

That design document guides:

- R/C/T/D/N task selection.
- single-task Runbook boundaries.
- expected artifacts and minimum formats.
- V0-V5 validation layering.
- D4/D5/N1 feedback decisions.

It does not replace runtime truth. Runtime and release behavior still come from `assets/interface.json`, with pipeline behavior in `assets/resource/pipeline/` and image resources in `assets/resource/image/`.

## Reusable Task Check Order

For follow-up MaaZJ refactor tasks:

1. Confirm the task type against the design document matrix.
2. Read `AGENTS.md` and the required skill references for the touched area.
3. Identify consumed artifacts and whether they are stale, missing fields, or inconsistent with runtime files.
4. Keep allowed and forbidden paths explicit in the task plan.
5. Apply the minimum validation layer required by the task.
6. Before review, test, or final, answer whether D4, D5, or N1 is needed.

## D4/D5/N1 Decisions

Use D4-design-feedback-sync when the design document has inaccurate fields, boundaries, Runbook steps, validation rules, or reusable prompts.

Use D5-agents-skill-sync when a stable rule needs to be reflected in `AGENTS.md` or this project skill, especially repository-level safety boundaries, canonical source rules, validation minimums, directory indexes, reusable workflow steps, or MaaZJ-specific check order.

Use N1-new-requirement-triage when a new user requirement is outside the current task boundary and needs classification, risk grading, validation selection, and follow-up task prompts.

Do not write one-off task logs, temporary guesses, or unverified exploration findings into `AGENTS.md` or the project skill. Keep those in `.agent/tasks/<task-id>/` or a design feedback record.

## Validation Layers

- V0: static file checks such as strict JSON, JSONC-aware references, and file existence.
- V1: MaaFramework resource load, usually `python .\check_resource.py .\assets\resource\`.
- V2: task entry startup through `Tasker.post_task(...)` or MFAAvalonia.
- V3: real controller flow reaching expected key nodes or terminal states.
- V4: reproducible evidence such as logs, screenshots, recordings, debug records, or manual observation notes.
- V5: regression matrix across multiple important flows.

For documentation-only, AGENTS-only, or skill-only work, resource validation can be skipped with a recorded reason. For resource changes, V1 is the minimum. For code or pipeline refactor completion, record V2/V3/V4 results or a degraded verification record with the reason, residual risk, and follow-up validation conditions.
