# src/pyomega/flutter.py
import abc
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
class Node(abc.ABC):
    @property
    def id(self) -> int:
        return id(self)

    @classmethod
    def parent_type(cls):
        return cls.__bases__[0]

    @property
    def parent_name(self):
        parent_type = type(self).parent_type()
        if hasattr(parent_type, "type_name"):
            return parent_type.type_name
        return parent_type.name

    @property
    def grandparent_name(self):
        return super().parent_name


@dataclass
class Object(Node):
    name: str = ""
    type_name: str = "Object"
    text: str = ""
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
    name: str = ""
    type_name: str = "Container"


@dataclass
class Center(Container):
    name: str = ""
    type_name: str = "Center"


@dataclass
class Text(Container):
    name: str = ""
    type_name: str = "Text"


@dataclass
class Style(Container):
    name: str = ""
    type_name: str = "Style"


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
    imports: List[str] = _make_factory(lambda: ["package:flutter/material.dart"])
    add_main: bool = False

    @property
    def indent(self):
        return self.level * "  "

    def __call__(self, root: App, **kwargs) -> str:
        assert isinstance(root, App)
        self.root = root
        self.source: str = (
            "import '"
            + "';\nimport '".join(import_name for import_name in self.imports)
            + "';\n\n"
        )

        if self.add_main:
            self.level += 1
            self.source += f"void main() {{\n{self.indent}runApp({root.name}());\n}}\n\n"
            self.level -= 1

        self.source += self.visit(root, **kwargs)
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
            self.level += 1
            return_code = self.visit(node.return_var, **kwargs)
            source += f"{self.indent}return {return_code};\n"
            self.level -= 1

        source += f"{self.indent}}}  // {node.name}\n"
        return source

    def visit_Object(self, node: Object, **kwargs) -> str:
        source: str = ""
        if len(node.name) > 0:
            source += f"{node.type_name} {node.name}"
            if len(node.elems) > 0:
                source += " = "

        if len(node.text) > 0 or len(node.elems) > 0:
            source += f"{node.type_name}(\n"
            self.level += 1
            if len(node.text) > 0:
                source += f'{self.indent}"{node.text}"'
                if len(node.elems) > 0:
                    source += ",\n"

            for key, elem in node.elems.items():
                right = self.visit(elem, **kwargs)
                source += f"{self.indent}{key}: {right},\n"
            self.level -= 1
            source += f"{self.indent})"  # ,  // {node.type_name}\n"

        return source
