#!/bin/bash

NETUID=${1:-1}  
CHAIN_ENDPOINT=${2:-"ws://127.0.0.1:9946"}  
WALLET_NAME=${3:-"openai_miner"}  
WALLET_HOTKEY=${4:-"default"}  

python -m pip install --upgrade --user -r ./neurons/miners/openai/requirements.txt

python ./neurons/miners/openai/miner.py --netuid $NETUID --subtensor.chain_endpoint $CHAIN_ENDPOINT --wallet.name $WALLET_NAME --wallet.hotkey $WALLET_HOTKEY --logging.debug 
