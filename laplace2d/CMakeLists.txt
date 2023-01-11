cmake_minimum_required(VERSION 3.15)

project(Laplace2D CXX)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

add_library(compiler_flags INTERFACE)

target_compile_options(compiler_flags INTERFACE -Wall -Wextra -pedantic -Werror -O1)

add_subdirectory(src)

