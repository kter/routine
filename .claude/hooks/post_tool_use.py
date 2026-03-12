#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol


class CommandRunner(Protocol):
    def __call__(
        self,
        args: list[str],
        *,
        cwd: Path,
        text: bool,
        capture_output: bool,
    ) -> subprocess.CompletedProcess[str]: ...


def load_payload(stdin_text: str) -> dict[str, Any]:
    if not stdin_text.strip():
        return {}

    payload = json.loads(stdin_text)
    if not isinstance(payload, dict):
        raise ValueError("hook payload must be a JSON object")

    return payload


def extract_file_path(payload: Mapping[str, Any]) -> str | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, Mapping):
        return None

    file_path = tool_input.get("file_path")
    if isinstance(file_path, str) and file_path:
        return file_path

    return None


def determine_project_dir(
    payload: Mapping[str, Any],
    env: Mapping[str, str],
    script_path: Path,
) -> Path:
    project_dir = env.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir).resolve()

    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd).resolve()

    return script_path.resolve().parents[2]


def relative_repo_path(project_dir: Path, file_path: str) -> str | None:
    try:
        return Path(file_path).resolve().relative_to(project_dir.resolve()).as_posix()
    except ValueError:
        return None


def build_make_command(
    payload: Mapping[str, Any],
    env: Mapping[str, str],
    script_path: Path,
) -> tuple[Path, list[str]] | None:
    file_path = extract_file_path(payload)
    if not file_path:
        return None

    project_dir = determine_project_dir(payload, env, script_path)
    relative_path = relative_repo_path(project_dir, file_path)
    if not relative_path:
        return None

    return project_dir, ["make", "claude-post-edit", f"FILE={relative_path}"]


def run_post_tool_use(
    stdin_text: str,
    env: Mapping[str, str],
    script_path: Path,
    runner: CommandRunner,
) -> tuple[int, str | None]:
    try:
        payload = load_payload(stdin_text)
    except (json.JSONDecodeError, ValueError) as exc:
        return 1, f"claude hook: failed to parse PostToolUse payload: {exc}"

    command = build_make_command(payload, env, script_path)
    if command is None:
        return 0, None

    project_dir, args = command
    result = runner(args, cwd=project_dir, text=True, capture_output=True)
    if result.returncode == 0:
        return 0, None

    message = result.stderr.strip() or result.stdout.strip()
    if not message:
        message = f"claude hook: format/lint failed for {args[-1].split('=', 1)[1]}"

    return 2, message


def main() -> int:
    exit_code, message = run_post_tool_use(
        sys.stdin.read(),
        os.environ,
        Path(__file__),
        subprocess.run,
    )
    if message:
        print(message, file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
