# tests/test_flutter.py
import sys
import ast

sys.path.append("./src")
from pyomega.flutter import *


def test_root_widget():
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
                                        type_name="TextStyle",
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
            ),
            title='"Hello World"',
        ),
    )
    assert example_root_widget is not None

    visitor = AppCodeGenerator(add_main=True)
    flutter_code = visitor(example_root_widget)
    with open("/tmp/test_flutter.dart", "w") as file:
        file.write(flutter_code)
    assert len(flutter_code) > 0
