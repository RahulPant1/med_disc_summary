"""
Anthropic Claude LLM client implementation
"""
import json
import logging
from typing import Dict, AsyncGenerator, Optional
from anthropic import Anthropic
from .base_client import BaseLLMClient

logger = logging.getLogger(__name__)


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude API client implementation"""

    def __init__(self, api_key: str):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key
        """
        super().__init__(api_key)
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        logger.info("Claude client initialized")

    async def analyze(self, prompt: str, system: Optional[str] = None) -> Dict:
        """
        Perform synchronous analysis with Claude

        Args:
            prompt: The prompt to send
            system: System instructions for Claude

        Returns:
            Dictionary with 'content' key containing the response
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system if system else "You are a helpful medical documentation reviewer.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return {
                "content": message.content[0].text,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Claude analysis error: {str(e)}")
            raise

    async def stream_analyze(
        self,
        prompt: str,
        system: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream analysis results from Claude

        Args:
            prompt: The prompt to send
            system: System instructions

        Yields:
            Text chunks as they arrive
        """
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=system if system else "You are a helpful medical documentation reviewer.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Claude streaming error: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """
        Test Claude API connection

        Returns:
            True if connection successful
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Test connection. Reply with OK."}
                ]
            )
            return bool(message.content[0].text)
        except Exception as e:
            logger.error(f"Claude connection test failed: {str(e)}")
            return False
