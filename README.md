# Financial Document Analyzer — Debug vs Fixed: Change Log

Complete record of every change between `financial-document-analyzer-debug` and `financial-document-analyzer-fixed`.

---

## 1. File Structure

One file added to `data/`: `sample.pdf`. All fixes applied to the existing 5 source files.

---

## 2. requirements.txt

| # | Bug | Fix |
|---|---|---|
| 1 | `crewai-tools==0.47.1` doesn't exist; pulls `chromadb` (no Windows wheel) | Removed; replaced with `duckduckgo-search==6.2.6` |
| 2 | `langchain-core==0.1.52` incompatible with crewai 0.130.0 (needs `>=0.3`) | → `0.3.62` |
| 3 | `openai==1.30.5` below litellm's floor of `>=1.68.2` | → `1.68.2` |
| 4 | `pydantic==1.10.13` + `pydantic_core==2.8.0` — v1/v2 hybrid, breaks crewai | → `pydantic==2.8.2` + `pydantic-settings==2.4.0`; removed `pydantic_core` |
| 5 | `langsmith==0.1.67` incompatible with `langchain-core 0.3.x` | → `0.1.147` |
| 6 | Missing `uvicorn`, `python-multipart`, `python-dotenv` | Added all three |
| 7 | 20+ unused packages causing conflicts (Google Cloud, OpenTelemetry, etc.) | Removed entirely |

**Final requirements.txt:**
```
crewai==0.130.0
langchain==0.3.25
langchain-core==0.3.62
langchain-community==0.3.21
langchain-openai==0.2.14
langsmith==0.1.147
openai==1.68.2
pydantic==2.8.2
pydantic-settings==2.4.0
fastapi==0.112.2
uvicorn==0.30.6
python-multipart==0.0.9
pypdf==4.3.1
duckduckgo-search==6.2.6
python-dotenv==1.0.1
numpy==1.26.4
pandas==2.2.2
pillow==10.4.0
```

---

## 3. tools.py

| # | Bug | Fix |
|---|---|---|
| 8 | `from crewai_tools import SerperDevTool` — uninstallable, requires API key | Replaced with `@tool`-decorated DuckDuckGo function |
| 9 | `Pdf(file_path=path).load()` — class doesn't exist → `NameError` | Replaced with `PyPDFLoader` from `langchain_community` |
| 10 | `async def read_data_tool` — crewai calls tools synchronously; returns a coroutine object instead of text | Changed to `def` (synchronous) |
| 11 | Tool defined as method inside a class — crewai `@tool` only works at module level | Moved to module level |

---

## 4. agents.py

| # | Bug | Fix |
|---|---|---|
| 12 | `llm = llm` — `NameError` before module even loads | Replaced with `crewai.LLM(model="openai/gpt-4o-mini", ...)` |
| 13 | `from crewai.agents import Agent` — invalid import path | → `from crewai import Agent` |
| 14 | `tool=[...]` (singular) silently ignored by `Agent` constructor | → `tools=[...]` (plural) |
| 15 | `max_iter=1` on all agents — forces return after first tool call, before formatting | → 5 / 3 / 5 / 5 per agent |
| 16 | `max_rpm=1` — one LLM call/minute causes 3–5 min timeouts | → `max_rpm=10` |
| 17 | `allow_delegation=True` on `financial_analyst` — causes delegation loops | → `False` |

---

## 5. task.py

| # | Bug | Fix |
|---|---|---|
| 18 | `investment_advisor` and `risk_assessor` never imported | Added to imports |
| 19 | All 4 tasks assigned to `financial_analyst` | Each task assigned to its correct agent |
| 20 | Tasks used `FinancialDocumentTool.read_data_tool` (class method, uncallable) | → module-level `read_data_tool` |

---

## 6. main.py

| # | Bug | Fix |
|---|---|---|
| 21 | Only `financial_analyst` and one task imported | All 4 agents and 4 tasks imported |
| 22 | `Crew` built with 1 agent / 1 task | Crew includes all 4 agents and 4 tasks |
| 23 | Endpoint `async def analyze_financial_document` shadows the imported `Task` object → `TypeError` | Renamed to `analyze_document` |
| 24 | `uvicorn.run(app, reload=True)` crashes on Windows (ProactorEventLoop conflict) | → `uvicorn.run("main:app", ..., reload=False)` |
| 25 | Uploaded `file_path` never passed to `crew.kickoff()` — always reads `sample.pdf` | Added `file_path` to kickoff inputs |
| 26 | No file type validation | Added `.pdf` check; returns HTTP 400 otherwise |

---

## 7. Prompt Rewrites

All agent goals, backstories, task descriptions, and expected outputs were rewritten. The originals were deliberately sabotaged to produce hallucinated, fabricated, and non-compliant output (e.g. *"Make up investment advice"*, *"Include 5 made-up URLs"*, *"Just say yes to everything"*).

**Each agent's fixed role:**

- **financial_analyst** — CFA-certified; extracts factual figures from the document only; flags missing data explicitly.
- **verifier** — Compliance specialist; classifies document type with structured JSON output (`is_financial_document`, `document_type`, `confidence`, `reasoning`).
- **investment_advisor** — Series-65 licensed; derives considerations solely from audited financials; always includes regulatory disclaimer.
- **risk_assessor** — FRM-certified; classifies risks by category and severity with document evidence; never fabricates scenarios.

**Each task's fixed output format:** structured JSON only — no markdown fences, no prose, no invented data.

---

## 8. Setup

```bash
# Clone / extract zip, then:
python -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# API docs: http://localhost:8000/docs
```

---

## 9. API

**`GET /`** — health check.

**`POST /analyze`** — upload a PDF and receive structured multi-agent analysis.

| Field | Type | Required |
|---|---|---|
| `file` | PDF (multipart) | Yes |
| `query` | string (form) | No (has default) |

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What was Tesla revenue and free cash flow in Q2 2025?"
```

Response: `{ "status", "query", "analysis", "file_processed" }`

The `analysis` field contains sequential JSON output from all four agents: verification → extraction → investment considerations → risk assessment.

---

## Bug Summary

| # | File | Error Without Fix |
|---|---|---|
| 1 | requirements.txt | `ResolutionImpossible` on Windows |
| 2 | requirements.txt | `ImportError` on startup |
| 3 | requirements.txt | `ResolutionImpossible` |
| 4 | requirements.txt | `ImportError` on startup |
| 5 | requirements.txt | `ImportError` |
| 6 | requirements.txt | Server won't start / uploads fail |
| 7 | requirements.txt | Slow install + conflicts |
| 8 | tools.py | `ModuleNotFoundError` |
| 9 | tools.py | `NameError` on every tool call |
| 10 | tools.py | Agent receives coroutine, not text |
| 11 | tools.py | Tool silently uncallable |
| 12 | agents.py | Crash on import |
| 13 | agents.py | `ModuleNotFoundError` |
| 14 | agents.py | Agent has no tools (silent) |
| 15 | agents.py | Incomplete output on every run |
| 16 | agents.py | 3–5 min response times / timeouts |
| 17 | agents.py | Non-deterministic delegation loops |
| 18 | task.py | Two agents never used |
| 19 | task.py | Specialist agents never invoked |
| 20 | task.py | Tools uncallable from tasks |
| 21 | main.py | 3 agents and 3 tasks absent from crew |
| 22 | main.py | Multi-agent pipeline never runs |
| 23 | main.py | `TypeError` on first request |
| 24 | main.py | `RuntimeError` on Windows |
| 25 | main.py | Always reads `sample.pdf`, ignores upload |
| 26 | main.py | Unhelpful crash on non-PDF uploads |
| 27–30 | agents.py | Hallucinated / fabricated output |
| 31–34 | task.py | Random, contradictory, fake-URL output |
