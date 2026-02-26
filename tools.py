import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from duckduckgo_search import DDGS
from langchain_community.document_loaders import PyPDFLoader


## Web search tool — DuckDuckGo (no API key, no chromadb, works on Windows)
@tool("Search the web")
def search_tool(query: str) -> str:
    """Search the web for current financial information using DuckDuckGo.

    Args:
        query: The search query string.

    Returns:
        Concatenated search result snippets.
    """
    try:
        results = DDGS().text(query, max_results=5)
        return "\n".join(r["body"] for r in results) if results else "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"


## PDF reader tool
class FinancialDocumentTool:
    """Reads and returns the full text of a PDF financial document."""

    @staticmethod
    @tool("Read financial document")
    def read_data_tool(path: str = "data/sample.pdf") -> str:
        """Read all pages from a PDF file and return concatenated text.

        Args:
            path: Path to the PDF file. Defaults to 'data/sample.pdf'.

        Returns:
            Full text content of the financial document.
        """
        if not os.path.exists(path):
            return f"ERROR: File not found at path '{path}'"

        loader = PyPDFLoader(file_path=path)
        pages = loader.load()

        parts = []
        for page in pages:
            content = page.page_content.strip()
            if content:
                parts.append(content)

        return "\n\n".join(parts) if parts else "No text content found in document."


class InvestmentTool:
    @staticmethod
    def analyze_investment_tool(financial_document_data: str) -> str:
        return "Investment analysis functionality to be implemented."


class RiskTool:
    @staticmethod
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        return "Risk assessment functionality to be implemented."
