# Standard Library Imports
import asyncio
import logging
from typing import Optional, List, Dict
from itertools import chain

# Local Imports
# Assuming AiClient is a class you've defined to interact with an AI model.
# It likely handles tasks like listing models, generating text, and creating embeddings.
from gui.services.ollama import AiClient

# Configure logging to display informational messages.
# This is helpful for understanding what the program is doing.
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this specific module.
logger = logging.getLogger(__name__)


class Test:
    """
    A class designed to interact with an AI client, providing methods
    for listing available models, generating text, engaging in chat,
    and creating vector embeddings.
    """

    def __init__(self, client: AiClient):
        """
        Initializes the Test class with an AI client.

        Args:
            client: An instance of the AiClient class, responsible for
                    communicating with the AI model.
        """
        self.client = client
        # Stores the name of the currently selected AI model.
        # It's initialized to None and can be set by list_models or
        # explicitly passed to other methods.
        self.model: Optional[str] = None

    async def list_models(self):
        """
        Asynchronously retrieves a list of available AI models from the client.

        Returns:
            A list of model objects (the exact structure depends on AiClient).

        Raises:
            RuntimeError: If no AI models are found to be available.
        """
        models = await self.client.list_models()
        if not models:
            raise RuntimeError("No models available.")
        # Automatically select the name of the first available model.
        # This can be useful as a default if no specific model is requested.
        self.model = models[0].name
        return models

    async def generate(self, prompt: Optional[str] = None, model: Optional[str] = None):
        """
        Asynchronously generates text based on a given prompt and model.

        Args:
            prompt: The text prompt to feed to the AI model. Defaults to
                    "tell me a joke" if no prompt is provided.
            model: The name of the AI model to use for generation. If not
                   specified, it defaults to the currently selected model (self.model).

        Returns:
            A string containing the generated text from the AI model.

        Raises:
            ValueError: If no model is specified and no model has been
                        selected previously.
        """
        # Use the provided prompt or the default if none is given.
        prompt = prompt or "tell me a joke"
        # Use the provided model or the currently selected model.
        model = model or self.model
        if not model:
            raise ValueError("Model must be specified or selected first.")

        # Initialize an empty list to store the chunks of the generated output.
        output: List[str] = []
        # Asynchronously iterate through the chunks of the generated text.
        async for chunk in await self.client.generate(prompt, model):
            output.append(chunk)
        # Join the chunks together to form the complete generated text.
        return "".join(output)

    async def chat(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
    ):
        """
        Asynchronously engages in a chat conversation with the AI model.

        Args:
            messages: A list of message dictionaries, where each dictionary
                      has "role" (e.g., "system", "user", "assistant") and
                      "content" keys. If None, a default conversation
                      about the weather on Mars is used.
            model: The name of the AI model to use for the chat. If not
                   specified, it defaults to the currently selected model (self.model).

        Returns:
            A string containing the AI's response in the chat conversation.

        Raises:
            ValueError: If no model is specified and no model has been
                        selected previously.
        """
        # Use the provided model or the currently selected model.
        model = model or self.model
        if not model:
            raise ValueError("Model must be specified or selected first.")

        # Define a default conversation if no messages are provided.
        if messages is None:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What's the weather like on Mars?"},
            ]

        # Initialize an empty list to store the chunks of the chat response.
        output: List[str] = []
        # Asynchronously iterate through the chunks of the chat response.
        async for chunk in await self.client.chat(messages, model):
            output.append(chunk)

        # Join the chunks together to form the complete chat response.
        return "".join(output)

    async def embeddings(self, prompt: str, model: str):
        """
        Asynchronously generates vector embeddings for a given text prompt using a specified model.

        Vector embeddings are numerical representations of text that capture its meaning,
        allowing for semantic comparisons between different pieces of text.

        Args:
            prompt: The text for which to generate an embedding.
            model: The name of the AI model to use for generating the embedding.

        Returns:
            A list of floating-point numbers representing the vector embedding of the prompt.
            The exact dimensionality and values depend on the specific embedding model used.
        """
        # Initialize an empty list to store the chunks of the embedding vector.
        output: List[List[float]] = []
        # Asynchronously iterate through the chunks of the embedding.
        # The 'stream=True' argument suggests that the embeddings might be returned in parts.
        async for chunk in await self.client.embeddings(prompt, model, stream=True):
            output.append(chunk)
        # 'chain.from_iterable' flattens the list of lists into a single list of numbers.
        return list(chain.from_iterable(output))


async def main():
    """
    The main asynchronous function that demonstrates the usage of the Test class
    to interact with the AI client.
    """
    testing_model = "tinyllama:latest"
    embedding_model = "nomic-embed-text:latest"
    # Create an instance of the AiClient. The 'async with' statement ensures
    # that any necessary setup and teardown of the client are handled properly.
    async with AiClient() as client:
        # Create an instance of the Test class, passing the AiClient object.
        test = Test(client)

        try:
            # List the available AI models.
            models = await test.list_models()
            print("Available Models:")
            # Iterate through the list of models and print their names and sizes.
            for m in models:
                print(f"- {m.name} ({m.size} bytes)")
        except RuntimeError as e:
            # If no models are available, log an error message.
            logger.error(e)
            # Exit the function.
            return

        # Initiate a chat using the 'tinyllama:latest' model.
        print("\nChatbot Response:")
        result = await test.chat(model=testing_model)
        print(result)

        # Generate text using the 'tinyllama:latest' model with the default prompt.
        print("\nGenerating Text:")
        result = await test.generate(model=testing_model)
        print(result)

        # Generate an embedding for the prompt "Hello, world!" using the 'nomic-embed-text:latest' model.
        print("\nVector Embeddings:")
        result = await test.embeddings(prompt="Hello, world!", model=embedding_model)
        print(len(result))


# This ensures that the 'main' function is executed when the script is run directly.
if __name__ == "__main__":
    # Run the asynchronous 'main' function using asyncio.
    asyncio.run(main())
