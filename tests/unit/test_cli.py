import subprocess
import sysconfig
from pathlib import Path


def test_installed_cli_starts() -> None:
    """Exercise the installed entry point from outside the source directory."""
    executable = Path(sysconfig.get_path("scripts")) / "sabermind"
    result = subprocess.run(
        [str(executable)],
        cwd=Path(sysconfig.get_path("scripts")),
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert result.stdout.strip() == "Hello from sabermind!"
    assert result.stderr == ""
