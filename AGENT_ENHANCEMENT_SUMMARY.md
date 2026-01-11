# Clinical Safety Agent Enhancement

## Summary
Enhanced the `ClinicalSafetyAgent` with 3 focused features that doctors value, without creating duplication or additional API calls.

## Why NOT a 3rd Agent?
- **Cost Efficiency**: Keeps API calls at 2 (vs 3 with new agent)
- **Simplicity**: Maintains clear mental model for doctors
- **Natural Fit**: All features answer "Could this harm my patient?"

## New Features Added to ClinicalSafetyAgent

### 1. Discharge Readiness Check
**Doctor Question**: "Is this patient really safe to go home?"

**What It Checks**:
- Severe unresolved findings at discharge (e.g., EF <30%, critical SpO₂, severe lab values)
- ICU-level diagnosis with minimal/unclear follow-up plan

**Key Principle**: Flag only if clearly unsafe - don't judge medical decisions

**New Issue Type**: `unsafe_discharge_readiness`

---

### 2. Follow-up Adequacy for High-Risk Patients
**Doctor Question**: "Did we clearly tell the patient what to do next?"

**What It Checks**:
- High-risk patients (cardiac, post-ICU, critical diagnosis) without follow-up timeframe
- Critical diagnosis (cancer, heart failure, post-MI) without specialty follow-up mentioned

**Key Principle**: Flag only if creates safety gap, not cosmetic issues

**No Duplication**:
- `CriticalDataSafetyAgent` checks if follow-up section EXISTS (data completeness)
- `ClinicalSafetyAgent` now checks if follow-up is ADEQUATE for high-risk cases (clinical safety)

**New Issue Type**: `inadequate_followup_highrisk`

---

### 3. Medication Instruction Ambiguity
**Doctor Question**: "Will the patient/pharmacist understand these instructions?"

**What It Checks**:
- Complex medication schedules without clarity (e.g., "D5-D7 skip weekends" - which days exactly?)
- SOS/PRN medications without clear indication or context

**Key Principle**: This is about CLARITY that prevents errors, NOT prescribing advice

**New Issue Type**: `ambiguous_medication_instruction`

---

## What We Deliberately DID NOT Add

To avoid doctor fatigue and maintain trust:

❌ General guideline adherence
❌ Missing "ideal" heart failure meds
❌ Readmission prediction scores
❌ Grammar, formatting, NABH cosmetics
❌ "Consider adding X medication"
❌ Risk scoring numbers

## Updated Mental Model

| Agent | Doctor Question |
|-------|----------------|
| Clinical Safety | "Could this harm my patient?" |
| Critical Data Safety | "Could this harm me legally?" |

## Clean Explanation for Doctors

"This tool flags only patient safety risks, legal/data errors, and discharge red flags — nothing else."

## Technical Changes

**File Modified**: `backend/agents/clinical_safety.py`

**Changes**:
1. Updated class docstring with 3 new focus areas
2. Added sections 5, 6, 7 to both Gemini and Claude prompts
3. Added 3 new issue types to JSON schema
4. Updated severity rules to include new HIGH-severity scenarios

**Architecture**:
- Still 2 agents = 2 API calls
- No duplication with CriticalDataSafetyAgent
- Focused, actionable checks only
