# src/pyomega/visit.py
import collections

from dataclasses import asdict, dataclass
from typing import Dict, List

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
            pass
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
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, **kwargs)


@dataclass
class CodeGenVisitor(Visitor):
    source: str = ""

    def __call__(self, root: Space) -> str:
        assert isinstance(root, Space)
        self.root = root
        self.source = self.visit(root)
        return self.source

    def visit_Space(self, node: Space) -> str:
        source = f"{node.name} = {{"
        iterators = [self.visit(iterator) for iterator in node.iterators]
        source += "[{iterators}]".format(iterators=", ".join(iterators))
        if len(node.relations) > 0:
            source += ": "
            relations = [self.visit(relation) for relation in node.relations]
            source += " ^ ".join(relations)
        source += "}"
        return source

    def visit_Iterator(self, node: Iterator) -> str:
        return node.name

    def visit_Constant(self, node: Constant) -> str:
        return node.name

    def visit_Literal(self, node: Literal) -> str:
        return node.value

    def visit_BinOp(self, node: BinOp) -> str:
        return "{left} {op} {right}".format(
            left=self.visit(node.left), op=node.op, right=self.visit(node.right)
        )

    def visit_Relation(self, node: Relation) -> str:
        return "{left} {left_op} {mid} {right_op} {right}".format(
            left=self.visit(node.left),
            left_op=node.left_op,
            mid=self.visit(node.mid),
            right_op=node.right_op,
            right=self.visit(node.right),
        )

    def visit_Function(self, node: Function) -> str:
        return "{name}({args})".format(
            name=node.name, args=", ".join([self.visit(arg) for arg in node.args])
        )