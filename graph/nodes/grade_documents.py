import time
from typing import Any, Dict
from graph.state import GraphState
from graph.chains.document_grader import document_grader_chain

def grade_documents(state: GraphState) -> Dict[str, Any]:
    print("---NODE: GRADING RETRIEVED DOCUMENTS---")
    question = state["question"]
    documents = state["documents"]
    
    filtered_documents = []
    web_search = False
    
    for i, doc in enumerate(documents):
        # Pause before every document invocation except the first to respect the 5 RPM limit
        if i > 0:
            print("  ...Cooling down for 12 seconds to prevent Gemini 429 Rate Limit...")
            time.sleep(12)
            
        # Grade the document text content
        score = document_grader_chain.invoke(
            {"question": question, "document": doc.page_content}
        )
        grade = score.binary_score
        
        if grade == "yes":
            print("  -> DOCUMENT RELEVANT")
            filtered_documents.append(doc)
        else:
            print("  -> DOCUMENT NOT RELEVANT")
            web_search = True
            
    return {"documents": filtered_documents, "question": question, "web_search": web_search}