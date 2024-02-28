#!/bin/bash

name=owner
btcli wallet new_coldkey --wallet.name $name --no_password --no_prompt
btcli wallet faucet --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli subnet create --wallet.name $name --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
