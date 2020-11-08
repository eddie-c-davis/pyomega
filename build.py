# build.py

from typing import Any, Dict

from setuptools_cpp import CMakeExtension, ExtensionBuilder, Pybind11Extension


ext_modules = [
    # A basic pybind11 extension in <project_root>/src/ext1:
    # Pybind11Extension(
    #     "pyomega.omega", ["src/omega/bindings/.cpp"], include_dirs=["src/ext1/include"]
    # ),
    # An extension with a custom <project_root>/src/ext2/CMakeLists.txt:
    CMakeExtension(f"pyomega.omega", sourcedir="src/omega"),
]


def build(setup_kwargs: Dict[str, Any]) -> None:
    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "cmdclass": dict(build_ext=ExtensionBuilder),
            "zip_safe": False,
        }
    )