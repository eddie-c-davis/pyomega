# src/pyomega/ir.py
import ast
import copy as cp
import inspect

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Set, Tuple

from pyomega import ir


"""
Implementation of a polyhedral expression parser in PyOmega.
"""


@dataclass
class Pass(ast.NodeTransformer):
    root_node: ast.Module = None
    pass_name: str = ""
    context: Dict[str, Any] = ()

    def __init__(self, pass_name: str = "", context: Dict[str, Any] = {}):
        self.pass_name = pass_name
        self.context = context

    def visit(self, node, **kwargs):
        """Visit a node."""
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, **kwargs)


@dataclass
class FunctionCallInliner(Pass):
    inline_root: ast.FunctionDef = None
    func_name: str = ""
    param_names: Dict[str, Any] = ()
    arg_names: List[str] = ()

    def __call__(self, call_func: Callable, inline_func: Callable):
        source = inspect.getsource(call_func)
        self.root_node = ast.parse(source)

        source = inspect.getsource(inline_func)
        self.inline_root = ast.parse(source).body[0]
        self.func_name = self.inline_root.name
        args = self.inline_root.args.args
        self.param_names = {args[i].arg: i for i in range(len(args))}

        new_root = self.visit(self.root_node)

        return new_root

    def _process_stmts(self, statements: List[Any]):
        new_statements = []
        for statement in statements:
            if isinstance(statement, ast.Return):
                statement = statement.value
            new_statement = cp.deepcopy(statement)
            if self.visit(new_statement):
                new_statements.append(new_statement)
        return new_statements

    def visit_Call(self, node: ast.Call):
        if node.func.id == self.func_name:
            self.arg_names = [arg.id for arg in node.args]
            new_statements = self._process_stmts(self.inline_root.body)
            # TODO: What to return here? -- new block statement?
            if len(new_statements) == 1:
                return new_statements[0]
            return new_statements
        return node

    def visit_Name(self, name: ast.Name):
        if name.id in self.param_names:
            position = self.param_names[name.id]
            name.id = self.arg_names[position]
        return name
