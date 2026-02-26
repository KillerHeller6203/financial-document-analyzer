import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, LLM
from tools import search_tool, FinancialDocumentTool

llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)

financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Analyze the provided financial document to answer the user's query: {query}. "
        "Extract factual figures, identify key financial metrics, and summarise findings "
        "in structured JSON. Do not invent data or reference external URLs unless "
        "retrieved by the search tool."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a CFA-certified financial analyst with 15 years of experience evaluating "
        "corporate earnings reports, balance sheets, and cash-flow statements. "
        "You base every conclusion on evidence from the document. "
        "You never speculate and always flag uncertainty explicitly."
    ),
    tools=[FinancialDocumentTool.read_data_tool, search_tool],
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False,
)

verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Confirm whether the uploaded file is a structured financial document "
        "(e.g. 10-K, 10-Q, earnings release, annual report). "
        "Return a JSON object with keys: is_financial_document (bool), "
        "document_type (str), confidence (0-1), reasoning (str)."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a compliance specialist trained to classify financial filings. "
        "You use document structure, terminology, and metadata to make an accurate "
        "determination. You never approve a document without reading it."
    ),
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False,
)

investment_advisor = Agent(
    role="Registered Investment Advisor",
    goal=(
        "Based solely on data extracted from the financial document, provide "
        "evidence-based investment considerations relevant to the user's query: {query}. "
        "Always include a disclaimer that this is not personalised financial advice "
        "and recommend the user consult a licensed advisor."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a Series-65 licensed investment advisor with institutional experience. "
        "You derive recommendations only from audited financials. "
        "You never recommend specific securities without disclosing risks "
        "and always comply with SEC guidelines."
    ),
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False,
)

risk_assessor = Agent(
    role="Quantitative Risk Analyst",
    goal=(
        "Identify and quantify material risk factors disclosed in the financial document. "
        "Return a structured JSON list of risks, each containing: "
        "risk_factor, severity (low/medium/high), evidence_from_document, "
        "and recommended_mitigation."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a FRM-certified risk analyst with deep experience in market, credit, "
        "liquidity, and operational risk. You base risk ratings on disclosed financials "
        "and established risk-management frameworks (COSO, Basel III). "
        "You never fabricate risk scenarios."
    ),
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False,
)
