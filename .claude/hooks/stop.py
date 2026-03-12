#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, NamedTuple, Protocol

MAX_SUMMARY_CHARS = 2000
SUMMARY_LINE_COUNT = 20
RELEVANT_CHANGE_PREFIXES = (
    "backend/",
    "tests/",
    ".claude/hooks/",
)
RELEVANT_CHANGE_PATHS = {
    "Makefile",
    ".claude/settings.json",
    ".codex/hooks.json",
}


class CommandRunner(Protocol):
    def __call__(
        self,
        args: list[str],
        *,
        cwd: Path,
        text: bool,
        capture_output: bool,
    ) -> subprocess.CompletedProcess[str]: ...


class HookResponse(NamedTuple):
    exit_code: int
    stdout_json: dict[str, Any] | None = None
    stderr: str | None = None


def load_payload(stdin_text: str) -> dict[str, Any]:
    if not stdin_text.strip():
        return {}

    payload = json.loads(stdin_text)
    if not isinstance(payload, dict):
        raise ValueError("hook payload must be a JSON object")

    return payload


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


def find_project_dir_with_target(start_dir: Path) -> Path | None:
    current = start_dir.resolve()
    for directory in (current, *current.parents):
        makefile = directory / "Makefile"
        if not makefile.is_file():
            continue

        if "agent-stop-unit-tests:" in makefile.read_text(encoding="utf-8"):
            return directory

    return None


def build_make_command(
    payload: Mapping[str, Any],
    env: Mapping[str, str],
    script_path: Path,
) -> tuple[Path, list[str]] | None:
    base_dir = determine_project_dir(payload, env, script_path)
    project_dir = find_project_dir_with_target(base_dir)
    if project_dir is None:
        return None

    return project_dir, ["make", "agent-stop-unit-tests"]


def parse_changed_file(status_line: str) -> str | None:
    if len(status_line) < 4:
        return None

    changed_file = status_line[3:].strip()
    if not changed_file:
        return None

    if " -> " in changed_file:
        return changed_file.split(" -> ", maxsplit=1)[1].strip() or None

    return changed_file


def list_changed_files(
    project_dir: Path,
    runner: CommandRunner,
) -> set[str] | None:
    result = runner(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=project_dir,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None

    return {
        changed_file
        for line in result.stdout.splitlines()
        if (changed_file := parse_changed_file(line)) is not None
    }


def should_run_unit_tests(
    project_dir: Path,
    runner: CommandRunner,
) -> bool:
    changed_files = list_changed_files(project_dir, runner)
    if changed_files is None:
        return True

    return any(
        changed_file in RELEVANT_CHANGE_PATHS or changed_file.startswith(RELEVANT_CHANGE_PREFIXES)
        for changed_file in changed_files
    )


def summarize_test_output(result: subprocess.CompletedProcess[str]) -> str:
    combined_output = "\n".join(
        part.strip()
        for part in (result.stdout, result.stderr)
        if isinstance(part, str) and part.strip()
    ).strip()
    if not combined_output:
        return "Unit tests failed with no output."

    summary = "\n".join(combined_output.splitlines()[-SUMMARY_LINE_COUNT:])
    if len(summary) <= MAX_SUMMARY_CHARS:
        return summary

    return summary[-MAX_SUMMARY_CHARS:]


def build_failure_response(
    payload: Mapping[str, Any],
    summary: str,
) -> HookResponse:
    if payload.get("stop_hook_active") is True:
        return HookResponse(
            exit_code=0,
            stdout_json={
                "systemMessage": (
                    "Stop hook reran unit tests and they are still failing. "
                    "Allowing stop to avoid an infinite loop.\n"
                    f"{summary}"
                )
            },
        )

    return HookResponse(
        exit_code=0,
        stdout_json={
            "decision": "block",
            "reason": (
                f"Unit tests failed in the Stop hook. Fix the failures before stopping.\n{summary}"
            ),
        },
    )


def run_stop_hook(
    stdin_text: str,
    env: Mapping[str, str],
    script_path: Path,
    runner: CommandRunner,
) -> HookResponse:
    try:
        payload = load_payload(stdin_text)
    except (json.JSONDecodeError, ValueError) as exc:
        return HookResponse(
            exit_code=1,
            stderr=f"claude hook: failed to parse Stop payload: {exc}",
        )

    command = build_make_command(payload, env, script_path)
    if command is None:
        return HookResponse(exit_code=0)

    project_dir, args = command
    if not should_run_unit_tests(project_dir, runner):
        return HookResponse(exit_code=0)

    result = runner(args, cwd=project_dir, text=True, capture_output=True)
    if result.returncode == 0:
        return HookResponse(exit_code=0)

    return build_failure_response(payload, summarize_test_output(result))


def main() -> int:
    response = run_stop_hook(
        sys.stdin.read(),
        os.environ,
        Path(__file__),
        subprocess.run,
    )
    if response.stdout_json is not None:
        print(json.dumps(response.stdout_json))
    if response.stderr:
        print(response.stderr, file=sys.stderr)
    return response.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
