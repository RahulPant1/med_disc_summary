"""
Clinical Safety Agent - Validates patient safety concerns
"""
from typing import Dict
from .base_agent import BaseAgent


class ClinicalSafetyAgent(BaseAgent):
    """
    Focus on immediate patient safety:
    - Drug safety (overdose, interactions, mismatches)
    - Abnormal findings without action
    - Dangerous abbreviations
    - Critical clinical logic errors
    """

    @property
    def PROMPTS(self) -> Dict[str, str]:
        return {
            "gemini": """You are a clinical safety specialist reviewing discharge summaries for CRITICAL PATIENT SAFETY ISSUES ONLY.

FOCUS EXCLUSIVELY ON:

1. Drug Safety Errors (HIGHEST PRIORITY):
   - Overdose/underdose (e.g., Clopidogrel 75mg BID instead of OD)
   - Drug-diagnosis mismatch (respiratory meds without respiratory diagnosis)
   - Dangerous interactions (anticoagulants + NSAIDs without indication)
   - Polypharmacy >10 medications in elderly (>65 years)
   - Misspelled drug or procedure names (clinical danger)

2. Dangerous Abbreviations (HIGH PRIORITY):
   - U or u (units) - can be read as 0
   - IU (International Unit) - can be read as IV
   - QD, QOD (daily/every other day) - confused with each other
   - MS, MSO4, MgSO4 (morphine vs magnesium)
   Flag ONLY if these exact abbreviations appear.

3. Abnormal Findings Without Documented Action:
   - Lab values requiring intervention (FBS >200, Hb <7, etc.) without management plan
   - Vital sign abnormalities without management plan
   - Critical findings without follow-up instructions

4. Clinical Logic Errors:
   - Missing diagnosis for prescribed medications
   - Procedures not matching stated diagnosis
   - Contradictory clinical information

IGNORE:
- Grammar, spelling of non-medical terms
- Sentence structure, clarity issues
- NABH formatting, section organization
- Non-dangerous abbreviations (K/c/o, B.P., etc.)
- Unit variations (mg vs mgm) unless causes dosing confusion

SEVERITY RULES:
- HIGH: Direct patient safety risk (overdose, untreated critical finding, dangerous interaction, dangerous abbreviation)
- MEDIUM: Clinical best practice (polypharmacy, documentation gaps)
- NEVER use LOW severity

Return ONLY valid JSON:
{{
  "issues": [
    {{
      "type": "drug_overdose|drug_diagnosis_mismatch|drug_interaction|dangerous_polypharmacy|drug_spelling_error|dangerous_abbreviation|abnormal_finding_no_action|missing_critical_diagnosis|procedure_mismatch|clinical_contradiction",
      "severity": "HIGH|MEDIUM",
      "location": "section name",
      "current": "problematic clinical data",
      "suggestion": "specific safety recommendation",
      "explanation": "patient safety concern"
    }}
  ]
}}

DISCHARGE SUMMARY:
{content}""",

            "claude": """<task>Review this discharge summary for CRITICAL PATIENT SAFETY ISSUES ONLY</task>

<focus_areas>
1. Drug Safety (HIGHEST PRIORITY):
   - Overdose/underdose errors
   - Drug-diagnosis mismatches
   - Dangerous interactions
   - Polypharmacy in elderly
   - Drug name misspellings

2. Dangerous Abbreviations:
   - U, IU, QD, QOD, MS, MSO4, MgSO4
   - Flag ONLY these specific abbreviations

3. Abnormal Findings:
   - Critical lab values without action
   - Abnormal vitals without management
   - Missing follow-up for critical findings

4. Clinical Logic:
   - Missing diagnosis for medications
   - Procedure-diagnosis mismatches
   - Contradictory information
</focus_areas>

<ignore>
- Grammar, non-medical spelling
- NABH formatting
- Non-dangerous abbreviations
- General quality issues
</ignore>

<severity>
HIGH: Patient safety risk
MEDIUM: Clinical best practice
LOW: NEVER USE
</severity>

<output_format>
{{
  "issues": [
    {{
      "type": "drug_overdose|drug_diagnosis_mismatch|drug_interaction|dangerous_polypharmacy|drug_spelling_error|dangerous_abbreviation|abnormal_finding_no_action|missing_critical_diagnosis|procedure_mismatch|clinical_contradiction",
      "severity": "HIGH|MEDIUM",
      "location": "section name",
      "current": "problematic data",
      "suggestion": "safety recommendation",
      "explanation": "safety concern"
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
            "gemini": "You are a clinical safety expert. Focus ONLY on patient safety risks.",
            "claude": "You are a clinical safety expert. Focus ONLY on patient safety risks."
        }
