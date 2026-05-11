# Generated Harness Files

Use this reference when deciding what the initializer creates for each profile.

## Profiles

### `minimal`

Creates the thin core:

- `AGENTS.md`
- `PLANS.md`
- `QUALITY_SCORE.md`
- `RELIABILITY.md`
- `docs/exec-plans/{active,completed}/`
- `docs/validation/`
- `docs/runbooks/`
- `docs/generated/`

### `standard`

Creates the core plus:

- `ARCHITECTURE.md`
- `DELIVERY.md`
- `DESIGN.md`
- `PRODUCT_SENSE.md`
- `SECURITY.md`

Conditionally adds:

- `FRONTEND.md` when the repo clearly signals a frontend surface
- `BACKEND.md` when the repo clearly signals a backend surface
- `AUTONOMY.md` when `--include-autonomy` is requested

Also includes ops-oriented templates such as runbooks, validation templates, incidents, ADRs, and core beliefs.

When autonomy is enabled, also adds:

- `docs/runbooks/autonomous-operations.md`
- `docs/validation/autonomy-drill-template.md`

### `full`

Creates the full current scaffold surface, including frontend and backend docs regardless of detection.

## Managed Document Rules

- Generated markdown docs contain a harness marker header.
- Existing managed docs may receive missing managed sections when the same marker is already present.
- Arbitrary user-authored docs are preserved and never appended into unless the user explicitly asks to overwrite.
- Agent-specific adapter files may also be generated, such as `CLAUDE.md` for Claude Code or `.codex/skills/...` for Codex.

## Manifest

`docs/generated/harness-manifest.json` is the machine-readable source of truth for:

- selected `profile`
- `enabled_surfaces`
- `autonomy`
- `agents_map_max_lines`
- `required_commands`
- `doc_gardening_required`
- trajectory metadata and managed files
