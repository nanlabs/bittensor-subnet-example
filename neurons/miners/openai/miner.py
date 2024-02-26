# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2024 nanlabs

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import argparse
import openai
import os
import time
import typing
import bittensor as bt

# Bittensor Miner Template:
import prompting

# import base miner class which takes care of most of the boilerplate
from prompting.base.miner import BaseMinerNeuron


class OpenAIMiner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(OpenAIMiner, self).__init__(config=config)

        parser = argparse.ArgumentParser(description="OpenAI Miner")

        parser.add_argument(
            "--openai.api_key",
            type=str,
            default=None,
            help="OpenAI API key for authenticating requests.",
        )

        parser.add_argument(
            "--openai.suffix",
            type=str,
            default=None,
            help="The suffix that comes after a completion of inserted text.",
        )
        parser.add_argument(
            "--openai.max_tokens",
            type=int,
            default=100,
            help="The maximum number of tokens to generate in the completion.",
        )
        parser.add_argument(
            "--openai.temperature",
            type=float,
            default=0.4,
            help="Sampling temperature to use, between 0 and 2.",
        )
        parser.add_argument(
            "--openai.top_p",
            type=float,
            default=1,
            help="Nucleus sampling parameter, top_p probability mass.",
        )
        parser.add_argument(
            "--openai.n",
            type=int,
            default=1,
            help="How many completions to generate for each prompt.",
        )
        parser.add_argument(
            "--openai.presence_penalty",
            type=float,
            default=0.1,
            help="Penalty for tokens based on their presence in the text so far.",
        )
        parser.add_argument(
            "--openai.frequency_penalty",
            type=float,
            default=0.1,
            help="Penalty for tokens based on their frequency in the text so far.",
        )
        parser.add_argument(
            "--openai.model_name",
            type=str,
            default="gpt-3.5-turbo",
            help="OpenAI model to use for completion.",
        )

        self.add_args(parser)

        # Load the configuration for the miner
        config = self.config

        api_key = config.openai.api_key  # Fetch from configuration
        if api_key is None:
            api_key = os.getenv(
                "OPENAI_API_KEY"
            )  # Fallback to environment variable
            if api_key is None:
                raise ValueError(
                    "OpenAI API key is required: the miner requires an `OPENAI_API_KEY` either passed directly to the constructor, defined in the configuration, or set in the environment variables."
                )

        # Additional configurations for wandb
        if config.wandb.on:
            self.wandb_run.tags = self.wandb_run.tags + ("openai_miner",)

        # Set the OpenAI API key
        openai.api_key = api_key

        self.client = openai.OpenAI(api_key=api_key)

    async def forward(
        self, synapse: prompting.protocol.Prompting
    ) -> prompting.protocol.Prompting:
        """
        Processes the incoming 'Prompting' synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (prompting.protocol.Prompting): The synapse object containing prompt data.

        Returns:
            prompting.protocol.Prompting: The synapse object with the completion data.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        
        bt.logging.debug(f"synapse: {synapse}")
        messages = [
            {
                "role": message.name,
                "content": self.append_criteria(
                    message.content + synapse.character_info, synapse.criteria
                ),
            }
            if message.name == "system"
            else {"role": message.name, "content": message.content}
            for message in synapse.messages
        ]
        bt.logging.debug(f"messages: {messages}")
        resp = (
            self.client.chat.completions.create(
                model=self.config.openai.model_name,
                messages=messages,
                temperature=self.config.openai.temperature,
                max_tokens=self.config.openai.max_tokens,
                top_p=self.config.openai.top_p,
                frequency_penalty=self.config.openai.frequency_penalty,
                presence_penalty=self.config.openai.presence_penalty,
                n=self.config.openai.n,
            )
            .choices[0]
            .message.content
        )
        synapse.completion = resp
        bt.logging.debug(f"completion: {resp}")

        return synapse

    async def blacklist(
        self, synapse: prompting.protocol.Prompting
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (prompting.protocol.Prompting): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        # TODO(developer): Define how miners should blacklist requests.
        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: prompting.protocol.Prompting) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (prompting.protocol.Prompting): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with OpenAIMiner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(5)
