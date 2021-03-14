# tests/test_passes.py
import astor
import sys

sys.path.append("./src")
from pyomega.passes import FunctionCallInliner


def add(a, b):
    return a + b


def sum(c: int, d: int):
    return add(c, d)


def test_inline_pass():
    inline_pass = FunctionCallInliner()
    inline_ast = inline_pass(sum, add)
    assert inline_ast is not None
    inline_code = astor.code_gen.to_source(inline_ast)
    assert inline_code.strip() == "def sum(c: int, d: int):\n    return c + d"
