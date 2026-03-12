from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pre_tool_use.py"
SPEC = importlib.util.spec_from_file_location("claude_pre_tool_use_hook", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_run_pre_tool_use_blocks_rm_rf() -> None:
    response = MODULE.run_pre_tool_use('{"tool_input": {"command": "rm -rf /tmp/build"}}')

    assert response.exit_code == 0
    assert response.stdout_json == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked destructive command: rm -rf. "
                "Run it manually outside Claude Code if you really intend to do it."
            ),
        }
    }
    assert response.stderr is None


def test_run_pre_tool_use_blocks_terraform_destroy_with_chdir() -> None:
    response = MODULE.run_pre_tool_use(
        '{"tool_input": {"command": "terraform -chdir=infra destroy"}}'
    )

    assert response.exit_code == 0
    assert response.stdout_json == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked destructive command: terraform destroy. "
                "Run it manually outside Claude Code if you really intend to do it."
            ),
        }
    }
    assert response.stderr is None


def test_run_pre_tool_use_blocks_make_tf_destroy_with_assignments() -> None:
    response = MODULE.run_pre_tool_use('{"tool_input": {"command": "make ENV=dev tf-destroy"}}')

    assert response.exit_code == 0
    assert response.stdout_json == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked destructive command: make tf-destroy. "
                "Run it manually outside Claude Code if you really intend to do it."
            ),
        }
    }
    assert response.stderr is None


def test_run_pre_tool_use_blocks_nested_shell_script() -> None:
    response = MODULE.run_pre_tool_use(
        '{"tool_input": {"command": "bash -lc \\"cd infra && terraform destroy\\""}}'
    )

    assert response.exit_code == 0
    assert response.stdout_json == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked destructive command: terraform destroy. "
                "Run it manually outside Claude Code if you really intend to do it."
            ),
        }
    }
    assert response.stderr is None


def test_run_pre_tool_use_allows_non_destructive_commands() -> None:
    response = MODULE.run_pre_tool_use(
        '{"tool_input": {"command": "terraform plan -out=dev.tfplan"}}'
    )

    assert response.exit_code == 0
    assert response.stdout_json is None
    assert response.stderr is None


def test_run_pre_tool_use_skips_payload_without_command() -> None:
    response = MODULE.run_pre_tool_use('{"tool_input": {"file_path": "README.md"}}')

    assert response.exit_code == 0
    assert response.stdout_json is None
    assert response.stderr is None
