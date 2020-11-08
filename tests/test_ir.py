# tests/test_console.py
import click.testing
import pytest

from pyomega import console


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_ast(runner):
    s = {[i, j]: 0 <= i < N ^ 0 <= j < M}
    stop=1