cmake_minimum_required(VERSION 3.9)
project(pyomega C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -DPIC -Xpreprocessor -ftree-vectorize -funroll-all-loops -std=c++11 -Wdeprecated-declarations")

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

include_directories(
    src src/chill src/chill/omega
    src/chill/omega/basic/include
    src/chill/omega/omega_lib/include
    src/chill/omega/code_gen/include
    src/chill/omega/parser
    src/util
    /usr/local/include/python3.7
    ${PYTHON_INCLUDE_DIRS}
)

set(OMEGA_FILES
    src/chill/omega/OmegaLib.cpp
    src/chill/omega/basic/src/ConstString.cc
    src/chill/omega/parser/parser.tab.cc
    src/chill/omega/parser/lex.yy.cc
    src/chill/omega/parser/AST.cc
    src/chill/omega/omega_lib/src/closure.cc
    src/chill/omega/omega_lib/src/farkas.cc
    src/chill/omega/omega_lib/src/hull.cc
    src/chill/omega/omega_lib/src/pres_beaut.cc
    src/chill/omega/omega_lib/src/pres_col.cc
    src/chill/omega/omega_lib/src/pres_dnf.cc
    src/chill/omega/omega_lib/src/pres_cnstr.cc
    src/chill/omega/omega_lib/src/pres_decl.cc
    src/chill/omega/omega_lib/src/pres_gen.cc
    src/chill/omega/omega_lib/src/pres_logic.cc
    src/chill/omega/omega_lib/src/pres_form.cc
    src/chill/omega/omega_lib/src/pres_conj.cc
    src/chill/omega/omega_lib/src/pres_print.cc
    src/chill/omega/omega_lib/src/pres_quant.cc
    src/chill/omega/omega_lib/src/pres_rear.cc
    src/chill/omega/omega_lib/src/pres_var.cc
    src/chill/omega/omega_lib/src/reach.cc
    src/chill/omega/omega_lib/src/hull_simple.cc
    src/chill/omega/omega_lib/src/Relation.cc
    src/chill/omega/omega_lib/src/RelBody.cc
    src/chill/omega/omega_lib/src/Relations.cc
    src/chill/omega/omega_lib/src/RelVar.cc
    src/chill/omega/omega_lib/src/omega_core/oc.cc
    src/chill/omega/omega_lib/src/omega_core/oc_eq.cc
    src/chill/omega/omega_lib/src/omega_core/oc_exp_kill.cc
    src/chill/omega/omega_lib/src/omega_core/oc_global.cc
    src/chill/omega/omega_lib/src/omega_core/oc_print.cc
    src/chill/omega/omega_lib/src/omega_core/oc_problems.cc
    src/chill/omega/omega_lib/src/omega_core/oc_query.cc
    src/chill/omega/omega_lib/src/omega_core/oc_quick_kill.cc
    src/chill/omega/omega_lib/src/omega_core/oc_simple.cc
    src/chill/omega/omega_lib/src/omega_core/oc_solve.cc
    src/chill/omega/omega_lib/src/omega_core/oc_util.cc
    src/chill/omega/code_gen/src/codegen.cc
    src/chill/omega/code_gen/src/CG.cc
    src/chill/omega/code_gen/src/CG_utils.cc
    src/chill/omega/code_gen/src/CG_stringBuilder.cc
)

add_library(pyomega SHARED ${OMEGA_FILES})
target_link_libraries(pyomega ${PYTHON_LIBRARIES})
