#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shlex
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, NamedTuple

SHELL_SEPARATORS = {"&&", "||", ";", "|", "&"}
COMMAND_WRAPPERS = {"sudo", "command", "builtin", "nohup"}
SCRIPT_SHELLS = {"bash", "sh", "zsh"}
SCRIPT_FLAGS = {"-c", "-lc"}
MAKE_COMMANDS = {"make", "gmake"}


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


def extract_command(payload: Mapping[str, Any]) -> str | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, Mapping):
        return None

    command = tool_input.get("command")
    if isinstance(command, str) and command.strip():
        return command

    return None


def shell_split(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars="|&;")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def split_command_segments(tokens: list[str]) -> list[list[str]]:
    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in SHELL_SEPARATORS:
            if current:
                segments.append(current)
                current = []
            continue

        current.append(token)

    if current:
        segments.append(current)

    return segments


def strip_env_assignments(tokens: list[str]) -> list[str]:
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "env":
            index += 1
            while index < len(tokens) and is_env_assignment(tokens[index]):
                index += 1
            continue

        if is_env_assignment(token):
            index += 1
            continue

        break

    return tokens[index:]


def is_env_assignment(token: str) -> bool:
    if "=" not in token or token.startswith("="):
        return False

    name = token.split("=", 1)[0]
    return bool(name) and name.replace("_", "").isalnum()


def normalize_segment(tokens: list[str]) -> list[str]:
    normalized = strip_env_assignments(tokens)

    while normalized and normalized[0] in COMMAND_WRAPPERS:
        normalized = normalized[1:]

    if not normalized:
        return []

    if normalized[0] in SCRIPT_SHELLS:
        for index, token in enumerate(normalized[1:], start=1):
            if token in SCRIPT_FLAGS and index + 1 < len(normalized):
                return shell_split(normalized[index + 1])

    return normalized


def token_basename(token: str) -> str:
    return Path(token).name


def blocks_rm_rf(tokens: list[str]) -> bool:
    if not tokens or token_basename(tokens[0]) != "rm":
        return False

    recursive = False
    force = False
    for token in tokens[1:]:
        if token == "--":
            break
        if not token.startswith("-") or token == "-":
            break

        if token.startswith("--"):
            if token == "--recursive":
                recursive = True
            if token == "--force":
                force = True
            continue

        for flag in token[1:]:
            if flag in {"r", "R"}:
                recursive = True
            if flag == "f":
                force = True

    return recursive and force


def blocks_terraform_destroy(tokens: list[str]) -> bool:
    if not tokens or token_basename(tokens[0]) != "terraform":
        return False

    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "-chdir":
            index += 2
            continue
        if token.startswith("-chdir="):
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue

        return token == "destroy"

    return False


def blocks_make_tf_destroy(tokens: list[str]) -> bool:
    if not tokens or token_basename(tokens[0]) not in MAKE_COMMANDS:
        return False

    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in {"-C", "-f"}:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        if is_env_assignment(token):
            index += 1
            continue
        if token == "tf-destroy":
            return True
        index += 1

    return False


def find_block_reason(command: str) -> str | None:
    try:
        segments = split_command_segments(shell_split(command))
    except ValueError:
        compact = " ".join(command.split())
        if "terraform destroy" in compact:
            return "Blocked destructive command: terraform destroy"
        if "rm -rf" in compact or "rm -fr" in compact:
            return "Blocked destructive command: rm -rf"
        return None

    for segment in segments:
        normalized = normalize_segment(segment)
        if not normalized:
            continue

        if normalized != segment:
            nested_reason = find_block_reason(" ".join(normalized))
            if nested_reason is not None:
                return nested_reason

        if blocks_rm_rf(normalized):
            return "Blocked destructive command: rm -rf"
        if blocks_terraform_destroy(normalized):
            return "Blocked destructive command: terraform destroy"
        if blocks_make_tf_destroy(normalized):
            return "Blocked destructive command: make tf-destroy"

    return None


def build_deny_response(reason: str) -> HookResponse:
    return HookResponse(
        exit_code=0,
        stdout_json={
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"{reason}. Run it manually outside Claude Code if you really intend to do it."
                ),
            }
        },
    )


def run_pre_tool_use(stdin_text: str) -> HookResponse:
    try:
        payload = load_payload(stdin_text)
    except (json.JSONDecodeError, ValueError) as exc:
        return HookResponse(
            exit_code=1,
            stderr=f"claude hook: failed to parse PreToolUse payload: {exc}",
        )

    command = extract_command(payload)
    if not command:
        return HookResponse(exit_code=0)

    reason = find_block_reason(command)
    if reason is None:
        return HookResponse(exit_code=0)

    return build_deny_response(reason)


def main() -> int:
    response = run_pre_tool_use(sys.stdin.read())
    if response.stdout_json is not None:
        print(json.dumps(response.stdout_json))
    if response.stderr:
        print(response.stderr, file=sys.stderr)
    return response.exit_code


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
