#!/bin/bash

# Logic for setting up and running the environment
setup_environment() {
    # Install the bittensor-prompting-example python package
    python -m pip install --upgrade --user -e .

    # Create and set up wallets
    # This section can be skipped if wallets are already set up
    if [ ! -f ~/.bittensor/wallets/owner/coldkeypub.txt ]; then
        btcli wallet new_coldkey --wallet.name owner --no_password --no_prompt
    fi
}

# Call setup_environment every time
setup_environment

# Run the localnet using node-subtensor
FEATURES='pow-faucet runtime-benchmarks' BT_DEFAULT_TOKEN_WALLET=$(cat ~/.bittensor/wallets/owner/coldkeypub.txt | grep -oP '"ss58Address": "\K[^"]+') ./scripts/localnet.sh &

# Register a subnet (this needs to be run each time we start a new local chain)
btcli subnet create --wallet.name owner --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt

btcli subnet list --subtensor.chain_endpoint ws://127.0.0.1:9946
