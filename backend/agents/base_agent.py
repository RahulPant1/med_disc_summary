"""
Abstract base class for validation agents
"""
import json
import logging
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from models.schemas import IssueModel
from llm.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all validation agents.
    Each agent analyzes specific aspects of discharge summaries.
    """

    def __init__(self):
        """Initialize the agent"""
        # Convert CamelCase to snake_case (e.g., CriticalDataAgent -> critical_data)
        class_name = self.__class__.__name__.replace("Agent", "")
        # Insert underscore before uppercase letters and convert to lowercase
        snake_case_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        self.name = snake_case_name

    @property
    @abstractmethod
    def PROMPTS(self) -> Dict[str, str]:
        """
        Prompts for different LLM providers.
        Must return dict with 'gemini' and 'claude' keys.
        """
        pass

    @property
    @abstractmethod
    def SYSTEM_MESSAGE(self) -> Dict[str, str]:
        """
        System messages for different LLM providers.
        Must return dict with 'gemini' and 'claude' keys.
        """
        pass

    def get_prompt(self, content: str, llm_provider: str) -> str:
        """
        Get the formatted prompt for the given LLM provider

        Args:
            content: Discharge summary content
            llm_provider: LLM provider (gemini/claude)

        Returns:
            Formatted prompt
        """
        prompt_template = self.PROMPTS.get(llm_provider)
        if not prompt_template:
            raise ValueError(f"No prompt defined for provider: {llm_provider}")

        return prompt_template.format(content=content)

    def get_system_message(self, llm_provider: str) -> Optional[str]:
        """
        Get the system message for the given LLM provider

        Args:
            llm_provider: LLM provider (gemini/claude)

        Returns:
            System message or None
        """
        return self.SYSTEM_MESSAGE.get(llm_provider)

    async def analyze(
        self,
        content: str,
        llm_client: BaseLLMClient,
        llm_provider: str
    ) -> List[IssueModel]:
        """
        Analyze discharge summary content

        Args:
            content: Discharge summary text
            llm_client: LLM client to use
            llm_provider: Provider name (gemini/claude)

        Returns:
            List of issues found
        """
        try:
            prompt = self.get_prompt(content, llm_provider)
            system_message = self.get_system_message(llm_provider)

            # Call LLM
            response = await llm_client.analyze(prompt, system_message)

            # Parse response
            issues = self.parse_response(response, llm_provider)

            logger.info(f"{self.name} agent found {len(issues)} issues")
            return issues

        except Exception as e:
            logger.error(f"Error in {self.name} agent: {str(e)}")
            return []

    def parse_response(self, response: Dict, llm_provider: str) -> List[IssueModel]:
        """
        Parse LLM response into IssueModel objects

        Args:
            response: Response from LLM
            llm_provider: Provider name

        Returns:
            List of IssueModel objects
        """
        try:
            content = response.get("content", "")

            # Extract JSON from response (handle markdown code blocks)
            json_str = content.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            # Parse JSON
            data = json.loads(json_str)

            # Convert to IssueModel objects
            issues = []
            for issue_data in data.get("issues", []):
                # Add category from agent name
                issue_data["category"] = self.name
                issues.append(IssueModel(**issue_data))

            return issues

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from {self.name}: {e}")
            logger.debug(f"Response content: {response.get('content', '')[:200]}")
            return []
        except Exception as e:
            logger.error(f"Error parsing response from {self.name}: {e}")
            return []
