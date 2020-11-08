# src/pyomega/ir.py
import ast

from dataclasses import dataclass
from typing import List, Tuple

from pyomega import ir


"""
Implementation of a polyhedral expression parser in PyOmega.
"""

@dataclass
class Parser(ast.NodeVisitor):
    expression: str = ""
    root: ast.Module = None
    space: ir.Space = ir.Space()

    def __init__(self, node: ast.Module = None, expression: str = ""):
        if node is None:
            node = ast.parse(expression)
        assert isinstance(node, ast.Module)
        self.root = node

    def parse(self) -> ir.Space:
        self.visit(self.root)
        return self.space

    def visit(self, node, **kwargs):
        """Visit a node."""
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, **kwargs)

    def visit_Module(self, node: ast.Module):
        assert len(node.body) > 0
        for child in node.body:
            self.visit(child)

    def visit_Assign(self, node: ast.Assign):
        assert len(node.targets) == 1
        self.visit(node.targets[0])
        self.visit(node.value)

    def visit_Name(self, node: ast.Name):
        if len(self.space.name) < 1:
            self.space.name = node.id

    def visit_Dict(self, node: ast.Dict):
        stop=1