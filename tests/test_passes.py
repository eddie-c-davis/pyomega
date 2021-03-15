# tests/test_passes.py
import astor
import sys

sys.path.append("./src")
from pyomega.passes import FunctionCallInliner


def madd(a, b):
    c = a * b
    return b + c


def sum(d: int, e: int):
    return madd(d, e)


def test_inline_pass():
    inline_pass = FunctionCallInliner()
    inline_ast = inline_pass(sum, madd)
    assert inline_ast is not None
    inline_code = astor.code_gen.to_source(inline_ast)
    assert inline_code.strip() == "def sum(d: int, e: int):\n    c = d * e\n    return e + c"
