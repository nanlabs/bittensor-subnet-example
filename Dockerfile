FROM opentensor/subtensor:latest as subtensor

# show backtraces
ENV RUST_BACKTRACE 1

# Necessary libraries for Rust execution
RUN apt-get update && \
    apt-get install -y curl build-essential protobuf-compiler clang git netcat && \
    rm -rf /var/lib/apt/lists/*

# Install cargo and Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

FROM subtensor AS subtensor-dev

# Options for setup script
ARG INSTALL_ZSH="true"
ARG UPGRADE_PACKAGES="false"
ARG USERNAME=devcontainer
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV EDITOR code

# Install needed packages and setup non-root user. Use a separate RUN statement to add your own dependencies.
COPY .devcontainer/common-debian.sh /tmp/library-scripts/
RUN <<EOF
apt-get update
/bin/bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}"
apt-get autoremove -y
apt-get clean -y
rm -rf /var/lib/apt/lists/* /tmp/library-scripts
EOF

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
