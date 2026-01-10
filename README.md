# Discharge Summary Validator MVP

A real-time discharge summary validation application with dual LLM support (Gemini & Claude), streaming results, and intelligent caching.

## Features

- **5 Specialized Validation Agents**:
  - Linguistic Quality (spelling, grammar, clarity)
  - Structural Compliance (NABH standards, sections)
  - Clinical Consistency (medical accuracy, safety)
  - Terminology Standards (abbreviations, standardization)
  - Critical Data Validation (dates, identifiers, legal requirements)

- **Dual LLM Support**: Choose between Google Gemini or Anthropic Claude
- **Real-time Streaming**: See validation results as they're generated
- **Intelligent Caching**: Redis-based caching with fallback to in-memory cache
- **Progressive UI**: Results appear as each agent completes analysis

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- Server-Sent Events (SSE) for streaming
- Redis for caching (optional)
- Google Gemini API
- Anthropic Claude API

### Frontend
- React 18
- Vite
- Tailwind CSS
- EventSource API for SSE

## Project Structure

```
discharge-validator-mvp/
├── backend/
│   ├── agents/          # 5 validation agents
│   ├── llm/             # LLM client implementations
│   ├── cache/           # Caching layer
│   ├── models/          # Pydantic schemas
│   ├── utils/           # Helper functions
│   └── main.py          # FastAPI server
├── frontend/
│   └── src/
│       ├── components/  # React components
│       ├── hooks/       # Custom React hooks
│       └── utils/       # Frontend utilities
└── discharge-validator-docs/  # Technical documentation
```

## Quick Start

### Get API Keys

1. **Google Gemini API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Free tier available

2. **Anthropic Claude API Key**:
   - Visit: https://console.anthropic.com/
   - Sign up and get API access
   - Request beta access if needed

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (optional - will use in-memory cache if not available)
- API keys for Gemini and/or Claude

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r ../requirements.txt
```

3. Configure environment variables:
```bash
cp ../.env.example ../.env
# Edit .env and add your API keys
```

4. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Access the application:
```
http://localhost:5173
```

## Environment Variables

Create a `.env` file in the project root with the following:

```bash
# LLM API Keys (Required)
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=false  # Set to true to enable Redis caching

# App Configuration
DEBUG=true
CORS_ORIGINS=http://localhost:5173
API_PORT=8000
```

## Usage

1. Open the application in your browser
2. Select your preferred LLM provider (Gemini or Claude)
3. Paste or upload a discharge summary
4. Click "Analyze" to start validation
5. Watch as results stream in real-time
6. Review issues categorized by severity and agent
7. Export results as needed

## Testing

For comprehensive testing procedures, see [TESTING_GUIDE.md](./TESTING_GUIDE.md).

### Quick Test

1. Start both backend and frontend servers
2. Open http://localhost:5173
3. Use the sample from `discharge-validator-docs/sample_data_file.md`
4. Paste into text area, select LLM provider, click "Analyze"
5. Verify 8-10 issues are detected

### Expected Results

The sample discharge summary contains 10 known issues:
- 3 HIGH severity (date inconsistencies, missing diabetes diagnosis)
- 4 MEDIUM severity (abbreviations, polypharmacy, age mismatch)
- 3 LOW severity (spelling errors, formatting)

### Performance Benchmarks

- **First analysis**: 20-30 seconds
- **Cached analysis** (same content): < 2 seconds
- **Cache hit rate**: 100% on repeat analysis

## Development Status

### Phase 1: Project Setup ✅
- [x] Project structure created
- [x] Dependencies configured
- [x] Git repository initialized

### Phase 2: Backend Foundation ✅
- [x] Core models and schemas
- [x] LLM client implementations (Gemini + Claude)
- [x] Caching layer with Redis/in-memory fallback
- [x] All 5 agent implementations
- [x] FastAPI server with SSE streaming

### Phase 3: Frontend Development ✅
- [x] React components (7 components)
- [x] Streaming hooks (useStreamingAnalysis)
- [x] UI/UX implementation with Tailwind CSS
- [x] Real-time progressive rendering

### Phase 4: Integration & Testing ✅
- [x] End-to-end integration
- [x] Validation with sample data
- [x] Comprehensive testing guide
- [x] Ready for deployment

## Architecture Highlights

- **Streaming Architecture**: Server-Sent Events for real-time result delivery
- **Caching Strategy**: Content-based hashing with 24-hour TTL
- **Parallel Execution**: Async/await for concurrent agent processing
- **Graceful Degradation**: Optional Redis with in-memory fallback

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (must be 3.11+)
- Verify virtual environment is activated
- Check `.env` file exists and has API keys

### Frontend won't start
- Check Node version: `node --version` (must be 18+)
- Delete `node_modules` and run `npm install` again
- Clear browser cache

### Analysis fails
- Verify API keys are correct in `.env`
- Check backend logs for errors
- Ensure backend is running on port 8000

### CORS errors
- Verify `CORS_ORIGINS=http://localhost:5173` in `.env`
- Restart backend server after changing `.env`

### Cache not working
- Check `REDIS_ENABLED=false` if Redis not installed
- In-memory cache will be used automatically

## API Documentation

When backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Cache Stats: http://localhost:8000/api/cache/stats

## Project Files

- `backend/main.py` - FastAPI server with SSE streaming
- `backend/agents/` - 5 specialized validation agents
- `frontend/src/App.jsx` - Main React application
- `frontend/src/hooks/useStreamingAnalysis.js` - SSE streaming hook
- `.env` - Environment configuration (API keys)
- `TESTING_GUIDE.md` - Comprehensive testing procedures

## License

MIT

## Contributing

This is an MVP project. Contributions welcome!

## Support

For issues or questions:
1. Check [TESTING_GUIDE.md](./TESTING_GUIDE.md)
2. Review backend logs
3. Check browser console for errors
4. Ensure all prerequisites are installed
