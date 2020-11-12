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
                self.space.add_iterator(ir.Iterator(name=elt.id))
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
            return "=="
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
        relation = ir.Relation()
        relation.left = self.visit(node.left)

        n_comparators = len(node.comparators)
        has_remaining = n_comparators % 2 > 0
        if has_remaining:
            n_comparators -= 1

        for n in range(0, n_comparators, 2):
            comp = node.comparators[n]
            op = node.ops[n]
            next_comp = node.comparators[n + 1]
            next_op = node.ops[n + 1]

            relation.left_op = self.visit_Op(op)
            if isinstance(comp, ast.BinOp):
                relation.right = self.visit(comp.left)
                self.space.add_relation(relation)
                # Begin next relation...
                relation = ir.Relation()
                relation.left = self.visit(comp.right)
                relation.left_op = self.visit_Op(next_op)
            else:
                relation.mid = self.visit(comp)
                relation.right_op = self.visit_Op(next_op)

            if isinstance(next_comp, ast.BinOp):
                relation.right = self.visit(next_comp.left)
                self.space.add_relation(relation)
                # Begin next relation...
                relation = ir.Relation()
                relation.left = self.visit(next_comp.right)
            else:
                relation.right = self.visit(next_comp)
                self.space.add_relation(relation)

        if has_remaining:
            if relation.right:
                relation.mid = relation.right
                relation.right_op = self.visit_Op(node.ops[-1])
            else:
                relation.left_op = self.visit_Op(node.ops[-1])
            relation.right = self.visit(node.comparators[-1])
            self.space.add_relation(relation)

    def visit_Num(self, node: ast.Num):
        return ir.Literal(value=str(node.n))
