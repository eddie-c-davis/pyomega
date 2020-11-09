# src/pyomega/ir.py
import ast

from dataclasses import dataclass
from typing import Dict, List


"""
Implementation of the intermediate representations used in PyOmega.
"""


@dataclass
class Node:
    children: List = ()

    @property
    def id(self):
        return id(self)


@dataclass
class Iterator(Node):
    name: str = ""


@dataclass
class Literal(Node):
    value: str = ""


@dataclass
class Function(Node):
    name: str = ""


@dataclass
class Constant(Node):
    name: str = ""


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