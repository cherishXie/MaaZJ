---
name: maazj-maafw-refactor
description: Use this skill for MaaZJ-specific MaaFramework resource refactors, ProjectInterface maintenance, pipeline analysis, Python agent integration checks, upstream alignment, or upgrade planning. Use when work touches `assets/interface.json`, `assets/resource/pipeline/`, MaaFramework/MFAAvalonia/MaaPracticeBoilerplate alignment, MaaHub references, or repository-specific MaaZJ automation context.
---

# MaaZJ MaaFramework Refactor Skill

Use this skill when a task needs MaaZJ-specific project knowledge beyond the root `AGENTS.md`.

Read only the references needed for the current task:

- Broad refactor, unfamiliar repository work, or project orientation: read `references/project-map.md`.
- Follow-up MaaZJ refactor, test automation, D4/D5/N1, or reusable task workflow work: read `references/refactor-workflow.md`.
- Pipeline work under `assets/resource/pipeline/`: read `references/pipeline-rules.md`.
- `assets/interface.json` maintenance, task entries, or `pipeline_override`: read `references/interface-rules.md`.
- MaaFramework, MFAAvalonia, MaaPracticeBoilerplate, or MaaHub alignment: read `references/upstream-alignment.md`.
- CI release, `deps/`, `install/`, artifact downloads, packaging, or runtime upgrades: read `references/upgrade-checklist.md`.

Always keep MaaZJ's runtime truth in mind:

- `assets/interface.json` is canonical for runtime and release behavior.
- Root `interface.json` is not canonical unless the task explicitly targets it.
- `assets/interface.json` must remain strict JSON.
- `assets/resource/pipeline/` may contain MaaFramework-compatible JSONC-like content and must not be strict-formatted blindly.

This skill is stored in the repository at `.codex/skills/maazj-maafw-refactor/` so future maintainers can reuse it with the project. It is not intended to be installed into the user's global Codex skills directory by default.
