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
    LINGUISTIC = "linguistic"
    STRUCTURAL = "structural"
    CLINICAL = "clinical"
    TERMINOLOGY = "terminology"
    CRITICAL_DATA = "critical_data"


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    CLAUDE = "claude"
