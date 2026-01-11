"""
Critical Data Safety Agent - Validates essential data integrity
"""
from typing import Dict
from .base_agent import BaseAgent


class CriticalDataSafetyAgent(BaseAgent):
    """
    Focus on critical data errors:
    - Timeline logic (impossible dates)
    - Missing identifiers
    - Test name errors
    - Missing critical sections
    """

    @property
    def PROMPTS(self) -> Dict[str, str]:
        return {
            "gemini": """You are a medical data integrity specialist focusing on CRITICAL DATA ERRORS ONLY.

FOCUS EXCLUSIVELY ON:

1. Timeline Logic Errors (HIGHEST PRIORITY):
   - Procedures before admission date
   - Discharge before admission
   - Impossible date sequences (e.g., procedure on 24/11 when admitted 24/11 but CAG on 16/10)
   - Report dates before procedure dates
   - Look for specific date contradictions

2. Missing Critical Identifiers:
   - UHID, IPD No, Patient Name
   - Age, Gender
   - Admission date (DOA), Discharge date (DOD)
   - Physician name/signature

3. Test Name Errors:
   - Wrong investigation names (FBS vs RBS confusion)
   - Critical lab test misspellings that could cause confusion

4. Missing Critical Sections (ONLY these 3):
   - Diagnosis section missing or empty
   - Medications/discharge advice section missing
   - Follow-up instructions missing

IGNORE:
- General NABH format compliance
- Section organization, formatting
- Non-critical missing sections (chief complaints, course in hospital)
- Minor date format inconsistencies
- Emergency contact information

SEVERITY RULES:
- HIGH: Legal/timeline impossibility, missing required identifiers, missing critical sections
- MEDIUM: Data inconsistencies (age mismatch across document)
- NEVER use LOW severity

Return ONLY valid JSON:
{{
  "issues": [
    {{
      "type": "timeline_impossible|date_logic_error|missing_identifier|missing_critical_section|test_name_error|age_mismatch",
      "severity": "HIGH|MEDIUM",
      "location": "section name",
      "current": "current state",
      "suggestion": "required correction",
      "explanation": "safety/legal concern"
    }}
  ]
}}

DISCHARGE SUMMARY:
{content}""",

            "claude": """<task>Validate critical data integrity in discharge summary</task>

<focus_areas>
1. Timeline Logic:
   - Procedures before admission
   - Impossible date sequences
   - Report dates before procedures

2. Missing Identifiers:
   - UHID, IPD, Name, Age, Gender
   - Admission/discharge dates
   - Physician identification

3. Test Name Errors:
   - Investigation name mistakes
   - Lab test misspellings

4. Missing Critical Sections:
   - Diagnosis
   - Medications
   - Follow-up instructions
</focus_areas>

<ignore>
- NABH formatting
- Section organization
- Non-critical sections
- Minor date formatting
</ignore>

<severity>
HIGH: Legal/timeline impossibility, missing IDs, missing critical sections
MEDIUM: Data inconsistencies
LOW: NEVER USE
</severity>

<output_format>
{{
  "issues": [
    {{
      "type": "timeline_impossible|date_logic_error|missing_identifier|missing_critical_section|test_name_error|age_mismatch",
      "severity": "HIGH|MEDIUM",
      "location": "section",
      "current": "current state",
      "suggestion": "correction",
      "explanation": "concern"
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
            "gemini": "You are a medical data integrity expert. Focus on critical data errors only.",
            "claude": "You are a medical data integrity expert. Focus on critical data errors only."
        }
