#!/bin/bash

if [ -z "$1" ]; then
  echo "Please provide the $type's name"
  exit 1
fi

if [ -z "$2" ]; then
  echo "Please provide the $type script"
  exit 1
fi

name=$1
script=$2
python neurons/$script --netuid 1 --subtensor.chain_endpoint ws://127.0.0.1:9946 --wallet.name $name --wallet.hotkey default --logging.debug
