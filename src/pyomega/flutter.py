# src/pyomega/flutter.py
import ast

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple


def _make_factory(factory_method: Callable):
    return field(default_factory=factory_method)


emptyList = _make_factory(list)
emptyDict = _make_factory(dict)


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
    arguments: List[Object] = emptyList


@dataclass
class Class(Node):
    name: str = "Class"
    members: List[Any] = emptyList
    methods: List[Method] = emptyList


@dataclass
class Container(Class):
    name: str = "Container"
    elems: Dict[str, Any] = emptyDict


@dataclass
class Center(Container):
    name: str = "Center"


@dataclass
class Text(Container):
    name: str = "Text"
    text: str = ""


@dataclass
class Style(Container):
    name: str = "Style"


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
    methods: List[Any] = _make_factory(
        lambda: [
            ("fontFamily", "Cabin"),
        ]
    )


@dataclass
class App(StatelessWidget):
    name: str = "App"
    methods: List[Method] = _make_factory(
        lambda: [
            Method(
                "build", Object("", "MaterialApp"), [Object("context", "BuildContext")]
            )
        ]
    )
    elems: Dict[str, Any] = emptyDict


@dataclass
class MaterialApp(App):
    name: str = "MaterialApp"
