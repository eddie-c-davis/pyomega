# src/pyomega/visit.py
import collections
import sys

from dataclasses import asdict, dataclass
from pycparser import c_parser, c_ast
from typing import Dict, List

sys.path.append("./src/omega")
from omega import OmegaLib
from pyomega.ir import *


"""
Implement visitors for the PyOmega IR.
"""


def iter_attributes(node: Node):
    """
    Yield a tuple of ``(attrib_name, value)`` for each item in ``asdict(node)``
    """
    attributes = asdict(node)
    for attrib_name in attributes:
        yield attrib_name, attributes[attrib_name]


@dataclass
class Visitor:
    root: Node = None

    def generic_visit(self, node: Node, **kwargs):
        items = []
        if isinstance(node, (str, bytes, bytearray)):
            return node
        elif isinstance(node, collections.abc.Mapping):
            items = node.items()
        elif isinstance(node, collections.abc.Iterable):
            items = enumerate(node)
        elif isinstance(node, Node):
            items = iter_attributes(node)
        for value in items:
            self.visit(value, **kwargs)

    def visit(self, node: Node, **kwargs):
        """Visit a node."""
        node_class = node.__class__
        method = "visit_" + node_class.__name__
        visitor = getattr(self, method, None)

        while not visitor and len(node_class.__bases__) > 0:  # Try parent class...
            node_class = node_class.__bases__[0]
            method = "visit_" + node_class.__name__
            visitor = getattr(self, method, None)

        if not visitor:
            visitor = self.generic_visit
        return visitor(node, **kwargs)


@dataclass
class CodeGenVisitor(Visitor):
    source: str = ""

    def __call__(self, root: Space) -> str:
        assert isinstance(root, Space)
        self.root = root
        self.constants: List[str] = []
        self.source: str = self.visit(root)
        return self.codegen()

    def codegen(self) -> str:
        name: str = self.root.name
        iterators = [iterator.name for iterator in self.root.iterators]
        schedule: str = "r0{name} := {{[{iterators}] -> [0, {tuple}, 0]}}".format(
            name=name, iterators=", ".join(iterators), tuple=", 0, ".join(iterators)
        )

        relation = self.source[self.source.find(" = ") + 3 :]
        rel_map: Dict[str, str] = {name: relation}
        sched_map: Dict[str, List[str]] = {name: [schedule]}

        constraints = [f"{constant} >= 1" for constant in self.constants]
        code = OmegaLib().codegen(rel_map, sched_map, [name], constraints).rstrip()
        if "error" in code.lower():
            raise RuntimeError(code)

        # Strip outer 'if' statement if existent...
        if code.startswith("if"):
            code = code[code.find("{") + 1 :].lstrip()
            code = code[0 : code.rfind("}") - 1].rstrip()

        header = "void {name}(int {inputs}) {{\n  int".format(
            name=name, inputs=", int ".join(self.constants)
        )
        omega_iters = [f"t{n * 2}" for n in range(1, len(iterators) + 1)]

        code = "{header} {iterators};\n{code}\n}}".format(
            header=header, iterators=", ".join(omega_iters), code=code
        )
        return code

    def visit_Space(self, node: Space) -> str:
        source = f"{node.name} = {{"
        iterators = [self.visit(iterator) for iterator in node.iterators]
        source += "[{iterators}]".format(iterators=", ".join(iterators))
        if len(node.relations) > 0:
            source += ": "
            relations = [self.visit(relation) for relation in node.relations]
            source += " && ".join(relations)
        source += "}"
        return source

    def visit_Iterator(self, node: Iterator) -> str:
        return node.name

    def visit_Constant(self, node: Constant) -> str:
        self.constants.append(node.name)
        return node.name

    def visit_Literal(self, node: Literal) -> str:
        return node.value

    def visit_BinOp(self, node: BinOp) -> str:
        return "{left} {op} {right}".format(
            left=self.visit(node.left), op=node.op, right=self.visit(node.right)
        )

    def visit_Relation(self, node: Relation) -> str:
        code = "{left} {left_op}".format(
            left=self.visit(node.left), left_op=node.left_op
        )
        if node.mid:
            code += " {mid} {right_op}".format(
                mid=self.visit(node.mid), right_op=node.right_op
            )
        code += " {right}".format(right=self.visit(node.right))
        return code

    def visit_Function(self, node: Function) -> str:
        return "{name}({args})".format(
            name=node.name, args=", ".join([self.visit(arg) for arg in node.args])
        )


class ASTVisitor(Visitor):
    code: str = ""
    root: c_ast.FuncDef = None

    def __call__(self, code: str) -> str:
        self.code = code
        parser = c_parser.CParser()
        ast = parser.parse(self.code, filename="<none>")
        self.root = ast.ext[0]
        assert isinstance(self.root, c_ast.FuncDef)
        return self.root
