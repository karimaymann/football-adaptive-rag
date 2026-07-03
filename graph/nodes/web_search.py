from typing import Any, Dict
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from graph.state import GraphState

def web_search(state: GraphState) -> Dict[str, Any]:
    print("---NODE: EXECUTING CORRECTIVE WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])
    
    # Initialize Tavily search tool (returns top 3 web results max)
    web_search_tool = TavilySearchResults(max_results=3)
    search_results = web_search_tool.invoke({"query": question})
    
    # Combine the web result snippets into unified text
    web_results_text = "\n".join([res["content"] for res in search_results])
    
    # Convert into a standard LangChain Document object structure so it fits perfectly
    web_document = Document(page_content=web_results_text, metadata={"source": "tavily"})
    documents.append(web_document)
    
    return {"documents": documents, "question": question}