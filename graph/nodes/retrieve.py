from typing import Any, Dict
from langchain_core.documents import Document
from graph.state import GraphState
from graph.chains.retriever import retriever

def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---NODE: RUNNING CHAINED KNOWLEDGE RETRIEVAL---")
    question = state["question"]
    existing_docs = state.get("documents", []) or []
    
    # Isolate previous database inputs from the global notebook
    sql_facts = ""
    for doc in existing_docs:
        if doc.metadata.get("source") == "sql_database":
            sql_facts += f"\nResolved Data Facts: {doc.page_content}"
            
    search_query = question
    if sql_facts:
        # Augment the text search query vector with your fresh SQL results
        search_query = f"{question} {sql_facts}"
        print(f"  -> Augmented Vector Search Query: {search_query}")
        
    chroma_documents = retriever.invoke(search_query)
    
    # Safely merge both historical structures back into the graph notebook
    return {"documents": existing_docs + chroma_documents, "question": question}