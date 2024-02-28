#!/bin/bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
SCRIPTS_DIR="${ROOT}"/scripts

wallet_name=$1

source "${SCRIPTS_DIR}"/setup.sh

# Add stake to the validator
btcli stake add --wallet.name "${wallet_name}" --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --amount 10000 --no_prompt
