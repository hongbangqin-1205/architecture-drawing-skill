"""Shared runtime and validation helpers for the architecture PPT skill."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence
from zipfile import BadZipFile, ZipFile


class SkillRuntimeError(RuntimeError):
    """Raised when the local runtime cannot satisfy the renderer requirements."""


def resolve_path(value: str | os.PathLike[str]) -> Path:
    return Path(value).expanduser().resolve()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise SkillRuntimeError(f"{label} is not a file: {path}")
    return path


def require_dir(path: Path, label: str) -> Path:
    if not path.is_dir():
        raise SkillRuntimeError(f"{label} is not a directory: {path}")
    return path


def first_existing_dir(candidates: Sequence[Path], label: str) -> Path:
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    rendered = "\n".join(f"  - {candidate}" for candidate in candidates)
    raise SkillRuntimeError(f"Could not locate {label}. Checked:\n{rendered}")


def discover_presentations_skill(explicit: str | None = None) -> Path:
    if explicit:
        return require_dir(resolve_path(explicit), "Presentations skill directory")

    env_value = os.environ.get("PRESENTATIONS_SKILL_DIR")
    if env_value:
        return require_dir(resolve_path(env_value), "Presentations skill directory")

    codex_home = resolve_path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    root = codex_home / "plugins" / "cache"
    candidates: list[Path] = []
    if root.is_dir():
        patterns = (
            "openai-primary-runtime/presentations/*/skills/presentations",
            "openai-bundled/presentations/*/skills/presentations",
            "*/presentations/*/skills/presentations",
        )
        for pattern in patterns:
            candidates.extend(path for path in root.glob(pattern) if path.is_dir())

    candidates = sorted(set(candidates), key=lambda path: path.as_posix(), reverse=True)
    for candidate in candidates:
        if (candidate / "container_tools" / "artifact_tool_utils.mjs").is_file():
            return candidate.resolve()

    raise SkillRuntimeError(
        "Could not discover the Presentations skill. Pass --presentations-skill-dir "
        "or set PRESENTATIONS_SKILL_DIR."
    )


def discover_node_modules(explicit: str | None = None) -> Path:
    if explicit:
        return require_dir(resolve_path(explicit), "Node modules directory")

    env_value = os.environ.get("RUNTIME_NODE_MODULES")
    if env_value:
        return require_dir(resolve_path(env_value), "Node modules directory")

    dependency_root = resolve_path(
        os.environ.get(
            "CODEX_PRIMARY_RUNTIME_ROOT",
            Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies",
        )
    )
    return first_existing_dir(
        [
            dependency_root / "node" / "node_modules",
            dependency_root / "node_modules",
        ],
        "Codex Node modules",
    )


def discover_runtime_python(explicit: str | None = None) -> Path:
    if explicit:
        return require_file(resolve_path(explicit), "Runtime Python executable")

    env_value = os.environ.get("RUNTIME_PYTHON")
    if env_value:
        return require_file(resolve_path(env_value), "Runtime Python executable")

    dependency_root = resolve_path(
        os.environ.get(
            "CODEX_PRIMARY_RUNTIME_ROOT",
            Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies",
        )
    )
    candidates = [
        dependency_root / "python" / "python.exe",
        dependency_root / "python" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    python_on_path = shutil.which("python") or shutil.which("python3")
    if python_on_path:
        return resolve_path(python_on_path)
    return resolve_path(sys.executable)


def discover_node(explicit: str | None = None) -> str:
    value = explicit or os.environ.get("RUNTIME_NODE")
    if value:
        path = resolve_path(value)
        return str(require_file(path, "Node executable"))

    dependency_root = resolve_path(
        os.environ.get(
            "CODEX_PRIMARY_RUNTIME_ROOT",
            Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies",
        )
    )
    bundled_candidates = [
        dependency_root / "node" / "bin" / "node.exe",
        dependency_root / "node" / "bin" / "node",
    ]
    for candidate in bundled_candidates:
        if candidate.is_file():
            return str(candidate.resolve())

    node_on_path = shutil.which("node")
    if not node_on_path:
        raise SkillRuntimeError("Could not find Node.js. Pass --node or set RUNTIME_NODE.")
    return node_on_path


def discover_runtime_bin_dir(explicit: str | None = None) -> Path | None:
    value = explicit or os.environ.get("RUNTIME_BIN_DIR")
    if value:
        return require_dir(resolve_path(value), "Runtime bin directory")

    dependency_root = resolve_path(
        os.environ.get(
            "CODEX_PRIMARY_RUNTIME_ROOT",
            Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies",
        )
    )
    candidates = [
        dependency_root / "bin" / "override",
        dependency_root / "bin" / "fallback",
    ]
    return next((path.resolve() for path in candidates if path.is_dir()), None)


def build_renderer_env(
    *,
    workspace_dir: Path,
    presentations_skill_dir: Path,
    final_pptx: Path,
    runtime_python: Path,
    runtime_node: str,
    runtime_node_modules: Path,
    runtime_bin_dir: Path | None,
    font: str,
) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "WORKSPACE_DIR": str(workspace_dir),
            "PRESENTATIONS_SKILL_DIR": str(presentations_skill_dir),
            "FINAL_PPTX": str(final_pptx),
            "RUNTIME_PYTHON": str(runtime_python),
            "RUNTIME_NODE": runtime_node,
            "RUNTIME_NODE_MODULES": str(runtime_node_modules),
            "PPT_FONT": font,
        }
    )
    if runtime_bin_dir is not None:
        env["RUNTIME_BIN_DIR"] = str(runtime_bin_dir)
    return env


def run_process(command: Sequence[str], env: Mapping[str, str], cwd: Path) -> int:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd),
        env=dict(env),
        check=False,
        text=True,
    )
    return completed.returncode


def count_pptx_media(pptx_path: Path) -> int:
    require_file(pptx_path, "Generated PPTX")
    try:
        with ZipFile(pptx_path) as package:
            return sum(
                name.startswith("ppt/media/") and not name.endswith("/")
                for name in package.namelist()
            )
    except BadZipFile as exc:
        raise SkillRuntimeError(f"Generated PPTX is not a valid ZIP package: {pptx_path}") from exc
