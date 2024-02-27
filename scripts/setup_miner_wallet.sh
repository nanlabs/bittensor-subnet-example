#!/bin/bash

# Create a coldkey for the owner role
wallet=${1:-miner}

if [[ ! -f ~/.bittensor/wallets/"${wallet}"/coldkeypub.txt ]]; then
    echo "Coldkey for wallet $wallet not found. Creating a new coldkey."

    btcli wallet new_coldkey --wallet.name "${wallet}" --no_password --no_prompt
    btcli wallet new_hotkey --wallet.name "${wallet}" --wallet.hotkey default --no_prompt
fi

# Transfer tokens to miner and validator coldkeys
export BT_MINER_TOKEN_WALLET=$(cat ~/.bittensor/wallets/"${wallet}"/coldkeypub.txt | grep -oP '"ss58Address": "\K[^"]+')

btcli wallet transfer --subtensor.network ws://127.0.0.1:9946 --wallet.name owner --dest "$BT_MINER_TOKEN_WALLET" --amount 1000 --no_prompt

# Register wallet hotkeys to subnet
btcli subnet register --wallet.name "${wallet}" --netuid 0 --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt

# Ensure both the miner and validator keys are successfully registered.
btcli subnet list --subtensor.chain_endpoint ws://127.0.0.1:9946
btcli wallet overview --wallet.name "${wallet}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
