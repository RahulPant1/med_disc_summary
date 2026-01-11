"""
Structural Compliance Agent - Validates NABH standards and document structure
"""
from typing import Dict
from .base_agent import BaseAgent


class StructuralAgent(BaseAgent):
    """
    Agent focused on structural compliance:
    - NABH standard compliance
    - Required sections presence
    - Section organization
    - Formatting consistency
    - Completeness of information
    """

    @property
    def PROMPTS(self) -> Dict[str, str]:
        return {
            "gemini": """You are a medical documentation compliance reviewer for NABH standards.

Analyze the discharge summary for structural compliance:
1. Required sections:
   - Patient Information (UHID, IPD No, Age, Gender, DOA, DOD)
   - Diagnosis
   - Chief Complaints
   - History of Present Illness
   - Significant Findings at Admission
   - Course in Hospital
   - Procedures (if applicable)
   - Condition at Discharge
   - Advice on Discharge
   - Follow-up instructions

2. Section completeness (each section should have adequate detail)
3. Formatting consistency
4. Logical organization and flow
5. Missing critical information

Return ONLY valid JSON in this exact format:
{{
  "issues": [
    {{
      "type": "missing_section|incomplete_section|formatting|organization|critical_info_missing",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name or document structure",
      "current": "what is currently present or missing",
      "suggestion": "what should be added or corrected",
      "explanation": "why this is important for NABH compliance"
    }}
  ]
}}

DISCHARGE SUMMARY:
{content}""",

            "claude": """<task>Review this discharge summary for structural compliance with NABH standards</task>

<focus_areas>
- Presence of all required sections
- Completeness of patient demographics
- Adequate detail in each section
- Formatting consistency
- Logical document organization
- Critical information completeness
</focus_areas>

<required_sections>
1. Patient Information (UHID, IPD, demographics, admission/discharge dates)
2. Diagnosis
3. Chief Complaints
4. History of Present Illness
5. Significant Findings at Admission
6. Course in Hospital
7. Procedures (if applicable)
8. Condition at Discharge
9. Discharge Advice/Medications
10. Follow-up Instructions
</required_sections>

<output_format>
Return ONLY valid JSON:
{{
  "issues": [
    {{
      "type": "missing_section|incomplete_section|formatting|organization|critical_info_missing",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name",
      "current": "current state",
      "suggestion": "what should be present",
      "explanation": "NABH compliance reason"
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
            "gemini": "You are a NABH compliance expert for medical discharge documentation.",
            "claude": "You are an expert in NABH healthcare standards and discharge summary compliance."
        }
