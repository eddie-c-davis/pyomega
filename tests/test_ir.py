# tests/test_console.py
import sys
import ast
import click.testing
import pytest

sys.path.append("./src")
from pyomega.parser import Parser


test_exprs = (
    "s0 = {[i, j]: 0 <= i < N ^ 0 <= j < M}",
    "s1 = {[i, j]: 0 <= i < N ^ 0 <= j < col(i)}",
)


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_ast(runner):
    for expr in test_exprs:
        root = ast.parse(expr)
        assert isinstance(root, ast.Module)
        assert len(root.body) == 1
        assert isinstance(root.body[0], ast.Assign)


def test_parser(runner):
    for expr in test_exprs:
        space = Parser(expression=expr).parse()
        assert space is not None