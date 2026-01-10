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

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (optional - will use in-memory cache if not available)

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

Use the sample discharge summary provided in `discharge-validator-docs/sample_data_file.md` which contains known validation issues for testing.

## Development Status

### Phase 1: Project Setup ✅
- [x] Project structure created
- [x] Dependencies configured
- [x] Git repository initialized

### Phase 2: Backend Foundation (In Progress)
- [ ] Core models and schemas
- [ ] LLM client implementations
- [ ] Caching layer
- [ ] Agent implementations
- [ ] FastAPI server with SSE

### Phase 3: Frontend Development (Pending)
- [ ] React components
- [ ] Streaming hooks
- [ ] UI/UX implementation

### Phase 4: Integration & Testing (Pending)
- [ ] End-to-end integration
- [ ] Validation with sample data
- [ ] Performance optimization

## Architecture Highlights

- **Streaming Architecture**: Server-Sent Events for real-time result delivery
- **Caching Strategy**: Content-based hashing with 24-hour TTL
- **Parallel Execution**: Async/await for concurrent agent processing
- **Graceful Degradation**: Optional Redis with in-memory fallback

## License

MIT

## Contributing

This is an MVP project. Contributions welcome!
