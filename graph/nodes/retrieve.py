import os
from typing import Any, Dict
from graph.state import GraphState
from graph.chains.retriever import retriever

DEBUG_DIR = "debug"
DEBUG_FILE = os.path.join(DEBUG_DIR, "retrieved_docs.txt")

def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---NODE: RETRIEVING DOCUMENTS FROM CHROMA---")
    question = state["question"]
    
    # Fetch documents from our database
    documents = retriever.invoke(question)
    
    # Print retrieved documents for debugging
    print(f"  -> Retrieved {len(documents)} documents")
    for i, doc in enumerate(documents):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "N/A")
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"  -> Doc {i+1} | source: {source} | page: {page}")
        print(f"     Preview: {preview}...")
    
    # Save full documents to file for offline debugging
    os.makedirs(DEBUG_DIR, exist_ok=True)
    with open(DEBUG_FILE, "w", encoding="utf-8") as f:
        f.write(f"QUERY: {question}\n")
        f.write(f"TOTAL DOCUMENTS RETRIEVED: {len(documents)}\n")
        f.write("=" * 60 + "\n\n")
        for i, doc in enumerate(documents):
            f.write(f"--- DOCUMENT {i+1} ---\n")
            f.write(f"Source: {doc.metadata.get('source', 'unknown')}\n")
            f.write(f"Page: {doc.metadata.get('page', 'N/A')}\n")
            f.write(f"Content:\n{doc.page_content}\n")
            f.write("\n" + "-" * 40 + "\n\n")
    print(f"  -> Saved full documents to {DEBUG_FILE}")
    
    # Pass retrieved chunks down to the next node in the graph state
    return {"documents": documents, "question": question}