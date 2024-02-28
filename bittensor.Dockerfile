FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime

# Create a non-root user
RUN useradd --create-home nonroot

# Install dependencies
RUN apt-get update && apt-get install -y \
        make \
        build-essential \
        git \
        clang \
        curl \
        libssl-dev \
        llvm \
        libudev-dev \
        protobuf-compiler \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER nonroot
WORKDIR /home/nonroot

# Install Rust and add wasm target
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "$HOME/.cargo/env" \
    && rustup update nightly \
    && rustup update stable \
    && rustup target add wasm32-unknown-unknown --toolchain nightly

# Update PATH environment variable
ENV PATH="$HOME/.local/bin:${PATH}"

# Upgrade pip and install bittensor
RUN pip install --upgrade pip \
    && pip install bittensor
