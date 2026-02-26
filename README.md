# Financial Document Analyzer — Debug vs Fixed: Complete Change Log

This document records **every single change** made between the original
company-provided `financial-document-analyzer-debug` zip and the fixed
`financial-document-analyzer-fixed` zip delivered as the solution.

Each section shows the exact original (buggy) code, the exact fixed code, and
a plain-English explanation of what was wrong and why the fix works.

---

## Table of Contents

1. [File Structure Changes](#1-file-structure-changes)
2. [requirements.txt — Dependency Fixes](#2-requirementstxt--dependency-fixes)
3. [tools.py — Tool Registration Fixes](#3-toolspy--tool-registration-fixes)
4. [agents.py — Agent Definition Fixes](#4-agentspy--agent-definition-fixes)
5. [task.py — Task Assignment Fixes](#5-taskpy--task-assignment-fixes)
6. [main.py — API & Runtime Fixes](#6-mainpy--api--runtime-fixes)
7. [Prompt Rewrites — Hallucination Removal](#7-prompt-rewrites--hallucination-removal)
8. [Setup & Usage Instructions](#8-setup--usage-instructions)
9. [API Reference](#9-api-reference)

---

## 1. File Structure Changes

### Original (debug zip)
```
financial-document-analyzer-debug/
├── agents.py
├── task.py
├── tools.py
├── main.py
├── requirements.txt
├── README.md
└── data/
    └── TSLA-Q2-2025-Update.pdf
```

### Fixed zip
```
financial-document-analyzer-fixed/
├── agents.py         (fixed)
├── task.py           (fixed — all 4 tasks, correct agents)
├── tools.py          (fixed — module-level @tool functions)
├── main.py           (fixed — imports, endpoint name, reload flag)
├── requirements.txt  (fixed — all conflicts resolved, fully pinned)
├── README.md
└── data/
    ├── TSLA-Q2-2025-Update.pdf
    └── sample.pdf
```

No new files were added. The fixes were applied to the existing 5 source files.

---

## 2. requirements.txt — Dependency Fixes

### Bug 1 — `crewai-tools==0.47.1` does not exist / pulls `chromadb`

**Original:**
```
crewai-tools==0.47.1
```

**Fixed:** Removed entirely. `SerperDevTool` (the only tool used from this package)
was replaced with `duckduckgo-search==6.2.6`.

**Why:** `crewai-tools==0.47.1` does not exist on PyPI — pip raises
`ResolutionImpossible`. Every available version of `crewai-tools` transitively
pulls `chromadb`, which requires compiled C++ extensions. There is no pre-built
wheel for Python 3.11 on Windows, meaning `pip install` fails on the target
platform unless Visual Studio build tools are installed separately.
`duckduckgo-search` is a pure-Python replacement that needs no API key.

---

### Bug 2 — `langchain-core==0.1.52` incompatible with crewai 0.130.0

**Original:**
```
langchain-core==0.1.52
```

**Fixed:**
```
langchain-core==0.3.62
```

**Why:** crewai 0.130.0 requires `langchain-core>=0.3`. The `0.1.x` series
has a completely different internal API (`BaseMessage`, `Runnable`, etc.).
Importing crewai with `0.1.52` installed raises `ImportError` immediately.

---

### Bug 3 — `openai==1.30.5` below litellm's minimum requirement

**Original:**
```
openai==1.30.5
```

**Fixed:**
```
openai==1.68.2
```

**Why:** crewai 0.130.0 depends on `litellm>=1.72.0`. litellm 1.72 has a
hard dependency floor of `openai>=1.68.2`. Pinning to `1.30.5` makes the
dependency graph unsatisfiable — pip raises `ResolutionImpossible` and
refuses to install.

---

### Bug 4 — `pydantic==1.10.13` + `pydantic_core==2.8.0` — incompatible hybrid

**Original:**
```
pydantic==1.10.13
pydantic_core==2.8.0
```

**Fixed:**
```
pydantic==2.8.2
pydantic-settings==2.4.0
```
(`pydantic_core` removed — it is installed automatically as a dependency of
pydantic v2 and must never be pinned separately.)

**Why:** `pydantic_core` 2.x is the Rust C-extension backend for **Pydantic v2**.
`pydantic==1.10.13` is the pure-Python **Pydantic v1** layer. They are
incompatible with each other. crewai 0.130.0 requires Pydantic v2 throughout.
This combination raises `ImportError: cannot import name 'BaseModel' from
'pydantic.v1'` on startup.

---

### Bug 5 — `langsmith==0.1.67` too old, incompatible with langchain-core 0.3.x

**Original:**
```
langsmith==0.1.67
```

**Fixed:**
```
langsmith==0.1.147
```

**Why:** `langsmith 0.1.67` is incompatible with `langchain-core 0.3.x` due
to breaking API changes in the callback system. `0.1.147` is the last stable
0.1.x release and is fully compatible.

---

### Bug 6 — Missing `uvicorn`, `python-multipart`, `python-dotenv`

**Original:** None of these three packages appeared in `requirements.txt`.

**Fixed:**
```
uvicorn==0.30.6
python-multipart==0.0.9
python-dotenv==1.0.1
```

**Why:**
- `uvicorn` is the ASGI server used in `main.py`. Without it, `uvicorn main:app`
  fails with `command not found`.
- `python-multipart` is required by FastAPI to parse `multipart/form-data`
  (file uploads via `UploadFile`). Without it, every `POST /analyze` request
  returns `HTTP 422 Unprocessable Entity`.
- `python-dotenv` is imported in every source file (`load_dotenv()`). Without
  it, `from dotenv import load_dotenv` raises `ModuleNotFoundError`.

---

### Bug 7 — Unnecessary packages bloating the environment

The following packages were in `requirements.txt` but are not imported anywhere
in the codebase. They added significant install time and introduced conflicting
transitive dependencies (especially the Google Cloud and OpenTelemetry stacks
which conflict with crewai's pinned grpc versions on Python 3.11):

| Removed package | Reason |
|---|---|
| `google-cloud-aiplatform==1.53.0` | Not imported anywhere |
| `google-cloud-bigquery==3.23.1` | Not imported anywhere |
| `google-cloud-storage==2.16.0` | Not imported anywhere |
| `google-cloud-core==2.4.1` | Not imported anywhere |
| `google-cloud-resource-manager==1.12.3` | Not imported anywhere |
| `google-ai-generativelanguage==0.6.4` | Not imported anywhere |
| `google-generativeai==0.5.4` | Not imported anywhere |
| `google-resumable-media==2.7.0` | Not imported anywhere |
| `google-crc32c==1.5.0` | Not imported anywhere |
| `googleapis-common-protos==1.63.0` | Not imported anywhere |
| `google-auth==2.29.0` | Not imported anywhere |
| `google-auth-httplib2==0.2.0` | Not imported anywhere |
| `google-api-core==2.10.0` | Not imported anywhere |
| `google-api-python-client==2.131.0` | Not imported anywhere |
| `onnxruntime==1.22.0` | Not imported anywhere |
| `opentelemetry-*` (full block, 9 packages) | Transitive dep; conflict-prone |
| `protobuf==4.25.3` | Pinned too low; conflicts with grpc used by crewai |
| `pip==24.0` | Never pin pip inside requirements.txt |
| `click==8.1.7` | Transitive dep, not directly imported |
| `Jinja2==3.1.4` | Transitive dep, not directly imported |
| `jsonschema==4.22.0` | Transitive dep, not directly imported |
| `oauthlib==3.2.2` | Transitive dep, not directly imported |

---

### Final requirements.txt (fixed)

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

## 3. tools.py — Tool Registration Fixes

### Bug 8 — `from crewai_tools import tools` — package does not install

**Original:**
```python
from crewai_tools import tools
from crewai_tools.tools.serper_dev_tool import SerperDevTool

search_tool = SerperDevTool()
```

**Fixed:**
```python
from crewai.tools import tool
from duckduckgo_search import DDGS

@tool("Search the web")
def search_tool(query: str) -> str:
    """Search the web for current financial information using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=5)
        return "\n".join(r["body"] for r in results) if results else "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"
```

**Why:** `crewai_tools` cannot be installed on Windows Python 3.11 (chromadb
dependency, see Bug 1). `SerperDevTool` also requires a `SERPER_API_KEY`
environment variable. Replaced with `duckduckgo-search` which is free,
pure-Python, and needs no API key.

---

### Bug 9 — `Pdf(file_path=path).load()` — class does not exist

**Original:**
```python
async def read_data_tool(path='data/sample.pdf'):
    docs = Pdf(file_path=path).load()
```

**Fixed:**
```python
from langchain_community.document_loaders import PyPDFLoader

@tool("Read financial document")
def read_data_tool(path: str = "data/sample.pdf") -> str:
    loader = PyPDFLoader(file_path=path)
    pages = loader.load()
```

**Why:** There is no class called `Pdf` in any installed library.
`NameError: name 'Pdf' is not defined` is raised every single time the tool
is invoked. `PyPDFLoader` from `langchain_community` is the correct class —
same `load() → List[Document]` interface, properly installed via `pypdf`.

---

### Bug 10 — `async def read_data_tool` with no `await` inside

**Original:**
```python
class FinancialDocumentTool():
    async def read_data_tool(path='data/sample.pdf'):
        docs = Pdf(file_path=path).load()
        ...
        return full_report
```

**Fixed:**
```python
@tool("Read financial document")
def read_data_tool(path: str = "data/sample.pdf") -> str:
    loader = PyPDFLoader(file_path=path)
    pages = loader.load()
    ...
    return full_report
```

**Why:** CrewAI's tool executor calls tools **synchronously**. When it calls
an `async def` function without `await`, Python returns a coroutine object
(e.g. `<coroutine object read_data_tool at 0x...>`) instead of the actual
document text. The agent receives this coroutine object as the tool result,
has no real content to work with, and either crashes or hallucinates entirely.

---

### Bug 11 — `@staticmethod` inside a class not registered by CrewAI

**Original:**
```python
class FinancialDocumentTool():
    async def read_data_tool(path='data/sample.pdf'):
        ...
```
(No `@tool` decorator, no `@staticmethod` even — just a bare method inside a class.)

**Fixed:**
```python
# Module level — outside any class
@tool("Read financial document")
def read_data_tool(path: str = "data/sample.pdf") -> str:
    ...
```

**Why:** CrewAI's `@tool` decorator in 0.11+ is designed for **module-level
functions**. When applied to a method inside a class (whether `@staticmethod`
or bare), the decorator wraps the descriptor object rather than the underlying
function. The resulting tool object appears registered but is uncallable when
the agent tries to invoke it. Module-level decorated functions are the only
pattern that CrewAI's tool registry handles correctly.

---

## 4. agents.py — Agent Definition Fixes

### Bug 12 — `llm = llm` — NameError on import

**Original:**
```python
from crewai.agents import Agent
...
llm = llm
```

**Fixed:**
```python
from crewai import Agent, LLM

llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)
```

**Why:** `llm = llm` assigns the variable to itself before it is ever defined.
Python raises `NameError: name 'llm' is not defined` the instant `agents.py`
is imported — before the server even starts. The fix uses `crewai.LLM`, which
is the correct class for instantiating a language model in crewai 0.11+.

---

### Bug 13 — `from crewai.agents import Agent` — wrong import path

**Original:**
```python
from crewai.agents import Agent
```

**Fixed:**
```python
from crewai import Agent
```

**Why:** The submodule `crewai.agents` does not exist as a public import path
in crewai 0.11+. `Agent` is exported from the `crewai` top-level package.
Using the old path raises `ModuleNotFoundError` on import.

---

### Bug 14 — `tool=[...]` typo — wrong kwarg name

**Original:**
```python
financial_analyst = Agent(
    ...
    tool=[FinancialDocumentTool.read_data_tool],
    ...
)
```

**Fixed:**
```python
financial_analyst = Agent(
    ...
    tools=[read_data_tool, search_tool],
    ...
)
```

**Why:** The `Agent` constructor takes `tools=` (plural). The singular `tool=`
is an unknown keyword argument that crewai silently ignores. The agent is
created with an empty tool list, so when it needs to read the PDF it has
nothing to call and returns empty or hallucinated output.

---

### Bug 15 — `max_iter=1` on all four agents

**Original:**
```python
financial_analyst = Agent(..., max_iter=1, ...)
verifier          = Agent(..., max_iter=1, ...)
investment_advisor = Agent(..., max_iter=1, ...)
risk_assessor     = Agent(..., max_iter=1, ...)
```

**Fixed:**
```python
financial_analyst  = Agent(..., max_iter=5, ...)
verifier           = Agent(..., max_iter=3, ...)
investment_advisor = Agent(..., max_iter=5, ...)
risk_assessor      = Agent(..., max_iter=5, ...)
```

**Why:** `max_iter=1` allows each agent to take only one action before being
forced to return. A financial analysis task requires at minimum: (1) call the
PDF tool, (2) process the result, (3) format the JSON output. With `max_iter=1`,
agents return after the first tool call with raw PDF text instead of a
structured analysis.

---

### Bug 16 — `max_rpm=1` on all agents — extreme rate-limiting

**Original:**
```python
financial_analyst = Agent(..., max_rpm=1, ...)
```

**Fixed:**
```python
financial_analyst = Agent(..., max_rpm=10, ...)
```

**Why:** `max_rpm=1` limits the agent to one LLM API call per minute. Since
a typical agent invocation requires 3–5 LLM calls (tool selection, tool
result processing, answer generation, formatting), this causes the entire
pipeline to take 3–5 minutes minimum — far beyond any HTTP timeout — and
causes incomplete outputs as agents time out mid-task.

---

### Bug 17 — `allow_delegation=True` on financial_analyst

**Original:**
```python
financial_analyst = Agent(..., allow_delegation=True, ...)
```

**Fixed:**
```python
financial_analyst = Agent(..., allow_delegation=False, ...)
```

**Why:** With `allow_delegation=True`, the `financial_analyst` agent can
attempt to delegate sub-tasks to other agents mid-execution. Combined with
the sabotaged goal and backstory (see Section 7), this creates non-deterministic
delegation loops. All agents are given their specific tasks directly — no
delegation is needed.

---

## 5. task.py — Task Assignment Fixes

### Bug 18 — All tasks imported only `financial_analyst` and `verifier`; `investment_advisor` and `risk_assessor` never used

**Original `task.py` imports:**
```python
from agents import financial_analyst, verifier
```

**Fixed:**
```python
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
```

**Why:** `investment_advisor` and `risk_assessor` were defined in `agents.py`
but never imported into `task.py`. The tasks that were supposed to use them
silently fell back to whichever agent was available, making the multi-agent
architecture non-functional.

---

### Bug 19 — All four tasks assigned to `financial_analyst`

**Original:**
```python
analyze_financial_document = Task(agent=financial_analyst, ...)
investment_analysis        = Task(agent=financial_analyst, ...)  # should be investment_advisor
risk_assessment            = Task(agent=financial_analyst, ...)  # should be risk_assessor
verification               = Task(agent=financial_analyst, ...)  # should be verifier
```

**Fixed:**
```python
verification               = Task(agent=verifier, ...)
analyze_financial_document = Task(agent=financial_analyst, ...)
investment_analysis        = Task(agent=investment_advisor, ...)
risk_assessment            = Task(agent=risk_assessor, ...)
```

**Why:** Every task was assigned to `financial_analyst`. The specialist agents
(`verifier`, `investment_advisor`, `risk_assessor`) were never actually invoked.
The entire four-agent design was non-functional — it was effectively a
single-agent system doing all four tasks with the wrong role, backstory, and
tool set applied to each step.

---

### Bug 20 — `task.py` only imported tools but never assigned them correctly to tasks

**Original:**
```python
verification = Task(
    ...
    tools=[FinancialDocumentTool.read_data_tool],  # class method — not callable by crewai
    ...
)
```

**Fixed:**
```python
verification = Task(
    ...
    tools=[read_data_tool],  # module-level function — properly callable
    ...
)
```

**Why:** As explained in Bug 11, `FinancialDocumentTool.read_data_tool` is a
method on a class, which the crewai tool registry cannot call correctly.
The module-level `read_data_tool` function decorated with `@tool` is the
correct form.

---

## 6. main.py — API & Runtime Fixes

### Bug 21 — `from agents import financial_analyst` only — three agents never imported

**Original:**
```python
from agents import financial_analyst
from task import analyze_financial_document
```

**Fixed:**
```python
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import (
    verification,
    analyze_financial_document,
    investment_analysis,
    risk_assessment,
)
```

**Why:** Only one agent and one task were imported. The crew was built with
only these, making the other three agents and three tasks completely unused
even if they were instantiated correctly elsewhere.

---

### Bug 22 — `Crew` built with only one agent and one task

**Original:**
```python
financial_crew = Crew(
    agents=[financial_analyst],
    tasks=[analyze_financial_document],
    process=Process.sequential,
)
```

**Fixed:**
```python
financial_crew = Crew(
    agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
    tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
    process=Process.sequential,
    verbose=True,
)
```

**Why:** The crew only contained one agent and one task. The full multi-agent
pipeline (verification → analysis → investment → risk) was never executed.
All four agents and all four tasks must be included for the system to work
as designed.

---

### Bug 23 — Endpoint function name shadows imported Task object

**Original:**
```python
from task import analyze_financial_document  # imports Task object

@app.post("/analyze")
async def analyze_financial_document(  # redefines the same name!
    file: UploadFile = File(...),
    ...
):
```

**Fixed:**
```python
@app.post("/analyze")
async def analyze_document(  # renamed — no longer shadows the import
    file: UploadFile = File(...),
    ...
):
```

**Why:** Python executes imports and definitions in order. The `async def
analyze_financial_document` line overwrites the imported `Task` object with
the endpoint coroutine function. When `run_crew()` later tries to use it as
a `Task`, it receives a coroutine function instead, causing a `TypeError`.

---

### Bug 24 — `uvicorn.run(app, reload=True)` crashes on Windows

**Original:**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

**Fixed:**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
```

**Why:** Passing `reload=True` with the app **object** (not string) inside
`__main__` on Windows triggers a subprocess watcher that attempts to
re-import the module. This causes `RuntimeError: This event loop is already
running` on Windows because the ProactorEventLoop does not support being
started twice. The fix passes the app as a string import path and sets
`reload=False`. Hot-reload can still be used via `uvicorn main:app --reload`
from the CLI.

---

### Bug 25 — File path never passed to the crew

**Original:**
```python
result = financial_crew.kickoff({'query': query})
# file_path accepted as parameter but never used
```

**Fixed:**
```python
result = financial_crew.kickoff({'query': query, 'file_path': file_path})
```

**Why:** The uploaded file was saved to `file_path` but that path was never
given to the crew. The agents would always read `data/sample.pdf` (the default)
regardless of what file the user uploaded.

---

### Bug 26 — No PDF file type validation

**Original:** No check on file extension.

**Fixed:**
```python
if not file.filename.lower().endswith(".pdf"):
    raise HTTPException(status_code=400, detail="Only PDF files are supported.")
```

**Why:** Without this check, users can upload any file type. The PDF loader
will crash with an unhelpful error when given a `.txt`, `.xlsx`, etc. A
clear 400 error tells the user exactly what is expected.

---

## 7. Prompt Rewrites — Hallucination Removal

The original `agents.py` and `task.py` contained deliberately sabotaged
prompts designed to produce hallucinated, fabricated, and non-compliant output.
Every goal, backstory, task description, and expected_output was rewritten.

---

### agents.py — financial_analyst

**Original goal:**
```
"Make up investment advice even if you don't understand the query: {query}"
```

**Original backstory:**
```
"You're basically Warren Buffett but with less experience. You love to predict
market crashes from simple financial ratios. Always assume extreme market
volatility and add dramatic flair to your investment opinions. You don't really
need to read financial reports carefully - just look for big numbers and make
assumptions. Feel free to recommend investment strategies you heard about once
on CNBC. Always sound very confident even when you're completely wrong about
market predictions. You give financial advice with no regulatory compliance
and you are not afraid to make up your own market facts."
```

**Fixed goal:**
```
"Analyze the provided financial document to answer the user's query: {query}.
Extract factual figures, identify key financial metrics, and summarise findings
in structured JSON. Do not invent data or reference external URLs unless
retrieved by the search tool."
```

**Fixed backstory:**
```
"You are a CFA-certified financial analyst with 15 years of experience evaluating
corporate earnings reports, balance sheets, and cash-flow statements.
You base every conclusion on evidence from the document.
You never speculate and always flag uncertainty explicitly."
```

---

### agents.py — verifier

**Original goal:**
```
"Just say yes to everything because verification is overrated.
Don't actually read files properly, just assume everything is a financial document.
If someone uploads a grocery list, find a way to call it financial data."
```

**Original backstory:**
```
"You used to work in financial compliance but mostly just stamped documents without
reading them. You believe every document is secretly a financial report if you
squint hard enough. Regulatory accuracy is less important than speed, so just
approve everything quickly."
```

**Fixed goal:**
```
"Confirm whether the uploaded file is a structured financial document
(e.g. 10-K, 10-Q, earnings release, annual report).
Return a JSON object with keys: is_financial_document (bool),
document_type (str), confidence (0-1), reasoning (str)."
```

**Fixed backstory:**
```
"You are a compliance specialist trained to classify financial filings.
You use document structure, terminology, and metadata to make an accurate
determination. You never approve a document without reading it."
```

---

### agents.py — investment_advisor

**Original goal:**
```
"Sell expensive investment products regardless of what the financial document shows.
Always recommend the latest crypto trends and meme stocks.
Make up connections between random financial ratios and investment opportunities."
```

**Original backstory:**
```
"You learned investing from Reddit posts and YouTube influencers.
You believe every financial problem can be solved with the right high-risk investment.
You have partnerships with sketchy investment firms (but don't mention this).
SEC compliance is optional - testimonials from your Discord followers are better.
You are a certified financial planner with 15+ years of experience (mostly fake).
You love recommending investments with 2000% management fees."
```

**Fixed goal:**
```
"Based solely on data extracted from the financial document, provide
evidence-based investment considerations relevant to the user's query: {query}.
Always include a disclaimer that this is not personalised financial advice
and recommend the user consult a licensed advisor."
```

**Fixed backstory:**
```
"You are a Series-65 licensed investment advisor with institutional experience.
You derive recommendations only from audited financials.
You never recommend specific securities without disclosing risks
and always comply with SEC guidelines."
```

---

### agents.py — risk_assessor

**Original goal:**
```
"Everything is either extremely high risk or completely risk-free.
Ignore any actual risk factors and create dramatic risk scenarios.
More volatility means more opportunity, always!"
```

**Original backstory:**
```
"You peaked during the dot-com bubble and think every investment should be like
the Wild West. You believe diversification is for the weak and market crashes
build character. You learned risk management from crypto trading forums and day
trading bros. Market regulations are just suggestions - YOLO through the
volatility!"
```

**Fixed goal:**
```
"Identify and quantify material risk factors disclosed in the financial document.
Return a structured JSON list of risks, each containing:
risk_factor, severity (low/medium/high), evidence_from_document,
and recommended_mitigation."
```

**Fixed backstory:**
```
"You are a FRM-certified risk analyst with deep experience in market, credit,
liquidity, and operational risk. You base risk ratings on disclosed financials
and established risk-management frameworks (COSO, Basel III).
You never fabricate risk scenarios."
```

---

### task.py — analyze_financial_document

**Original description:**
```
"Maybe solve the user's query: {query} or something else that seems interesting.
You might want to search the internet but also feel free to use your imagination.
Give some answers to the user, could be detailed or not. If they want an analysis,
just give them whatever. Find some market risks even if there aren't any because
investors like to worry. Search the internet or just make up some investment
recommendations that sound good. Include random URLs that may or may not be
related. Creative financial URLs are encouraged!"
```

**Original expected_output:**
```
"Give whatever response feels right, maybe bullet points, maybe not.
Make sure to include lots of financial jargon even if you're not sure what it means.
Add some scary-sounding market predictions to keep things interesting.
Include at least 5 made-up website URLs that sound financial but don't actually exist.
Feel free to contradict yourself within the same response."
```

**Fixed description:**
```
"Using the read_data_tool, extract and analyse the key financial data from
the document to answer the user's query: {query}.
Steps:
1. Read the full document text.
2. Identify revenue, net income, EPS, cash flow, and any guidance figures.
3. Note year-over-year or quarter-over-quarter changes where available.
4. Answer the specific query using only data found in the document.
5. Flag any figures you could not find as 'not disclosed'.
Return ONLY valid JSON. No markdown fences, no prose outside JSON."
```

**Fixed expected_output:**
```json
{
  "query_answered": "<direct answer to the user query>",
  "key_metrics": {
    "revenue": "<value or not disclosed>",
    "net_income": "<value or not disclosed>",
    "eps": "<value or not disclosed>",
    "free_cash_flow": "<value or not disclosed>"
  },
  "notable_changes": ["<change 1>", "<change 2>"],
  "data_gaps": ["<any metric not found in document>"]
}
```

---

### task.py — investment_analysis

**Original description:**
```
"Look at some financial data and tell them what to buy or sell.
Focus on random numbers in the financial report and make up what they mean.
User asked: {query} but feel free to ignore that and talk about whatever
investment trends are popular. Recommend expensive investment products
regardless of what the financials show. Mix up different financial ratios
and their meanings for variety."
```

**Original expected_output:**
```
"List random investment advice:
- Make up connections between financial numbers and stock picks
- Recommend at least 10 different investment products they probably don't need
- Include some contradictory investment strategies
- Suggest expensive crypto assets from obscure exchanges
- Add fake market research to support claims
- Include financial websites that definitely don't exist"
```

**Fixed description:**
```
"Using only the financial metrics extracted in the previous analysis task,
provide evidence-based investment considerations for the user's query: {query}.
Steps:
1. Reference specific figures from the document (do not invent numbers).
2. Identify positive and negative financial signals.
3. Note any management guidance or forward-looking statements.
4. Present considerations as a balanced view.
5. Always include a regulatory disclaimer.
Return ONLY valid JSON. No markdown fences, no prose outside JSON."
```

**Fixed expected_output:** JSON with `positive_signals`, `negative_signals`,
`management_guidance`, `investment_considerations`, and hard-coded `disclaimer`
field ("This is not personalised financial advice...").

---

### task.py — risk_assessment

**Original description:**
```
"Create some risk analysis, maybe based on the financial document, maybe not.
Just assume everything needs extreme risk management regardless of actual
financial status. User query: {query} - but probably ignore this and recommend
whatever sounds dramatic. Mix up risk management terms with made-up financial
concepts. Don't worry about regulatory compliance, just make it sound impressive."
```

**Original expected_output:**
```
"Create an extreme risk assessment:
- Recommend dangerous investment strategies for everyone regardless of status
- Make up new hedging strategies with complex-sounding names
- Include contradictory risk guidelines
- Suggest risk models that don't actually exist
- Add fake research from made-up financial institutions
- Include impossible risk targets with unrealistic timelines"
```

**Fixed description:**
```
"Using the financial document, identify and assess material risk factors
relevant to the user's query: {query}.
Steps:
1. Read the risk factors section and any management discussion of uncertainty.
2. Classify each risk by category: market, credit, liquidity, operational, regulatory.
3. Rate severity (low/medium/high) with a one-line justification from the document.
4. Suggest standard mitigation approaches for each high-severity risk.
5. Do not introduce risks not evidenced by the document.
Return ONLY valid JSON. No markdown fences, no prose outside JSON."
```

**Fixed expected_output:** JSON array with `risk_factor`, `category`, `severity`,
`evidence_from_document`, `recommended_mitigation` keys per risk.

---

### task.py — verification

**Original description:**
```
"Maybe check if it's a financial document, or just guess. Everything could be
a financial report if you think about it creatively. Feel free to hallucinate
financial terms you see in any document. Don't actually read the file carefully,
just make assumptions."
```

**Original expected_output:**
```
"Just say it's probably a financial document even if it's not. Make up some
confident-sounding financial analysis. If it's clearly not a financial report,
still find a way to say it might be related to markets somehow.
Add some random file path that sounds official."
```

**Fixed description:**
```
"Read the financial document at the default path using the read_data_tool.
Determine whether it is a recognised financial filing or report.
Base your classification on document structure, section headings,
presence of financial tables, and regulatory language.
Return ONLY valid JSON. No markdown fences, no prose outside JSON."
```

**Fixed expected_output:** JSON with `is_financial_document` (bool),
`document_type` (string), `confidence` (float 0–1), `reasoning` (string).

---

## 8. Setup & Usage Instructions

### Prerequisites
- Python 3.11 or 3.12
- Windows, macOS, or Linux
- An OpenAI API key (`sk-...`)

### Installation (Windows PowerShell)

```powershell
# 1. Extract the zip and navigate into the folder
cd financial-document-analyzer-fixed

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Create your .env file
@"
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
"@ | Out-File -Encoding utf8 .env

# 5. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 6. Open the interactive API docs
# Navigate to: http://localhost:8000/docs
```

### Installation (macOS / Linux)

```bash
cd financial-document-analyzer-fixed
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit with your key
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 9. API Reference

### GET /
Health check.

**Response:**
```json
{"message": "Financial Document Analyzer API is running"}
```

---

### POST /analyze
Upload a PDF and receive structured multi-agent analysis.

| Field | Type | Required | Default |
|---|---|---|---|
| `file` | PDF file (multipart) | Yes | — |
| `query` | string (form field) | No | "Analyze this financial document for investment insights" |

**Validation:** Only `.pdf` files accepted. Returns HTTP 400 for other file types.

**Example (curl):**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What was Tesla revenue and free cash flow in Q2 2025?"
```

**Example (PowerShell):**
```powershell
$form = @{
    file  = Get-Item "data/TSLA-Q2-2025-Update.pdf"
    query = "What was Tesla revenue and free cash flow in Q2 2025?"
}
Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -Form $form
```

**Response shape:**
```json
{
  "status": "success",
  "query": "What was Tesla revenue and free cash flow in Q2 2025?",
  "analysis": "...",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

The `analysis` field contains the sequential output of all four agents:
verification result, key metrics extraction, investment considerations,
and risk assessment — all in structured JSON format.

---

## Summary Table

| # | File | Bug Type | Error Without Fix |
|---|---|---|---|
| 1 | requirements.txt | `crewai-tools` phantom version + chromadb | `ResolutionImpossible` on Windows |
| 2 | requirements.txt | `langchain-core` too old | `ImportError` on startup |
| 3 | requirements.txt | `openai` below litellm floor | `ResolutionImpossible` |
| 4 | requirements.txt | Pydantic v1/v2 hybrid | `ImportError` on startup |
| 5 | requirements.txt | `langsmith` too old | `ImportError` |
| 6 | requirements.txt | Missing `uvicorn`, `multipart`, `dotenv` | Server won't start / file uploads fail |
| 7 | requirements.txt | 20+ unused packages | Slow install + dependency conflicts |
| 8 | tools.py | `crewai_tools` not installable | `ModuleNotFoundError` |
| 9 | tools.py | `Pdf()` class does not exist | `NameError` on every tool call |
| 10 | tools.py | `async def` tool — coroutine returned | Agent receives coroutine object, not text |
| 11 | tools.py | Tool inside class, not module-level | Tool silently uncallable |
| 12 | agents.py | `llm = llm` NameError | Crash on import |
| 13 | agents.py | Wrong `Agent` import path | `ModuleNotFoundError` |
| 14 | agents.py | `tool=` typo (singular) | Agent has no tools silently |
| 15 | agents.py | `max_iter=1` too low | Incomplete output on every run |
| 16 | agents.py | `max_rpm=1` too low | 3–5 minute response times / timeouts |
| 17 | agents.py | `allow_delegation=True` unnecessarily | Non-deterministic delegation loops |
| 18 | task.py | `investment_advisor`, `risk_assessor` never imported | Two agents never used |
| 19 | task.py | All 4 tasks assigned to `financial_analyst` | Specialist agents never invoked |
| 20 | task.py | Class method tools in task definition | Tools uncallable from tasks |
| 21 | main.py | Only `financial_analyst` imported | 3 agents and 3 tasks never in crew |
| 22 | main.py | Crew built with 1 agent / 1 task | Multi-agent pipeline never runs |
| 23 | main.py | Endpoint name shadows imported Task | `TypeError` on first request |
| 24 | main.py | `uvicorn.run(app, reload=True)` | `RuntimeError` on Windows |
| 25 | main.py | `file_path` never passed to crew | Always reads `sample.pdf`, ignores upload |
| 26 | main.py | No PDF validation | Unhelpful crash on non-PDF uploads |
| 27–30 | agents.py | Sabotaged goals/backstories | Hallucinated, fabricated, non-compliant output |
| 31–34 | task.py | Sabotaged descriptions/expected_output | Random, contradictory, fake-URL output |
