#include <string>
#include <iostream>
#include <vector>

#include <mpi.h>

#include "Mapper2D.h"
#include "Parameter.h"
#include "utilities.h"

int main()
{
    Timer timer;

    constexpr SimulationParameter parameter;

    // The fixed number of partitions in x an y direction, e.g. 2x2 = 4
    // The total number of processes has to match the call of mpirun. 
    // In this case: mpirun -np 4 ./Laplace_mpi
    constexpr int numPartsX = 1;
    constexpr int numPartsY = 1;

    constexpr int localNx = parameter.gridNx / numPartsX; //division using integers -> not precise
    constexpr int localNy = parameter.gridNy / numPartsY;

    // -> hence, we calculate the effective numbers again
    // constexpr int realGridNx = localNx * numPartsX;
    // constexpr int realGridNy = localNy * numPartsY;

    constexpr Mapper2D innerGrid(localNx, localNy);

    /* do parallelisation from here on ... */

    /* How to derive the 2D-process number form the 1D-MPI-rank:
    ...
    Mapper2D processTopology = Mapper2D(numPartsX, numPartsY);
    int myXRank = processTopology.xForPos(myRank);
    int myYRank = processTopology.yForPos(myRank);
    ...
    */

    // The entire grid has a ghost layer on each side.
    constexpr Mapper2D entireGrid(innerGrid.nx() + 2, innerGrid.ny() + 2);

    /* receive buffers for ghost layer data */
    double *leftReceiveBuffer   = new double[innerGrid.ny()];
    double *rightReceiveBuffer  = new double[innerGrid.ny()];
    double *topReceiveBuffer    = new double[innerGrid.nx()];
    double *bottomReceiveBuffer = new double[innerGrid.nx()];

    /* send buffers */
    /* double* leftSendBuffer = new double[entireGrid.ny()-2]; */
    /* ... */

    std::vector<double> oldData (entireGrid.size());
    std::vector<double> newData (entireGrid.size());

    /* initialization */
    for (size_t i = 0; i < entireGrid.size(); i++)
        oldData[i] = 0.0;

    /* In the parallel version also initialize send buffers here ... */

    /* In the parallel version the following variables need to be calculated. The name "cell" is an equivalent for process. */
    bool isLeftBoundaryCell = true;
    bool isRightBoundaryCell = true;
    bool isBottomBoundaryCell = true;
    bool isTopBoundaryCell = true;

    /* set boundary conditions ... */
    if (isLeftBoundaryCell)
        for (size_t i = 0; i < innerGrid.ny(); i++)
            leftReceiveBuffer[i] = parameter.bcLeft;

    if (isRightBoundaryCell)
        for (size_t i = 0; i < innerGrid.ny(); i++)
            rightReceiveBuffer[i] = parameter.bcRight;

    if (isTopBoundaryCell)
        for (size_t i = 0; i < innerGrid.nx(); i++)
            topReceiveBuffer[i] = parameter.bcTop;

    if (isBottomBoundaryCell)
        for (size_t i = 0; i < innerGrid.nx(); i++)
            bottomReceiveBuffer[i] = parameter.bcBottom;

    int iteration = 0;

    timer.startNupsTimer();

    /* iteration */
    bool done = false;
    while (!done)
    {
        double error = 0.0;
        double diff;
        /* in the parallel version: Do the send and receive here. Prefer doing it in the background (nonblocking / async). Watch out for deadlocks! */
        /* ... */

        /* first do the calculations without the ghost layers */
        for (size_t y = 2; y < entireGrid.ny() - 2; y++)
            for (size_t x = 2; x < entireGrid.nx() - 2; x++)
            {
                newData[entireGrid.pos(x, y)] = 0.25 * (oldData[entireGrid.pos(x - 1, y)] +
                                                        oldData[entireGrid.pos(x + 1, y)] +
                                                        oldData[entireGrid.pos(x, y - 1)] +
                                                        oldData[entireGrid.pos(x, y + 1)]);
                diff = newData[entireGrid.pos(x, y)] - oldData[entireGrid.pos(x, y)];
                error = error + diff * diff;
            }

        /* now ghost layers should have been received ... */

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
            error = error + diff * diff;
            /* myTopSendBuffer[i-1] = newData[entireGrid.pos(i,1)];*/

            // bottom
            newData[entireGrid.pos(x, entireGrid.ny() - 2)] = 0.25 * (oldData[entireGrid.pos(x - 1, entireGrid.ny() - 2)] +
                                                                         oldData[entireGrid.pos(x + 1, entireGrid.ny() - 2)] +
                                                                         oldData[entireGrid.pos(x, entireGrid.ny() - 3)] +
                                                                         oldData[entireGrid.pos(x, entireGrid.ny() - 1)]);
            diff = newData[entireGrid.pos(x, entireGrid.ny() - 2)] - oldData[entireGrid.pos(x, entireGrid.ny() - 2)];
            error = error + diff * diff;
            /* myBottomSendBuffer[i-1] = newData[entireGrid.pos(i,entireGrid.ny()-2)];*/
        }

        /* Insert corners */
        /*leftSendBuffer[0] = newData[entireGrid.pos(1,1)];
        leftSendBuffer[entireGrid.ny()-3] = newData[entireGrid.pos(1,entireGrid.ny()-2)];
        rightSendBuffer[0] = newData[entireGrid.pos(entireGrid.nx()-2,1)];
        rightSendBuffer[entireGrid.ny()-3] = newData[entireGrid.pos(entireGrid.nx()-2,entireGrid.ny()-2)];*/
        for (size_t y = 2; y < entireGrid.ny() - 2; y++)
        {
            newData[entireGrid.pos(1, y)] = 0.25 * (oldData[entireGrid.pos(1, y - 1)] +
                                                    oldData[entireGrid.pos(1, y + 1)] +
                                                    oldData[entireGrid.pos(0, y)] +
                                                    oldData[entireGrid.pos(2, y)]);
            diff = newData[entireGrid.pos(1, y)] - oldData[entireGrid.pos(1, y)];
            error = error + diff * diff;
            /* leftSendBuffer[j-1] = newData[entireGrid.pos(1,j)];*/

            newData[entireGrid.pos(entireGrid.nx() - 2, y)] = 0.25 * (oldData[entireGrid.pos(entireGrid.nx() - 3, y)] +
                                                                         oldData[entireGrid.pos(entireGrid.nx() - 1, y)] +
                                                                         oldData[entireGrid.pos(entireGrid.nx() - 2, y - 1)] +
                                                                         oldData[entireGrid.pos(entireGrid.nx() - 2, y + 1)]);
            diff = newData[entireGrid.pos(entireGrid.nx() - 2, y)] - oldData[entireGrid.pos(entireGrid.nx() - 2, y)];
            error = error + diff * diff;
            /* rightSendBuffer[j-1] = newData[entireGrid.pos(entireGrid.nx()-2,j)];*/
        }

        std::swap(oldData, newData);

        /* Stop in case of little change */
        done = (error < 1.0e-4);

        iteration++;
        if ((iteration % parameter.outputInterval) == 0)
        {
            const auto mnups = timer.getMNups(innerGrid.size() * parameter.outputInterval);
            std::cout << "time step: " << iteration << " error: " << error << " MNUPS: " << mnups << "\n";

            timer.startNupsTimer();
        }
    }

    /* Output (Only process 0. In the parallel case process 0 needs to collect the necessary data for the output from the other processes. */

    // if (myRank == 0)
    // {
    //     double *resultData = new double[realGridNx * realGridNy];
    //     Mapper2D globalGrid = Mapper2D(realGridNx, realGridNy);
    //     for (size_t x = 1; x < entireGrid.nx() - 1; x++)
    //         for (size_t y = 1; y < entireGrid.ny() - 1; y++)
    //             resultData[globalGrid.pos(x - 1, y - 1)] = oldData[entireGrid.pos(x, y)];

    //     for (int partX = 0; partX < numPartsX; partX++)
    //         for (int partY = 0; partY < numPartsY; partY++)
    //             if (partX || partY) //if (!(i==0 && j==0)
    //             {
    //                 std::cout << "Partition X = " << partX << ", Partition Y = " << partY << std::endl;
    //                 for (size_t y = 0; y < entireGrid.ny() - 2; y++) // line by line
    //                     MPI_Recv(resultData + globalGrid.pos(partX * localNx, partY * localNy + y), entireGrid.nx() - 2, MPI_DOUBLE, processTopology.pos(partX, partY), 0, MPI_COMM_WORLD, &status);
    //             }
    //     writeUCDFile(parameter.outputFileName, resultData, globalGrid);
    //     delete[] resultData;
    // }
    // else
    // {
    //     for (size_t y = 1; y < entireGrid.ny() - 1; y++) // line by line
    //         MPI_Ssend(oldData.data() + entireGrid.pos(1, y), entireGrid.nx() - 2, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
    // }

    const auto runtime = timer.getRuntimeSeconds();
    std::cout << "Runtime: " << runtime << " s. " << std::endl;
    std::cout << "Average MNUPS: " << timer.getMNupsForEntireRuntime(innerGrid.size() * iteration) << std::endl;

    /* in case of parallel processing remove this line */
    writeUCDFile(parameter.outputFileName, oldData, entireGrid);

    delete[] leftReceiveBuffer;
    delete[] rightReceiveBuffer;
    delete[] topReceiveBuffer;
    delete[] bottomReceiveBuffer;

    return 0;
}
