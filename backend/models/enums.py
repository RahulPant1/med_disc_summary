"""
Enums for the discharge validator application
"""
from enum import Enum


class Severity(str, Enum):
    """Issue severity levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Category(str, Enum):
    """Validation agent categories"""
    CLINICAL_SAFETY = "clinical_safety"
    CRITICAL_DATA_SAFETY = "critical_data_safety"


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    CLAUDE = "claude"
