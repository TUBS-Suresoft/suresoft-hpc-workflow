# Laplace2d

[![Matrix](https://img.shields.io/matrix/suresoft-general:matrix.org?server_fqdn=matrix.org)](https://matrix.to/#/#suresoft-general:matrix.org)


## Introduction
This project includes an applications of a 2D Laplace heat transfer in a plate. It is developed as a showcase for the [SURESOFT](https://www.tu-braunschweig.de/suresoft) workflow addressing reproducibiblity on HPC platforms.

## Workflow
The workflow is grouped into three [jobs](.gitlab-ci.yml) in the Continuous Integration pipeline using GitLab CI.





## Prerequiste
-  priviliged gitlab runner available in project


## Actors
### .gitlab-ci.yml
1. builds singularity image basesd on Containers/rockylinux9-mpich.def
2. copy image with hpc-rocket to cluster (rocket.yml) and submit slurm job (laplace.job)
   - before add REMOTE_HOST, REMOTE_USER and REMOTE_PASSWORD (or PRIVATE_KEY) according to variable names in rocket.yml to gitlab CI project settings

### Containers/rockylinux9-mpich.def
- defines singularity image
- defines executing of laplace binary

### rocket.yml
- defines files to copy to cluster
- defines result files to copy back to gitlab
- defines slurm job file to submit

### laplace.job
- slurm settings
- executes singularity image


## Output data

As a result the executables will write [UCD](https://dav.lbl.gov/archive/NERSC/Software/express/help6.1/help/reference/dvmac/UCD_Form.htm) files into the build directory. Those files can be viewed with e.g. [Paraview](https://www.paraview.org/).

![VirtualFluids](img/laplace2d.png)
