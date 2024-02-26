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

from dotenv import load_dotenv, find_dotenv
import os
import time
import typing
import bittensor as bt

# Bittensor Miner Template:
import prompting

# import base miner class which takes care of most of the boilerplate
from prompting.base.miner import BaseMinerNeuron

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback


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
        self.identity_tags = None

        bt.logging.info(f"Initializing with model {self.config.neuron.model_id}...")

        if self.config.wandb.on:
            self.identity_tags =  ("openai_miner", ) + (self.config.neuron.model_id, )

        _ = load_dotenv(find_dotenv())
        api_key = os.environ.get("OPENAI_API_KEY")

        # Set openai key and other args
        self.model = ChatOpenAI(
            api_key=api_key,
            model_name=self.config.neuron.model_id,
            max_tokens = self.config.neuron.max_tokens,
            temperature = self.config.neuron.temperature,
        )

        self.system_prompt = "You are a friendly chatbot who always responds concisely and helpfully. You are honest about things you don't know."
        self.accumulated_total_tokens = 0
        self.accumulated_prompt_tokens = 0
        self.accumulated_completion_tokens = 0
        self.accumulated_total_cost = 0

    def get_cost_logging(self, cb):
        bt.logging.info(f"Total Tokens: {cb.total_tokens}")
        bt.logging.info(f"Prompt Tokens: {cb.prompt_tokens}")
        bt.logging.info(f"Completion Tokens: {cb.completion_tokens}")
        bt.logging.info(f"Total Cost (USD): ${round(cb.total_cost,4)}")

        self.accumulated_total_tokens += cb.total_tokens
        self.accumulated_prompt_tokens += cb.prompt_tokens
        self.accumulated_completion_tokens += cb.completion_tokens
        self.accumulated_total_cost += cb.total_cost

        return  {
            'total_tokens': cb.total_tokens,
            'prompt_tokens': cb.prompt_tokens,
            'completion_tokens': cb.completion_tokens,
            'total_cost': cb.total_cost,
            'accumulated_total_tokens': self.accumulated_total_tokens,
            'accumulated_prompt_tokens': self.accumulated_prompt_tokens,
            'accumulated_completion_tokens': self.accumulated_completion_tokens,
            'accumulated_total_cost': self.accumulated_total_cost,
        }

    async def forward(
        self, synapse: prompting.protocol.Prompting
    ) -> prompting.protocol.Prompting:
        """
        Processes the incoming synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (Prompting): The synapse object containing the 'dummy_input' data.

        Returns:
            Prompting: The synapse object with the 'dummy_output' field set to twice the 'dummy_input' value.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        try:
            with get_openai_callback() as cb:
                start_time = time.time()
                bt.logging.debug(f"Message received, forwarding synapse: {synapse}")

                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("user", "{input}")
                ])
                chain = prompt | self.model | StrOutputParser()

                role = synapse.roles[-1]
                message = synapse.messages[-1]

                bt.logging.debug(f"💬 Querying openai: {prompt}")
                response = chain.invoke(
                    {"role": role, "input": message}
                )

                synapse.completion = response
                synapse_latency = time.time() - start_time

                if self.config.wandb.on:
                    self.log_event(
                        timing=synapse_latency,
                        prompt=message,
                        completion=response,
                        system_prompt=self.system_prompt,
                        extra_info=self.get_cost_logging(cb)
                    )

            bt.logging.debug(f"✅ Served Response: {response}")
            self.step += 1

            return synapse
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            synapse.completion = "Error: " + str(e)
        finally:
            if self.config.neuron.stop_on_forward_exception:
                self.should_exit = True
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

            if miner.should_exit:
                bt.logging.warning("Ending miner...")
                break
