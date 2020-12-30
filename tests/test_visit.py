# tests/test_visit.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import RelParser
from pyomega.visit import ASTVisitor, CodeGenVisitor


def codegen_test(expr, code):
    space = RelParser(expression=expr).parse()
    visitor = CodeGenVisitor()
    source = visitor(space)
    assert source == code

    visitor = ASTVisitor()
    ast = visitor(source)
    assert ast is not None


def test_2d():
    expr = "s2d = {[i, j]: 0 <= i < N ^ 0 <= j < M}"
    code = "void s2d(int N, int M) {\n  int t2, t4;\nfor(t2 = 0; t2 <= N-1; t2++) {\n  for(t4 = 0; t4 <= M-1; t4++) {\n    s0(t2,t4);\n  }\n}\n}"
    codegen_test(expr, code)


def test_3d():
    expr = "s3d = {[i, j, k]: 0 <= i < N ^ 0 <= j < M ^ 0 <= k < K}"
    code = "void s3d(int N, int M, int K) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= N-1; t2++) {\n  for(t4 = 0; t4 <= M-1; t4++) {\n    for(t6 = 0; t6 <= K-1; t6++) {\n      s0(t2,t4,t6);\n    }\n  }\n}\n}"
    codegen_test(expr, code)


def test_spmv():
    expr = "spmv = {[i, n, j]: 0 <= i < N ^ rp(i) <= n < rp(i + 1) ^ j == col(n)}"
    code = "void spmv(int N) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= N-1; t2++) {\n    for(t4 = rp(t2); t4 <= rp1(t2)-1; t4++) {\n      t6=col(t2,t4);\n      s0(t2,t4,t6);\n    }\n  }\n}"
    codegen_test(expr, code)


def test_krp():
    expr = "krp = {[n, i, j, k, r]: 0 <= n < M ^ i == ind0(n) ^ j == ind1(n) ^ k == ind2(n) ^ 0 <= r < R}"
    code = "void krp(int M, int R) {\n  int t2, t4, t6, t8, t10;\nfor(t2 = 0; t2 <= M-1; t2++) {\n  t4=ind0(t2);\n  t6=ind1(t2);\n  t8=ind2(t2);\n  for(t10 = 0; t10 <= R-1; t10++) {\n    s0(t2,t4,t6,t8,t10);\n  }\n}\n}"
    codegen_test(expr, code)
