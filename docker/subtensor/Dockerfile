FROM ubuntu:20.04 as subtensor-builder

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    protobuf-compiler \
    clang \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone and build Subtensor
RUN git clone https://github.com/opentensor/subtensor.git /subtensor && \
    cd /subtensor && \
    ./scripts/init.sh && \
    cargo build --release --features pow-faucet

# Start with the PyTorch base image
FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime

# Create a non-root user for better security
RUN useradd --create-home nonroot

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        python3-pip \
        git \
        make \
        build-essential \
        clang \
        libssl-dev \
        llvm \
        libudev-dev \
        protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER nonroot
WORKDIR /home/nonroot

# Install Rust for the non-root user
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "$HOME/.cargo/env" \
    && rustup update nightly \
    && rustup update stable \
    && rustup target add wasm32-unknown-unknown --toolchain nightly

# Create necessary directories
RUN mkdir -p /home/nonroot/scripts/subtensor \
    && mkdir /home/nonroot/target \
    && mkdir /home/nonroot/target/release

# Copy necessary files from the builder stage
COPY --chown=nonroot:nonroot --from=subtensor-builder /subtensor/target/release/node-subtensor /home/nonroot/target/release/
COPY --chown=nonroot:nonroot --from=subtensor-builder /subtensor/scripts/* /home/nonroot/scripts/subtensor/
COPY --chown=nonroot:nonroot --from=subtensor-builder /subtensor/Cargo.toml /home/nonroot/

# Ensure scripts are executable
RUN chmod +x /home/nonroot/scripts/subtensor/*

# Set PATH environment variable
ENV PATH="/home/nonroot/.local/bin:${PATH}"

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir bittensor

# Copy the entrypoint script
COPY --chown=nonroot:nonroot entrypoint.sh /home/nonroot

RUN chmod +x /home/nonroot/entrypoint.sh

# Set the ENTRYPOINT
ENTRYPOINT ["/home/nonroot/entrypoint.sh"]
