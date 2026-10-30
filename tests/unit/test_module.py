import runpy

import pytest


def test_module_entry_point(capsys: pytest.CaptureFixture[str]) -> None:
    """Use the same module entry point as the VS Code launch configuration."""
    runpy.run_module("sabermind", run_name="__main__")
    output = capsys.readouterr()
    assert output.out == "Hello from sabermind!\n"
    assert output.err == ""
