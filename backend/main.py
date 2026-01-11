"""
FastAPI server for Discharge Summary Validator
"""
import asyncio
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
from utils.report_generator import ReportGenerator
from agents.clinical_safety import ClinicalSafetyAgent
from agents.critical_data_safety import CriticalDataSafetyAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global managers
cache_manager: Optional[CacheManager] = None
report_generator: Optional[ReportGenerator] = None
latest_report_path: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global cache_manager, report_generator

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

    # Initialize report generator
    report_generator = ReportGenerator(output_dir="reports")

    logger.info(f"Cache initialized: {cache_manager.get_stats()}")
    logger.info("Report generator initialized")

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
        "docs": "/docs",
        "test_page": "/test"
    }


@app.get("/test")
async def test_page():
    """Serve SSE test page"""
    from fastapi.responses import HTMLResponse

    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>SSE Test - Discharge Validator</title>
    <style>
        body {
            font-family: monospace;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .log {
            background: #252526;
            border: 1px solid #3c3c3c;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            max-height: 600px;
            overflow-y: auto;
        }
        .event {
            margin: 10px 0;
            padding: 8px;
            border-left: 3px solid #007acc;
            background: #2d2d30;
        }
        .event-type {
            color: #4ec9b0;
            font-weight: bold;
        }
        .event-data {
            color: #ce9178;
            margin-left: 20px;
            white-space: pre-wrap;
        }
        button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background: #1177bb;
        }
        .stats {
            background: #3c3c3c;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        textarea {
            width: 100%;
            height: 150px;
            background: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 10px;
            font-family: monospace;
        }
        .success { color: #4ec9b0; }
        .error { color: #f48771; }
    </style>
</head>
<body>
    <h1>SSE Stream Testing Tool</h1>

    <div class="stats">
        <div>Status: <span id="status">Ready</span></div>
        <div>Events Received: <span id="event-count">0</span></div>
        <div>Duration: <span id="duration">0s</span></div>
    </div>

    <h3>Test Content</h3>
    <textarea id="content">Patient: John Doe
Age: 45 years
Admission Date: 24/11/2024
Discharge Date: 25/11/2024

Chief Complaint: Chest pain

History: Patient presented with acute chest pain.</textarea>

    <div>
        <button onclick="testAnalysis('gemini')">Test Gemini Analysis</button>
        <button onclick="clearLog()">Clear Log</button>
    </div>

    <h3>Event Log</h3>
    <div id="log" class="log"></div>

    <script>
        let eventCount = 0;
        let startTime = null;
        let durationInterval = null;

        function log(message, type = 'info') {
            const logDiv = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = 'event';

            const color = type === 'error' ? 'error' : type === 'complete' ? 'success' : 'event-type';
            entry.innerHTML = \`<span class="\${color}">\${type.toUpperCase()}</span>: \${message}\`;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function updateStats() {
            document.getElementById('event-count').textContent = eventCount;
            if (startTime) {
                const duration = ((Date.now() - startTime) / 1000).toFixed(1);
                document.getElementById('duration').textContent = duration + 's';
            }
        }

        async function testAnalysis(llmProvider) {
            const content = document.getElementById('content').value;
            if (!content.trim()) {
                alert('Please enter discharge summary content');
                return;
            }

            eventCount = 0;
            startTime = Date.now();
            document.getElementById('status').textContent = 'Streaming...';
            clearLog();

            log(\`Starting analysis with \${llmProvider}...\`, 'start');

            try {
                const response = await fetch('/api/analyze/stream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: content,
                        llm_provider: llmProvider
                    })
                });

                if (!response.ok) {
                    throw new Error(\`HTTP \${response.status}\`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                durationInterval = setInterval(updateStats, 100);

                while (true) {
                    const { done, value } = await reader.read();

                    if (done) {
                        log('Stream ended', 'complete');

                        // Process final buffer
                        if (buffer.trim()) {
                            log(\`Final buffer: \${buffer.length} chars\`, 'buffer');
                            const finalLines = buffer.split('\\n\\n').filter(line => line.trim());
                            log(\`Processing \${finalLines.length} final events\`, 'buffer');

                            for (const line of finalLines) {
                                const eventMatch = line.match(/^event: (.+)$/m);
                                const dataMatch = line.match(/^data: (.+)$/m);

                                if (eventMatch && dataMatch) {
                                    const eventType = eventMatch[1];
                                    const data = JSON.parse(dataMatch[1]);
                                    eventCount++;
                                    const dataStr = JSON.stringify(data, null, 2);
                                    log(\`<div class="event-type">\${eventType}</div><div class="event-data">\${dataStr}</div>\`, 'event');
                                }
                            }
                        }

                        break;
                    }

                    buffer += decoder.decode(value, { stream: true });

                    // Process complete events
                    const lines = buffer.split('\\n\\n');
                    buffer = lines.pop() || '';

                    for (const line of lines) {
                        if (!line.trim()) continue;

                        const eventMatch = line.match(/^event: (.+)$/m);
                        const dataMatch = line.match(/^data: (.+)$/m);

                        if (eventMatch && dataMatch) {
                            const eventType = eventMatch[1];
                            const data = JSON.parse(dataMatch[1]);
                            eventCount++;
                            updateStats();
                            const dataStr = JSON.stringify(data, null, 2);
                            log(\`<div class="event-type">\${eventType}</div><div class="event-data">\${dataStr}</div>\`, 'event');
                        }
                    }
                }

                document.getElementById('status').textContent = 'Complete';
                clearInterval(durationInterval);
                updateStats();

            } catch (err) {
                log(\`ERROR: \${err.message}\`, 'error');
                document.getElementById('status').textContent = 'Error';
                clearInterval(durationInterval);
            }
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
            eventCount = 0;
            startTime = null;
            if (durationInterval) {
                clearInterval(durationInterval);
            }
            document.getElementById('status').textContent = 'Ready';
            updateStats();
        }

        updateStats();
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)


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
        global latest_report_path
        total_agents = 2
        completed_agents = 0
        cache_hits = 0
        all_issues = []
        all_results = {}  # Store results for report generation
        start_time = time.time()

        try:
            # Check if we have cached results for this exact content
            cached_data = report_generator.get_cached_results(
                request.content,
                request.llm_provider.value
            )

            if cached_data:
                # Use cached results - no API calls needed!
                logger.info("Using cached results from previous analysis")

                # Send started event
                yield {
                    "event": "started",
                    "data": json.dumps({
                        "total_agents": total_agents,
                        "llm_provider": request.llm_provider.value,
                        "from_cache": True,
                        "cached_at": cached_data.get('cached_at')
                    })
                }

                # Stream cached agent results IN ORDER
                all_results = cached_data['results']
                agent_order = ['clinical_safety', 'critical_data_safety']

                for agent_name in agent_order:
                    agent_data = all_results.get(agent_name, {})
                    issues = agent_data.get('issues', [])
                    all_issues.extend(issues)
                    completed_agents += 1
                    cache_hits += 1

                    agent_result = AgentResult(
                        agent_name=agent_name,
                        issues=issues,
                        from_cache=True,
                        processing_time=0.0
                    )

                    event_data = {
                        **agent_result.model_dump(),
                        "progress_percentage": (completed_agents / total_agents) * 100
                    }

                    yield {
                        "event": "agent_complete",
                        "data": json.dumps(event_data)
                    }

                # Send completion event with cached summary
                summary_data = cached_data['summary'].copy()
                summary_data['cache_hit_rate'] = 100.0  # All from cache
                summary_data['total_processing_time'] = time.time() - start_time

                yield {
                    "event": "analysis_complete",
                    "data": json.dumps(summary_data)
                }

                # CRITICAL: Add delay to ensure all events are flushed to client
                # before connection closes. Without this, cached results (which
                # yield all events instantly) close the connection before the
                # client receives all events from the network buffer.
                await asyncio.sleep(0.1)

                logger.info(f"Cached analysis returned: {len(all_issues)} issues in {time.time() - start_time:.2f}s")
                return

            # No cache hit - proceed with normal analysis
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
                ClinicalSafetyAgent(),
                CriticalDataSafetyAgent()
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

                # Store results for report generation
                all_results[agent.name] = {
                    "issues": issues,
                    "from_cache": from_cache,
                    "processing_time": processing_time
                }

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
            summary_data = summary.model_dump()
            yield {
                "event": "analysis_complete",
                "data": json.dumps(summary_data)
            }

            # Small delay to ensure event is flushed before any cleanup
            await asyncio.sleep(0.05)

            # Generate report file
            try:
                report_path, content_hash = report_generator.generate_report(
                    content=request.content,
                    results=all_results,
                    summary=summary_data,
                    llm_provider=request.llm_provider.value
                )
                latest_report_path = report_path
                logger.info(f"Report generated: {report_path} (hash: {content_hash[:8]}...)")
            except Exception as e:
                logger.error(f"Failed to generate report: {str(e)}")

            logger.info(f"Analysis complete: {len(all_issues)} issues found in {total_time:.2f}s")

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())


@app.post("/api/test/stream")
async def test_stream():
    """Test SSE streaming"""
    async def test_generator():
        for i in range(5):
            yield {
                "event": "test",
                "data": json.dumps({"count": i, "message": f"Test event {i}"})
            }
        yield {
            "event": "complete",
            "data": json.dumps({"message": "Test complete"})
        }

    return EventSourceResponse(test_generator())


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


@app.get("/api/report/download")
async def download_report():
    """Download the latest validation report"""
    from fastapi.responses import FileResponse

    if not latest_report_path or not os.path.exists(latest_report_path):
        raise HTTPException(status_code=404, detail="No report available")

    return FileResponse(
        path=latest_report_path,
        media_type="text/plain",
        filename=os.path.basename(latest_report_path)
    )


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
