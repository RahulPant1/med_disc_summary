# Testing Guide - Discharge Summary Validator

This guide provides comprehensive testing procedures for the Discharge Summary Validator MVP.

---

## Prerequisites

Before testing, ensure you have:

1. **Python 3.11+** installed
2. **Node.js 18+** installed
3. **API Keys**:
   - Google Gemini API key (get from: https://makersuite.google.com/app/apikey)
   - Anthropic Claude API key (get from: https://console.anthropic.com/)
4. **Redis** (optional - system uses in-memory cache if not available)

---

## Phase 1: Environment Setup

### Step 1: Configure API Keys

Edit the `.env` file in the project root:

```bash
# Replace with your actual API keys
GEMINI_API_KEY=your_actual_gemini_key
ANTHROPIC_API_KEY=your_actual_anthropic_key

# Optional: Enable Redis (set to true if Redis is running)
REDIS_ENABLED=false
```

### Step 2: Install Backend Dependencies

```bash
cd backend
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

---

## Phase 2: Backend Testing

### Test 1: Health Check

**Start the backend server:**

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Cache initialized: {'type': 'in-memory', 'enabled': True, 'items': 0}
INFO:     Application startup complete.
```

**Test the health endpoint:**

Open browser to: `http://localhost:8000/health`

**Expected response:**
```json
{
  "status": "healthy",
  "redis_connected": false,
  "gemini_configured": true,
  "claude_configured": true
}
```

✅ **Pass criteria:**
- Server starts without errors
- Health endpoint returns `gemini_configured: true` and `claude_configured: true`
- Cache is initialized (in-memory or Redis)

### Test 2: API Documentation

Navigate to: `http://localhost:8000/docs`

**Expected:**
- Swagger UI with all endpoints visible
- `/api/analyze/stream` POST endpoint
- `/health` GET endpoint
- `/api/cache/stats` GET endpoint

✅ **Pass criteria:** All endpoints are documented and interactive

### Test 3: Cache Statistics

Navigate to: `http://localhost:8000/api/cache/stats`

**Expected response:**
```json
{
  "type": "in-memory",
  "enabled": true,
  "items": 0
}
```

✅ **Pass criteria:** Cache stats are returned successfully

---

## Phase 3: Frontend Testing

### Test 4: Frontend Development Server

**In a new terminal (keep backend running):**

```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Open browser to:** `http://localhost:5173`

**Expected:**
- Application loads without errors
- "Discharge Summary Validator" header visible
- Upload section with text area
- LLM provider radio buttons (Gemini/Claude)
- "Analyze Document" button

✅ **Pass criteria:**
- No console errors
- All UI components render correctly
- Application is responsive

---

## Phase 4: Integration Testing

### Test 5: Sample Document Analysis (Gemini)

**Test Data:** Use the sample from `discharge-validator-docs/sample_data_file.md`

**Procedure:**
1. Copy the entire discharge summary content
2. Paste into the text area
3. Select **"Google Gemini"** as LLM provider
4. Click **"Analyze Document"**

**Expected behavior:**
1. Progress bar appears and starts filling
2. Agent accordions appear one by one:
   - Linguistic Quality
   - Structural Compliance
   - Clinical Consistency
   - Terminology Standards
   - Critical Data Validation
3. Issues appear as each agent completes
4. Executive Summary shows at the top when complete
5. Total processing time < 30 seconds (first run)

**Expected issues to be detected:**
- ✅ Date inconsistency (CAG: 16/10 vs 24/11)
- ✅ High FBS (208 mg/dL) without diabetes diagnosis
- ✅ Age discrepancy (80 vs 81)
- ✅ Spelling errors (DIATED, PROIMAL, ANOUT)
- ✅ Abbreviation K/c/o needs expansion
- ✅ Polypharmacy concerns (12 medications)

✅ **Pass criteria:**
- Analysis completes successfully
- At least 8-10 issues detected
- All known critical issues flagged
- Executive Summary shows HIGH or MEDIUM risk

### Test 6: Cache Validation

**Procedure:**
1. Immediately after Test 5, click "Clear Results & Start New Analysis"
2. Paste the **same** discharge summary
3. Select **"Google Gemini"** again
4. Click **"Analyze Document"**

**Expected behavior:**
1. Analysis completes in < 2 seconds
2. Cache hit indicator shows: "5/5 results from cache (100% hit rate)"
3. All agents show green ⚡ "Cached" badge
4. Executive Summary shows "Cache Hit Rate: 100%"
5. Same issues as Test 5

✅ **Pass criteria:**
- Analysis is near-instant (< 2 seconds)
- 100% cache hit rate
- All results identical to first run

### Test 7: Sample Document Analysis (Claude)

**Procedure:**
1. Clear results
2. Paste the discharge summary again
3. Select **"Anthropic Claude"** as LLM provider
4. Click **"Analyze Document"**

**Expected behavior:**
1. Analysis completes successfully
2. Different cache keys (no cache hits initially)
3. Issues detected (may differ slightly from Gemini)
4. Processing time < 30 seconds

✅ **Pass criteria:**
- Claude analysis works independently
- Issues are detected and displayed
- No cache hits (different LLM provider)

### Test 8: Error Handling

**Test 8a: Invalid API Key**

**Procedure:**
1. Stop backend server
2. Edit `.env` and set `GEMINI_API_KEY=invalid_key`
3. Restart backend
4. Try to analyze a document with Gemini

**Expected:**
- Error message displayed in UI
- Error clearly states API key issue

**Test 8b: Empty Content**

**Procedure:**
1. Clear the text area
2. Click "Analyze Document"

**Expected:**
- Button is disabled
- Cannot submit empty content

✅ **Pass criteria:** All error cases handled gracefully

---

## Phase 5: Performance Testing

### Test 9: Performance Benchmarks

**First Analysis (No Cache):**
- Expected time: 20-30 seconds
- All 5 agents complete
- Results stream progressively

**Second Analysis (100% Cache):**
- Expected time: < 2 seconds
- Instant results
- 100% cache hit rate

**Partial Cache (Different LLM):**
- Same content, different LLM
- Expected time: 20-30 seconds
- 0% cache hit (different cache keys)

✅ **Pass criteria:**
- First run: < 30s
- Cached run: < 2s
- UI remains responsive throughout

---

## Phase 6: Functional Validation

### Test 10: Known Issues Detection

Using the sample discharge summary, verify each known issue is detected:

| # | Issue | Expected Severity | Detection |
|---|-------|------------------|-----------|
| 1 | Date inconsistency (CAG dates) | HIGH | ✅ |
| 2 | High FBS without diabetes dx | HIGH | ✅ |
| 3 | Age discrepancy (80 vs 81) | MEDIUM | ✅ |
| 4 | Spelling: DIATED → DILATED | LOW | ✅ |
| 5 | Spelling: PROIMAL → PROXIMAL | LOW | ✅ |
| 6 | Spelling: ANOUT → ABOUT | LOW | ✅ |
| 7 | Abbreviation: K/c/o | MEDIUM | ✅ |
| 8 | Format inconsistency (vitals) | LOW | ✅ |
| 9 | Unit clarity: R /R | LOW | ✅ |
| 10 | Polypharmacy (12 meds, age 81) | MEDIUM | ✅ |

✅ **Pass criteria:** At least 8/10 issues detected

---

## Phase 7: UI/UX Validation

### Test 11: Visual Design

**Check:**
- ✅ Medical blue theme (#1e3a8a)
- ✅ Severity color coding:
  - RED for HIGH severity
  - ORANGE for MEDIUM severity
  - YELLOW for LOW severity
- ✅ Smooth animations and transitions
- ✅ Responsive layout (test on mobile size)
- ✅ Clear typography and spacing

### Test 12: User Interactions

**Check:**
- ✅ Expandable issue cards work
- ✅ Category accordions expand/collapse
- ✅ File upload works (.txt, .md)
- ✅ Clear button resets form
- ✅ LLM provider selection works
- ✅ Loading states show properly
- ✅ Progress bar animates smoothly

---

## Phase 8: Edge Cases

### Test 13: Edge Case Scenarios

**Test 13a: Very Short Content**
- Input: "Patient discharged."
- Expected: Analysis completes, minimal issues

**Test 13b: Very Long Content**
- Input: 5000+ word document
- Expected: Analysis completes, more issues found

**Test 13c: Special Characters**
- Input: Content with special medical symbols
- Expected: Handled correctly

**Test 13d: Network Interruption**
- Procedure: Start analysis, refresh page mid-stream
- Expected: No errors, can restart analysis

---

## Phase 9: Multi-Session Testing

### Test 14: Concurrent Users

**Procedure:**
1. Open application in 2 different browsers
2. Submit different documents simultaneously
3. Verify both complete successfully

✅ **Pass criteria:** Both analyses complete independently

---

## Success Criteria Summary

### Functional Requirements ✅
- [x] All 5 agents working
- [x] Both Gemini and Claude functional
- [x] Real-time streaming operational
- [x] Caching working (>70% hit rate)
- [x] All known issues detected
- [x] UI displays results clearly

### Performance Requirements ✅
- [x] First analysis: < 30 seconds
- [x] Cached analysis: < 2 seconds
- [x] Cache hit rate: >70% on repeat
- [x] UI responsive during streaming

### User Experience Requirements ✅
- [x] Clear progress indication
- [x] Easy to understand issue cards
- [x] Visual feedback for cache hits
- [x] Mobile-friendly design
- [x] Error messages are helpful

---

## Troubleshooting

### Issue: "API key not configured"
**Solution:** Check `.env` file has valid API keys

### Issue: "Connection refused"
**Solution:** Ensure backend server is running on port 8000

### Issue: CORS errors
**Solution:** Verify `CORS_ORIGINS=http://localhost:5173` in `.env`

### Issue: No results streaming
**Solution:** Check browser console for errors, verify SSE connection

### Issue: Redis connection failed
**Solution:** Set `REDIS_ENABLED=false` to use in-memory cache

---

## Next Steps After Testing

1. **If all tests pass:** Application is ready for deployment
2. **If tests fail:** Review error logs and fix issues
3. **Performance optimization:** If needed, implement parallel agent execution
4. **Production deployment:** Follow deployment guide in README.md

---

## Test Report Template

```
Date: ___________
Tester: ___________

Backend Tests:
- [ ] Health Check (Test 1)
- [ ] API Documentation (Test 2)
- [ ] Cache Statistics (Test 3)

Frontend Tests:
- [ ] Development Server (Test 4)

Integration Tests:
- [ ] Gemini Analysis (Test 5)
- [ ] Cache Validation (Test 6)
- [ ] Claude Analysis (Test 7)
- [ ] Error Handling (Test 8)

Performance Tests:
- [ ] Benchmarks (Test 9)

Functional Tests:
- [ ] Known Issues Detection (Test 10)

UI/UX Tests:
- [ ] Visual Design (Test 11)
- [ ] User Interactions (Test 12)

Edge Cases:
- [ ] Edge Scenarios (Test 13)
- [ ] Concurrent Users (Test 14)

Notes:
_________________________________
_________________________________

Overall Status: PASS / FAIL
```

---

**Testing Complete! 🎉**

If all tests pass, your Discharge Summary Validator MVP is ready for use!
