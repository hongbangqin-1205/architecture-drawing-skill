#!/usr/bin/env python3
"""CLI wrapper for the editable architecture PPT renderer."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from utils import (
    SkillRuntimeError,
    build_renderer_env,
    count_pptx_media,
    discover_node,
    discover_node_modules,
    discover_presentations_skill,
    discover_runtime_bin_dir,
    discover_runtime_python,
    require_file,
    resolve_path,
    run_process,
)


SCRIPT_DIR = Path(__file__).resolve().parent
RENDERER_PATH = SCRIPT_DIR / "build_editable_architecture_ppt.mjs"


def validate_receipt(receipt_path: Path, started_ns: int) -> dict:
    receipt_path = require_file(receipt_path, "Validation receipt")
    if receipt_path.stat().st_mtime_ns < started_ns:
        raise SkillRuntimeError(f"Validation receipt is stale: {receipt_path}")
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    integrity = payload.get("packageIntegrity", {})
    layout = payload.get("presentationLayout", {})
    first_party = payload.get("firstPartyImport", {})
    if integrity.get("status") != "pass":
        raise SkillRuntimeError("PPTX package integrity validation did not pass.")
    if layout.get("finding_count") not in (0, None):
        raise SkillRuntimeError("PPTX layout geometry validation reported findings.")
    if first_party.get("passed") is not True:
        raise SkillRuntimeError("First-party artifact-tool import validation did not pass.")
    return payload


def recover_renderer_exit(
    *,
    exit_code: int,
    final_pptx: Path,
    preview_path: Path,
    receipt_path: Path,
    started_ns: int,
) -> bool:
    if exit_code == 0:
        return False
    try:
        require_file(final_pptx, "Generated PPTX")
        require_file(preview_path, "Generated preview")
        if final_pptx.stat().st_mtime_ns < started_ns or preview_path.stat().st_mtime_ns < started_ns:
            return False
        validate_receipt(receipt_path, started_ns)
    except (SkillRuntimeError, OSError, json.JSONDecodeError):
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an editable architecture diagram PPTX using native PPT shapes."
    )
    parser.add_argument(
        "--workspace-dir",
        default=os.environ.get("WORKSPACE_DIR", os.getcwd()),
        help="Workspace directory used for staging and finalizer state.",
    )
    parser.add_argument(
        "--output",
        default=os.environ.get("FINAL_PPTX"),
        help="Final PPTX path. Also accepted through FINAL_PPTX.",
    )
    parser.add_argument("--presentations-skill-dir", default=None)
    parser.add_argument("--node", default=None, help="Node.js executable.")
    parser.add_argument("--node-modules", default=None, help="Runtime node_modules directory.")
    parser.add_argument("--runtime-python", default=None, help="Python executable used by the finalizer.")
    parser.add_argument("--runtime-bin-dir", default=None, help="Runtime bin/override directory.")
    parser.add_argument(
        "--font",
        default=os.environ.get("PPT_FONT", "Microsoft YaHei"),
        help="Font family used for the slide.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate runtime paths and print the renderer invocation without generating files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.output:
        raise SkillRuntimeError("Pass --output or set FINAL_PPTX.")

    workspace_dir = resolve_path(args.workspace_dir)
    if not workspace_dir.is_dir():
        raise SkillRuntimeError(f"Workspace directory is not a directory: {workspace_dir}")

    final_pptx = resolve_path(args.output)
    if final_pptx.parent == workspace_dir:
        raise SkillRuntimeError(
            "Output must be written to a subdirectory of the workspace, such as "
            f"{workspace_dir / 'outputs' / final_pptx.name}."
        )
    renderer = require_file(RENDERER_PATH, "Node renderer")
    presentations_skill_dir = discover_presentations_skill(args.presentations_skill_dir)
    runtime_node = discover_node(args.node)
    runtime_node_modules = discover_node_modules(args.node_modules)
    runtime_python = discover_runtime_python(args.runtime_python)
    runtime_bin_dir = discover_runtime_bin_dir(args.runtime_bin_dir)

    env = build_renderer_env(
        workspace_dir=workspace_dir,
        presentations_skill_dir=presentations_skill_dir,
        final_pptx=final_pptx,
        runtime_python=runtime_python,
        runtime_node=runtime_node,
        runtime_node_modules=runtime_node_modules,
        runtime_bin_dir=runtime_bin_dir,
        font=args.font,
    )
    command = [runtime_node, str(renderer)]

    summary = {
        "workspace_dir": str(workspace_dir),
        "output": str(final_pptx),
        "presentations_skill_dir": str(presentations_skill_dir),
        "runtime_node": runtime_node,
        "runtime_node_modules": str(runtime_node_modules),
        "runtime_python": str(runtime_python),
        "runtime_bin_dir": str(runtime_bin_dir) if runtime_bin_dir else None,
        "font": args.font,
        "command": command,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    final_pptx.parent.mkdir(parents=True, exist_ok=True)
    started_ns = time.time_ns()
    renderer_exit_code = run_process(command, env, workspace_dir)
    media_count = count_pptx_media(final_pptx)
    preview = final_pptx.with_name(f"{final_pptx.stem}-preview.png")
    receipt = workspace_dir / ".codex-finalizer" / "editable-architecture.validation.json"
    recovered = recover_renderer_exit(
        exit_code=renderer_exit_code,
        final_pptx=final_pptx,
        preview_path=preview,
        receipt_path=receipt,
        started_ns=started_ns,
    )
    if renderer_exit_code != 0 and not recovered:
        raise SkillRuntimeError(
            f"Renderer failed with exit code {renderer_exit_code}: {' '.join(command)}"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "renderer_exit_code": renderer_exit_code,
                "recovered_after_renderer_cleanup_error": recovered,
                "pptx": str(final_pptx),
                "preview": str(preview) if preview.is_file() else None,
                "ppt_media_count": media_count,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SkillRuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
