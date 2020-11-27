# tests/test_flutter.py
import sys
import ast

sys.path.append("./src")
from pyomega.flutter import *


def test_root_widget():
    # TODO: `MaterialApp` needs to be the `return_var`...
    example_root_widget = MaterialApp("ExampleRootWidget")
    example_root_widget.methods[0].return_var = Object(
        type_name="MaterialApp",
        elems=dict(
            home=Container(
                elems=dict(
                    color="Colors.blueGrey",
                    child=Center(
                        elems=dict(
                            child=Text(
                                text="Hey there!",
                                elems=dict(
                                    style=Style(
                                        name="TextStyle",
                                        elems=dict(
                                            decoration="TextDecoration.none",
                                            color="Colors.white",
                                        ),
                                    ),
                                ),
                            )
                        )
                    ),
                )
            )
        ),
    )
    assert example_root_widget is not None

    visitor = AppCodeGenerator()
    flutter_code = visitor(example_root_widget)
    assert len(flutter_code) > 0
