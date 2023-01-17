#include <string>
#include <iostream>
#include <vector>
#include <cassert>

#include <mpi.h>

#include "Mapper2D.h"
#include "Parameter.h"
#include "utilities.h"

int main(int argc, char **argv)
{
    Timer timer;

    SimulationParameter parameter;

    // The fixed number of partitions in x an y direction, e.g. 2x2 = 4
    // The total number of processes has to match the call of mpirun. 
    // In this case: mpirun -np 4 ./Laplace_mpi

    if (argc < 3) {
        std::cout << "Usage: mpirun -np <numPartsX * numPartsY> ./Laplace_mpi <numPartsX> <numPartsY>" << std::endl;
        return 1;
    }

    if(argc == 5) {
        parameter.gridNx = std::stod(argv[3]);
        parameter.gridNy = std::stod(argv[4]);
    }

    const int numPartsX = std::stoi(argv[1]);
    const int numPartsY = std::stoi(argv[2]);

    std::cout << "Run simulation with grid size: " << parameter.gridNx  << " x " << parameter.gridNy << std::endl;

    const int localNx = parameter.gridNx / numPartsX; //division using integers -> not precise
    const int localNy = parameter.gridNy / numPartsY;

    // -> hence, we calculate the effective numbers again
    // we need the numbers to collect all data in the end.
    const int realGridNx = localNx * numPartsX;
    const int realGridNy = localNy * numPartsY;

    const Mapper2D innerGrid(localNx, localNy);
 
    /* do parallelisation from here on ... */
    int numProcs, myRank;
    MPI_Status status;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &numProcs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myRank);

    std::cout << "Process " << myRank << ". App runs with processes: " << numProcs << " [" << numPartsX << " x " << numPartsY << "]\n";
    
    assert(numProcs == numPartsX * numPartsY);

    const Mapper2D processTopology = Mapper2D(numPartsX, numPartsY);
    int myRankX = processTopology.xForPos(myRank);
    int myRankY = processTopology.yForPos(myRank);

    // The entire grid has a ghost layer on each side.
    const Mapper2D entireGrid(innerGrid.nx() + 2, innerGrid.ny() + 2);

    /* receive buffers for ghost layer data */
    double *leftReceiveBuffer   = new double[innerGrid.ny()];
    double *rightReceiveBuffer  = new double[innerGrid.ny()];
    double *topReceiveBuffer    = new double[innerGrid.nx()];
    double *bottomReceiveBuffer = new double[innerGrid.nx()];

    /* send buffers */
    double *leftSendBuffer   = new double[innerGrid.ny()];
    double *rightSendBuffer  = new double[innerGrid.ny()];
    double *topSendBuffer    = new double[innerGrid.nx()];
    double *bottomSendBuffer = new double[innerGrid.nx()];

    std::vector<double> oldData (entireGrid.size());
    std::vector<double> newData (entireGrid.size());

    /* initialization */
    for (size_t i = 0; i < entireGrid.size(); i++)
        oldData[i] = 0.0;

    /* In the parallel version also initialize send buffers here ... */
    for (size_t x = 1; x < entireGrid.nx() - 1; x++)
    {
        topSendBuffer[x - 1] = oldData[entireGrid.pos(x, 1)]; // 0.0
        bottomSendBuffer[x - 1] = oldData[entireGrid.pos(x, entireGrid.ny() - 2)]; // 0.0
    }

    for (size_t y = 1; y < entireGrid.ny() - 1; y++)
    {
        leftSendBuffer[y - 1] = oldData[entireGrid.pos(1, y)]; // 0.0
        rightSendBuffer[y - 1] = oldData[entireGrid.pos(entireGrid.nx() - 2, y)]; // 0.0
    }

    /* In the parallel version the following variables need to be calculated. The name "cell" is an equivalent for process. */
    bool isLeftBoundaryCell   = (myRankX == 0);
    bool isRightBoundaryCell  = (myRankX == numPartsX - 1);
    bool isBottomBoundaryCell = (myRankY == numPartsY - 1);
    bool isTopBoundaryCell    = (myRankY == 0);

    /* set boundary conditions ... */
    if (isLeftBoundaryCell)
        for (size_t y = 0; y < innerGrid.ny(); y++)
            leftReceiveBuffer[y] = parameter.bcLeft;

    if (isRightBoundaryCell)
        for (size_t y = 0; y < innerGrid.ny(); y++)
            rightReceiveBuffer[y] = parameter.bcRight;

    if (isTopBoundaryCell)
        for (size_t x = 0; x < innerGrid.nx(); x++)
            topReceiveBuffer[x] = parameter.bcTop;

    if (isBottomBoundaryCell)
        for (size_t x = 0; x < innerGrid.nx(); x++)
            bottomReceiveBuffer[x] = parameter.bcBottom;

    int iteration = 0;

    timer.startNupsTimer();

    MPI_Request request;
    MPI_Request requests[8];
    /*Iteration*/
    bool done = false;
    while (!done)
    {
        double err = 0.0, err_global;
        double diff;

        /* in the parallel version: Do the send and receive here. Prefer doing it in the background (nonblocking / async). Watch out for deadlocks! */

        // even exchanges with right:
        if (myRankX % 2 == 0)
        {
            if (!isRightBoundaryCell)
            {
                MPI_Isend(rightSendBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX + 1, myRankY), 0, MPI_COMM_WORLD, &request);
                MPI_Irecv(rightReceiveBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX + 1, myRankY), 0, MPI_COMM_WORLD, &requests[0]);
            }
        }
        // odd exchanges with left
        else
        {
            if (!isLeftBoundaryCell)
            {
                MPI_Irecv(leftReceiveBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX - 1, myRankY), 0, MPI_COMM_WORLD, &requests[1]);
                MPI_Isend(leftSendBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX - 1, myRankY), 0, MPI_COMM_WORLD, &request);
            }
        }

        // even exchanges with left:
        if (myRankX % 2 == 0)
        {
            if (!isLeftBoundaryCell)
            {
                MPI_Isend(leftSendBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX - 1, myRankY), 0, MPI_COMM_WORLD, &request);
                MPI_Irecv(leftReceiveBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX - 1, myRankY), 0, MPI_COMM_WORLD, &requests[2]);
            }
        }
        // odd exchanges with right
        else
        {
            if (!isRightBoundaryCell)
            {
                MPI_Irecv(rightReceiveBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX + 1, myRankY), 0, MPI_COMM_WORLD, &requests[3]);
                MPI_Isend(rightSendBuffer, innerGrid.ny(), MPI_DOUBLE, processTopology.pos(myRankX + 1, myRankY), 0, MPI_COMM_WORLD, &request);
            }
        }
        // even exchanges with bottom:
        if (myRankY % 2 == 0)
        {
            if (!isBottomBoundaryCell)
            {
                MPI_Isend(bottomSendBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY + 1), 0, MPI_COMM_WORLD, &request);
                MPI_Irecv(bottomReceiveBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY + 1), 0, MPI_COMM_WORLD, &requests[4]);
            }
        }
        // odd exchanges with top
        else
        {
            if (!isTopBoundaryCell)
            {
                MPI_Irecv(topReceiveBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY - 1), 0, MPI_COMM_WORLD, &requests[5]);
                MPI_Isend(topSendBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY - 1), 0, MPI_COMM_WORLD, &request);
            }
        }

        // even exchanges with top:
        if (myRankY % 2 == 0)
        {
            if (!isTopBoundaryCell)
            {
                MPI_Isend(topSendBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY - 1), 0, MPI_COMM_WORLD, &request);
                MPI_Irecv(topReceiveBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY - 1), 0, MPI_COMM_WORLD, &requests[6]);
            }
        }
        // odd exchanges with bottom
        else
        {
            if (!isBottomBoundaryCell)
            {
                MPI_Irecv(bottomReceiveBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY + 1), 0, MPI_COMM_WORLD, &requests[7]);
                MPI_Isend(bottomSendBuffer, innerGrid.nx(), MPI_DOUBLE, processTopology.pos(myRankX, myRankY + 1), 0, MPI_COMM_WORLD, &request);
            }
        }

        /* first do the calculations without the ghost layers */
        for (size_t y = 2; y < entireGrid.ny() - 2; y++)
            for (size_t x = 2; x < entireGrid.nx() - 2; x++)
            {
                newData[entireGrid.pos(x, y)] = 0.25 * (oldData[entireGrid.pos(x - 1, y)] +
                                                       oldData[entireGrid.pos(x + 1, y)] +
                                                       oldData[entireGrid.pos(x, y - 1)] +
                                                       oldData[entireGrid.pos(x, y + 1)]);
                diff = newData[entireGrid.pos(x, y)] - oldData[entireGrid.pos(x, y)];
                err = err + diff * diff;
            }

        /* now ghost layers should have been received ... */
        MPI_Barrier(MPI_COMM_WORLD);



        if (myRankX % 2 == 0)
        {
            if (!isRightBoundaryCell)
            {
                MPI_Wait(&requests[0], MPI_STATUS_IGNORE);
            }
        }
        // odd exchanges with left
        else
        {
            if (!isLeftBoundaryCell)
            {
                MPI_Wait(&requests[1], MPI_STATUS_IGNORE);
            }
        }

        // even exchanges with left:
        if (myRankX % 2 == 0)
        {
            if (!isLeftBoundaryCell)
            {
                MPI_Wait(&requests[2], MPI_STATUS_IGNORE);
            }
        }
        // odd exchanges with right
        else
        {
            if (!isRightBoundaryCell)
            {
                MPI_Wait(&requests[3], MPI_STATUS_IGNORE);
            }
        }
        // even exchanges with bottom:
        if (myRankY % 2 == 0)
        {
            if (!isBottomBoundaryCell)
            {
                MPI_Wait(&requests[4], MPI_STATUS_IGNORE);
            }
        }
        // odd exchanges with top
        else
        {
            if (!isTopBoundaryCell)
            {
                MPI_Wait(&requests[5], MPI_STATUS_IGNORE);
            }
        }

        // even exchanges with top:
        if (myRankY % 2 == 0)
        {
            if (!isTopBoundaryCell)
            {
                MPI_Wait(&requests[6], MPI_STATUS_IGNORE);
            }
        }
        // odd exchanges with bottom
        else
        {
            if (!isBottomBoundaryCell)
            {
                MPI_Wait(&requests[7], MPI_STATUS_IGNORE);
            }
        }


        /* insert ghost layers */
        for (size_t x = 1; x < entireGrid.nx() - 1; x++)
        {
            oldData[entireGrid.pos(x, 0)] = topReceiveBuffer[x - 1];
            oldData[entireGrid.pos(x, entireGrid.ny() - 1)] = bottomReceiveBuffer[x - 1];
        }

        for (size_t y = 1; y < entireGrid.ny() - 1; y++)
        {
            oldData[entireGrid.pos(0, y)] = leftReceiveBuffer[y - 1];
            oldData[entireGrid.pos(entireGrid.nx() - 1, y)] = rightReceiveBuffer[y - 1];
        }

        /* Now do the rest of the calculation including the ghost layers. */
        for (size_t x = 1; x < entireGrid.nx() - 1; x++)
        {
            // top
            newData[entireGrid.pos(x, 1)] = 0.25 * (oldData[entireGrid.pos(x - 1, 1)] +
                                                   oldData[entireGrid.pos(x + 1, 1)] +
                                                   oldData[entireGrid.pos(x, 0)] +
                                                   oldData[entireGrid.pos(x, 2)]);
            diff = newData[entireGrid.pos(x, 1)] - oldData[entireGrid.pos(x, 1)];
            err = err + diff * diff;
            topSendBuffer[x - 1] = newData[entireGrid.pos(x, 1)];

            // bottom
            newData[entireGrid.pos(x, entireGrid.ny() - 2)] = 0.25 * (oldData[entireGrid.pos(x - 1, entireGrid.ny() - 2)] +
                                                            oldData[entireGrid.pos(x + 1, entireGrid.ny() - 2)] +
                                                            oldData[entireGrid.pos(x, entireGrid.ny() - 3)] +
                                                            oldData[entireGrid.pos(x, entireGrid.ny() - 1)]);
            diff = newData[entireGrid.pos(x, entireGrid.ny() - 2)] - oldData[entireGrid.pos(x, entireGrid.ny() - 2)];
            err = err + diff * diff;
            bottomSendBuffer[x - 1] = newData[entireGrid.pos(x, entireGrid.ny() - 2)];
        }
        /* Insert corners */
        // Not necessary, as the calculation stamp only takes into account the top, bottom, left and right node
        // leftSendBuffer[0] = newData[entireGrid.pos(1,1)];
        // leftSendBuffer[entireGrid.ny()-3] = newData[entireGrid.pos(1,entireGrid.ny()-2)];
        // rightSendBuffer[0] = newData[entireGrid.pos(entireGrid.nx()-2,1)];
        // rightSendBuffer[entireGrid.ny()-3] = newData[entireGrid.pos(entireGrid.nx()-2,entireGrid.ny()-2)];
        //for (int j=2; j<entireGrid.ny()-2; j++)
        for (size_t y = 1; y < entireGrid.ny() - 1; y++)
        {
            newData[entireGrid.pos(1, y)] = 0.25 * (oldData[entireGrid.pos(1, y - 1)] +
                                                   oldData[entireGrid.pos(1, y + 1)] +
                                                   oldData[entireGrid.pos(0, y)] +
                                                   oldData[entireGrid.pos(2, y)]);
            diff = newData[entireGrid.pos(1, y)] - oldData[entireGrid.pos(1, y)];
            err = err + diff * diff;
            leftSendBuffer[y - 1] = newData[entireGrid.pos(1, y)];

            newData[entireGrid.pos(entireGrid.nx() - 2, y)] = 0.25 * (oldData[entireGrid.pos(entireGrid.nx() - 3, y)] +
                                                            oldData[entireGrid.pos(entireGrid.nx() - 1, y)] +
                                                            oldData[entireGrid.pos(entireGrid.nx() - 2, y - 1)] +
                                                            oldData[entireGrid.pos(entireGrid.nx() - 2, y + 1)]);
            diff = newData[entireGrid.pos(entireGrid.nx() - 2, y)] - oldData[entireGrid.pos(entireGrid.nx() - 2, y)];
            err = err + diff * diff;
            rightSendBuffer[y - 1] = newData[entireGrid.pos(entireGrid.nx() - 2, y)];
        }

        std::swap(oldData, newData);

        /* Stop in case of little change */
        //Allreduce = reduce + broadcast
        MPI_Allreduce(&err, &err_global, 1, MPI_DOUBLE,
                      MPI_SUM, MPI_COMM_WORLD);
        done = (err_global < parameter.error);

        iteration++;
        if (myRank == 0 && (iteration % parameter.outputInterval == 0))
        {
            const auto mnups = timer.getMNups(innerGrid.size() * parameter.outputInterval);

            std::cout << "time step: " << iteration << " error: " << err_global << " MNUPS: " << mnups << "\n";

            timer.startNupsTimer();
        }
    }

    if (myRank == 0)
    {
        const auto runtime = timer.getRuntimeSeconds();
        std::cout << "Runtime: " << runtime << " s. " << std::endl;
        std::cout << "Average MNUPS: " << timer.getMNupsForEntireRuntime(innerGrid.size() * iteration) << std::endl;
    }

    /* Output (only process 0. In the parallel case, it must of course still receive the data from all other processes - without the Ghostlayer. Here programmed out, alternatively MPI_Gather can be used. */

    if (myRank == 0)
    {
        double *resultData = new double[realGridNx * realGridNy];
        Mapper2D globalGrid = Mapper2D(realGridNx, realGridNy);
        for (size_t x = 1; x < entireGrid.nx() - 1; x++)
            for (size_t y = 1; y < entireGrid.ny() - 1; y++)
                resultData[globalGrid.pos(x - 1, y - 1)] = oldData[entireGrid.pos(x, y)];

        for (int partX = 0; partX < numPartsX; partX++)
            for (int partY = 0; partY < numPartsY; partY++)
                if (partX || partY) //if (!(i==0 && j==0)
                {
                    // std::cout << "Partition X = " << partX << ", Partition Y = " << partY << std::endl;
                    for (size_t y = 0; y < entireGrid.ny() - 2; y++) // line by line
                        MPI_Recv(resultData + globalGrid.pos(partX * localNx, partY * localNy + y), entireGrid.nx() - 2, MPI_DOUBLE, processTopology.pos(partX, partY), 0, MPI_COMM_WORLD, &status);
                }
        writeUCDFile(parameter.outputFileName, resultData, globalGrid);
        delete[] resultData;
    }
    else
    {
        for (size_t y = 1; y < entireGrid.ny() - 1; y++) // line by line
            MPI_Ssend(oldData.data() + entireGrid.pos(1, y), entireGrid.nx() - 2, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
    }

    delete[] leftReceiveBuffer;
    delete[] rightReceiveBuffer;
    delete[] topReceiveBuffer;
    delete[] bottomReceiveBuffer;

    delete[] leftSendBuffer;
    delete[] rightSendBuffer;
    delete[] topSendBuffer;
    delete[] bottomSendBuffer;


    MPI_Barrier(MPI_COMM_WORLD);

    MPI_Finalize();

    return 0;
}
