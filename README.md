# Architecture Diagram PPT

Generate simplified business, data, technical, and data-structure architecture diagrams as editable PowerPoint slides. The diagram is built from native PPT shapes and text boxes rather than an embedded screenshot.

## Location

`C:\Users\17842\Desktop\1\.codex\skills\architecture-diagram-ppt`

## Structure

```text
architecture-diagram-ppt/
|-- SKILL.md
|-- metadata.json
|-- agents/
|   `-- openai.yaml
|-- examples/
|   |-- example1.md
|   `-- example2.md
|-- scripts/
|   |-- main.py
|   |-- utils.py
|   `-- build_editable_architecture_ppt.mjs
|-- resources/
|   |-- prompt.md
|   |-- config.yaml
|   `-- editable-ppt-workflow.md
|-- tests/
|   |-- test_cases.md
|   `-- eval.yaml
|-- README.md
`-- CHANGELOG.md
```

`agents/openai.yaml` is retained because it provides the display name and short description used by Codex. It is intentionally outside the requested generic tree.

## Usage

1. Read `resources/prompt.md` to extract the source architecture into a compact specification.
2. Adapt the content arrays and positions in `scripts/build_editable_architecture_ppt.mjs` for the current diagram.
3. Run the Python wrapper to provide runtime paths and invoke the Node renderer:

```powershell
$python = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $python scripts/main.py `
  --workspace-dir "C:\work\project" `
  --output "C:\work\project\outputs\architecture.pptx"
```

The wrapper discovers the latest bundled Presentations skill and Codex runtime when their standard cache locations are present. Explicit paths can be supplied with:

- `--presentations-skill-dir`
- `--node`
- `--node-modules`
- `--runtime-python`
- `--runtime-bin-dir`
- `--font`

Equivalent environment variables are also supported: `WORKSPACE_DIR`, `PRESENTATIONS_SKILL_DIR`, `FINAL_PPTX`, `PPT_FONT`, `RUNTIME_NODE`, `RUNTIME_NODE_MODULES`, `RUNTIME_PYTHON`, and `RUNTIME_BIN_DIR`.

Use `--dry-run` to validate paths and print the command without generating a PPTX.

Write the PPTX to a workspace subdirectory such as `outputs\architecture.pptx`. The finalizer reserves the workspace root for private validation state.

## Verification

```powershell
$python = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $python -B -m py_compile scripts/main.py scripts/utils.py
node --check scripts/build_editable_architecture_ppt.mjs
& $python -B scripts/main.py --workspace-dir . --output outputs/check.pptx --dry-run
```

The generated slide should pass package integrity, layout geometry, font policy, and first-party import checks. For a pure shape diagram, inspect the package and confirm `ppt/media/` does not contain the main diagram.

On Windows, the bundled artifact-tool can occasionally return a native cleanup exit code after the PPTX, preview, and validation receipt have all been written successfully. The wrapper reports this explicitly as `recovered_after_renderer_cleanup_error: true` only when the fresh outputs and a passing validation receipt are present. Any earlier renderer failure still exits with an error.
