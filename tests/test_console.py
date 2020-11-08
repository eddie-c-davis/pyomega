# tests/test_console.py
import click.testing
import pytest

from pyomega import console


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_main_succeeds(runner):
    assert runner.invoke(console.main).exit_code == 0