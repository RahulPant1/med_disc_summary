"""
Google Gemini LLM client implementation
"""
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

        # Updated model list for 2026 - prioritize 2.5 and 3.0 series
        model_names = [
            'gemini-2.5-flash',         # Current best price/performance
            #'gemini-2.5-pro',           # Current most powerful stable
            'gemini-3-flash-preview',   # Newest preview
            'gemini-flash-latest'      # Auto-updating alias
        ]

        # Get list of actually available models to verify existence
        try:
            available_models = [m.name.replace('models/', '') for m in genai.list_models()]
            logger.info(f"Actual available Gemini models: {available_models[:10]}")  # Show first 10
        except Exception as e:
            logger.warning(f"Could not list models: {e}")
            available_models = []

        # Try each model name, verifying it exists in available models
        model_initialized = False
        for model_name in model_names:
            # Check if model exists in available models
            if available_models and model_name not in available_models:
                logger.debug(f"Model {model_name} not in available models list")
                continue

            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                logger.info(f"Gemini client initialized with {model_name}")
                model_initialized = True
                break
            except Exception as e:
                logger.debug(f"Model {model_name} initialization failed: {e}")
                continue

        if not model_initialized:
            raise ValueError(
                f"Could not initialize any Gemini model. "
                f"Tried: {model_names}. "
                f"Available: {available_models[:5] if available_models else 'Could not fetch list'}. "
                f"Please check your API key and google-generativeai package version (run: pip install -U google-generativeai)"
            )

    async def analyze(self, prompt: str, system: Optional[str] = None) -> Dict:
        """
        Perform asynchronous analysis with Gemini

        Args:
            prompt: The prompt to send
            system: System instructions (prepended to prompt)

        Returns:
            Dictionary with 'content' key containing the response
        """
        try:
            # Combine system and prompt if system instructions provided
            full_prompt = f"{system}\n\n{prompt}" if system else prompt

            # Use async generation and await it
            response = await self.model.generate_content_async(full_prompt)

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
            system: System instructions (prepended to prompt)

        Yields:
            Text chunks as they arrive
        """
        try:
            # Combine system and prompt if system instructions provided
            full_prompt = f"{system}\n\n{prompt}" if system else prompt

            # Use async streaming
            response = await self.model.generate_content_async(full_prompt, stream=True)

            async for chunk in response:
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
