# tests/test_flutter.py
import sys
import ast

sys.path.append("./src")
from pyomega.flutter import *


def test_root_widget():
    materialApp = MaterialApp(
        name="ExampleRootWidget",
        members=dict(
            home=Container(
                members=dict(
                    color="Colors.blueGrey",
                    child=Center(
                        members=dict(
                            child=Text(
                                text="Hey there!",
                                style=Style(
                                    name="TextStyle",
                                    members=dict(
                                        decoration="TextDecoration.none",
                                        color="Colors.white",
                                    ),
                                ),
                            )
                        )
                    ),
                )
            )
        )
    )
    assert True
