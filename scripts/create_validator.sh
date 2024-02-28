#!/bin/bash

$type = "validator"
$name = $1
source ./create.sh
btcli stake add --wallet.name $name --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --amount 10000 --no_prompt
