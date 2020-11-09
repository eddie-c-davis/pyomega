# src/pyomega/ir.py
import ast

from dataclasses import dataclass
from typing import Dict, List


"""
Implementation of the intermediate representations used in PyOmega.
"""


@dataclass
class Node:
    @property
    def id(self) -> int:
        return id(self)


@dataclass
class Iterator(Node):
    name: str = ""


@dataclass
class Literal(Node):
    value: str = ""


@dataclass
class Function(Node):
    name: str
    args: List[Node]

    def add(self, arg: Node) -> None:
        self.args.append(arg)


@dataclass
class Constant(Node):
    name: str = ""


@dataclass
class BinOp(Node):
    left: Node = None
    op: str = ""
    right: Node = None


@dataclass
class Relation(Node):
    name: str = ""
    left: Node = None
    left_op: str = ""
    mid: Node = None
    right_op: str = ""
    right: Node = None


@dataclass
class Space(Node):
    name: str = ""
    iterators: List[Iterator] = ()
    relations: List[Relation] = ()

    def __init__(self):
        self.iterators = []
        self.relations = []