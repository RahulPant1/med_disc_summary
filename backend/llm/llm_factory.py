"""
Factory pattern for LLM client creation
"""
import logging
from typing import Optional
from llm.base_client import BaseLLMClient
from llm.gemini_client import GeminiClient
from llm.claude_client import ClaudeClient
from models.enums import LLMProvider

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory class for creating LLM client instances"""

    @staticmethod
    def get_client(provider: LLMProvider, api_key: str) -> BaseLLMClient:
        """
        Create an LLM client based on the provider type

        Args:
            provider: The LLM provider (gemini or claude)
            api_key: API key for the provider

        Returns:
            Initialized LLM client

        Raises:
            ValueError: If provider is not supported
        """
        if not api_key:
            raise ValueError(f"API key not provided for {provider}")

        if provider == LLMProvider.GEMINI:
            logger.info("Creating Gemini client")
            return GeminiClient(api_key)
        elif provider == LLMProvider.CLAUDE:
            logger.info("Creating Claude client")
            return ClaudeClient(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def test_all_connections(gemini_key: Optional[str], claude_key: Optional[str]) -> dict:
        """
        Test connections for all configured LLM providers

        Args:
            gemini_key: Gemini API key (optional)
            claude_key: Claude API key (optional)

        Returns:
            Dictionary with connection status for each provider
        """
        results = {}

        if gemini_key:
            try:
                client = GeminiClient(gemini_key)
                results['gemini'] = client.test_connection()
            except Exception as e:
                logger.error(f"Gemini test failed: {e}")
                results['gemini'] = False
        else:
            results['gemini'] = None

        if claude_key:
            try:
                client = ClaudeClient(claude_key)
                results['claude'] = client.test_connection()
            except Exception as e:
                logger.error(f"Claude test failed: {e}")
                results['claude'] = False
        else:
            results['claude'] = None

        return results
