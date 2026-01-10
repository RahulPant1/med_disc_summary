"""
Abstract base class for LLM clients
"""
from abc import ABC, abstractmethod
from typing import Dict, AsyncGenerator, Optional


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM client implementations.
    All LLM clients must implement these methods.
    """

    def __init__(self, api_key: str):
        """
        Initialize the LLM client

        Args:
            api_key: API key for the LLM provider
        """
        self.api_key = api_key

    @abstractmethod
    async def analyze(self, prompt: str, system: Optional[str] = None) -> Dict:
        """
        Perform a single request-response analysis

        Args:
            prompt: The prompt to send to the LLM
            system: Optional system message/instructions

        Returns:
            Dictionary containing the LLM response
        """
        pass

    @abstractmethod
    async def stream_analyze(
        self,
        prompt: str,
        system: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream analysis results as they are generated

        Args:
            prompt: The prompt to send to the LLM
            system: Optional system message/instructions

        Yields:
            Chunks of the response as they arrive
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the API connection is working

        Returns:
            True if connection successful, False otherwise
        """
        pass
