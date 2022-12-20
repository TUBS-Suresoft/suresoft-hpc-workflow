#ifndef UCD_FILE_WRITER_H
#define UCD_FILE_WRITER_H

#include <string>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <chrono>

#include "Mapper2D.h"


class Timer 
{
public:
    Timer() 
    {
        startRuntime = std::chrono::high_resolution_clock::now();
    }

    size_t getRuntimeSeconds() const
    {
        std::chrono::duration<double> diff = std::chrono::high_resolution_clock::now() - startRuntime;
        return (size_t)diff.count();
    }

    void startNupsTimer()
    {
        startNupsTime = std::chrono::high_resolution_clock::now();
    }

    size_t getMNups(long updated_nodes) const
    {
        return calculateMNups(updated_nodes, startNupsTime);
    }

    size_t calculateMNups(long updated_nodes, std::chrono::time_point<std::chrono::high_resolution_clock> startTime) const
    {
        // MNUPS = Million Node Updates per Second
        std::chrono::duration<double> diff = std::chrono::high_resolution_clock::now() - startTime;
        return (size_t)((double)updated_nodes / diff.count() / 1E6);
    }

    size_t getMNupsForEntireRuntime(long updated_nodes) const
    {
        return calculateMNups(updated_nodes, startRuntime);
    }

private:
    std::chrono::time_point<std::chrono::high_resolution_clock> startRuntime;
    std::chrono::time_point<std::chrono::high_resolution_clock> startNupsTime;
};

double calcError(const double* oldData, const double* newData, Mapper2D grid)
{
    double error = 0.;
    for(unsigned long i = 0; i < grid.size(); i++)
    {
        const double diff = newData[i] - oldData[i];
        error = error + diff * diff;
    }
    return error;
}

double calcError(const std::vector<double>& oldData, const std::vector<double>& newData, Mapper2D grid)
{
    return calcError(oldData.data(), newData.data(), grid);
}


void writeUCDFile(const char* filename, const double *temperature, Mapper2D const &domain)
{
    const size_t Lx = domain.nx();
    const size_t Hy = domain.ny();
    std::fstream fp;
    fp << std::setprecision(15);
    const size_t numberOfNodes = Lx * Hy;
    const size_t numberOfElements = (Lx - 1) * (Hy - 1);
    const int datasize = 1;

    fp.open(filename, std::ios::out | std::ios::trunc);

    if (!fp)
    {
        std::cout << " Error opening the file " << filename << "\n";
        exit(1);
    }

    fp << numberOfNodes << " " << numberOfElements << " " << datasize << " 0 0 " << std::endl;
    for (size_t i = 1; i <= numberOfNodes; i++)
    {
        const size_t column = (i - 1) % Lx;
        const size_t row = (i - 1) / Lx;
        fp << i << " " << column << "  " << row << "  0.0\n";
    }

    for (size_t i = 1; i <= numberOfElements; i++)
    {
        const size_t row = (i - 1) / (Lx - 1);
        const size_t column = (i - 1) % (Lx - 1);

        fp << i << " 1 quad " << row * Lx + column + 1 << " " << row * Lx + column + 2 << " " << (row + 1) * Lx + column + 2 << "  " << (row + 1) * Lx + column + 1 << "\n";
    }

    fp << "1 1 \nT,no_unit\n";

    for (size_t j = 1; j <= Hy; j++)
        for (size_t i = 1; i <= Lx; i++)
        {
            const size_t position = domain.pos(i - 1, j - 1);
            const double T = temperature[position];

            fp << position + 1 << " " << T << "\n";
        }
    fp.close();
}

void writeUCDFile(const char* filename, const std::vector<double>& temperature, Mapper2D const &domain)
{
    writeUCDFile(filename, temperature.data(), domain);
}

#endif
