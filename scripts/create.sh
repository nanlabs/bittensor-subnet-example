if [ -z "$1" ]; then
  echo "Please provide the $type's name"
  exit 1
fi

btcli wallet new_coldkey --wallet.name $name --no_password --no_prompt
btcli wallet new_hotkey --wallet.name $name --wallet.hotkey default --no_prompt
btcli wallet faucet --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli subnet register --wallet.name $name --netuid 1 --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli subnet list --subtensor.chain_endpoint ws://127.0.0.1:9946
btcli wallet overview --wallet.name $name --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
