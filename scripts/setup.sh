if [ -z "$wallet_name" ]; then
  echo "Please provide the wallet name as an argument"
  exit 1
fi

if [[ ! -f ~/.bittensor/wallets/"${wallet_name}"/coldkeypub.txt ]]; then
    echo "Coldkey for wallet $wallet_name not found. Creating a new coldkey."

    btcli wallet new_coldkey --wallet.name "${wallet_name}" --no_password --no_prompt
    btcli wallet new_hotkey --wallet.name "${wallet_name}" --wallet.hotkey default --no_prompt
fi

# Transfer tokens to coldkeys
btcli wallet faucet --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
btcli wallet faucet --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt

# Register wallet hotkeys to subnet
btcli subnet register --wallet.name "${wallet_name}" --netuid 1 --wallet.hotkey default --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt

# Ensure both the miner and validator keys are successfully registered.
btcli subnet list --subtensor.chain_endpoint ws://127.0.0.1:9946
btcli wallet overview --wallet.name "${wallet_name}" --subtensor.chain_endpoint ws://127.0.0.1:9946 --no_prompt
