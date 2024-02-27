FROM opentensor/subtensor:latest

# show backtraces
ENV RUST_BACKTRACE 1

# Necessary libraries for Rust execution
RUN apt-get update && \
    apt-get install -y curl build-essential protobuf-compiler clang git netcat && \
    rm -rf /var/lib/apt/lists/*

# Install cargo and Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
