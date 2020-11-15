cmake_minimum_required(VERSION 3.9)
project(pyomega C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -DPIC -Xpreprocessor -ftree-vectorize -funroll-all-loops -std=c++11 -Wdeprecated-declarations")

find_package(PythonLibs REQUIRED)

include_directories(
    .
    chill
    chill/omega
    chill/omega/basic/include
    chill/omega/omega_lib/include
    chill/omega/code_gen/include
    chill/omega/parser
    /usr/local/include/python3.7
    ${PYTHON_INCLUDE_DIRS}
)

set(OMEGA_FILES
    chill/omega/basic/src/ConstString.cc
    chill/omega/basic/src/Link.cc
    chill/omega/parser/parser.tab.cc
    chill/omega/parser/lex.yy.cc
    chill/omega/parser/AST.cc
    chill/omega/omega_lib/src/closure.cc
    chill/omega/omega_lib/src/farkas.cc
    chill/omega/omega_lib/src/hull.cc
    chill/omega/omega_lib/src/pres_beaut.cc
    chill/omega/omega_lib/src/pres_col.cc
    chill/omega/omega_lib/src/pres_dnf.cc
    chill/omega/omega_lib/src/pres_cnstr.cc
    chill/omega/omega_lib/src/pres_decl.cc
    chill/omega/omega_lib/src/pres_gen.cc
    chill/omega/omega_lib/src/pres_logic.cc
    chill/omega/omega_lib/src/pres_form.cc
    chill/omega/omega_lib/src/pres_conj.cc
    chill/omega/omega_lib/src/pres_print.cc
    chill/omega/omega_lib/src/pres_quant.cc
    chill/omega/omega_lib/src/pres_rear.cc
    chill/omega/omega_lib/src/pres_var.cc
    chill/omega/omega_lib/src/reach.cc
    chill/omega/omega_lib/src/hull_simple.cc
    chill/omega/omega_lib/src/Relation.cc
    chill/omega/omega_lib/src/RelBody.cc
    chill/omega/omega_lib/src/Relations.cc
    chill/omega/omega_lib/src/RelVar.cc
    chill/omega/omega_lib/src/omega_core/oc.cc
    chill/omega/omega_lib/src/omega_core/oc_eq.cc
    chill/omega/omega_lib/src/omega_core/oc_exp_kill.cc
    chill/omega/omega_lib/src/omega_core/oc_global.cc
    chill/omega/omega_lib/src/omega_core/oc_print.cc
    chill/omega/omega_lib/src/omega_core/oc_problems.cc
    chill/omega/omega_lib/src/omega_core/oc_query.cc
    chill/omega/omega_lib/src/omega_core/oc_quick_kill.cc
    chill/omega/omega_lib/src/omega_core/oc_simple.cc
    chill/omega/omega_lib/src/omega_core/oc_solve.cc
    chill/omega/omega_lib/src/omega_core/oc_util.cc
    chill/omega/code_gen/src/codegen.cc
    chill/omega/code_gen/src/CG.cc
    chill/omega/code_gen/src/CG_utils.cc
    chill/omega/code_gen/src/CG_stringBuilder.cc
    OmegaLib.cpp
)

# Build python module
include(FetchContent)
set(FETCHCONTENT_UPDATES_DISCONNECTED ON)

FetchContent_Declare(pybind11_fetch
    URL https://github.com/pybind/pybind11/archive/v2.6.0.tar.gz
)
FetchContent_GetProperties(pybind11_fetch)
if(NOT pybind11_fetch_POPULATED)
    message(STATUS "Fetching pybind11 for python bindings...")
    FetchContent_Populate(pybind11_fetch)
    add_subdirectory(${pybind11_fetch_SOURCE_DIR} ${pybind11_fetch_BINARY_DIR})
endif()

pybind11_add_module(omega MODULE ${OMEGA_FILES})
