#ifndef PARAMETER_H
#define PARAMETER_H

struct SimulationParameter
{
    SimulationParameter() = default;

    size_t gridNx = 4096;
    size_t gridNy = 4096;

    double bcTop = 15.0;
    double bcBottom = 5.0;
    double bcLeft = 0.0;
    double bcRight = 9.0;

    size_t outputInterval = 1000;

    const double error = 1.0e-3;

    const char* outputFileName = "results/TemperatureField.avs";
};

#endif
