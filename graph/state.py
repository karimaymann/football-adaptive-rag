from typing import List, TypedDict

class GraphState(TypedDict):
    """
    Represents the state of our advanced self-correcting RAG graph.
    """
    question: str          # The original query typed by the user
    generation: str        # The latest text response written by our generator LLM
    web_search: bool       # A binary flag to trigger the Corrective RAG fallback path
    documents: List[str]   # The collection of text chunks currently available for context