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

from pydantic import BaseModel, Field
from typing import List
import bittensor as bt


class Message(BaseModel):
    content: str = Field(
        ..., title="Content", description="The content of the message."
    )


class PromptingMixin(BaseModel):
    """
    A Pydantic model representing a chat session between a single user and a large language model (LLM),
    potentially extending functionality from a base class for integration into a broader system.

    This model manages the chat session, including initializing the session with LLM details,
    handling message exchange, and updating the chat's completion status.

    Attributes:
        character_info (str): Descriptive information about the LLM, such as its version or capabilities.
        criteria (List[str]): Guidelines or criteria for the LLM's responses to ensure they meet certain standards or styles.
        messages (List[Message]): Records the history of messages exchanged in the session.
        completion (str): Tracks the latest LLM response or the overall completion status of the chat session.

    Example of Usage:
        ```python
        # Initialize a chat session with LLM details and criteria
        chat_session = PromptingMixin(
            character_info="GPT-4, the latest language model.",
            criteria=["Be informative and engaging."],
            messages=[],
        )

        # Add a message to the session
        chat_session.add_message("What is the weather like today?")

        # Update the session's completion status after getting a response
        chat_session.update_completion("It's sunny and warm outside.")
        ```
    """

    class Config:
        """
        Pydantic model configuration class for Prompting. This class sets validation of attribute assignment as True.
        validate_assignment set to True means the pydantic model will validate attribute assignments on the class.
        """

        validate_assignment = True

    character_info: str = Field(
        ...,
        title="Character Info",
        description="Information about the LLM.",
        allow_mutation=False,
    )
    criteria: List[str] = Field(
        ...,
        title="Criteria",
        description="Criteria guiding the LLM's responses.",
        allow_mutation=False,
    )
    messages: List[Message] = Field(
        ...,
        title="Messages",
        description="Dialogue history of the chat session.",
        allow_mutation=False,
    )
    completion: str = Field(
        "",
        title="Completion",
        description="Latest response or completion status of the chat.",
    )

    def add_message(self, content: str):
        """
        Adds a new message to the dialogue history.

        Parameters:
            content (str): The content of the message to be added.
        """
        self.messages.append(Message(content=content))

    def update_completion(self, completion: str):
        """
        Updates the completion status of the chat.

        Parameters:
            completion (str): The new completion status or LLM's response.
        """
        self.completion = completion

class Prompting(PromptingMixin, bt.Synapse):
    """
    The Prompting class encapsulates functionalities related to a simplified chat session
    between a single user and an LLM, leveraging the infrastructure or methods provided by Synapse.

    This class inherits from ChatSession to manage the chat details and from Synapse to incorporate
    any additional functionalities or requirements specific to the underlying system or LLM interaction.

    Methods such as `deserialize` from Synapse can be utilized or overridden here to suit the
    deserialization needs of the Prompting instances, alongside any other methods that Synapse might offer.

    Example of Usage:
        ```python
        # Assuming Synapse provides certain functionalities required for integration
        prompting = Prompting(
            character_info="GPT-4, for engaging and informative conversations.",
            criteria=["Ensure accuracy.", "Maintain a friendly tone."],
            messages=[],
        )

        # Interacting with the LLM
        prompting.add_message("Tell me a joke.")
        prompting.update_completion("Why did the computer go to the doctor? Because it had a virus!")

        # Utilizing Synapse specific methods, if any
        deserialized_prompting = prompting.deserialize()
        ```
    """

    def deserialize(self) -> "Prompting":
        """
        Returns the instance of the current Prompting object, potentially utilizing
        custom deserialization logic provided by Synapse or defined specifically for Prompting.

        Returns:
            Prompting: The current instance of the Prompting class.
        """
        return self
