# src/pyomega/ir.py
import ast
import copy as cp
import inspect

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Set, Tuple, Union


"""
Implementation of compiler pass infrastructure.
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
    current_block: List[ast.AST] = ()
    new_block: List[ast.AST] = ()

    def __call__(
        self,
        func_node: Union[Callable, ast.FunctionDef],
        inline_node: Union[Callable, ast.FunctionDef],
        **kwargs
    ):
        if isinstance(func_node, Callable):
            source = inspect.getsource(func_node)
            func_node = ast.parse(source).body[0]
        self.root_node = func_node

        if isinstance(inline_node, Callable):
            source = inspect.getsource(inline_node)
            inline_node = ast.parse(source).body[0]
        self.inline_root = inline_node

        self.func_name = self.inline_root.name
        args = self.inline_root.args.args
        self.param_names = {args[i].arg: i for i in range(len(args))}

        return self.visit(self.root_node, **kwargs)

    def _process_stmts(self, statements: List[Any]):
        self.new_block = []
        outer_block = self.current_block
        self.current_block = self.new_block

        for statement in statements:
            # Inside a function call If arg_names is nonempty
            new_statement = cp.deepcopy(statement) if self.arg_names else statement
            if self.visit(new_statement):
                self.new_block.append(new_statement)

        self.current_block = outer_block

        return self.new_block

    def visit_FunctionDef(self, node: ast.FunctionDef):
        node.body = self._process_stmts(node.body)
        # TODO: Currently have multiple return statements...
        node.body.pop()
        return node

    def visit_With(self, node: ast.With):
        node.body = self._process_stmts(node.body)
        return node

    def visit_If(self, node: ast.If):
        node.body = self._process_stmts(node.body)
        if node.orelse:
            node.orelse = self._process_stmts(node.orelse)
        return node

    def visit_Call(self, node: ast.Call):
        if node.func.id == self.func_name:
            self.arg_names = [arg.id for arg in node.args]
            new_statements = self._process_stmts(self.inline_root.body)
            self.arg_names = []
            return new_statements[-1]
        return node

    def visit_Name(self, name: ast.Name):
        if name.id in self.param_names:
            position = self.param_names[name.id]
            name.id = self.arg_names[position]
        return name
