# tests/test_flutter.py
import sys
import ast

sys.path.append("./src")
from pyomega.flutter import *


def test_root_widget():
    example_root_widget = MaterialApp(
        name="ExampleRootWidget",
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
    assert True
