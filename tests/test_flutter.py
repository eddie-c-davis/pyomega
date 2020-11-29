# tests/test_flutter.py
import sys
import ast

sys.path.append("./src")
from pyomega.flutter import *


def test_hello_world():
    hello_world_app = MaterialApp("HelloWorldApp", title="Hello World")
    hello_world_app.set_return(
        Container(
            color="Colors.black",
            child=Center(
                child=Text(
                    text="Hey there!",
                    style=Style(
                        type_name="TextStyle",
                        decoration="TextDecoration.none",
                        color="Colors.white",
                    ),
                )
            ),
        ),
    )
    assert hello_world_app is not None

    visitor = AppCodeGenerator()
    flutter_code = visitor(hello_world_app)
    expected_code = """import 'package:flutter/material.dart';

class HelloWorldApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Container(
        child: Center(
          child: Text(
            "Hey there!",
            style: TextStyle(
              color: Colors.white,
              decoration: TextDecoration.none,
            ),
          ),
        ),
        color: Colors.black,
      ),
      title: "Hello World",
    );
  }  // build
}  // HelloWorldApp
"""
    assert flutter_code == expected_code


# def test_scaffold_button():
#     hello_world_app = MaterialApp("ScaffoldButtonApp")
#     hello_world_app.methods[0].return_var = Object(
#         type_name="MaterialApp",
#         elems=dict(
#             home=Material(
#                 elems=dict(
#                     color="Colors.blueGrey",
#                     child=Center(
#                         elems=dict(
#                             child=Text(
#                                 text="Hey there!",
#                                 elems=dict(
#                                     style=Style(
#                                         type_name="TextStyle",
#                                         elems=dict(
#                                             decoration="TextDecoration.none",
#                                             color="Colors.white",
#                                         ),
#                                     ),
#                                 ),
#                             )
#                         )
#                     ),
#                 )
#             ),
#             title='"Hello World"',
#         ),
#     )
#     assert hello_world_app is not None
#
#     visitor = AppCodeGenerator()
#     flutter_code = visitor(hello_world_app)
#     with open("/tmp/test_flutter.dart", "w") as file:
#         file.write(flutter_code)
