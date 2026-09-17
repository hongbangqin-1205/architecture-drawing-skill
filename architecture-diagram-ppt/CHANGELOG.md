# Changelog

## 1.1.0 - 2026-09-16

- Normalized the skill into the requested standard directory structure.
- Added `metadata.json`, `examples/`, `resources/`, and `tests/`.
- Added a Python command wrapper at `scripts/main.py` and shared helpers at `scripts/utils.py`.
- Moved the detailed editable-PPT workflow into `resources/editable-ppt-workflow.md`.
- Kept the validated native-shape Node renderer instead of replacing it with a less capable implementation.
- Added runtime path discovery, dry-run validation, and PPTX media inspection support.
- Added safe recovery for Windows artifact-tool cleanup exits only when fresh PPTX, preview, and passing validation receipt outputs are present.

## 1.0.0

- Initial editable architecture diagram PPT skill.
