# src/pyomega/ir.py
import ast

from dataclasses import dataclass
from typing import Dict, List, Tuple


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

    def add_iterator(self, iterator: Iterator):
        assert isinstance(iterator, Iterator)
        self.iterators.append(iterator)

    def add_relation(self, relation: Relation):
        assert isinstance(relation, Relation)
        exists = False
        for n in range(len(self.relations) - 1, -1, -1):
            exists = exists or relation.id == self.relations[n].id
            if exists:
                return
        self.relations.append(relation)


class Statement(Node):
    number: int = 0
    schedule: Tuple[int]


class Computation(Node):
    name: str = ""
    space: Space = None
    statements: List[Statement] = ()