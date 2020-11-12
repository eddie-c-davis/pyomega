# tests/test_console.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import Parser


test_exprs = (
    "s0 = {[i, j]: 0 <= i < N ^ 0 <= j < M}",
    "s1 = {[i, j]: 0 <= i < N ^ rp(i) <= j < rp(i + 1)}",
    "s2 = {[i, j, k]: 0 <= i < N ^ 0 <= j < M ^ 0 <= k < K}",
    # MTTKRP:
    # Space csf("Icsf", 0 <= p < F ^ i==ind0(p) ^ pos0(p) <= q < pos0(p+1) ^ j==ind1(q) ^
    #                   pos1(q) <= n < pos1(q+1) ^ k==ind2(n) ^ 0 <= r < R);
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
        if len(space.iterators) > 2:
            assert space.iterators[2].name == "k"
            assert len(space.relations) == 3
        else:
            assert len(space.relations) == 2
