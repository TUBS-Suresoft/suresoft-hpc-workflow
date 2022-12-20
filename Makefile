build-container:
	docker run --privileged --rm -v ${PWD}:/home/singularity -w /home/singularity quay.io/singularity/singularity:v3.10.4-arm64 build --force Containers/MPICHCentOS.sif Containers/MPICHCentOS.def

run-container:
	docker run --privileged --rm -v ${PWD}:/home/singularity -w /home/singularity quay.io/singularity/singularity:v3.10.4-arm64 run --app laplace Containers/MPICHCentOS.sif