MVP DEVELOPMENT PLAN FOR CLAUDE CODE
EXECUTIVE SUMMARY
Goal: Create a dynamic, real-time discharge summary validation app with dual LLM support (Gemini/Claude), streaming results, and intelligent caching.

📋 PROJECT STRUCTURE
discharge-validator-mvp/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Abstract agent class
│   │   ├── linguistic.py       # Agent 1
│   │   ├── structural.py       # Agent 2
│   │   ├── clinical.py         # Agent 3
│   │   ├── terminology.py      # Agent 4
│   │   └── critical_data.py    # Agent 5
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── claude_client.py
│   │   └── llm_factory.py      # Factory pattern for LLM selection
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_cache.py      # Caching layer
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models
│   │   └── enums.py
│   └── utils/
│       ├── __init__.py
│       ├── parser.py           # Text extraction
│       └── hasher.py           # Content hashing for cache
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── UploadSection.jsx
│   │   │   ├── ExecutiveSummary.jsx
│   │   │   ├── RealTimeIssueStream.jsx
│   │   │   ├── IssueCard.jsx
│   │   │   ├── CategoryAccordion.jsx
│   │   │   └── ProgressIndicator.jsx
│   │   ├── hooks/
│   │   │   ├── useStreamingResults.js
│   │   │   └── useWebSocket.js
│   │   └── utils/
│   │       └── api.js
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
├── package.json
├── .env.example
└── README.md

🔧 TECHNICAL ARCHITECTURE
1. STREAMING ARCHITECTURE
User Upload → FastAPI → Agent Orchestrator → Stream Results
                ↓
         Cache Check (Redis)
                ↓
         WebSocket/SSE Stream
                ↓
         Frontend Updates in Real-time
Key Design Decisions:

Server-Sent Events (SSE) for real-time streaming (simpler than WebSocket for one-way data)
Async/Await pattern for parallel agent execution
Progressive rendering on frontend


2. CACHING STRATEGY
pythonCache Key Structure:
{llm_provider}:{agent_name}:{content_hash}

Example:
"gemini:linguistic:a3f5d8c2..." → Cached Result
"claude:clinical:a3f5d8c2..." → Different cache entry

Cache TTL: 24 hours
Cache Invalidation: On document update
```

**Caching Logic:**
```
1. Hash the discharge summary content
2. For each agent:
   - Check cache: {llm}:{agent}:{hash}
   - If HIT → Return cached result immediately
   - If MISS → Call LLM → Cache result → Stream to frontend
3. Partial cache hits accelerate processing
Benefits:

✅ Same document reviewed again = instant results
✅ Different LLM on same content = only new agent calls made
✅ Reduces API costs by ~80% for repeated analyses
✅ Faster demo iterations


3. DUAL LLM SUPPORT
python# Factory Pattern Implementation

class LLMFactory:
    @staticmethod
    def get_client(provider: str, api_key: str):
        if provider == "gemini":
            return GeminiClient(api_key)
        elif provider == "claude":
            return ClaudeClient(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

# Usage in agents
llm = LLMFactory.get_client(
    provider=user_selected_llm,
    api_key=config.api_keys[user_selected_llm]
)
API Abstraction Layer:
pythonclass BaseLLMClient(ABC):
    @abstractmethod
    async def analyze(self, prompt: str, system: str) -> dict:
        pass
    
    @abstractmethod
    async def stream_analyze(self, prompt: str, system: str):
        # Generator for streaming responses
        pass

4. REAL-TIME STREAMING FLOW
Backend (FastAPI SSE):
python@app.post("/analyze/stream")
async def stream_analysis(request: AnalysisRequest):
    async def event_generator():
        # Stage 1: Send initial status
        yield {
            "event": "started",
            "data": {"total_agents": 5, "llm": request.llm_provider}
        }
        
        # Stage 2: Execute agents in parallel with streaming
        agents = [Linguistic, Structural, Clinical, Terminology, CriticalData]
        
        for idx, agent in enumerate(agents):
            # Check cache first
            cache_key = f"{request.llm}:{agent.name}:{hash(request.content)}"
            cached = await cache.get(cache_key)
            
            if cached:
                yield {
                    "event": "agent_complete",
                    "data": {
                        "agent": agent.name,
                        "issues": cached,
                        "from_cache": True,
                        "progress": (idx+1)/5 * 100
                    }
                }
            else:
                # Stream LLM response
                async for chunk in agent.analyze_stream(request.content, llm):
                    yield {
                        "event": "agent_progress",
                        "data": {
                            "agent": agent.name,
                            "partial_result": chunk
                        }
                    }
                
                # Cache the complete result
                await cache.set(cache_key, agent.result, ttl=86400)
                
                yield {
                    "event": "agent_complete",
                    "data": {
                        "agent": agent.name,
                        "issues": agent.result,
                        "from_cache": False,
                        "progress": (idx+1)/5 * 100
                    }
                }
        
        # Stage 3: Final summary
        yield {
            "event": "analysis_complete",
            "data": {"summary": aggregate_results()}
        }
    
    return EventSourceResponse(event_generator())
Frontend (React Hook):
javascriptfunction useStreamingAnalysis(content, llmProvider) {
    const [results, setResults] = useState({});
    const [progress, setProgress] = useState(0);
    const [loading, setLoading] = useState(false);
    
    const startAnalysis = async () => {
        setLoading(true);
        const eventSource = new EventSource(
            `/analyze/stream?llm=${llmProvider}`
        );
        
        eventSource.addEventListener('agent_complete', (e) => {
            const data = JSON.parse(e.data);
            setResults(prev => ({
                ...prev,
                [data.agent]: data.issues
            }));
            setProgress(data.progress);
        });
        
        eventSource.addEventListener('analysis_complete', (e) => {
            setLoading(false);
            eventSource.close();
        });
    };
    
    return { results, progress, loading, startAnalysis };
}

5. AGENT PROMPT ENGINEERING
Each agent has optimized prompts for both Gemini and Claude:
pythonclass LinguisticAgent(BaseAgent):
    PROMPTS = {
        "gemini": """
You are a medical documentation quality reviewer focusing on linguistic aspects.

Analyze the discharge summary for:
1. Spelling errors (medical and general)
2. Grammar issues
3. Sentence structure problems (>40 words = flag)
4. Duplicate content
5. Clarity issues

Return JSON only:
{
  "issues": [
    {
      "type": "spelling|grammar|structure|duplication|clarity",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name",
      "current": "problematic text",
      "suggestion": "corrected version",
      "explanation": "why this is an issue"
    }
  ]
}

DISCHARGE SUMMARY:
{content}
        """,
        
        "claude": """
<task>Review discharge summary for linguistic quality</task>

<focus_areas>
- Medical terminology spelling accuracy
- Grammar and sentence structure
- Text clarity and readability  
- Content duplication detection
</focus_areas>

<output_format>
Return only valid JSON with issues array. Each issue must have:
type, severity, location, current text, suggestion, explanation.
</output_format>

<discharge_summary>
{content}
</discharge_summary>
        """
    }
    
    def get_prompt(self, content: str, llm_provider: str) -> str:
        return self.PROMPTS[llm_provider].format(content=content)

🚀 MVP FEATURES PRIORITIZATION
PHASE 1 - Core MVP (Week 1)
✅ Text upload (paste or file)
✅ LLM provider selection (Gemini/Claude)
✅ 3 core agents (Linguistic, Structural, Clinical)
✅ Real-time streaming results
✅ Basic caching (in-memory)
✅ Simple UI with progress bar
PHASE 2 - Enhanced (Week 2)
✅ All 5 agents
✅ Redis caching
✅ PDF upload support
✅ Issue severity filtering
✅ Export to PDF
✅ Better UI/UX
PHASE 3 - Production Ready (Week 3)
✅ ERPNext integration
✅ User authentication
✅ Audit logging
✅ Analytics dashboard
✅ Auto-fix suggestions

📦 DEPENDENCIES
Backend (requirements.txt):
txtfastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
google-generativeai==0.3.2
anthropic==0.18.1
redis==5.0.1
python-multipart==0.0.6
pypdf2==3.0.1
python-dotenv==1.0.0
sse-starlette==1.8.2
httpx==0.26.0
Frontend (package.json):
json{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.5",
    "lucide-react": "^0.312.0",
    "tailwindcss": "^3.4.1"
  }
}

🎯 CLAUDE CODE IMPLEMENTATION PLAN
Step 1: Initialize Project
bash# Tell Claude Code:
"Create a new FastAPI + React project with the structure I'll provide. 
Use Python 3.11+ for backend and React 18 for frontend."
```

### **Step 2: Backend Setup** (Prompt for Claude Code)
```
Create the backend with these specifications:

1. FastAPI app with SSE support for streaming
2. Five agent classes (Linguistic, Structural, Clinical, Terminology, CriticalData)
3. Dual LLM support using factory pattern (Gemini and Claude APIs)
4. Redis caching with content hashing
5. Pydantic models for type safety
6. Environment variable configuration (.env)

Each agent should:
- Have separate prompts for Gemini and Claude
- Return structured JSON with issues
- Support streaming responses
- Cache results with 24hr TTL

Implement the streaming endpoint:
POST /api/analyze/stream
- Accept: {content: str, llm_provider: "gemini"|"claude"}
- Stream agent results as they complete
- Use Server-Sent Events (SSE)
- Check cache before LLM calls
```

### **Step 3: Frontend Development** (Prompt for Claude Code)
```
Create a React frontend with:

1. Components:
   - Upload section (text area + file upload)
   - LLM provider selector (Gemini/Claude radio buttons)
   - Real-time progress bar
   - Streaming results display (issues appear as agents complete)
   - Issue cards grouped by agent/severity
   - Executive summary at top

2. Features:
   - EventSource for SSE connection
   - Progressive rendering of results
   - Loading states per agent
   - Cache hit indicators (show if result was cached)
   - Export to PDF button

3. Styling:
   - Use Tailwind CSS
   - Color-coded severity (Red=High, Orange=Medium, Yellow=Low)
   - Responsive design
   - Clean medical UI aesthetic

4. State Management:
   - Track results per agent
   - Overall progress percentage
   - Loading/error states
```

### **Step 4: Integration & Testing**
```
1. Set up environment variables for API keys
2. Implement error handling for LLM API failures
3. Add request/response logging
4. Test with the provided discharge summary
5. Verify caching works (second analysis should be instant)
6. Test both Gemini and Claude providers

🔐 ENVIRONMENT CONFIGURATION
.env.example:
bash# LLM API Keys
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# App Configuration
DEBUG=true
CORS_ORIGINS=http://localhost:5173

📊 CACHING IMPLEMENTATION DETAILS
Cache Key Strategy:
pythonimport hashlib

def generate_cache_key(llm_provider: str, agent_name: str, content: str) -> str:
    """
    Generate deterministic cache key
    
    Examples:
    - gemini:linguistic:a3f5d8c2e1b4...
    - claude:clinical:a3f5d8c2e1b4...
    
    Same content + same agent + different LLM = different cache
    """
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"{llm_provider}:{agent_name}:{content_hash}"

# Usage
cache_key = generate_cache_key("gemini", "linguistic", discharge_summary)
Cache Hit Rate Tracking:
python# Track cache performance
cache_stats = {
    "total_requests": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "hit_rate": 0.0
}

# Display to user
"⚡ Cache Hit Rate: 76% (3/5 agents used cached results)"
```

---

## 🎨 UI/UX SPECIFICATIONS

### Layout:
```
┌─────────────────────────────────────────────┐
│  [Logo] Discharge Summary Validator         │
├─────────────────────────────────────────────┤
│                                              │
│  LLM Provider: ○ Gemini  ⦿ Claude          │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ Paste discharge summary here...      │  │
│  │                                       │  │
│  │ [Or drag & drop PDF]                 │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  [Analyze] [Clear]                          │
│                                              │
├─────────────────────────────────────────────┤
│  Analysis Progress: ████████░░ 80%          │
│  ⚡ 3/5 results from cache (saved 2 API calls)│
├─────────────────────────────────────────────┤
│  EXECUTIVE SUMMARY                           │
│  🔴 Critical: 2  🟠 Medium: 5  🟡 Low: 8   │
├─────────────────────────────────────────────┤
│  ✅ Linguistic Quality (from cache)         │
│     └─ 3 issues found                       │
│                                              │
│  ⏳ Structural Compliance (analyzing...)     │
│                                              │
│  ✅ Clinical Consistency (completed)        │
│     └─ 2 critical issues                    │
│                                              │
│  [ View Detailed Report ] [ Export PDF ]    │
└─────────────────────────────────────────────┘
Issue Card Animation:

Fade in as each agent completes
Green pulse for cache hits
Loading spinner for active agents
Expand/collapse for details


🚀 DEPLOYMENT COMMANDS
Development:
bash# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
Production:
bash# Docker Compose
docker-compose up -d

# Or manual
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
npm run build && serve -s dist
```

---

## 🎯 SUCCESS CRITERIA FOR MVP

### Functional:
✅ Upload discharge summary (text/PDF)
✅ Select LLM provider (Gemini/Claude)
✅ Stream results in real-time (issues appear progressively)
✅ Cache working (same content = instant second analysis)
✅ All 5 agents running
✅ Results categorized by severity
✅ Export functionality

### Performance:
✅ First analysis: <30 seconds
✅ Cached analysis: <2 seconds
✅ Cache hit rate: >70% for repeated docs
✅ UI responsive during streaming

### User Experience:
✅ Clear progress indication
✅ Easy to understand issue cards
✅ Visual feedback for cache hits
✅ Mobile-friendly design

---

## 📝 EXACT PROMPTS FOR CLAUDE CODE

### **Prompt 1: Project Initialization**
```
Create a new project called "discharge-validator-mvp" with:
- Backend: FastAPI (Python 3.11+) with async support
- Frontend: React 18 + Vite + Tailwind CSS
- Structure as outlined in the plan
- Include .env.example, requirements.txt, package.json
- Initialize git repository
```

### **Prompt 2: Backend Core**
```
Implement the FastAPI backend with:

1. main.py with SSE streaming endpoint
2. Five agent classes in agents/ directory
3. Dual LLM clients (Gemini + Claude) with factory pattern
4. Redis caching with content hashing
5. Pydantic schemas for validation

The streaming endpoint should:
- Accept discharge summary text and LLM provider choice
- Check cache for each agent before calling LLM
- Stream results as Server-Sent Events
- Return JSON with issues array
- Track cache hits vs misses

Each agent returns:
{
  "issues": [
    {
      "category": "agent name",
      "type": "specific issue type",
      "severity": "HIGH|MEDIUM|LOW",
      "location": "section name",
      "current": "problematic text",
      "suggestion": "fix",
      "explanation": "why"
    }
  ]
}
```

### **Prompt 3: Frontend Implementation**
```
Create React frontend with real-time streaming:

1. Upload component with text area and file upload
2. LLM provider selector (radio buttons for Gemini/Claude)
3. Progress bar showing completion percentage
4. Results stream component that:
   - Connects via EventSource to /api/analyze/stream
   - Shows loading state per agent
   - Displays issues as they arrive
   - Indicates cache hits with green badge
   - Groups issues by severity
5. Executive summary showing total counts
6. Export to PDF functionality

Use Tailwind for styling:
- Medical blue theme (#1e3a8a primary)
- Color-coded severity badges
- Smooth animations for incoming results
- Responsive grid layout
```

### **Prompt 4: Integration & Polish**
```
Complete the integration:

1. Connect frontend to backend API
2. Add error handling for API failures
3. Implement retry logic for LLM calls
4. Add loading skeletons
5. Test with the provided discharge summary
6. Verify caching works correctly
7. Add README with setup instructions
8. Include sample .env configuration
```

---

## 🔍 TESTING CHECKLIST

### Test with Your Sample Document:
- [ ] Upload successful
- [ ] Both Gemini and Claude work
- [ ] Date inconsistency detected (CAG dates)
- [ ] High FBS flagged (208 mg/dL)
- [ ] Spelling error caught (DIATED → DILATED)
- [ ] Age mismatch noted (80 vs 81)
- [ ] Abbreviations flagged
- [ ] Second analysis uses cache
- [ ] Results stream in real-time
- [ ] Export to PDF works

---

## 💡 SMART USAGE TIPS FOR CLAUDE CODE

### **Iterative Development:**
1. Start with basic structure (Prompt 1)
2. Build backend agents one at a time
3. Test each agent independently
4. Add frontend incrementally
5. Integrate and refine

### **Debugging with Claude Code:**
```
"The linguistic agent is not returning results. 
Please check the prompt formatting and JSON parsing. 
Show me the full error trace and suggest fixes."
```

### **Performance Optimization:**
```
"The streaming is slow. Can you:
1. Implement parallel agent execution
2. Add connection pooling for Redis
3. Optimize the LLM prompts for faster responses"
```

### **Feature Additions:**
```
"Add a feature to highlight issues directly in the 
original text with color-coded annotations"

🎯 FINAL DELIVERABLE
After completion, you should have:

Working MVP that:

Accepts discharge summary input
Validates using 5 specialized agents
Streams results in real-time
Caches aggressively (80%+ hit rate)
Supports both Gemini and Claude
Exports professional reports


Clean Codebase with:

Type hints throughout
Comprehensive docstrings
Error handling
Logging
Configuration management


Documentation including:

Setup instructions
API documentation
Architecture diagrams
Testing guide



