# tests/test_console.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import Parser


test_exprs = (
    "s0 = {[i, j]: 0 <= i < N ^ 0 <= j < M}",
    "s1 = {[i, j]: 0 <= i < N ^ rp(i) <= j < rp(i + 1)}",
)


def test_ast():
    for expr in test_exprs:
        root = ast.parse(expr)
        assert isinstance(root, ast.Module)
        assert len(root.body) == 1
        assert isinstance(root.body[0], ast.Assign)


def test_parser():
    for expr in test_exprs:
        space = Parser(expression=expr).parse()
        assert space.name[0] == "s"
        assert space.iterators[0].name == "i"
        assert space.iterators[1].name == "j"
        assert len(space.relations) == 2
