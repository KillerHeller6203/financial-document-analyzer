from crewai import Task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool

verification = Task(
    description=(
        "Read the financial document at the default path using the read_data_tool. "
        "Determine whether it is a recognised financial filing or report. "
        "Base your classification on document structure, section headings, "
        "presence of financial tables, and regulatory language."
    ),
    expected_output=(
        "A JSON object with the following keys:\n"
        "{\n"
        '  "is_financial_document": true | false,\n'
        '  "document_type": "<e.g. Earnings Release | 10-Q | Annual Report | Unknown>",\n'
        '  "confidence": <float 0.0-1.0>,\n'
        '  "reasoning": "<one sentence citing specific evidence from the document>"\n'
        "}"
    ),
    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

analyze_financial_document = Task(
    description=(
        "Using the read_data_tool, extract and analyse the key financial data from "
        "the document to answer the user's query: {query}.\n"
        "Steps:\n"
        "1. Read the full document text.\n"
        "2. Identify revenue, net income, EPS, cash flow, and any guidance figures.\n"
        "3. Note year-over-year or quarter-over-quarter changes where available.\n"
        "4. Answer the specific query using only data found in the document.\n"
        "5. Flag any figures you could not find as 'not disclosed'."
    ),
    expected_output=(
        "A JSON object with the following keys:\n"
        "{\n"
        '  "query_answered": "<direct answer to the user query>",\n'
        '  "key_metrics": {\n'
        '    "revenue": "<value or not disclosed>",\n'
        '    "net_income": "<value or not disclosed>",\n'
        '    "eps": "<value or not disclosed>",\n'
        '    "free_cash_flow": "<value or not disclosed>"\n'
        "  },\n"
        '  "notable_changes": ["<change 1>", "<change 2>"],\n'
        '  "data_gaps": ["<any metric not found in document>"]\n'
        "}"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

investment_analysis = Task(
    description=(
        "Using only the financial metrics extracted in the previous analysis task, "
        "provide evidence-based investment considerations for the user's query: {query}.\n"
        "Steps:\n"
        "1. Reference specific figures from the document (do not invent numbers).\n"
        "2. Identify positive and negative financial signals.\n"
        "3. Note any management guidance or forward-looking statements.\n"
        "4. Present considerations as a balanced view.\n"
        "5. Always include a regulatory disclaimer."
    ),
    expected_output=(
        "A JSON object with the following keys:\n"
        "{\n"
        '  "positive_signals": ["<signal with supporting figure>"],\n'
        '  "negative_signals": ["<signal with supporting figure>"],\n'
        '  "management_guidance": "<summary or not provided>",\n'
        '  "investment_considerations": "<balanced 2-3 sentence summary>",\n'
        '  "disclaimer": "This is not personalised financial advice. '
        'Consult a licensed financial advisor before making investment decisions."\n'
        "}"
    ),
    agent=investment_advisor,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

risk_assessment = Task(
    description=(
        "Using the financial document, identify and assess material risk factors "
        "relevant to the user's query: {query}.\n"
        "Steps:\n"
        "1. Read the risk factors section and any management discussion of uncertainty.\n"
        "2. Classify each risk by category: market, credit, liquidity, operational, regulatory.\n"
        "3. Rate severity (low/medium/high) with a one-line justification from the document.\n"
        "4. Suggest standard mitigation approaches for each high-severity risk.\n"
        "5. Do not introduce risks not evidenced by the document."
    ),
    expected_output=(
        "A JSON array of risk objects:\n"
        "[\n"
        "  {\n"
        '    "risk_factor": "<name>",\n'
        '    "category": "<market | credit | liquidity | operational | regulatory>",\n'
        '    "severity": "<low | medium | high>",\n'
        '    "evidence_from_document": "<direct quote or paraphrase>",\n'
        '    "recommended_mitigation": "<standard industry practice>"\n'
        "  }\n"
        "]"
    ),
    agent=risk_assessor,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)
