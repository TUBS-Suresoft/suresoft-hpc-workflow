FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    git \
    mpich \
    cmake

# Add non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID usergroup\
   && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

ENV SHELL /bin/bash