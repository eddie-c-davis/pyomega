# tests/test_visit.py
import sys
from typing import List

sys.path.append("./src")
from pyomega.parser import IRParser
from pyomega.visit import ASTVisitor, CodeGenerator


def codegen_test(expr: str, code: str, names: List[str]) -> None:
    # TODO(eddied): Refactor this into a class, not a test function!

    ir_parser = IRParser(expr)
    space, py_ast, fields = ir_parser.parse()
    assert(names == [field for field in fields])

    cg_visitor = CodeGenerator()
    source = cg_visitor(space, py_ast)

    ast_visitor = ASTVisitor()
    c_ast = ast_visitor(source)

    # Assert generated source produces a valid C AST...
    assert c_ast is not None

    # Assert expected code is generated
    assert source == code


def test_dmv():
    expr = "s2d = {[i, j]: 0 <= i < N ^ 0 <= j < M}\n"
    expr += "y[i] += A[i, j] * x[j]"
    code = "auto void s0(const int const int i, const int j);\n\ninline void s0(const int const int i, const int j) { y[i] += A[i, j] * x[j]; }\n\nvoid s2d(int N, int M) {\n  int t2, t4;\nfor(t2 = 0; t2 <= N-1; t2++) {\n  for(t4 = 0; t4 <= M-1; t4++) {\n    s0(t2,t4);\n  }\n}\n}"
    codegen_test(expr, code, ["y", "A", "x"])


def test_matmul():
    expr = "s3d = {[i, j, k]: 0 <= i < N ^ 0 <= j < M ^ 0 <= k < K}\n"
    expr += "C[i, j] += A[i, k] * B[k, j]"
    code = "auto void s0(const int const int i, const int j, const int k);\n\ninline void s0(const int const int i, const int j, const int k) { C[i, j] += A[i, k] * B[k, j]; }\n\nvoid s3d(int N, int M, int K) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= N-1; t2++) {\n  for(t4 = 0; t4 <= M-1; t4++) {\n    for(t6 = 0; t6 <= K-1; t6++) {\n      s0(t2,t4,t6);\n    }\n  }\n}\n}"
    codegen_test(expr, code, ["C", "A", "B"])


def test_spmv():
    expr = "spmv = {[i, n, j]: 0 <= i < N ^ rp(i) <= n < rp(i + 1) ^ j == col(n)}\n"
    expr += "y[i] += A[n] * x[j]"
    code = "auto void s0(const int const int i, const int n, const int j);\n\ninline void s0(const int const int i, const int n, const int j) { y[i] += A[n] * x[j]; }\n\nvoid spmv(int N) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= N-1; t2++) {\n    for(t4 = rp(t2); t4 <= rp1(t2)-1; t4++) {\n      t6=col(t2,t4);\n      s0(t2,t4,t6);\n    }\n  }\n}"
    codegen_test(expr, code, ["y", "A", "x"])


def test_spmv_coo():
    expr = "spmv = {[n, i, j]: 0 <= n < M ^ i == row(n) ^ j == col(n)}\n"
    expr += "y[i] += A[n] * x[j]"
    code = "auto void s0(const int const int n, const int i, const int j);\n\ninline void s0(const int const int n, const int i, const int j) { y[i] += A[n] * x[j]; }\n\nvoid spmv(int M) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= M-1; t2++) {\n  t4=row(t2);\n  t6=col(t2);\n  s0(t2,t4,t6);\n}\n}"
    codegen_test(expr, code, ["y", "A", "x"])


def test_krp():
    expr = "krp = {[n, i, j, k, r]: 0 <= n < M ^ i == ind0(n) ^ j == ind1(n) ^ k == ind2(n) ^ 0 <= r < R}\n"
    expr += "A[i, r] += X[n] * C[k, r] * B[j, r]"
    code = "auto void s0(const int const int n, const int i, const int j, const int k, const int r);\n\ninline void s0(const int const int n, const int i, const int j, const int k, const int r) { A[i, r] += X[n] * C[k, r] * B[j, r]; }\n\nvoid krp(int M, int R) {\n  int t2, t4, t6, t8, t10;\nfor(t2 = 0; t2 <= M-1; t2++) {\n  t4=ind0(t2);\n  t6=ind1(t2);\n  t8=ind2(t2);\n  for(t10 = 0; t10 <= R-1; t10++) {\n    s0(t2,t4,t6,t8,t10);\n  }\n}\n}"
    codegen_test(expr, code, ["A", "X", "C", "B"])


def test_lap():
    expr = "lap = {[i, j, k]: 0 <= i < I ^ 0 <= j < J ^ 0 <= k < K}\n"
    expr += "out[i, j, k] = -4.0 * inp[i, j, k] + inp[i + 1, j, k] + inp[i - 1, j, k] + inp[i, j - 1, k] + inp[i, j + 1, k]"
    code = "auto void s0(const int const int i, const int j, const int k);\n\ninline void s0(const int const int i, const int j, const int k) { out[i, j, k] = -4.0 * inp[i, j, k] + inp[i + 1, j, k] + inp[i - 1, j, k] + inp[i, j - 1, k] + inp[i, j + 1, k]; }\n\nvoid lap(int I, int J, int K) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= I-1; t2++) {\n  for(t4 = 0; t4 <= J-1; t4++) {\n    for(t6 = 0; t6 <= K-1; t6++) {\n      s0(t2,t4,t6);\n    }\n  }\n}\n}"
    codegen_test(expr, code, ["out", "inp"])
