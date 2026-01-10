"""
Clinical Consistency Agent - Validates medical accuracy and safety
"""
from typing import Dict
from .base_agent import BaseAgent


class ClinicalAgent(BaseAgent):
    """
    Agent focused on clinical consistency and safety:
    - Diagnosis-treatment alignment
    - Medical data consistency
    - Drug-diagnosis compatibility
    - Vital signs abnormalities
    - Lab values interpretation
    - Polypharmacy concerns
    - Clinical logic and safety
    """

    @property
    def PROMPTS(self) -> Dict[str, str]:
        return {
            "gemini": """You are a clinical safety reviewer for medical discharge summaries.

Analyze the discharge summary for clinical consistency and safety:
1. Diagnosis-treatment alignment (do medications match diagnoses?)
2. Internal medical data consistency (contradictory information)
3. Abnormal vital signs or lab values without appropriate action
4. Drug interactions or contraindications
5. Polypharmacy concerns (especially in elderly patients)
6. Missing clinical information that affects safety
7. Procedures matching diagnoses
8. Clinical logic issues

Important examples to catch:
- High blood sugar without diabetes diagnosis/management
- Conflicting dates for procedures
- Age discrepancies
- Abnormal vital signs without explanation
- Multiple medications without documented indication

Return ONLY valid JSON in this exact format:
{{
  "issues": [
    {{
      "type": "diagnosis_mismatch|data_inconsistency|vital_sign_abnormal|drug_safety|polypharmacy|missing_clinical_info|procedure_mismatch|clinical_logic",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "relevant section",
      "current": "current problematic clinical information",
      "suggestion": "recommended action or correction",
      "explanation": "clinical safety or consistency concern"
    }}
  ]
}}

DISCHARGE SUMMARY:
{content}""",

            "claude": """<task>Review this discharge summary for clinical consistency and patient safety concerns</task>

<focus_areas>
- Diagnosis and treatment alignment
- Internal consistency of clinical data
- Abnormal findings requiring attention:
  * Vital signs outside normal range
  * Lab values requiring intervention
  * Unaddressed critical findings
- Medication safety:
  * Appropriate for diagnoses
  * Drug interactions
  * Polypharmacy (especially in elderly)
- Procedural consistency with diagnoses
- Temporal consistency (dates, sequences)
- Age-appropriate care
</focus_areas>

<critical_checks>
- High glucose without diabetes management
- Date inconsistencies in procedures
- Age discrepancies in documentation
- Multiple cardiovascular medications without documented indication
- Missing follow-up for abnormal findings
</critical_checks>

<output_format>
Return ONLY valid JSON:
{{
  "issues": [
    {{
      "type": "diagnosis_mismatch|data_inconsistency|vital_sign_abnormal|drug_safety|polypharmacy|missing_clinical_info|procedure_mismatch|clinical_logic",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name",
      "current": "problematic clinical data",
      "suggestion": "clinical recommendation",
      "explanation": "safety or consistency concern"
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
            "gemini": "You are a clinical safety expert specializing in medical documentation review.",
            "claude": "You are a clinical safety expert. Focus on medical consistency and patient safety."
        }
