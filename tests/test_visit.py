# tests/test_console.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import Parser
from pyomega.visit import CodeGenVisitor


def codegen_test(expr):
    space = Parser(expression=expr).parse()
    visitor = CodeGenVisitor()
    source = visitor(space)
    assert source == expr


def test_2d():
    expr = "s2d = {[i, j]: 0 <= i < N ^ 0 <= j < M}"
    codegen_test(expr)


def test_3d():
    expr = "s3d = {[i, j, k]: 0 <= i < N ^ 0 <= j < M ^ 0 <= k < K}"
    codegen_test(expr)


def test_spmv():
    expr = "spmv = {[i, n, j]: 0 <= i < N ^ rp(i) <= n < rp(i + 1) ^ j == col(n)}"
    codegen_test(expr)


def test_krp():
    expr = "krp = {[n, i, j, k, r]: 0 <= n < M ^ i == ind0(n) ^ j == ind1(n) ^ k == ind2(n) ^ 0 <= r < R}"
    # expr = "krp = {[p, i, q, j, n, k, r]: 0 <= p < F ^ i == ind0(p) ^ pos0(p) <= q < pos0(p+1) ^ j == ind1(q) ^ pos1(q) <= n < pos1(q+1) ^ k == ind2(n) ^ 0 <= r < R}"
    codegen_test(expr)