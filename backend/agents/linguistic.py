"""
Linguistic Quality Agent - Validates spelling, grammar, and clarity
"""
from typing import Dict
from .base_agent import BaseAgent


class LinguisticAgent(BaseAgent):
    """
    Agent focused on linguistic quality:
    - Spelling errors (medical and general)
    - Grammar issues
    - Sentence structure problems
    - Duplicate content
    - Clarity issues
    """

    @property
    def PROMPTS(self) -> Dict[str, str]:
        return {
            "gemini": """You are a medical documentation quality reviewer focusing on linguistic aspects.

Analyze the discharge summary for:
1. Spelling errors (medical terminology and general words)
2. Grammar issues (verb tense, subject-verb agreement, etc.)
3. Sentence structure problems (sentences over 40 words should be flagged)
4. Duplicate or redundant content
5. Clarity issues (ambiguous phrasing, unclear statements)

Return ONLY valid JSON in this exact format:
{{
  "issues": [
    {{
      "type": "spelling|grammar|structure|duplication|clarity",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name where issue is found",
      "current": "exact problematic text",
      "suggestion": "corrected version or improvement",
      "explanation": "brief explanation of why this is an issue"
    }}
  ]
}}

DISCHARGE SUMMARY:
{content}""",

            "claude": """<task>Review this discharge summary for linguistic quality issues</task>

<focus_areas>
- Medical terminology spelling accuracy
- Grammar and sentence structure
- Text clarity and readability
- Content duplication detection
- Sentences exceeding 40 words
</focus_areas>

<output_format>
Return ONLY valid JSON with this structure:
{{
  "issues": [
    {{
      "type": "spelling|grammar|structure|duplication|clarity",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name",
      "current": "problematic text",
      "suggestion": "corrected version",
      "explanation": "why this is an issue"
    }}
  ]
}}
</output_format>

<discharge_summary>
{content}
</discharge_summary>"""
        }

    @property
    def SYSTEM_MESSAGE(self) -> Dict[str, str]:
        return {
            "gemini": "You are a medical documentation quality expert specializing in linguistic accuracy.",
            "claude": "You are a medical documentation quality expert. Focus on linguistic accuracy and clarity."
        }
