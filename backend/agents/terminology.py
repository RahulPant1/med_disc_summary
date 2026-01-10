"""
Terminology Standards Agent - Validates medical terminology and abbreviations
"""
from typing import Dict
from .base_agent import BaseAgent


class TerminologyAgent(BaseAgent):
    """
    Agent focused on medical terminology standards:
    - Abbreviation usage and expansion
    - Standard medical terminology
    - Drug name standardization
    - Unit consistency
    - Terminology clarity
    """

    @property
    def PROMPTS(self) -> Dict[str, str]:
        return {
            "gemini": """You are a medical terminology standardization expert.

Analyze the discharge summary for terminology issues:
1. Abbreviations that should be expanded (especially non-standard ones like "K/c/o")
2. Inconsistent abbreviation usage
3. Non-standard medical terminology
4. Drug name inconsistencies (brand vs generic)
5. Unit inconsistencies (mg vs mgm, etc.)
6. Ambiguous medical terms
7. Local language or slang in medical context

Common issues to flag:
- "K/c/o" should be "Known case of"
- Inconsistent vital sign abbreviations (B.P. vs BP)
- Mixed use of brand and generic drug names
- Non-standard medical abbreviations

Return ONLY valid JSON in this exact format:
{{
  "issues": [
    {{
      "type": "abbreviation|terminology|drug_name|units|ambiguous_term",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section where found",
      "current": "current term or abbreviation",
      "suggestion": "standard terminology or expansion",
      "explanation": "why standardization is needed"
    }}
  ]
}}

DISCHARGE SUMMARY:
{content}""",

            "claude": """<task>Review this discharge summary for medical terminology standardization</task>

<focus_areas>
- Non-standard abbreviations requiring expansion
- Inconsistent abbreviation usage across document
- Medical terminology accuracy and standardization
- Drug naming consistency (brand vs generic)
- Unit standardization and clarity
- Ambiguous or unclear medical terms
</focus_areas>

<abbreviation_standards>
- Spell out non-standard abbreviations on first use
- Flag potentially confusing abbreviations (K/c/o, c/o, etc.)
- Check for consistent vital sign notation
- Verify medication abbreviations are standard
- Ensure time and dose units are clear
</abbreviation_standards>

<output_format>
Return ONLY valid JSON:
{{
  "issues": [
    {{
      "type": "abbreviation|terminology|drug_name|units|ambiguous_term",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name",
      "current": "current usage",
      "suggestion": "standardized version",
      "explanation": "standardization rationale"
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
            "gemini": "You are a medical terminology standardization expert.",
            "claude": "You are an expert in medical terminology standards and abbreviation guidelines."
        }
