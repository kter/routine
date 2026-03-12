from __future__ import annotations

import importlib.util
from pathlib import Path
from subprocess import CompletedProcess

MODULE_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "post_tool_use.py"
SPEC = importlib.util.spec_from_file_location("claude_post_tool_use_hook", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_make_command_uses_repo_relative_file_path(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    project_dir.mkdir()
    file_path = project_dir / "frontend" / "src" / "app.tsx"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("const x = 1;\n", encoding="utf-8")

    payload = {"tool_input": {"file_path": str(file_path)}}

    command = MODULE.build_make_command(
        payload,
        {"CLAUDE_PROJECT_DIR": str(project_dir)},
        MODULE_PATH,
    )

    assert command == (
        project_dir.resolve(),
        ["make", "claude-post-edit", "FILE=frontend/src/app.tsx"],
    )


def test_build_make_command_ignores_files_outside_project() -> None:
    payload = {"tool_input": {"file_path": "/tmp/outside.py"}}

    command = MODULE.build_make_command(
        payload,
        {"CLAUDE_PROJECT_DIR": "/work/repo"},
        MODULE_PATH,
    )

    assert command is None


def test_run_post_tool_use_returns_blocking_error_when_make_fails(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    project_dir.mkdir()
    file_path = project_dir / "backend" / "src" / "routineops" / "main.py"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("print('x')\n", encoding="utf-8")

    payload = f'{{"tool_input": {{"file_path": "{file_path}"}}}}'

    def runner(
        args: list[str],
        *,
        cwd: Path,
        text: bool,
        capture_output: bool,
    ) -> CompletedProcess[str]:
        assert args == ["make", "claude-post-edit", "FILE=backend/src/routineops/main.py"]
        assert cwd == project_dir.resolve()
        assert text is True
        assert capture_output is True
        return CompletedProcess(args=args, returncode=1, stdout="", stderr="lint failed")

    exit_code, message = MODULE.run_post_tool_use(
        payload,
        {"CLAUDE_PROJECT_DIR": str(project_dir)},
        MODULE_PATH,
        runner,
    )

    assert exit_code == 2
    assert message == "lint failed"


def test_run_post_tool_use_skips_payload_without_file_path() -> None:
    exit_code, message = MODULE.run_post_tool_use(
        '{"tool_input": {"content": "no file"}}',
        {},
        MODULE_PATH,
        lambda *args, **kwargs: CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    assert exit_code == 0
    assert message is None
