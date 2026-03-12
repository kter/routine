from __future__ import annotations

import importlib.util
from pathlib import Path
from subprocess import CompletedProcess

MODULE_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "stop.py"
SPEC = importlib.util.spec_from_file_location("claude_stop_hook", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_make_command_uses_project_dir_from_env(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    project_dir.mkdir()
    (project_dir / "Makefile").write_text(
        "agent-stop-unit-tests:\n\t@echo ok\n",
        encoding="utf-8",
    )

    command = MODULE.build_make_command({}, {"CLAUDE_PROJECT_DIR": str(project_dir)}, MODULE_PATH)

    assert command == (
        project_dir.resolve(),
        ["make", "agent-stop-unit-tests"],
    )


def test_run_stop_hook_blocks_stop_when_unit_tests_fail(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    project_dir.mkdir()
    (project_dir / "Makefile").write_text(
        "agent-stop-unit-tests:\n\t@echo ok\n",
        encoding="utf-8",
    )

    def runner(
        args: list[str],
        *,
        cwd: Path,
        text: bool,
        capture_output: bool,
    ) -> CompletedProcess[str]:
        assert args == ["make", "agent-stop-unit-tests"]
        assert cwd == project_dir.resolve()
        assert text is True
        assert capture_output is True
        return CompletedProcess(
            args=args,
            returncode=1,
            stdout="FAILED tests/unit/test_example.py::test_case\n1 failed, 9 passed",
            stderr="",
        )

    response = MODULE.run_stop_hook(
        "{}",
        {"CLAUDE_PROJECT_DIR": str(project_dir)},
        MODULE_PATH,
        runner,
    )

    assert response.exit_code == 0
    assert response.stdout_json == {
        "decision": "block",
        "reason": (
            "Unit tests failed in the Stop hook. Fix the failures before stopping.\n"
            "FAILED tests/unit/test_example.py::test_case\n"
            "1 failed, 9 passed"
        ),
    }
    assert response.stderr is None


def test_run_stop_hook_warns_instead_of_blocking_when_already_active(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    project_dir.mkdir()
    (project_dir / "Makefile").write_text(
        "agent-stop-unit-tests:\n\t@echo ok\n",
        encoding="utf-8",
    )

    def runner(
        args: list[str],
        *,
        cwd: Path,
        text: bool,
        capture_output: bool,
    ) -> CompletedProcess[str]:
        return CompletedProcess(
            args=args,
            returncode=1,
            stdout="1 failed, 9 passed",
            stderr="",
        )

    response = MODULE.run_stop_hook(
        '{"stop_hook_active": true}',
        {"CLAUDE_PROJECT_DIR": str(project_dir)},
        MODULE_PATH,
        runner,
    )

    assert response.exit_code == 0
    assert response.stdout_json == {
        "systemMessage": (
            "Stop hook reran unit tests and they are still failing. "
            "Allowing stop to avoid an infinite loop.\n"
            "1 failed, 9 passed"
        )
    }
    assert response.stderr is None


def test_run_stop_hook_allows_stop_when_unit_tests_pass(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    project_dir.mkdir()
    (project_dir / "Makefile").write_text(
        "agent-stop-unit-tests:\n\t@echo ok\n",
        encoding="utf-8",
    )

    response = MODULE.run_stop_hook(
        "{}",
        {"CLAUDE_PROJECT_DIR": str(project_dir)},
        MODULE_PATH,
        lambda *args, **kwargs: CompletedProcess(
            args=["make", "agent-stop-unit-tests"],
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    assert response.exit_code == 0
    assert response.stdout_json is None
    assert response.stderr is None


def test_build_make_command_walks_up_to_repo_root(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    nested_dir = project_dir / "backend"
    nested_dir.mkdir(parents=True)
    (project_dir / "Makefile").write_text(
        "agent-stop-unit-tests:\n\t@echo ok\n",
        encoding="utf-8",
    )

    command = MODULE.build_make_command({"cwd": str(nested_dir)}, {}, MODULE_PATH)

    assert command == (
        project_dir.resolve(),
        ["make", "agent-stop-unit-tests"],
    )


def test_build_make_command_skips_when_target_is_missing(tmp_path: Path) -> None:
    project_dir = tmp_path / "repo"
    project_dir.mkdir()
    (project_dir / "Makefile").write_text("test-unit:\n\t@echo ok\n", encoding="utf-8")

    command = MODULE.build_make_command({"cwd": str(project_dir)}, {}, MODULE_PATH)

    assert command is None
