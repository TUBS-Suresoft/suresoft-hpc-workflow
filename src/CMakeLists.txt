

# MPI Parallel
find_package(MPI)
if(MPI_FOUND)
    add_executable(laplace main.cpp)
    target_link_libraries(laplace PUBLIC compiler_flags MPI::MPI_CXX)

    message(STATUS "MPI example added.")
else()
    message(STATUS "MPI not found. Skip example.")
endif()

