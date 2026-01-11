"""
Critical Data Validation Agent - Validates dates, identifiers, and legal requirements
"""
from typing import Dict
from .base_agent import BaseAgent


class CriticalDataAgent(BaseAgent):
    """
    Agent focused on critical data validation:
    - Date consistency and accuracy
    - Patient identifiers (UHID, IPD)
    - Timeline logic
    - Legal and regulatory requirements
    - Signature and authentication
    - Consent documentation
    """

    @property
    def PROMPTS(self) -> Dict[str, str]:
        return {
            "gemini": """You are a medical-legal compliance reviewer for discharge documentation.

Analyze the discharge summary for critical data accuracy:
1. Date consistency:
   - Admission date (DOA) vs discharge date (DOD)
   - Procedure dates matching hospital stay
   - Timeline logic (procedures before admission, etc.)
   - Date format consistency

2. Patient identifiers:
   - UHID present and valid
   - IPD number present
   - Age consistency throughout document
   - Gender consistency

3. Legal requirements:
   - Consultant/physician identification
   - Department specification
   - Emergency contact information
   - Follow-up instructions present

4. Critical missing information:
   - Missing dates
   - Missing identifiers
   - Incomplete contact information

Examples of critical issues:
- Procedure date before admission date
- Different ages mentioned in same document
- Missing discharge date
- Conflicting dates (CAG on 16/10 but PTCA on 24/11 when admitted 24/11)

Return ONLY valid JSON in this exact format:
{{
  "issues": [
    {{
      "type": "date_inconsistency|date_logic|missing_identifier|age_mismatch|missing_legal_info|format_inconsistency",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "relevant section",
      "current": "current problematic data",
      "suggestion": "correction or what should be present",
      "explanation": "legal or safety implication"
    }}
  ]
}}

DISCHARGE SUMMARY:
{content}""",

            "claude": """<task>Review this discharge summary for critical data accuracy and legal compliance</task>

<focus_areas>
Date Validation:
- Admission vs discharge date logic
- Procedure dates within hospital stay
- Date format consistency
- Timeline coherence

Patient Identifiers:
- UHID completeness
- IPD number presence
- Age consistency across document
- Gender consistency

Legal Requirements:
- Physician identification
- Department specification
- Emergency contact information
- Follow-up instructions
- Required signatures/authentication

Critical Data Completeness:
- All required dates present
- All identifiers present
- Contact information complete
</focus_areas>

<critical_date_checks>
- Procedures must occur between admission and discharge
- Dates should be logically sequential
- Age mentioned should be consistent
- Date formats should be standardized
</critical_date_checks>

<output_format>
Return ONLY valid JSON:
{{
  "issues": [
    {{
      "type": "date_inconsistency|date_logic|missing_identifier|age_mismatch|missing_legal_info|format_inconsistency",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name",
      "current": "current state",
      "suggestion": "required correction",
      "explanation": "legal/safety concern"
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
            "gemini": "You are a medical-legal compliance expert focusing on critical data accuracy.",
            "claude": "You are an expert in medical-legal compliance and critical data validation."
        }
