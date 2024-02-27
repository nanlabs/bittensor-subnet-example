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
import bittensor as bt
import os
import time
import typing

# Bittensor Miner Template:
import prompting

# import base miner class which takes care of most of the boilerplate
from prompting.base.miner import BaseMinerNeuron


class OpenAIMiner(BaseMinerNeuron):
    """Langchain-based miner which uses OpenAI's API as the LLM.

    You should also install the dependencies for this miner, which can be found in the requirements.txt file in this directory.
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        """
        Adds OpenAI-specific arguments to the command line parser.
        """
        super().add_args(parser)

    def __init__(self, config=None):
        super().__init__(config=config)

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

        # Log the model being used for completion
        bt.logging.info(f"Initializing with model {config.openai.model_name}")

        api_key = config.openai.api_key  # Fetch from configuration
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")  # Fallback to environment variable
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
        Processes the incoming synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (Prompting): The synapse object containing the input data to be processed.

        Returns:
            Prompting: The synapse object with the processed data.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        try:
            start_time = time.time()
            bt.logging.debug(f"Message received, forwarding synapse: {synapse}")

            messages = [
                (
                    {
                        "role": message.name,
                        "content": self.append_criteria(
                            message.content + synapse.character_info, synapse.criteria
                        ),
                    }
                    if message.name == "system"
                    else {"role": message.name, "content": message.content}
                )
                for message in synapse.messages
            ]
            bt.logging.debug(f"messages: {messages}")

            bt.logging.debug(f"💬 Querying openai with message: {messages}")
            response = (
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
            synapse.completion = response
            synapse_latency = time.time() - start_time
            # Log the time taken to process the request.
            bt.logging.info(f"Processed synapse in {synapse_latency} seconds.")

            bt.logging.debug(f"✅ Served Response: {response}")
            return synapse
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            synapse.completion = "Error: " + str(e)
        finally:
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
            synapse (Prompting): A synapse object constructed from the headers of the incoming request.

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
        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(
                f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

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
            synapse (Prompting): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        priority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", priority
        )
        return priority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with OpenAIMiner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(5)
