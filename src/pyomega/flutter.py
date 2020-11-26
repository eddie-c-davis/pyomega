# src/pyomega/flutter.py
import ast

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


"""
Implementation of the intermediate representations used in PyOmega.
"""


@dataclass
class Node:
    @property
    def id(self) -> int:
        return id(self)

@dataclass
class Method(Node):
    name: str = "Method"


@dataclass
class Widget(Node):
    name: str = "Widget"
    members: List[Any] = []
    methods: List[Method] = []


@dataclass
class StatelessWidget(Widget):
    name: str = "StatelessWidget"


@dataclass
class AppSettings(Widget):
    name: str = "App"


@dataclass
class ThemeData(Widget):
    name: str = "App"
    methods: List[Any] = [
        ("fontFamily",  "Cabin"),

    ]


@dataclass
class App(StatelessWidget):
    name: str = "App"
    members: List[Any] = [
        AppSettings("settings"),
        ThemeData("theme"),
    ],


