"""
Google Gemini LLM client implementation
"""
import json
import logging
from typing import Dict, AsyncGenerator, Optional
import google.generativeai as genai
from .base_client import BaseLLMClient

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """Google Gemini API client implementation"""

    def __init__(self, api_key: str):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key for Gemini
        """
        super().__init__(api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini client initialized")

    async def analyze(self, prompt: str, system: Optional[str] = None) -> Dict:
        """
        Perform synchronous analysis with Gemini

        Args:
            prompt: The prompt to send
            system: System instructions (prepended to prompt for Gemini)

        Returns:
            Dictionary with 'content' key containing the response
        """
        try:
            # Combine system and prompt for Gemini
            full_prompt = f"{system}\n\n{prompt}" if system else prompt

            response = self.model.generate_content(full_prompt)

            return {
                "content": response.text,
                "model": "gemini-pro"
            }
        except Exception as e:
            logger.error(f"Gemini analysis error: {str(e)}")
            raise

    async def stream_analyze(
        self,
        prompt: str,
        system: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream analysis results from Gemini

        Args:
            prompt: The prompt to send
            system: System instructions

        Yields:
            Text chunks as they arrive
        """
        try:
            # Combine system and prompt for Gemini
            full_prompt = f"{system}\n\n{prompt}" if system else prompt

            response = self.model.generate_content(full_prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming error: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """
        Test Gemini API connection

        Returns:
            True if connection successful
        """
        try:
            response = self.model.generate_content("Test connection. Reply with OK.")
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False
