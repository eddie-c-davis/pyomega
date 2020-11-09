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
    relation: ir.Relation = ir.Relation()

    def __init__(self, node: ast.Module = None, expression: str = ""):
        if node is None:
            node = ast.parse(expression)
        assert isinstance(node, ast.Module)
        self.root = node
        self.space = ir.Space()

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
        self.space.name = node.targets[0].id
        self.visit(node.value)

    def visit_Name(self, node: ast.Name):
        for iterator in self.space.iterators:
            if node.id == iterator.name:
                return iterator
        return ir.Constant(name=node.id)

    def visit_Dict(self, node: ast.Dict):
        for key in node.keys:
            for elt in key.elts:
                self.space.iterators.append(ir.Iterator(name=elt.id))
        for value in node.values:
            self.visit(value)

    def visit_Op(self, node: ast.AST):
        if isinstance(node, ast.LtE):
            return "<="
        elif isinstance(node, ast.Lt):
            return "<"
        if isinstance(node, ast.GtE):
            return ">="
        elif isinstance(node, ast.Gt):
            return ">"
        elif isinstance(node, ast.Eq):
            return "="
        elif isinstance(node, ast.NotEq):
            return "!="
        elif isinstance(node, ast.Add):
            return "+"
        elif isinstance(node, ast.Sub):
            return "-"
        elif isinstance(node, ast.Mult):
            return "*"
        elif isinstance(node, (ast.Div, ast.FloorDiv)):
            return "/"
        elif isinstance(node, ast.Mod):
            return "%"
        elif isinstance(node, ast.Pow):
            # TODO: Are exponents supported in Presburger expressions?
            return "**"
        raise TypeError("Unrecognized operator: " + str(node))

    def visit_Call(self, node: ast.Call):
        func: ir.Function = ir.Function(node.func.id, list())
        for arg in node.args:
            func.add(self.visit(arg))
        return func

    def visit_BinOp(self, node: ast.BinOp):
        bin_op = ir.BinOp()
        bin_op.left = self.visit(node.left)
        bin_op.op = self.visit_Op(node.op)
        bin_op.right = self.visit(node.right)
        return bin_op

    def visit_Compare(self, node: ast.Compare):
        # TODO: Generalize this method...
        assert len(node.comparators) == 4

        self.relation = ir.Relation()
        self.relation.left = self.visit(node.left)
        self.relation.left_op = self.visit_Op(node.ops[0])
        self.relation.mid = self.visit(node.comparators[0])
        self.relation.right_op = self.visit_Op(node.ops[1])
        assert isinstance(node.comparators[1], ast.BinOp)
        self.relation.right = self.visit(node.comparators[1].left)
        self.space.relations.append(self.relation)

        self.relation = ir.Relation()
        self.relation.left = self.visit(node.comparators[1].right)
        self.relation.left_op = self.visit_Op(node.ops[2])
        self.relation.mid = self.visit(node.comparators[2])
        self.relation.right_op = self.visit_Op(node.ops[3])
        self.relation.right = self.visit(node.comparators[3])
        self.space.relations.append(self.relation)

    def visit_Num(self, node: ast.Num):
        return ir.Literal(value=str(node.n))