# Upstream Alignment

## Principle

MaaZJ should gradually align with current MaaFramework ecosystem practices, but business resources must not be overwritten by templates or community examples.

Historical observations in repository documents can become stale. Before implementation that depends on versions, release dates, artifact names, API support, or template structure, re-check the current official upstream state.

## Upstreams To Re-check

- `MaaXYZ/MaaFramework`
- `MaaXYZ/MFAAvalonia`
- `MaaXYZ/MaaPracticeBoilerplate`
- `MaaXYZ/MaaHub`

## MaaFramework

Before upgrading or changing resource semantics, confirm:

- latest stable release;
- runtime artifact names;
- resource loading behavior;
- pipeline protocol;
- `recognition` and `action` fields;
- custom action/custom recognition API;
- Python agent runtime requirements.

## MFAAvalonia

Before changing ProjectInterface behavior or release workflow, confirm:

- latest stable release;
- artifact naming;
- supported ProjectInterface fields;
- task display and task configuration capabilities;
- controller/resource/agent configuration behavior.

Prefer `MaaXYZ/MFAAvalonia` as the target upstream unless the user explicitly requests another source.

## MaaPracticeBoilerplate

Use MaaPracticeBoilerplate as a template-structure reference, not as a source to overwrite MaaZJ business resources.

Confirm current:

- directory layout;
- CI patterns;
- install/configure scripts;
- README conventions;
- resource organization.

Adopt only patterns that fit MaaZJ.

## MaaHub

Use MaaHub as a reference for skill, pipeline, custom, and experience organization.

Do not treat MaaHub samples as MaaZJ business implementation. Before adopting an idea, check:

- MaaFramework version used by the sample;
- whether the sample flow matches MaaZJ's game flow;
- whether resource names, images, OCR text, and ROI are applicable;
- whether current MaaZJ validation still passes.

## Documentation Rule

When recording upstream facts, include the check date. If the fact could change, phrase implementation plans as requiring re-confirmation rather than relying on a stale snapshot.
