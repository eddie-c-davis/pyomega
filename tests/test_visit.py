# tests/test_console.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import Parser
from pyomega.visit import CodeGenVisitor


test_exprs = (
    "s0 = {[i, j]: 0 <= i < N ^ 0 <= j < M}",
    "s1 = {[i, j]: 0 <= i < N ^ rp(i) <= j < rp(i + 1)}",
)


def test_codegen():
    for expr in test_exprs:
        space = Parser(expression=expr).parse()
        visitor = CodeGenVisitor()
        source = visitor(space)
        assert source == expr