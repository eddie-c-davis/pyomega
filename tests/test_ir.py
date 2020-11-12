# tests/test_console.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import Parser
from pyomega.visit import CodeGenVisitor


def ast_test(expr):
    root = ast.parse(expr)
    assert isinstance(root, ast.Module)
    assert len(root.body) == 1
    assert isinstance(root.body[0], ast.Assign)


def parser_test(expr, name="s", iterators=("i", "j"), n_relations=2):
    space = Parser(expression=expr).parse()
    assert space.name == name
    assert len(space.iterators) == len(iterators)
    for n in range(len(iterators)):
        assert space.iterators[n].name == iterators[n]
    assert len(space.relations) == n_relations


def test_2d():
    expr = "s2d = {[i, j]: 0 <= i < N ^ 0 <= j < M}"
    ast_test(expr)
    parser_test(expr, "s2d")


def test_3d():
    expr = "s3d = {[i, j, k]: 0 <= i < N ^ 0 <= j < M ^ 0 <= k < K}"
    ast_test(expr)
    parser_test(expr, "s3d", ("i", "j", "k"), 3)


def test_spmv():
    expr = "spmv = {[i, n, j]: 0 <= i < N ^ rp(i) <= n < rp(i + 1) ^ j == col(n)}"
    ast_test(expr)
    parser_test(expr, "spmv", ("i", "n", "j"), 3)


# def test_krp():
#     expr = "krp = {[p, i, q, j, n, k, r]: 0 <= p < F ^ i==ind0(p) ^ pos0(p) <= q < pos0(p+1) ^ j==ind1(q) ^ pos1(q) <= n < pos1(q+1) ^ k==ind2(n) ^ 0 <= r < R}"
#     ast_test(expr)
#     parser_test(expr, "spmv", ("i", "n", "j"), 3)
