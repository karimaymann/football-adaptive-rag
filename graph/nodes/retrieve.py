from typing import Any, Dict
from graph.state import GraphState
from graph.chains.retriever import retriever

def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---NODE: RETRIEVING DOCUMENTS FROM CHROMA---")
    question = state["question"]
    
    # Fetch documents from our database
    documents = retriever.invoke(question)
    
    # Pass retrieved chunks down to the next node in the graph state
    return {"documents": documents, "question": question}