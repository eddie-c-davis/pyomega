# tests/test_ir.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import CompParser, RelParser
from pyomega.visit import CodeGenVisitor


def ast_test(expr):
    root = ast.parse(expr)
    assert isinstance(root, ast.Module)
    assert len(root.body) > 0
    for statement in root.body:
        assert isinstance(statement, (ast.Assign, ast.AugAssign))


def parser_test(expr, name="s", iterators=("i", "j"), n_relations=2):
    # Assume 1st statement is relation, remaining are computations (for now)
    statements = expr.split("\n")
    space = RelParser(expression=statements[0]).parse()
    assert space.name == name
    assert tuple(space.iterators.keys()) == iterators
    assert len(space.relations) == n_relations

    for statement in statements[1:]:
        fields, tree = CompParser(space, expression=statement).parse()
        assert len(fields) > 0
        assert tree is not None


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


def test_spmv_coo():
    expr = "spmv = {[n, i, j]: 0 <= n < NNZ ^ i == row(n) ^ j == col(n)}"
    expr += "\ny[i] += A[n] * x[j]"
    ast_test(expr)
    parser_test(expr, "spmv", ("n", "i", "j"), 3)


def test_krp():
    # expr = "krp = {[p, i, q, j, n, k, r]: 0 <= p < F ^ i == ind0(p) ^ pos0(p) <= q < pos0(p+1) ^ j == ind1(q) ^ pos1(q) <= n < pos1(q+1) ^ k == ind2(n) ^ 0 <= r < R}"
    expr = "krp = {[n, i, j, k, r]: 0 <= n < M ^ i == ind0(n) ^ j == ind1(n) ^ k == ind2(n) ^ 0 <= r < R}"
    ast_test(expr)
    parser_test(expr, "krp", ("n", "i", "j", "k", "r"), 5)
