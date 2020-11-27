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
class Object(Node):
    name: str = "Object"
    type_name: str = ""


@dataclass
class Method(Node):
    name: str = "Method"
    # return_type: str = "void"
    return_var: Object = None
    arguments: List[Object] = []


@dataclass
class Class(Node):
    name: str = "Class"
    members: List[Any] = []
    methods: List[Method] = []


@dataclass
class Container(Class):
    name: str = "Container"
    members = Dict[str, Any] = {}


@dataclass
class Center(Container):
    name: str = "Center"
    members = Dict[str, Any] = {}


@dataclass
class Text(Container):
    name: str = "Text"
    members = Dict[str, Any] = {}
    text: str = ""


@dataclass
class Style(Container):
    name: str = "Style"
    members = Dict[str, Any] = {}


@dataclass
class Widget(Class):
    name: str = "Widget"


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
        ("fontFamily", "Cabin"),
    ]


@dataclass
class App(StatelessWidget):
    name: str = "App"
    methods = [
        Method("build", Object("", "MaterialApp"), [Object("context", "BuildContext")])
    ]
    members = Dict[str, Any] = {}


@dataclass
class MaterialApp(App):
    name: str = "MaterialApp"
    members: Dict[str, Any] = {}
