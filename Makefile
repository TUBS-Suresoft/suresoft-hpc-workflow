DEF?=Containers/rockylinux9-mpich
IMG:=quay.io/singularity/singularity:v3.10.4


ifneq '$(strip $(shell uname -m))' 'x86_64'
IMG:=${IMG}-arm64
endif

build-container:
	@echo $(shell uname -m)
	docker run --privileged --rm -v ${PWD}:/home/singularity -w /home/singularity ${IMG} build --force ${DEF}.sif ${DEF}.def

run-container:
	docker run --privileged --rm -v ${PWD}:/home/singularity -w /home/singularity ${IMG} run --app laplace Containers/rockylinux9-mpich.sif