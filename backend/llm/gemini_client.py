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

        # Try different model names in order of preference
        model_names = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro',
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-pro'
        ]

        # Log available models for debugging
        try:
            available_models = [m.name for m in genai.list_models()]
            logger.info(f"Available Gemini models: {available_models[:5]}")  # Show first 5
        except Exception as e:
            logger.warning(f"Could not list models: {e}")

        # Try each model name until one works
        model_initialized = False
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test if model works
                self.model_name = model_name
                logger.info(f"Gemini client initialized with {model_name}")
                model_initialized = True
                break
            except Exception as e:
                logger.debug(f"Model {model_name} not available: {e}")
                continue

        if not model_initialized:
            raise ValueError("Could not initialize any Gemini model. Please check your API key and available models.")

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
                "model": self.model_name
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
