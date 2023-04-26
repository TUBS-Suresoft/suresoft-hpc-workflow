load_modules() {
    module purge
    module load singularity/3.9.9
    module load mpi/mpich/mpich_3.2
    module list
}

echo_slurm_parameters() {
    echo "SLURM_JOBID=$SLURM_JOBID"
    echo "SLURM_JOB_NODELIST=$SLURM_JOB_NODELIST"
    echo "SLURM_NNODES=$SLURM_NNODES"
    echo "SLURM_TASKS_PER_NODE=$SLURM_TASKS_PER_NODE"
    echo "working directory = $SLURM_SUBMIT_DIR"
    echo ""
}