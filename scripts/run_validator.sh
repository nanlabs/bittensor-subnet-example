#!/bin/bash  

WALLET_NAME=${1:-"openai_miner"}  
WALLET_HOTKEY=${2:-"default"}  
NETUID=${3:-1}  
CHAIN_ENDPOINT=${4:-"ws://127.0.0.1:9946"}  

python3 neurons/validators/validator.py --netuid $NETUID --subtensor.chain_endpoint $CHAIN_ENDPOINT --wallet.name $WALLET_NAME --wallet.hotkey $WALLET_HOTKEY --logging.debug 