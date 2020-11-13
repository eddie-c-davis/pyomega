cmake_minimum_required(VERSION 3.15)
project(pybind11_wrap)

set(CMAKE_CXX_STANDARD 11)

add_library(pybind11_wrap SHARED src/pybind11.cpp src/pybind11.h)
