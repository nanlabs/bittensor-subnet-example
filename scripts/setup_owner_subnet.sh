#!/bin/bash

wallet_name=owner

# Install the bittensor-prompting-example python package
python -m pip install --upgrade --user -e .

# Create and set up wallets
# This section can be skipped if wallets are already set up
if [ ! -f ~/.bittensor/wallets/"${wallet_name}"/coldkeypub.txt ]; then
    btcli wallet new_coldkey --wallet.name "${wallet_name}" --no_password --no_prompt
fi

btcli wallet faucet --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt

# Register a subnet (this needs to be run each time we start a new local chain)
btcli subnet create --wallet.name "${wallet_name}" --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt

btcli subnet list --subtensor.chain_endpoint ws://127.0.0.1:9946
