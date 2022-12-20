build-container:
	docker run --privileged --rm -v ${PWD}:/home/singularity -w /home/singularity quay.io/singularity/singularity:v3.10.4-arm64 build --force Containers/rockylinux9-mpich.sif Containers/rockylinux9-mpich.def

run-container:
	docker run --privileged --rm -v ${PWD}:/home/singularity -w /home/singularity quay.io/singularity/singularity:v3.10.4-arm64 run --app laplace Containers/rockylinux9-mpich.sif