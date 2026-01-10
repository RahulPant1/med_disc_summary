# Instructions for Claude Code

## 📋 Overview
You are building a **Discharge Summary Validation MVP** with real-time streaming results and intelligent caching.

---

## 📁 Reference Documents
Read these files in order:
1. `PROJECT_PLAN.md` - Complete technical architecture
2. `SAMPLE_DISCHARGE_SUMMARY.md` - Test data with known issues
3. This file - Execution instructions

---

## 🎯 Build Process (Follow in Order)

### **Phase 1: Project Setup**
```bash
# Create project structure exactly as specified in PROJECT_PLAN.md
# Include all directories and files
```

**Deliverables:**
- [ ] Project folder structure created
- [ ] `requirements.txt` with all dependencies
- [ ] `package.json` for frontend
- [ ] `.env.example` with required variables
- [ ] `.gitignore` configured

---

### **Phase 2: Backend Foundation**

#### 2.1 Core Models & Schemas
Create in `backend/models/`:
- [ ] `enums.py` - Severity, Category, LLMProvider enums
- [ ] `schemas.py` - Pydantic models for requests/responses

**Models needed:**
```python
class IssueModel(BaseModel):
    category: str
    type: str
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    location: str
    current: str
    suggestion: str
    explanation: str

class AnalysisRequest(BaseModel):
    content: str
    llm_provider: Literal["gemini", "claude"]

class AgentResult(BaseModel):
    agent_name: str
    issues: List[IssueModel]
    from_cache: bool
    processing_time: float
```

#### 2.2 LLM Clients
Create in `backend/llm/`:
- [ ] `base_client.py` - Abstract base class
- [ ] `gemini_client.py` - Google Gemini implementation
- [ ] `claude_client.py` - Anthropic Claude implementation
- [ ] `llm_factory.py` - Factory pattern for client selection

**Key methods:**
```python
class BaseLLMClient(ABC):
    @abstractmethod
    async def analyze(self, prompt: str, system: str) -> dict:
        """Single request-response"""
        pass
    
    @abstractmethod
    async def stream_analyze(self, prompt: str, system: str):
        """Streaming generator"""
        pass
```

#### 2.3 Caching Layer
Create in `backend/cache/`:
- [ ] `redis_cache.py` - Redis integration with hashing

**Key functions:**
```python
def generate_cache_key(llm: str, agent: str, content: str) -> str:
    """Create deterministic hash-based key"""
    
async def get_cached_result(key: str) -> Optional[dict]:
    """Retrieve from cache"""
    
async def set_cached_result(key: str, value: dict, ttl: int = 86400):
    """Store with 24hr TTL"""
```

#### 2.4 Agent Implementations
Create in `backend/agents/`:
- [ ] `base_agent.py` - Abstract agent class
- [ ] `linguistic.py` - Spelling, grammar, clarity
- [ ] `structural.py` - NABH compliance, sections
- [ ] `clinical.py` - Medical consistency, safety
- [ ] `terminology.py` - Abbreviations, standardization
- [ ] `critical_data.py` - Dates, identifiers, legal

**Each agent must:**
1. Have prompts optimized for BOTH Gemini and Claude
2. Return standardized JSON with issues array
3. Support async execution
4. Handle errors gracefully

**Example agent structure:**
```python
class LinguisticAgent(BaseAgent):
    name = "linguistic"
    
    PROMPTS = {
        "gemini": "...",
        "claude": "..."
    }
    
    async def analyze(self, content: str, llm_client, llm_provider: str):
        prompt = self.PROMPTS[llm_provider].format(content=content)
        result = await llm_client.analyze(prompt)
        return self.parse_result(result)
```

#### 2.5 FastAPI Server
Create `backend/main.py`:
- [ ] CORS configuration
- [ ] Environment variable loading
- [ ] Health check endpoint
- [ ] Main streaming endpoint

**Critical endpoint:**
```python
@app.post("/api/analyze/stream")
async def stream_analysis(request: AnalysisRequest):
    """
    Stream analysis results using Server-Sent Events
    
    Event types:
    - started: Initial metadata
    - agent_progress: Partial results during processing
    - agent_complete: Full results for one agent
    - analysis_complete: Final summary
    """
    async def event_generator():
        # Implementation as per PROJECT_PLAN.md
        pass
    
    return EventSourceResponse(event_generator())
```

---

### **Phase 3: Frontend Development**

#### 3.1 React Setup
Initialize in `frontend/`:
- [ ] Vite + React project
- [ ] Tailwind CSS configuration
- [ ] Lucide React icons

#### 3.2 Core Components
Create in `frontend/src/components/`:

**UploadSection.jsx:**
```jsx
// Text area + file upload
// LLM provider selection (radio buttons)
// Analyze button with loading state
```

**ProgressIndicator.jsx:**
```jsx
// Progress bar (0-100%)
// Cache hit counter
// Current agent being processed
```

**RealTimeIssueStream.jsx:**
```jsx
// Container for streaming results
// Uses EventSource for SSE
// Displays issues as they arrive
// Shows which results came from cache
```

**IssueCard.jsx:**
```jsx
// Individual issue display
// Color-coded by severity
// Expandable for details
// Shows: type, location, current, suggestion, explanation
```

**CategoryAccordion.jsx:**
```jsx
// Group issues by agent/category
// Collapsible sections
// Count badges
```

**ExecutiveSummary.jsx:**
```jsx
// Overall statistics
// Total issues by severity
// Risk level indicator
// Cache performance metrics
```

#### 3.3 Custom Hooks
Create in `frontend/src/hooks/`:

**useStreamingAnalysis.js:**
```javascript
function useStreamingAnalysis() {
    const [results, setResults] = useState({});
    const [progress, setProgress] = useState(0);
    const [loading, setLoading] = useState(false);
    const [cacheHits, setCacheHits] = useState(0);
    
    const startAnalysis = async (content, llmProvider) => {
        // EventSource connection
        // Handle events: started, agent_complete, analysis_complete
        // Update state progressively
    };
    
    return { results, progress, loading, cacheHits, startAnalysis };
}
```

#### 3.4 Main App
Create `frontend/src/App.jsx`:
- [ ] Layout with upload section and results
- [ ] State management for analysis
- [ ] Error handling and display
- [ ] Export functionality

---

### **Phase 4: Integration & Testing**

#### 4.1 Environment Configuration
Create `.env`:
```bash
GEMINI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
REDIS_HOST=localhost
REDIS_PORT=6379
CORS_ORIGINS=http://localhost:5173
```

#### 4.2 Testing Checklist
Use `SAMPLE_DISCHARGE_SUMMARY.md` for testing:

**Functional Tests:**
- [ ] Upload text successfully
- [ ] Select Gemini provider - analysis works
- [ ] Select Claude provider - analysis works
- [ ] Results stream in real-time (not all at once)
- [ ] Second analysis uses cache (instant results)
- [ ] Cache hit indicator shows correctly

**Validation Tests (Known Issues):**
- [ ] Date inconsistency detected (CAG: 16/10 vs 24/10 vs 24/11)
- [ ] High FBS (208 mg/dL) flagged as clinical risk
- [ ] Age discrepancy caught (80 vs 81)
- [ ] Spelling errors found (DIATED, PROIMAL, ANOUT)
- [ ] Abbreviation K/c/o flagged
- [ ] Polypharmacy noted (12 meds for 81-year-old)

**Performance Tests:**
- [ ] First analysis completes in <30 seconds
- [ ] Cached analysis completes in <2 seconds
- [ ] UI remains responsive during streaming
- [ ] No race conditions in result display

#### 4.3 Error Handling
Test failure scenarios:
- [ ] Invalid API key - show clear error
- [ ] Redis connection failure - fallback gracefully
- [ ] LLM timeout - retry logic
- [ ] Malformed response - log and skip agent
- [ ] Network interruption - reconnect SSE

---

## 🚨 Critical Implementation Notes

### **For Caching:**
```python
# IMPORTANT: Hash the EXACT content, not trimmed/normalized
# This ensures cache hits only for identical documents
cache_key = f"{llm_provider}:{agent_name}:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
```

### **For Streaming:**
```python
# Use sse-starlette for proper SSE formatting
from sse_starlette.sse import EventSourceResponse

# Events must be valid JSON strings
yield {
    "event": "agent_complete",
    "data": json.dumps(agent_result)
}
```

### **For Agent Prompts:**
- Include clear instructions for JSON-only output
- Specify exact field names and types
- Add examples for clarity
- Keep prompts under 2000 tokens
- Different prompts for Gemini vs Claude (they respond to different styles)

### **For Frontend SSE:**
```javascript
const eventSource = new EventSource('/api/analyze/stream');

// Handle different event types
eventSource.addEventListener('agent_complete', (e) => {
    const data = JSON.parse(e.data);
    // Update state
});

// Always close when done
eventSource.close();
```

---

## 📊 Expected Output Structure

After analysis, the frontend should display:

```
┌─────────────────────────────────────────┐
│ EXECUTIVE SUMMARY                        │
│ Overall Risk: 🔴 HIGH                   │
│ Total Issues: 15                         │
│ 🔴 Critical: 3  🟠 Medium: 7  🟡 Low: 5│
│ ⚡ Cache: 3/5 agents (60% hit rate)     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔴 CRITICAL ISSUES (3)                  │
├─────────────────────────────────────────┤
│ [Clinical Consistency]                   │
│ Date Inconsistency in CAG Procedure      │
│ Evidence: "CAG was done on 16/10/2025"  │
│          "PTCA was done on 24/11/2025"  │
│ Suggestion: Verify and standardize dates│
└─────────────────────────────────────────┘

... (more issues grouped by severity)
```

---

## 🎯 Definition of Done

The MVP is complete when:

### Functional Requirements:
- [x] All 5 agents implemented and working
- [x] Both Gemini and Claude providers functional
- [x] Real-time streaming working (progressive results)
- [x] Caching operational (>70% hit rate on second run)
- [x] All known issues in sample data detected
- [x] UI displays results clearly

### Code Quality:
- [x] Type hints throughout Python code
- [x] Comprehensive error handling
- [x] Logging configured
- [x] Comments for complex logic
- [x] No hardcoded secrets

### Documentation:
- [x] README.md with setup instructions
- [x] API documentation
- [x] Environment variables documented
- [x] Testing guide included

---

## 🐛 Common Pitfalls to Avoid

1. **Don't** call all agents sequentially - use `asyncio.gather()` for parallel execution
2. **Don't** forget to close EventSource connections
3. **Don't** cache results without TTL - set 24hr expiration
4. **Don't** expose API keys in frontend code
5. **Don't** parse LLM responses without try-catch
6. **Don't** block the UI while streaming
7. **Don't** forget CORS configuration for local development

---

## 📚 Reference Resources

**Python Libraries:**
- FastAPI SSE: https://github.com/sysid/sse-starlette
- Anthropic SDK: https://docs.anthropic.com/claude/reference/client-sdks
- Google Gemini: https://ai.google.dev/tutorials/python_quickstart

**Frontend:**
- EventSource API: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
- React Streaming: https://react.dev/reference/react/Suspense

---

## ✅ Final Checklist Before Delivery

- [ ] All dependencies in requirements.txt and package.json
- [ ] .env.example includes all required variables
- [ ] README.md has clear setup instructions
- [ ] Sample discharge summary successfully analyzed
- [ ] Both LLM providers tested
- [ ] Caching verified working
- [ ] No errors in browser console
- [ ] No errors in backend logs
- [ ] Code formatted and linted
- [ ] Git repository initialized with .gitignore

---

## 🚀 Start Command

Once setup is complete, run:

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Redis
redis-server

# Terminal 3 - Frontend
cd frontend
npm run dev
```

Access at: http://localhost:5173

---

**Good luck! Build methodically, test thoroughly, and refer back to PROJECT_PLAN.md for detailed specifications.**