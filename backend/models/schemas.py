"""
Pydantic schemas for request/response validation
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import Severity, Category, LLMProvider


class IssueModel(BaseModel):
    """Model for a single validation issue"""
    category: str = Field(..., description="Agent category that found the issue")
    type: str = Field(..., description="Specific type of issue")
    severity: Severity = Field(..., description="Issue severity level")
    location: str = Field(..., description="Location in the document")
    current: str = Field(..., description="Current problematic text")
    suggestion: str = Field(..., description="Suggested correction")
    explanation: str = Field(..., description="Why this is an issue")


class AnalysisRequest(BaseModel):
    """Request model for discharge summary analysis"""
    content: str = Field(..., min_length=1, description="Discharge summary content")
    llm_provider: LLMProvider = Field(..., description="LLM provider to use")


class AgentResult(BaseModel):
    """Result from a single agent analysis"""
    agent_name: str = Field(..., description="Name of the agent")
    issues: List[IssueModel] = Field(default_factory=list, description="List of issues found")
    from_cache: bool = Field(default=False, description="Whether result came from cache")
    processing_time: float = Field(..., description="Time taken to process in seconds")


class AnalysisProgress(BaseModel):
    """Progress update during streaming analysis"""
    agent_name: str = Field(..., description="Current agent being processed")
    status: str = Field(..., description="Status: started, processing, completed")
    progress_percentage: float = Field(..., description="Overall progress 0-100")


class AnalysisSummary(BaseModel):
    """Final summary of the analysis"""
    total_issues: int = Field(..., description="Total number of issues found")
    high_severity_count: int = Field(default=0, description="Number of high severity issues")
    medium_severity_count: int = Field(default=0, description="Number of medium severity issues")
    low_severity_count: int = Field(default=0, description="Number of low severity issues")
    cache_hit_rate: float = Field(..., description="Percentage of results from cache")
    total_processing_time: float = Field(..., description="Total time taken in seconds")
    agents_completed: int = Field(..., description="Number of agents completed")


class HealthCheckResponse(BaseModel):
    """Health check endpoint response"""
    status: str = Field(default="healthy", description="Service status")
    redis_connected: bool = Field(..., description="Redis connection status")
    gemini_configured: bool = Field(..., description="Gemini API key configured")
    claude_configured: bool = Field(..., description="Claude API key configured")
