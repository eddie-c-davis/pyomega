# src/pyomega/visit.py
import collections
import re
import sys

from dataclasses import asdict, dataclass
from pycparser import c_parser, c_ast
from typing import Any, Dict, List

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
class CodeGenerator(Visitor):
    source: str = ""

    def __call__(self, space: Space, ast: ast.Module, fields: Dict[str, Any]) -> str:
        assert isinstance(space, Space)
        self.space = space
        self.ast = ast
        self.constants: List[str] = []
        self.source: str = self.visit(space)
        self.fields = fields

        return self.codegen()

    def codegen(self) -> str:
        py_to_c = PyToCTranslator()
        c_code = py_to_c(self.ast)
        c_statements = c_code.split("\n")

        # Define prototypes...
        iterators: List[str] = list(self.space.iterators.keys())
        iter_str: str = ", ".join(iterators)

        source: str = ""
        # for index, statement in enumerate(c_statements):
        #     source += f"auto void s{index}({iter_str});\n"

        # source += "\n"
        for index, statement in enumerate(c_statements):
            # source += f"inline void s{index}({iter_str}) {{ {statement} }}\n"
            for iterator in iterators:
                statement = re.sub(f"\\b[{iterator}]\\b", f"({iterator})", statement)
            source += f"#define s{index}({iter_str}) {{ {statement} }}\n"

        name: str = self.space.name
        tuple_str = ", 0, ".join(iterators)
        schedule: str = f"r0{name} := {{[{iter_str}] -> [0, {tuple_str}, 0]}}"

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

        # Constants first
        params: List[str] = [f"const int {constant}" for constant in self.constants]

        # Fields next
        for field in self.fields.values():
            is_constant = any([not access.is_write for access in field.accesses])
            params.append(
                f"{'const ' if is_constant else ''}{field.dtype} *{field.name}"
            )

        header = f"void {name}({', '.join(params)}) {{\n  int"
        omega_iters = [f"t{n * 2}" for n in range(1, len(iterators) + 1)]

        code = "{header} {iterators};\n{code}\n}}".format(
            header=header, iterators=", ".join(omega_iters), code=code
        )
        source += "\n" + code

        return source

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

    def __call__(self, code: str) -> c_ast.FuncDef:
        self.code = code
        parser = c_parser.CParser()
        self.root = parser.parse(self.code, filename="<none>")
        assert isinstance(self.root, c_ast.FileAST)
        return self.root


class Transformer(Visitor):
    """Like ast.NodeTransformer"""

    pass


@dataclass
class PyToCTranslator(Visitor):
    source: str = ""

    def __call__(self, root: ast.Module) -> str:
        stmt_sources = [self.visit(stmt) for stmt in root.body]
        self.source = ";\n".join(stmt_sources) + ";"
        return self.source

    def visit_Assign(self, node: ast.Assign) -> str:
        assert len(node.targets) < 2
        target = self.visit(node.targets[0])
        value = self.visit(node.value)
        return f"{target} = {value}"

    def visit_AugAssign(self, node: ast.AugAssign) -> str:
        target = self.visit(node.target)
        op = self.visit(node.op)
        value = self.visit(node.value)
        return f"{target} {op}= {value}"

    def visit_BinOp(self, node: ast.BinOp) -> str:
        left = self.visit(node.left)
        op = self.visit(node.op)
        right = self.visit(node.right)
        return f"{left} {op} {right}"

    def visit_UnaryOp(self, node: ast.UnaryOp) -> str:
        operand = self.visit(node.operand)
        op = self.visit(node.op)
        return f"{op}{operand}"

    def visit_Subscript(self, node: ast.Subscript) -> str:
        c_value = self.visit(node.value)
        c_slice = self.visit(node.slice)
        return f"{c_value}[{c_slice}]"

    def visit_Name(self, node: ast.Name) -> str:
        return node.id

    def visit_Index(self, node: ast.Index) -> str:
        return self.visit(node.value)

    def visit_Tuple(self, node: ast.Tuple) -> str:
        return ", ".join([self.visit(elt) for elt in node.elts])

    def visit_Constant(self, node: ast.Constant) -> str:
        return f"{node.value}"

    def visit_Add(self, node: ast.Add) -> str:
        return "+"

    def visit_UAdd(self, node: ast.UAdd) -> str:
        return "+"

    def visit_Sub(self, node: ast.Sub) -> str:
        return "-"

    def visit_USub(self, node: ast.USub) -> str:
        return "-"

    def visit_Mult(self, node: ast.Mult) -> str:
        return "*"

    def visit_Div(self, node: ast.Div) -> str:
        return "/"

    def visit_FloorDiv(self, node: ast.FloorDiv) -> str:
        return "/"

    def visit_Mod(self, node: ast.Mod) -> str:
        return "%"

    def visit_Pow(self, node: ast.Pow) -> str:
        return "pow"

    def visit_LShift(self, node: ast.LShift) -> str:
        return "<<"

    def visit_RShift(self, node: ast.RShift) -> str:
        return ">>"

    def visit_BitOr(self, node: ast.BitOr) -> str:
        return "|"

    def visit_BitXor(self, node: ast.BitXor) -> str:
        return "^"

    def visit_BitAnd(self, node: ast.BitAnd) -> str:
        return "&"

    def visit_MatMult(self, node: ast.MatMult) -> str:
        raise RuntimeError("Unsupported operator: MatMult ('@')")
