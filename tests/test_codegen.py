# tests/test_visit.py
import sys
from typing import List

sys.path.append("./src")
from pyomega.parser import IRParser
from pyomega.visit import ASTVisitor, CodeGenerator


def codegen_test(
    expr: str,
    code: str,
    names: List[str],
    file_name: str = "",
    check_c_ast: bool = False,
) -> None:
    # TODO(eddied): Refactor this into a class, not a test function!

    ir_parser = IRParser(expr)
    space, py_ast, fields = ir_parser.parse()
    assert names == [field for field in fields]

    cg_visitor = CodeGenerator()
    source = cg_visitor(space, py_ast, fields)

    if file_name:
        with open(f"{file_name}.c", "w") as file:
            file.write(source)

    # Assert expected code is generated
    assert source == code

    # Assert generated source produces a valid C AST...
    if check_c_ast:
        ast_visitor = ASTVisitor()
        c_ast = ast_visitor(source)
        assert c_ast is not None


def test_dmv():
    expr = "dmv = {[i, j]: 0 <= i < N ^ 0 <= j < M}\n"
    expr += "y[i] += A[i, j] * x[j]"
    code = "#define s0(i, j) { y[(i)] += A[(i), (j)] * x[(j)]; }\n\nvoid dmv(const int N, const int M, float *y, const float *A, const float *x) {\n  int t2, t4;\nfor(t2 = 0; t2 <= N-1; t2++) {\n  for(t4 = 0; t4 <= M-1; t4++) {\n    s0(t2,t4);\n  }\n}\n}"
    codegen_test(expr, code, ["y", "A", "x"], "dmv")


def test_matmul():
    expr = "matmul = {[i, j, k]: 0 <= i < N ^ 0 <= j < M ^ 0 <= k < K}\n"
    expr += "C[i, j] += A[i, k] * B[k, j]"
    code = "#define s0(i, j, k) { C[(i), (j)] += A[(i), (k)] * B[(k), (j)]; }\n\nvoid matmul(const int N, const int M, const int K, float *C, const float *A, const float *B) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= N-1; t2++) {\n  for(t4 = 0; t4 <= M-1; t4++) {\n    for(t6 = 0; t6 <= K-1; t6++) {\n      s0(t2,t4,t6);\n    }\n  }\n}\n}"
    codegen_test(expr, code, ["C", "A", "B"], "matmul")


def test_spmv():
    expr = "spmv = {[i, n, j]: 0 <= i < N ^ rp(i) <= n < rp(i + 1) ^ j == col(n)}\n"
    expr += "y[i] += A[n] * x[j]"
    code = "#define s0(i, n, j) { y[(i)] += A[(n)] * x[(j)]; }\n\nvoid spmv(const int N, float *y, const float *A, const float *x) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= N-1; t2++) {\n    for(t4 = rp(t2); t4 <= rp1(t2)-1; t4++) {\n      t6=col(t2,t4);\n      s0(t2,t4,t6);\n    }\n  }\n}"
    codegen_test(expr, code, ["y", "A", "x"], "spmv")


def test_spmv_coo():
    expr = "spmv = {[n, i, j]: 0 <= n < M ^ i == row(n) ^ j == col(n)}\n"
    expr += "y[i] += A[n] * x[j]"
    code = "#define s0(n, i, j) { y[(i)] += A[(n)] * x[(j)]; }\n\nvoid spmv(const int M, float *y, const float *A, const float *x) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= M-1; t2++) {\n  t4=row(t2);\n  t6=col(t2);\n  s0(t2,t4,t6);\n}\n}"
    codegen_test(expr, code, ["y", "A", "x"], "spmv_coo")


def test_krp():
    expr = "krp = {[n, i, j, k, r]: 0 <= n < M ^ i == ind0(n) ^ j == ind1(n) ^ k == ind2(n) ^ 0 <= r < R}\n"
    expr += "A[i, r] += X[n] * C[k, r] * B[j, r]"
    code = "#define s0(n, i, j, k, r) { A[(i), (r)] += X[(n)] * C[(k), (r)] * B[(j), (r)]; }\n\nvoid krp(const int M, const int R, float *A, const float *X, const float *C, const float *B) {\n  int t2, t4, t6, t8, t10;\nfor(t2 = 0; t2 <= M-1; t2++) {\n  t4=ind0(t2);\n  t6=ind1(t2);\n  t8=ind2(t2);\n  for(t10 = 0; t10 <= R-1; t10++) {\n    s0(t2,t4,t6,t8,t10);\n  }\n}\n}"
    codegen_test(expr, code, ["A", "X", "C", "B"], "krp")


def test_lap():
    expr = "lap = {[i, j, k]: 0 <= i < I ^ 0 <= j < J ^ 0 <= k < K}\n"
    expr += "out[i, j, k] = -4.0 * inp[i, j, k] + inp[i + 1, j, k] + inp[i - 1, j, k] + inp[i, j - 1, k] + inp[i, j + 1, k]"
    code = "#define s0(i, j, k) { out[(i), (j), (k)] = -4.0 * inp[(i), (j), (k)] + inp[(i) + 1, (j), (k)] + inp[(i) - 1, (j), (k)] + inp[(i), (j) - 1, (k)] + inp[(i), (j) + 1, (k)]; }\n\nvoid lap(const int I, const int J, const int K, float *out, const float *inp) {\n  int t2, t4, t6;\nfor(t2 = 0; t2 <= I-1; t2++) {\n  for(t4 = 0; t4 <= J-1; t4++) {\n    for(t6 = 0; t6 <= K-1; t6++) {\n      s0(t2,t4,t6);\n    }\n  }\n}\n}"
    codegen_test(expr, code, ["out", "inp"], "lap")


def test_corners():
    dom_expr = "dom = {[i, j, k]: 0 <= i < N ^ 0 <= j < N ^ 0 <= k < K"
    copy_expr = dom_expr + " ^ i == N - 1 ^ j == 0}\n"
    copy_expr += "out[i, j, k] = inp[0, j + 5, 0]"

    ir_parser = IRParser(copy_expr)
    space, py_ast, fields = ir_parser.parse()

    cg_visitor = CodeGenerator()
    source = cg_visitor(space, py_ast, fields)

    code = "#define s0(i, j, k) { out[(i), (j), (k)] = inp[0, (j) + 5, 0]; }\n\nvoid dom(const int N, const int N, const int K, const int N, float *out, const float *inp) {\n  int t2, t4, t6;\nfor(t6 = 0; t6 <= K-1; t6++) {\n  s0(N-1,0,t6);\n}\n}"
    assert code == source
