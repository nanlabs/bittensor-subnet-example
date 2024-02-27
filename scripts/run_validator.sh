#!/bin/bash  

NETUID=${1:-0}  
CHAIN_ENDPOINT=${2:-"ws://127.0.0.1:9946"}  
WALLET_NAME=${3:-"validator"}  
WALLET_HOTKEY=${4:-"default"}  

python3 neurons/validators/validator.py --netuid $NETUID --subtensor.chain_endpoint $CHAIN_ENDPOINT --wallet.name $WALLET_NAME --wallet.hotkey $WALLET_HOTKEY --logging.debug 