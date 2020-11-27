# src/pyomega/flutter.py
import ast

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

from pyomega.visit import Visitor


def _make_factory(factory_method: Callable):
    return field(default_factory=factory_method)


_list_factory = _make_factory(list)
_dict_factory = _make_factory(dict)


"""
Implementation of the intermediate representations used in PyOmega.
"""


@dataclass
class Node:
    @property
    def id(self) -> int:
        return id(self)

    @classmethod
    def parent_type(cls):
        return cls.__bases__[0]


@dataclass
class Object(Node):
    name: str = ""
    type_name: str = "Object"
    elems: Dict[str, Any] = _dict_factory


@dataclass
class Method(Node):
    name: str = "Method"
    return_type: str = "void"
    return_var: Object = None
    overriden: bool = False
    arguments: List[Object] = _list_factory


@dataclass
class Class(Node):
    name: str = "Class"
    methods: List[Method] = _list_factory
    members: List[Object] = _list_factory


@dataclass
class Container(Object):
    name: str = "Container"


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
                "build",
                "Widget",
                Object("", "MaterialApp"),
                True,
                [Object("context", "BuildContext")],
            )
        ]
    )
    elems: Dict[str, Any] = _dict_factory

    @property
    def parent_name(self):
        return type(self).parent_type().name


@dataclass
class MaterialApp(App):
    name: str = "MaterialApp"

    @property
    def parent_name(self):
        return type(self).parent_type().parent_type().name


"""
Code generators...
"""


@dataclass
class AppCodeGenerator(Visitor):
    source: str = ""
    level: int = 0

    @property
    def indent(self):
        return self.level * "  "

    def __call__(self, root: App, **kwargs) -> str:
        assert isinstance(root, App)
        self.root = root
        self.source: str = self.visit(root, **kwargs)
        return self.source

    def visit_App(self, node: App, **kwargs) -> str:
        source = f"class {node.name} extends {node.parent_name} {{\n"

        self.level += 1
        for member in node.members:
            source += self.visit(member, **kwargs)

        for method in node.methods:
            source += self.visit(method, **kwargs)
        self.level -= 1

        source += f"}}  // {node.name}\n"
        return source

    def visit_Method(self, node: Method, **kwargs) -> str:
        arg_list = ", ".join(
            [self.visit(argument, **kwargs) for argument in node.arguments]
        )
        source: str = self.indent + "@override\n" if node.overriden else ""
        source += f"{self.indent}{node.return_type} {node.name}({arg_list}) {{\n"

        if node.return_var:
            source += self.visit(node.return_var, **kwargs)

        source += f"}}  // {node.name}\n"
        return source

    def visit_Object(self, node: Object, **kwargs) -> str:
        source: str = ""
        if len(node.name) > 0:
            source += f"{node.type_name} {node.name}"
            if len(node.elems) > 0:
                source += " = "

        if len(node.elems) > 0:
            source += f"{node.type_name}(\n"
            self.level += 1
            for key, elem in node.elems.items():
                right = self.visit(elem, **kwargs)
                source += f"{self.indent}{key}: {right}"
            self.level -= 1
            source += f"{self.indent});  // {node.type_name}\n"

        return source
