

# MPI Parallel
find_package(MPI)
if(MPI_FOUND)
    add_executable(Laplace2D_mpi_blocking main_mpi_blocking.cpp)
    target_link_libraries(Laplace2D_mpi_blocking PUBLIC compiler_flags MPI::MPI_CXX)

    add_executable(Laplace2D_mpi_non_blocking main_mpi_non_blocking.cpp)
    target_link_libraries(Laplace2D_mpi_non_blocking PUBLIC compiler_flags MPI::MPI_CXX)

    message(STATUS "MPI example added.")
else()
    message(STATUS "MPI not found. Skip example.")
endif()

