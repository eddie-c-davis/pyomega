cmake_minimum_required(VERSION 3.9)
project(edsl C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -DPIC -Xpreprocessor -ftree-vectorize -funroll-all-loops -std=c++11")

include_directories(lib/iegenlib/src
                    lib/isl lib/isl/imath lib/isl/include lib/isl/bld lib/isl/bld/include lib/gmp
                    lib/chill lib/chill/omega/basic/include lib/chill/omega/omega_lib/include
                    lib/chill/omega/code_gen/include lib/chill/omega/parser
                    lib/gtest  lib/gtest/include
                    lib/eigen lib/eigen/unsupported
                    lib/taco/include
                    out src src/util test
)

set(EDSL_FILES   src/poly/PolyLib.hpp
                 src/iegenlib/IEGenLib.hpp
                 src/omega/OmegaLib.hpp
                 src/pdfg/Digraph.hpp
                 src/pdfg/GraphIL.hpp
                 src/pdfg/Codegen.hpp
                 src/pdfg/InspGen.hpp
                 src/pdfg/FlowGraph.hpp
                 src/pdfg/Visitor.hpp
)

set(IEGEN_FILES  lib/iegenlib/src/set_relation/environment.cc
                 lib/iegenlib/src/set_relation/expression.cc
                 lib/iegenlib/src/set_relation/isl_str_manipulation.cc
                 lib/iegenlib/src/set_relation/set_relation.cc
                 lib/iegenlib/src/set_relation/SubMap.cc
                 lib/iegenlib/src/set_relation/TupleDecl.cc
                 lib/iegenlib/src/set_relation/UFCallMap.cc
                 lib/iegenlib/src/set_relation/UninterpFunc.cc
                 lib/iegenlib/src/util/util.cc
                 lib/iegenlib/src/parser/gen_scanner.cc
                 lib/iegenlib/src/parser/gen_parser.cc
                 lib/iegenlib/src/parser/parser.cc
)

set(ISL_FILES lib/isl/imath/gmp_compat.c
        lib/isl/imath/imath.c
        lib/isl/imath/imrat.c
        lib/isl/isl_map.c
        lib/isl/isl_input.c
        lib/isl/isl_output.c
        lib/isl/isl_printer.c
        lib/isl/isl_coalesce.c
        lib/isl/isl_union_map.c
        lib/isl/isl_map_simplify.c
        lib/isl/isl_map_subtract.c
        lib/isl/isl_ctx.c
        lib/isl/isl_space.c
        lib/isl/isl_mat.c
        lib/isl/isl_local_space.c
        lib/isl/isl_dim_map.c
        lib/isl/isl_map_list.c
        lib/isl/isl_map_simplify.c
        lib/isl/isl_val.c
        lib/isl/isl_int_sioimath.h
        lib/isl/isl_int_sioimath.c
        lib/isl/isl_val_sioimath.c
        lib/isl/isl_imath.c
        lib/isl/isl_obj.c
        lib/isl/isl_affine_hull.c
        lib/isl/isl_convex_hull.c
        lib/isl/isl_bernstein.c
        lib/isl/isl_blk.c
        lib/isl/isl_bound.c
        lib/isl/isl_id.c
        lib/isl/isl_id_to_ast_expr.c
        lib/isl/isl_seq.c
        lib/isl/isl_equalities.c
        lib/isl/isl_factorization.c
        lib/isl/isl_hash.c
        lib/isl/isl_tab.c
        lib/isl/isl_tab_pip.c
        lib/isl/isl_transitive_closure.c
        lib/isl/isl_vec.c
        lib/isl/isl_aff.c
        lib/isl/isl_reordering.c
        lib/isl/isl_constraint.c
        lib/isl/isl_lp.c
        lib/isl/isl_polynomial.c
        lib/isl/isl_sort.c
        lib/isl/isl_farkas.c
        lib/isl/isl_tarjan.c
        lib/isl/isl_fold.c
        lib/isl/isl_morph.c
        lib/isl/isl_arg.c
        lib/isl/isl_options.c
        lib/isl/isl_point.c
        lib/isl/isl_range.c
        lib/isl/isl_sample.c
        lib/isl/isl_scan.c
        lib/isl/isl_stream.c
        lib/isl/isl_version.c
        lib/isl/isl_vertices.c
        lib/isl/basis_reduction_tab.c
        lib/isl/isl_set_list.c
        lib/isl/isl_ast.c
        lib/isl/isl_ast_build.c
        lib/isl/isl_ast_build_expr.c
        lib/isl/isl_ast_codegen.c
        lib/isl/isl_ast_graft.c
        lib/isl/isl_band.c
        lib/isl/isl_ilp.c
        lib/isl/isl_schedule.c
        lib/isl/isl_schedule_node.c
        lib/isl/isl_schedule_tree.c
        lib/isl/isl_schedule_band.c
        lib/isl/isl_schedule_read.c
        lib/isl/print.c
)

set(OMEGA_FILES lib/chill/omega/basic/src/ConstString.cc
                lib/chill/omega/parser/parser.tab.cc
                lib/chill/omega/parser/lex.yy.cc
                lib/chill/omega/parser/AST.cc
                lib/chill/omega/omega_lib/src/closure.cc
                lib/chill/omega/omega_lib/src/farkas.cc
                lib/chill/omega/omega_lib/src/hull.cc
                lib/chill/omega/omega_lib/src/pres_beaut.cc
                lib/chill/omega/omega_lib/src/pres_col.cc
                lib/chill/omega/omega_lib/src/pres_dnf.cc
                lib/chill/omega/omega_lib/src/pres_cnstr.cc
                lib/chill/omega/omega_lib/src/pres_decl.cc
                lib/chill/omega/omega_lib/src/pres_gen.cc
                lib/chill/omega/omega_lib/src/pres_logic.cc
                lib/chill/omega/omega_lib/src/pres_form.cc
                lib/chill/omega/omega_lib/src/pres_conj.cc
                lib/chill/omega/omega_lib/src/pres_print.cc
                lib/chill/omega/omega_lib/src/pres_quant.cc
                lib/chill/omega/omega_lib/src/pres_rear.cc
                lib/chill/omega/omega_lib/src/pres_var.cc
                lib/chill/omega/omega_lib/src/reach.cc
                lib/chill/omega/omega_lib/src/hull_simple.cc
                lib/chill/omega/omega_lib/src/Relation.cc
                lib/chill/omega/omega_lib/src/RelBody.cc
                lib/chill/omega/omega_lib/src/Relations.cc
                lib/chill/omega/omega_lib/src/RelVar.cc
                lib/chill/omega/omega_lib/src/omega_core/oc.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_eq.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_exp_kill.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_global.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_print.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_problems.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_query.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_quick_kill.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_simple.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_solve.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_util.cc
                lib/chill/omega/code_gen/src/codegen.cc
                lib/chill/omega/code_gen/src/CG.cc
                lib/chill/omega/code_gen/src/CG_utils.cc
                lib/chill/omega/code_gen/src/CG_stringBuilder.cc
)

set(TESTING "true")
#set(MAKELIB "true")
#set(PAPI_ON "true")
#set(PARBUILD "true")

link_directories(lib lib/taco/lib)
if (PAPI_ON)
    include_directories(lib/papi/src)
    link_directories(lib/papi/src lib/papi/src/libpfm4/lib)
endif()

set(TACO_ON, "true")
if (TACO_ON)
    link_directories(lib/taco/lib)
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O3")
add_library(polylib SHARED ${EDSL_FILES} ${IEGEN_FILES} ${ISL_FILES} ${OMEGA_FILES})

if (TESTING)
    set(GTEST_FILES lib/gtest/src/gtest.cc
                    lib/gtest/src/gtest-filepath.cc
                    lib/gtest/src/gtest-death-test.cc
                    lib/gtest/src/gtest-test-part.cc
                    lib/gtest/src/gtest-printers.cc
                    lib/gtest/src/gtest-port.cc
    )

    set(UNIT_TESTS test/driver.cpp test/eDSLTest.cpp test/BenchmarkTest.hpp test/InspExecTest.hpp)
    #       test/ConjGradTest.hpp test/ConjGradCOOTest.cpp test/ConjGradCSRTest.cpp test/ConjGradDSRTest.cpp
    #       test/ConjGradELLTest.cpp test/ConjGradCSBTest.cpp test/ConjGradDIATest.cpp test/JacobiTest.cpp
    #       test/MiniFluxDivTest.cpp test/TensorDecompTest.hpp test/TensorDecompTestCOO.cpp
    #       test/TensorDecompTestCSF.cpp test/TensorDecompTestHiCOO.cpp) # test/TensAlgCompTest.cpp)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -fopenmp -ftree-vectorize -funroll-all-loops")

    enable_testing()
    add_executable(edslTest ${UNIT_TESTS} ${GTEST_FILES} ${EDSL_FILES})

    target_link_libraries(edslTest m polylib)# omp gsl gslcblas)
    if (PAPI_ON)
        target_link_libraries(edslTest papi pfm)
        target_compile_definitions(edslTest PRIVATE PAPI_ON=1)
    #else()
    #    target_link_libraries(edslTest likwid) # taco) # cudart) # blas lapack lapacke splatt)
    endif()

    #target_link_libraries(edslTest ${LINK_LIBS})
    add_test(driver eDSLTest) # ConjGradCOOTest ConjGradCSRTest TensorDecompTest) #TensAlgCompTest) # JacobiTest)
    #add_test(driver ConjGradCOOTest ConjGradCSRTest)# TensorDecompTest)

#elseif (MAKELIB)
#    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O3")
#    add_library(polylib SHARED ${EDSL_FILES} ${IEGEN_FILES} ${ISL_FILES} ${OMEGA_FILES})

elseif (PARBUILD)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp -ftree-vectorize -funroll-all-loops -O3")
    #find_package(MPI REQUIRED)
    #include_directories(${MPI_INCLUDE_PATH})
    add_executable(cg_par test/cg_par.cpp)
    target_link_libraries(cg_par m omp) #${MPI_LIBRARIES})
    #target_compile_definitions(cg_par PRIVATE LIKWID_PERF=1)

    add_executable(cp_par test/cp_par.cpp)
    target_link_libraries(cp_par m omp gsl gslcblas)

else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O3 -Wno-deprecated -Wno-deprecated-declarations -Wno-format-overflow")
    set(DRIVER src/main.cpp)
    add_executable(edsl ${DRIVER} ${EDSL_FILES}) # ${IEGEN_FILES} ${ISL_FILES} ${OMEGA_FILES})
    target_link_libraries(edsl m polylib)
endif()
