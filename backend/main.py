"""
FastAPI server for Discharge Summary Validator
"""
import json
import os
import time
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from models.schemas import (
    AnalysisRequest,
    AgentResult,
    AnalysisSummary,
    HealthCheckResponse
)
from models.enums import LLMProvider
from llm.llm_factory import LLMFactory
from cache.redis_cache import CacheManager
from utils.hasher import generate_cache_key
from agents.linguistic import LinguisticAgent
from agents.structural import StructuralAgent
from agents.clinical import ClinicalAgent
from agents.terminology import TerminologyAgent
from agents.critical_data import CriticalDataAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global cache manager
cache_manager: Optional[CacheManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global cache_manager

    # Startup
    logger.info("Starting Discharge Validator API...")

    # Initialize cache manager
    redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD", None)

    cache_manager = CacheManager(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_password=redis_password,
        redis_enabled=redis_enabled
    )

    logger.info(f"Cache initialized: {cache_manager.get_stats()}")

    yield

    # Shutdown
    logger.info("Shutting down Discharge Validator API...")


# Create FastAPI app
app = FastAPI(
    title="Discharge Summary Validator API",
    description="Real-time discharge summary validation with dual LLM support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Discharge Summary Validator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    gemini_key = os.getenv("GEMINI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")

    redis_connected = await cache_manager.is_connected() if cache_manager else False

    return HealthCheckResponse(
        status="healthy",
        redis_connected=redis_connected,
        gemini_configured=bool(gemini_key),
        claude_configured=bool(claude_key)
    )


@app.post("/api/analyze/stream")
async def stream_analysis(request: AnalysisRequest):
    """
    Stream analysis results using Server-Sent Events (SSE)

    Event types:
    - started: Initial metadata
    - agent_progress: Progress update
    - agent_complete: Agent finished
    - analysis_complete: All agents done
    - error: Error occurred
    """

    async def event_generator():
        total_agents = 5
        completed_agents = 0
        cache_hits = 0
        all_issues = []
        start_time = time.time()

        try:
            # Get API key for selected LLM
            if request.llm_provider == LLMProvider.GEMINI:
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": "Gemini API key not configured"})
                    }
                    return
            else:  # Claude
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": "Claude API key not configured"})
                    }
                    return

            # Initialize LLM client
            llm_client = LLMFactory.get_client(request.llm_provider, api_key)

            # Send started event
            yield {
                "event": "started",
                "data": json.dumps({
                    "total_agents": total_agents,
                    "llm_provider": request.llm_provider.value
                })
            }

            # Initialize all agents
            agents = [
                LinguisticAgent(),
                StructuralAgent(),
                ClinicalAgent(),
                TerminologyAgent(),
                CriticalDataAgent()
            ]

            # Process each agent
            for idx, agent in enumerate(agents):
                agent_start_time = time.time()

                # Generate cache key
                cache_key = generate_cache_key(
                    request.llm_provider.value,
                    agent.name,
                    request.content
                )

                # Check cache
                cached_result = await cache_manager.get(cache_key)

                if cached_result:
                    # Cache hit
                    cache_hits += 1
                    issues = [issue for issue in cached_result.get("issues", [])]
                    from_cache = True
                    processing_time = 0.0
                    logger.info(f"Cache hit for {agent.name}")
                else:
                    # Cache miss - run analysis
                    logger.info(f"Running {agent.name} agent...")
                    from_cache = False

                    # Send progress event
                    yield {
                        "event": "agent_progress",
                        "data": json.dumps({
                            "agent_name": agent.name,
                            "status": "analyzing",
                            "progress_percentage": (idx / total_agents) * 100
                        })
                    }

                    # Run agent analysis
                    issue_models = await agent.analyze(
                        request.content,
                        llm_client,
                        request.llm_provider.value
                    )

                    # Convert to dict for caching and response
                    issues = [issue.model_dump() for issue in issue_models]
                    processing_time = time.time() - agent_start_time

                    # Cache the result
                    await cache_manager.set(
                        cache_key,
                        {"issues": issues},
                        ttl=86400  # 24 hours
                    )

                # Accumulate issues
                all_issues.extend(issues)
                completed_agents += 1

                # Send agent complete event
                agent_result = AgentResult(
                    agent_name=agent.name,
                    issues=issues,
                    from_cache=from_cache,
                    processing_time=processing_time
                )

                yield {
                    "event": "agent_complete",
                    "data": json.dumps({
                        **agent_result.model_dump(),
                        "progress_percentage": (completed_agents / total_agents) * 100
                    })
                }

            # Calculate summary statistics
            total_time = time.time() - start_time
            high_count = sum(1 for issue in all_issues if issue.get("severity") == "HIGH")
            medium_count = sum(1 for issue in all_issues if issue.get("severity") == "MEDIUM")
            low_count = sum(1 for issue in all_issues if issue.get("severity") == "LOW")

            summary = AnalysisSummary(
                total_issues=len(all_issues),
                high_severity_count=high_count,
                medium_severity_count=medium_count,
                low_severity_count=low_count,
                cache_hit_rate=(cache_hits / total_agents) * 100,
                total_processing_time=total_time,
                agents_completed=completed_agents
            )

            # Send completion event
            yield {
                "event": "analysis_complete",
                "data": json.dumps(summary.model_dump())
            }

            logger.info(f"Analysis complete: {len(all_issues)} issues found in {total_time:.2f}s")

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())


@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    if not cache_manager:
        raise HTTPException(status_code=500, detail="Cache manager not initialized")

    return cache_manager.get_stats()


@app.post("/api/cache/clear")
async def clear_cache():
    """Clear all cached results"""
    if not cache_manager:
        raise HTTPException(status_code=500, detail="Cache manager not initialized")

    success = await cache_manager.clear_all()

    return {
        "success": success,
        "message": "Cache cleared successfully" if success else "Failed to clear cache"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
