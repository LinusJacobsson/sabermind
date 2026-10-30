import pytest

from sabermind import main


def test_main_prints_startup_message(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    output = capsys.readouterr()
    assert output.out == "Hello from sabermind!\n"
    assert output.err == ""
